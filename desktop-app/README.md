# ACVS Desktop App

Tauri 2 + React + TypeScript desktop client for the AI Content Verification
System. Smaller, faster, and more secure than Electron.

## Why Tauri?

- **~10 MB binary** vs Electron's 100+ MB
- **Rust backend** — memory-safe, no Node.js runtime
- **Native webview** — uses the OS webview, no Chromium bundle
- **Secure by default** — strict CSP, capability-scoped APIs

## Build

```bash
# Prerequisites: Rust toolchain + system webview2 (Windows) / WebKitGTK (Linux)
cd desktop-app
npm install
npm run tauri dev      # dev mode (hot reload)
npm run tauri build    # production binaries
```

Binaries land in `src-tauri/target/release/bundle/`.

## Architecture

```
src-tauri/src/main.rs   # Rust backend: invoke handlers for login, scan, history
src/                    # React frontend
├── App.tsx             # Single-page UI
└── main.tsx            # React entry point
```

The React frontend calls Rust via `@tauri-apps/api/core`'s `invoke()`. Rust
makes HTTP calls to the ACVS backend using `reqwest`. Tokens are kept in
Rust-side state, never exposed to JS globals.
