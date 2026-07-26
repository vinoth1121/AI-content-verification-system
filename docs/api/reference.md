# API Reference (v1)

Base URL: `http://localhost:8000` · All paths prefixed with `/api/v1` ·
All authenticated routes require `Authorization: Bearer <jwt>`.

## Auth

### POST /auth/register
Create a new account. The first user is automatically promoted to admin.

**Body**
```json
{ "email": "user@example.com", "full_name": "Ada Lovelace", "password": "Password123!" }
```

**201 Response**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": 1, "email": "user@example.com", "full_name": "Ada Lovelace", "role": "admin", "is_active": true }
}
```

**Errors**
- 409 Conflict — email already registered
- 422 Unprocessable Entity — validation failed

### POST /auth/login
```json
{ "email": "user@example.com", "password": "Password123!" }
```
Returns the same shape as register. 401 on invalid credentials.

### POST /auth/refresh
```json
{ "refresh_token": "eyJ..." }
```
Returns a fresh `access_token` + `refresh_token` pair.

### GET /auth/me
Returns the current user. Bearer-auth required.

## Scan

### POST /scan/text
```json
{ "text": "It is important to note that…", "title": "optional" }
```

### POST /scan/fake-news
Same body as `/scan/text`. Runs fake-news stylometric + claim-structure analysis.

### POST /scan/image
Multipart form-data, field name `file`. PNG / JPEG / WEBP up to 10 MB.

### POST /scan/audio
Multipart form-data, field name `file`. WAV / MP3 / FLAC up to 50 MB.

### POST /scan/video
Multipart form-data, field name `file`. MP4 / WEBM up to 100 MB.

### Response shape (all scan endpoints)
```json
{
  "id": 42,
  "modality": "text",
  "status": "completed",
  "confidence": 0.7234,
  "label": "ai_generated",
  "explanation": "Signals suggesting AI-generation: …",
  "result": { "features": { "burstiness": 0.32, "lexical_diversity": 0.71, "..." } },
  "created_at": "2026-07-26T10:30:00Z",
  "completed_at": "2026-07-26T10:30:01Z",
  "duration_ms": 47
}
```

### GET /scan/history
Query params: `page` (default 1), `page_size` (default 20, max 100),
`modality` (optional: text | image | audio | video | fake_news).

### GET /scan/history/{id}
Returns a single scan. 404 if not owned by current user.

## Admin (admin role only)

### GET /admin/stats
Returns platform-wide KPIs.

### GET /admin/users
Paginated list of all users. Query: `page`, `page_size`.

### POST /admin/users/{id}/toggle-active
Enable / disable a user. Returns `{ "id": 4, "is_active": false }`.

### POST /admin/users/{id}/promote
Toggle admin role. Returns `{ "id": 4, "role": "admin" }`.

## Meta

### GET /health
```json
{ "status": "ok", "env": "development", "version": "0.1.0" }
```

### GET /
Discovery links.

## Error envelope

All errors return JSON:
```json
{ "detail": "Human-readable message" }
```

HTTP status codes follow REST conventions:
- 400 Bad Request — invalid input
- 401 Unauthorized — missing / invalid token
- 403 Forbidden — insufficient role
- 404 Not Found — resource doesn't exist
- 409 Conflict — duplicate resource
- 413 Payload Too Large — upload exceeded limit
- 422 Unprocessable Entity — validation failed
- 429 Too Many Requests — rate limited
- 500 Internal Server Error — unhandled
