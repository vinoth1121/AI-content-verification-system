# Architecture

## High-Level Overview

The ACVS is a **monorepo** of six components that share a single REST API
and a single AI detection engine. Clients are thin; all heavy lifting
(auth, persistence, AI inference) happens server-side.

```
┌──────────────────────────────────────────────────────────────────────┐
│                            CLIENTS                                    │
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌──────────────────┐  │
│  │ Android  │  │ Desktop  │  │  Browser   │  │  Admin Dashboard │  │
│  │ (Kotlin) │  │ (Tauri)  │  │  Ext (MV3) │  │   (Next.js 16)   │  │
│  └────┬─────┘  └────┬─────┘  └─────┬──────┘  └────────┬─────────┘  │
│       │             │              │                   │             │
│       └─────────────┴──────────────┴───────────────────┘             │
│                            HTTPS / JWT                                │
└────────────────────────────────────┬─────────────────────────────────┘
                                     │
┌────────────────────────────────────▼─────────────────────────────────┐
│                       BACKEND API (FastAPI)                          │
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │   Auth   │  │   Scan   │  │  Admin   │  │   Meta   │            │
│  │ (JWT+Rfr)│  │ (history)│  │ (RBAC)   │  │ (/health)│            │
│  └──────────┘  └────┬─────┘  └──────────┘  └──────────┘            │
│                     │                                                 │
│                     │  scan_service                                   │
│                     ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                 AI Detection Engine (Python)                    ││
│  │  TextDetector · ImageDetector · AudioDetector · VideoDetector  ││
│  │  FakeNewsDetector · Explainability Layer                        ││
│  └─────────────────────────────────────────────────────────────────┘│
└────────────────────────────┬─────────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────────┐
│            PostgreSQL  ·  Redis  ·  Object Storage                    │
└──────────────────────────────────────────────────────────────────────┘
```

## Layered Backend (Clean Architecture)

The backend follows a four-layer Clean Architecture:

| Layer        | Folder                  | Responsibility                                |
|--------------|-------------------------|-----------------------------------------------|
| API          | `app/api/v1/`           | HTTP routers, request/response DTOs           |
| Service      | `app/services/`         | Business logic, orchestration                 |
| Domain       | `app/models`, `schemas/`| SQLAlchemy ORM + Pydantic DTOs                |
| Infra        | `app/db`, `app/core/`   | DB sessions, security, config, deps           |

**Dependency rule**: outer layers depend on inner layers, never the reverse.
Routers depend on services; services depend on domain + infra; domain
depends on nothing.

### SOLID in practice

- **S**ingle Responsibility — each service has one job (`auth_service`,
  `scan_service`).
- **O**pen/Closed — detectors implement the same `detect(payload) → dict`
  contract; new modalities can be added without touching callers.
- **L**iskov — the lazy wrappers in `engine.py` are behaviourally
  substitutable for the underlying detectors.
- **I**nterface Segregation — `ACVSApi` (Retrofit) only exposes the
  endpoints each Android feature uses, not the whole API surface.
- **D**ependency Inversion — FastAPI routers depend on `SessionLocal`
  abstracted via `Depends(get_db)`; tests swap in an in-memory SQLite.

## AI Engine Design

The engine is a **standalone Python package** (`ai_engine/`) so it can be:

1. Imported in-process by the backend (current default).
2. Deployed as a sidecar service (Phase 2 — for horizontal scaling).
3. Tested independently of the API.

### Detector contract

Every detector returns the same dict shape:

```python
{
    "label": str,            # human | ai_generated | deepfake | suspicious | authentic
    "confidence": float,     # 0.0 - 1.0
    "modality": str,
    "explanation": str,      # human-readable
    "features": dict,        # explainability
    "heatmap_path": str | None,
    "flagged_segments": list[dict] | None,
}
```

This contract is enforced by `ScanResult` Pydantic schema in the backend.
Adding a new modality is purely additive: implement `detect_<modality>`
in `engine.py`, add an endpoint, and the dashboard already knows how to
render the result.

### Explainability

