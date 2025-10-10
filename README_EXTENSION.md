# ⚠️ CHROME EXTENSION SOURCE LOCATION

**IMPORTANT: The Chrome extension source code is located in `ext-chrome/`**

## Quick Start

```bash
cd ext-chrome
npm install
npm run build
```

## Load in Chrome

1. Go to `chrome://extensions/`
2. Enable "Developer mode"  
3. Click "Load unpacked"
4. Select: `ext-chrome/dist/`

## Development

All extension development happens in `ext-chrome/`:

```bash
cd ext-chrome

# Development
npm run dev      # Watch mode
npm test         # Run tests
npm run lint     # Lint code

# Production
npm run build    # Build for Chrome Web Store
```

## Source Structure

```
ext-chrome/
├── src/              ← EXTENSION SOURCE CODE
│   ├── bg/           # Background service worker
│   ├── common/       # Shared types, constants, utils
│   └── ui/           # Popup and options UI
├── tests/            ← EXTENSION TESTS
├── dist/             ← BUILD OUTPUT (load this in Chrome)
├── manifest.json     ← EXTENSION MANIFEST
├── package.json
└── vite.config.ts
```

## ⚠️ DO NOT create `./src/` in project root!

The root directory should NOT contain:
- ❌ `./src/` - Extension source is in `ext-chrome/src/`
- ❌ `./tests/` - Extension tests are in `ext-chrome/tests/`
- ❌ `./dist/` - Extension build is in `ext-chrome/dist/`
- ❌ `./manifest.json` - Extension manifest is in `ext-chrome/manifest.json`

## Root Directory Structure

The root contains the full platform (API, Gateway, UI, etc.):

```
ecomind/
├── api/              # Python FastAPI backend
├── gateway/          # Go ingestion service
├── worker/           # Event processors
├── ui/               # Next.js dashboard
├── ext-chrome/       # ← CHROME EXTENSION (SINGLE SOURCE OF TRUTH)
├── sdks/             # TypeScript & Python SDKs
├── infra/            # Terraform, Helm charts
└── ops/              # Monitoring, load tests
```

## Chrome Web Store Submission

**Package:** `ext-chrome/dist/` (zip contents, not the folder itself)

```bash
cd ext-chrome
npm run build
cd dist
zip -r ../ecomind-extension.zip .
```

Upload `ecomind-extension.zip` to Chrome Web Store.

---

**Last Updated:** 2025-10-10  
**Consolidation:** Root `./src/` removed to prevent confusion (see `EXTENSION_SOURCE_CONSOLIDATION.md`)
