# AI Content Verification System

> Production-ready, cross-platform system for detecting AI-generated text, fake news, deepfake images, deepfake videos, AI-generated audio, and manipulated media.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![Next.js](https://img.shields.io/badge/Next.js-16-black)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688)]()

## Overview

The AI Content Verification System (ACVS) is a privacy-first, cross-platform suite that lets individuals, journalists, enterprises, and platforms verify whether content is human-authored or AI-manipulated. It combines a CPU-friendly AI detection engine, a hardened FastAPI backend, and clients for the web, browser, Android, and desktop.

### Detection Capabilities

| Modality | Method | Confidence Score | Explainability |
|---|---|---|---|
| **AI Text** | Statistical stylometry (perplexity proxy, burstiness, lexical diversity, sentence variance) | 0.00 – 1.00 | Top contributing features |
| **Fake News** | Source credibility + linguistic cues + claim structure analysis | 0.00 – 1.00 | Reasoning chain |
| **Image Deepfake** | Frequency-domain analysis (DCT), noise residual, ELA-like artifacts | 0.00 – 1.00 | Heatmap + contributing features |
| **Video Deepfake** | Per-frame image analysis + temporal consistency | 0.00 – 1.00 | Flagged frames |
| **Audio Deepfake** | Spectral analysis, MFCC variance, pitch contour smoothness | 0.00 – 1.00 | Spectrogram + flagged segments |

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                    │
│  Android (Kotlin)  •  Desktop (Tauri)  •  Browser Ext (MV3)       │
│  Admin Dashboard (Next.js)                                         │
└──────────────────────────┬─────────────────────────────────────────┘
                           │ HTTPS / JWT
┌──────────────────────────▼─────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                            │
│  Auth (JWT + Refresh)  •  RBAC  •  Rate Limiting  •  Audit Log     │
│  Scan History  •  Notifications  •  Cloud Sync                     │
└──────────────────────────┬─────────────────────────────────────────┘
                           │ Internal gRPC / HTTP
┌──────────────────────────▼─────────────────────────────────────────┐
│                  AI DETECTION ENGINE (Python)                      │
│  TextDetector  •  ImageDetector  •  AudioDetector  •  VideoDetector│
│  FakeNewsDetector  •  Explainability Layer                         │
└──────────────────────────┬─────────────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────────────┐
│            PostgreSQL  •  Redis  •  Object Storage                 │
└────────────────────────────────────────────────────────────────────┘
```

### Clean Architecture Layers (Backend)

1. **API Layer** (`app/api/v1`) — HTTP routers, request/response DTOs
2. **Service Layer** (`app/services`) — Business logic, orchestration
3. **Domain Layer** (`app/models`, `app/schemas`) — SQLAlchemy entities + Pydantic schemas
4. **Infrastructure** (`app/db`, `app/core`) — DB sessions, security, config

## Monorepo Layout

```
AI-content-verification-system/
├── backend/              # FastAPI backend (auth, scan history, REST API)
├── ai-engine/            # Standalone AI detection engine (Python)
├── admin-dashboard/      # Next.js 16 admin dashboard
├── browser-extension/    # Manifest V3 Chrome/Firefox extension
├── android-app/          # Kotlin + Jetpack Compose Android app
├── desktop-app/          # Tauri 2 + React desktop app
├── docs/                 # Architecture, API, deployment docs
├── scripts/              # Build & utility scripts
├── docker-compose.yml
└── README.md
```

## Quick Start

### 1. Backend API + AI Engine

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # edit secrets
uvicorn app.main:app --reload --port 8000
# Swagger UI: http://localhost:8000/docs
```

### 2. Admin Dashboard

```bash
cd admin-dashboard
npm install
cp .env.local.example .env.local
npm run dev                # http://localhost:3000
```

### 3. Browser Extension

```bash
cd browser-extension
npm install
npm run build
# Load `dist/` as an unpacked extension in chrome://extensions
```

See `docs/deployment/` for Android, Desktop, and Docker Compose instructions.

## Security

- Argon2 password hashing (OWASP-recommended)
- JWT access (15 min) + refresh (7 days) tokens
- Rate limiting: 60 req/min per IP, 5 scans/min per user
- All AI inference server-side — model weights never leave the server
- PII auto-redacted from logs
- CORS allow-list, Helmet-style security headers
- Audit log for every authentication & scan event

## Privacy

- No content is stored beyond what the user explicitly saves as "Scan History"
- Uploads for image/audio/video detection are deleted after inference
- User may export and delete all data (GDPR-ready)

## Development Schedule

- **Start:** 2026-07-26
- **End:** 2026-10-20
- **Cadence:** Daily at 17:00 IST

See `docs/ROADMAP.md` for the full sprint plan.

## License

MIT © 2026 AI Content Verification System Contributors