Every detector exposes a `features` dict. The dashboard renders these as
a feature-grid card. The `explanation` string is generated by
`humanize_explanation(positive_signals, negative_signals)` which composes
a short sentence from the top contributing features.

### Why CPU-friendly heuristics?

Production deployments can swap each detector with a transformer-based
variant (e.g. RoBERTa fine-tuned on HC3 for text, EfficientNet for
images) without touching callers. The heuristic baseline lets the system
run anywhere — even on a $5 VPS — for development and small teams.

## Security Architecture

- **Password hashing**: Argon2id (memory-hard, GPU-resistant) via passlib.
- **JWT**: HS256, 15-min access + 7-day refresh, jti claim for revocation.
- **RBAC**: `user` and `admin` roles enforced via `Depends(require_admin)`.
- **Rate limiting**: 60 req/min global, 5 scans/min per user (slowapi).
- **CORS allow-list**: explicit origins only, no `*`.
- **Upload limits**: text 50 KB, image 10 MB, audio 50 MB, video 100 MB.
- **Auto-delete uploads**: media is removed after inference; only the
  verdict is persisted.
- **PII redaction**: log records redact emails and file names.

## Privacy Architecture

- **No content persistence** for image/audio/video scans — only the
  verdict is stored.
- **GDPR-ready**: users can export and delete all their data.
- **On-premise option**: every component can run on a single server
  without any external API calls.

## Deployment Topologies

### Single-server (dev / small team)

```
┌───────────────┐   ┌───────────────┐   ┌──────────┐
│  Next.js dev  │   │  FastAPI      │   │  SQLite  │
│  (port 3000)  │──▶│  (port 8000)  │──▶│  (file)  │
└───────────────┘   └───────────────┘   └──────────┘
```

### Production (multi-tenant)

```
                   ┌──────────────────────────┐
                   │      Load Balancer       │
                   └────────────┬─────────────┘
                                │
       ┌────────────────────────┼────────────────────────┐
       │                        │                        │
┌──────▼──────┐          ┌──────▼──────┐          ┌──────▼──────┐
│  Next.js    │          │  FastAPI    │          │  FastAPI    │
│  (admin)    │          │  (api #1)   │          │  (api #2)   │
└─────────────┘          └──────┬──────┘          └──────┬──────┘
                                │                        │
                       ┌────────┴────────┬───────────────┘
                       │                 │
                ┌──────▼──────┐   ┌──────▼──────┐
                │ PostgreSQL  │   │    Redis    │
                │  (HA)       │   │  (cache+rl) │
                └─────────────┘   └─────────────┘
                                │
                       ┌────────▼────────┐
                       │   AI Engine     │
                       │   (sidecar pods)│
                       └─────────────────┘
```

## Cross-Cutting Concerns

### Observability

- **Structured logging**: loguru with JSON formatter in production.
- **Audit log**: every auth event and scan is persisted with user_id,
  timestamp, and duration.
- **Metrics**: Prometheus endpoint (Phase 2).

### Performance

- DB connection pool (size 10, overflow 20).
- Lazy AI-engine imports so API startup is fast.
- TanStack Query on the dashboard with 30-second stale time.
- Tauri native webview for desktop (no Chromium overhead).

### Scalability

- The backend is **stateless** — JWT + DB-backed sessions let it scale
  horizontally.
- The AI engine can be **sidecar-deployed** (gRPC) for GPU pooling.
- Scan history queries are indexed on `(user_id, created_at)`.

## Trade-offs

| Decision | Reasoning |
|---|---|
| **SQLite in dev, Postgres in prod** | SQLite has zero-config; Postgres gives us row-level locks, JSONB, and replication. SQLAlchemy makes the swap a one-line change. |
| **CPU-only baseline detectors** | Lets the system run on a $5 VPS. Swap-in points for transformer models are documented. |
| **JWT over server sessions** | Stateless → horizontal scaling. Refresh tokens limit blast radius. |
| **Tauri over Electron** | 10× smaller binary, lower memory, memory-safe backend. Trade-off: requires Rust toolchain to build. |
| **Monorepo over polyrepo** | Single PR can touch backend + dashboard + extension. Simplifies CI and version alignment. |
