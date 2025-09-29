# 🌱 Ecomind Chrome Extension

A Chrome Manifest V3 extension that tracks AI API usage and estimates environmental footprint with privacy-first design.

## Features

- **Privacy-First**: Never logs or transmits prompt text or model outputs
- **Local Tracking**: Track API calls locally with daily usage statistics
- **Environmental Impact**: Estimate energy, water, and CO₂ footprint
- **Provider Support**: Built-in support for OpenAI, Anthropic, Replicate, Together, Cohere, Perplexity, and Google AI
- **Custom Providers**: Add your own API domains to track
- **Backend Integration**: Optional backend reporting with configurable endpoints
- **Daily Reset**: Automatic midnight reset with historical data archiving

## Installation

### Development Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Build the extension**:
   ```bash
   npm run build
   ```

3. **Load unpacked extension in Chrome**:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" in the top right
   - Click "Load unpacked" and select the `ecomind-extension` directory
   - The extension should appear in your extensions list

### Production Build

```bash
npm run build
```

The built extension will be in the `dist/` directory.

## Configuration

### Options Page

Access the options page by:
- Clicking the extension icon and selecting "Options"
- Or going to `chrome://extensions/` and clicking "Options" under Ecomind

### Settings

**Backend Configuration:**
- `Backend URL`: Base URL of your backend API service
- `User ID`: Unique identifier for your usage data

**Privacy Settings:**
- `Local-only mode`: Keep all data on device, never send to backend
- `Enable telemetry`: Send anonymous usage data to backend (when not in local-only mode)

**Custom Providers:**
- Add additional domains to track (e.g., `api.custom-ai.com` or `*.custom-ai.com`)

**Environmental Parameters:**
- `kWh per API call`: Energy consumption per request (default: 0.0003)
- `PUE`: Power Usage Effectiveness multiplier (default: 1.5)
- `Water (L per kWh)`: Water consumption per kWh (default: 1.8)
- `CO₂ (kg per kWh)`: Carbon emissions per kWh (default: 0.4)

## Backend API

If you want to use backend reporting, implement these endpoints:

### POST /ingest

Receives usage data:

```json
{
  "user_id": "user123",
  "provider": "openai",
  "model": "gpt-4",
  "tokens_in": 0,
  "tokens_out": 0,
  "ts": "2023-12-01T15:30:00Z"
}
```

### GET /today?user_id=<user_id>

Returns aggregated daily data:

```json
{
  "date": "2023-12-01",
  "call_count": 15,
  "kwh": 0.0045,
  "water_liters": 0.0081,
  "co2_kg": 0.0018,
  "top_providers": [
    {"provider": "openai", "count": 10},
    {"provider": "anthropic", "count": 5}
  ],
  "top_models": [
    {"model": "gpt-4", "count": 8},
    {"model": "claude-3-sonnet", "count": 5}
  ]
}
```

### GET /health (optional)

Health check endpoint for connection testing.

## Privacy

Ecomind is designed with privacy as the top priority:

- **No Content Logging**: Never accesses, stores, or transmits prompt text or model responses
- **Minimal Metadata**: Only tracks timestamps, provider names, and model identifiers when detectable
- **Local-First**: All data can be kept locally on your device
- **Opt-In Telemetry**: Backend reporting is disabled by default and requires explicit configuration
- **No Tracking**: No analytics, cookies, or user tracking beyond what you explicitly configure

**Note**: Due to Manifest V3 limitations, model detection from request bodies is limited. The extension primarily tracks API call counts and estimates environmental impact, with model names extracted from URLs when possible.

See [PRIVACY.md](PRIVACY.md) for detailed privacy practices.

## Development

### Scripts

- `npm run dev` - Build in watch mode for development
- `npm run build` - Production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues
- `npm run format` - Format code with Prettier
- `npm run test` - Run tests (when implemented)

### Project Structure

```
ecomind-extension/
├── src/
│   ├── bg/                  # Background scripts
│   │   ├── service-worker.ts
│   │   ├── providers.ts
│   │   ├── storage.ts
│   │   ├── telemetry.ts
│   │   └── time.ts
│   ├── ui/                  # User interface
│   │   ├── popup.html
│   │   ├── popup.ts
│   │   ├── popup.css
│   │   ├── options.html
│   │   ├── options.ts
│   │   ├── options.css
│   │   └── components.ts
│   ├── common/              # Shared utilities
│   │   ├── types.ts
│   │   ├── constants.ts
│   │   └── util.ts
│   └── icons/               # Extension icons
├── manifest.json            # Extension manifest
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

### Adding New Providers

To add support for a new AI provider:

1. Add provider configuration in `src/common/constants.ts`:
   ```typescript
   {
     name: 'newprovider',
     domains: ['api.newprovider.com'],
     modelExtractor: (url: string, body?: string) => {
       // Extract model from URL or request body
       return 'model-name';
     }
   }
   ```

2. Update the manifest.json `host_permissions` if needed.

### Testing

Load the extension in Chrome and:

1. Visit sites that use AI APIs (ChatGPT, Claude, etc.)
2. Check the popup to see tracked usage
3. Verify the badge count updates
4. Test the options page configuration
5. Try the "Clear Today" functionality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `npm run lint` and `npm run format`
5. Test the extension thoroughly
6. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

For issues or questions:
- Open an issue on GitHub
- Check the browser extension console for error messages
- Verify your Chrome version supports Manifest V3

---

*Ecomind helps you understand the environmental impact of your AI usage while respecting your privacy.*