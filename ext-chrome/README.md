# Ecomind Browser Extension (Chrome MV3)

Privacy-first browser extension for tracking AI API usage and environmental footprint.

## Features

- Track AI API calls to OpenAI, Anthropic, Cohere, Replicate, Together, Perplexity, Google AI
- Estimate energy (kWh), water (L), and CO₂ (kg) footprint
- Local-only mode or optional backend telemetry
- Badge showing daily call count
- Midnight auto-reset with rollover

## Development

```bash
npm install
npm run dev      # watch mode
npm run build    # production
npm run lint
npm test
```

## Load in Chrome

1. Build: `npm run build`
2. Go to `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked" and select `ext-chrome/dist/`

## Configuration

Click extension icon → Options:

- **Backend URL**: API base URL (e.g., `http://localhost:8000`)
- **Org ID / User ID**: Identifiers for telemetry
- **Local-only mode**: Keep all data on device
- **Custom providers**: Add domains to track
- **Environmental factors**: kWh/call, PUE, water/kWh, CO₂/kWh

## Backend Integration

Extension can send events to:
- `POST /v1/ingest` – submit event
- `GET /v1/today?org_id=X&user_id=Y` – fetch aggregated data

## Privacy

- **Never logs prompt text or completions**
- Metadata only: timestamps, provider, model (when detectable from URL)
- Local-first by default
- See [PRIVACY.md](../PRIVACY.md)

## Architecture

```
ext-chrome/
├── src/
│   ├── bg/           # Background service worker
│   ├── ui/           # Popup + options pages
│   └── common/       # Shared types/constants
├── manifest.json
├── vite.config.ts
└── package.json
```

For full docs, see main [README](../README.md).