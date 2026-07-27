# Admin Dashboard

Next.js 16 + TypeScript + Tailwind CSS + shadcn/ui admin dashboard for the AI
Content Verification System.

## Features

- **Auth**: login + register with JWT session persistence
- **Overview tab**: KPI cards, recent scans, modality + verdict distribution charts
- **New Scan tab**: text + fake-news + image + audio + video upload
- **History tab**: paginated filterable table with detail view
- **Platform tab (admin)**: aggregated stats + avg confidence per modality
- **Users tab (admin)**: enable/disable + role toggle
- **Dark/light theme**, responsive, accessibility-compliant

## Development

This dashboard is designed to run inside the ACVS workspace, where a
Caddyfile gateway routes `/api/*` calls to the FastAPI backend on port
8000 via the `XTransformPort` query parameter.

```bash
npm install
npm run dev          # http://localhost:3000
```

The API client is at `src/lib/api/acvs.ts` and uses the gateway pattern.
