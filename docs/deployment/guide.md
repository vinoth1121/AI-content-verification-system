# Deployment

## Development (single machine)

### Prerequisites
- Python 3.11+
- Node 20+ / Bun
- 4 GB RAM

### Steps
```bash
# 1. Backend + AI engine
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit JWT_SECRET in .env
uvicorn app.main:app --reload --port 8000

# 2. Admin dashboard (separate terminal)
cd admin-dashboard
npm install
cp .env.local.example .env.local
npm run dev

# 3. Browser extension
cd browser-extension
npm install
npm run build
# Load dist/ as unpacked extension in chrome://extensions
```

## Docker Compose (staging)

```yaml
version: "3.9"
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql+psycopg2://acvs:acvs@db:5432/acvs
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=${JWT_SECRET}
    depends_on: [db, redis]

  admin-dashboard:
    build: ./admin-dashboard
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on: [backend]

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: acvs
      POSTGRES_PASSWORD: acvs
      POSTGRES_DB: acvs
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    volumes: ["redisdata:/data"]

volumes:
  pgdata:
  redisdata:
```

```bash
docker compose up -d
```

## Production Checklist

- [ ] Postgres HA (managed RDS / Cloud SQL)
- [ ] Redis HA (managed ElastiCache / Memorystore)
- [ ] HTTPS termination at load balancer
- [ ] Strong `JWT_SECRET` (≥ 48 chars, generated via `secrets.token_urlsafe(48)`)
- [ ] CORS allow-list set to production domains
- [ ] Rate limiting tuned (`RATE_LIMIT_GLOBAL`, `RATE_LIMIT_SCAN`)
- [ ] Object storage for media uploads (S3 / GCS) — Phase 2
- [ ] Prometheus + Grafana for metrics — Phase 2
- [ ] Log aggregation (Loki / ELK) — Phase 2
- [ ] Database backups (daily snapshot + WAL archiving)
- [ ] AI engine sidecar pool (if scaling beyond 1 backend pod) — Phase 2

## Mobile (Android)

```bash
cd android-app
./gradlew assembleRelease
# Sign APK with production keystore
# Upload to Play Console
```

## Desktop

```bash
cd desktop-app
npm install
npm run tauri build
# Binaries at src-tauri/target/release/bundle/
```

## Browser Extension

```bash
cd browser-extension
npm run build
# Zip dist/ and upload to Chrome Web Store / Firefox Add-ons
```
