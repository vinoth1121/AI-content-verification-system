# Browser Extension

Manifest V3 Chrome / Firefox extension that lets users verify any text,
image, or article they encounter on the web — directly from the context
menu or a popup.

## Features

- **Right-click → Verify with ACVS** on any selected text, image, or link
- **Popup** with quick text scan + recent verdicts
- **Options page** to configure backend URL
- **Non-intrusive overlay** that shows the verdict without leaving the page
- **JWT auth** stored in `chrome.storage.local`

## Build

```bash
npm install
npm run build
# Load dist/ as an unpacked extension in chrome://extensions
```

## Architecture

```
src/
├── background.ts    # Service worker: context menu, API calls, message routing
├── content.ts       # Injected into pages — renders verdict overlay
├── popup.ts         # Popup UI logic
└── options.ts       # Options page logic
```

The extension uses **message passing** between the content script, popup,
and background worker. All HTTP calls happen in the background worker to
keep CSP simple and to share the auth token across contexts.
