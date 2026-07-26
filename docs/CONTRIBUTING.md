# Contributing

## Workflow

1. **Fork & clone** the repo.
2. **Create a branch** named `feat/<short-description>` or `fix/<issue-id>`.
3. **Run tests** locally before pushing:
   ```bash
   # Backend + AI engine
   cd backend && pytest
   cd ../ai-engine && pytest

   # Admin dashboard
   cd admin-dashboard && npm run lint && npm run test
   ```
4. **Open a PR** — CI must pass (lint + tests).
5. **Squash-merge** to `main`.

## Code Style

- Python: black + isort + flake8 (line length 100)
- TypeScript / TSX: ESLint + Prettier (Next.js config)
- Kotlin: ktlint
- Rust: rustfmt + clippy

## Commit Messages

Follow Conventional Commits:

```
feat(backend): add /api/v1/scan/video endpoint
fix(dashboard): correct confidence bar color for suspicious label
docs(api): document /admin/users endpoint
refactor(ai-engine): extract normalisation helper from text detector
test(backend): cover JWT refresh flow
chore(deps): bump fastapi to 0.110.1
```

## Project Structure

See `docs/architecture/overview.md` for the full layered architecture.
Each component has its own `README.md` with build instructions.

## Adding a New Detector

1. Implement `detect_<modality>(payload) -> dict` in
   `ai-engine/ai_engine/detectors/<modality>.py`. Follow the contract:
   ```python
   {
       "label": str, "confidence": float, "modality": str,
       "explanation": str, "features": dict,
       "heatmap_path": str | None, "flagged_segments": list[dict] | None,
   }
   ```
2. Add a lazy wrapper in `ai-engine/ai_engine/engine.py`.
3. Add a router endpoint in `backend/app/api/v1/scan.py`.
4. Add a service function in `backend/app/services/scan_service.py`.
5. Add a Pydantic enum entry to `ScanModality` in `app/models/scan.py`.
6. Add tests in `ai-engine/tests/` and `backend/tests/`.
7. Update `docs/api/reference.md`.

## Reporting Bugs

Open an issue with:
- Component (backend / dashboard / extension / android / desktop / ai-engine)
- Version (commit hash or release tag)
- Reproduction steps
- Expected vs actual behaviour
- Logs (redact PII)

## Security Reports

**Do not open public issues for security vulnerabilities.**
Email security@acvs.io with details. We respond within 48 hours and
credit reporters in release notes.
