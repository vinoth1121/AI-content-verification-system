# Roadmap

Twelve-week development plan (26 Jul 2026 → 20 Oct 2026).

## Phase 1 — Foundation (Week 1-2) ✅
- [x] Monorepo structure
- [x] Backend API: auth, scan, admin, health
- [x] AI engine: text + image detectors (CPU baseline)
- [x] Admin dashboard: overview, new scan, history, admin tabs
- [x] Browser extension scaffold
- [x] Android app scaffold
- [x] Desktop app scaffold
- [x] Architecture documentation

## Phase 2 — Detection Depth (Week 3-5)
- [ ] Swap text detector for fine-tuned RoBERTa (HC3 dataset)
- [ ] Add CLIP-based image detector for diffusion-model fingerprints
- [ ] Add Wav2Vec2-based audio detector
- [ ] Real fact-checking for fake-news (retrieval against trusted sources)
- [ ] Calibration dataset + per-modality AUC metrics
- [ ] Pluggable model registry (swap detectors without redeploy)

## Phase 3 — Production Hardening (Week 6-8)
- [ ] Postgres migration (Alembic)
- [ ] Redis-backed rate limiting + scan queue
- [ ] S3 / GCS object storage for media uploads
- [ ] Prometheus metrics + Grafana dashboards
- [ ] Structured logging (JSON) + Loki aggregation
- [ ] Comprehensive integration tests (Playwright for dashboard, Postman for API)
- [ ] Load testing (k6) — target 500 RPS per pod
- [ ] Security audit (OWASP ZAP)

## Phase 4 — Cross-Platform Features (Week 9-10)
- [ ] Android: image / audio / video upload from gallery
- [ ] Android: push notifications for batch scans
- [ ] Android: background monitoring service
- [ ] Desktop: drag-and-drop file upload
- [ ] Desktop: system tray + global hotkey
- [ ] Browser extension: real-time page-wide scan
- [ ] Browser extension: sync settings across devices

## Phase 5 — Polish & Launch (Week 11-12)
- [ ] UI polish: empty states, loading skeletons, error boundaries
- [ ] Internationalisation (i18n) — Hindi, Spanish, Mandarin
- [ ] Accessibility audit (WCAG 2.2 AA)
- [ ] Documentation site (mkdocs-material)
- [ ] Play Store / Web Store / Snap submissions
- [ ] Production deployment + monitoring handoff
- [ ] Post-launch retrospective

## Stretch Goals (post-October)
- On-device inference (TensorFlow Lite on Android, ONNX Runtime on desktop)
- Browser extension: deepfake detection in video calls (WebRTC)
- API for third-party integrations (publishers, social platforms)
- Self-serve organisational tenant management
