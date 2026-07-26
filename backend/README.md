# Backend — FastAPI

The backend is a FastAPI service that exposes the REST API consumed by every
client (admin dashboard, Android, desktop, browser extension).

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # edit JWT_SECRET etc.
uvicorn app.main:app --reload --port 8000
```

Swagger UI: <http://localhost:8000/docs>
ReDoc: <http://localhost:8000/redoc>

## Project layout

```
backend/
├── app/
│   ├── api/v1/                # HTTP routers (auth, scan, admin, meta)
│   ├── core/                  # config, security, deps
│   ├── db/                    # engine, session, Base
│   ├── models/                # SQLAlchemy ORM
│   ├── schemas/               # Pydantic DTOs
│   ├── services/              # Business logic (auth_service, scan_service)
│   └── main.py                # App factory
├── tests/                     # pytest + TestClient
├── alembic/                   # Migrations
├── requirements.txt
└── .env.example
```

## API surface (v1)

| Method | Path                       | Description                          | Auth     |
|--------|----------------------------|--------------------------------------|----------|
| POST   | `/api/v1/auth/register`    | Create account (first user = admin)  | Public   |
| POST   | `/api/v1/auth/login`       | Email/password login                 | Public   |
| POST   | `/api/v1/auth/refresh`     | Rotate access token                  | Refresh  |
| GET    | `/api/v1/auth/me`          | Current user                         | Bearer   |
| POST   | `/api/v1/scan/text`        | Detect AI-generated text             | Bearer   |
| POST   | `/api/v1/scan/fake-news`   | Detect misinformation                | Bearer   |
| POST   | `/api/v1/scan/image`       | Detect image deepfakes               | Bearer   |
| POST   | `/api/v1/scan/audio`       | Detect AI-generated audio            | Bearer   |
| POST   | `/api/v1/scan/video`       | Detect video deepfakes               | Bearer   |
| GET    | `/api/v1/scan/history`     | Paginated user scan history          | Bearer   |
| GET    | `/api/v1/scan/history/:id` | Scan detail                          | Bearer   |
| GET    | `/api/v1/admin/stats`      | Platform KPIs                        | Admin    |
| GET    | `/api/v1/admin/users`      | List users                           | Admin    |
| POST   | `/api/v1/admin/users/:id/toggle-active` | Enable/disable user     | Admin    |
| POST   | `/api/v1/admin/users/:id/promote`      | Toggle admin role       | Admin    |

## Tests

```bash
pytest -v
```
