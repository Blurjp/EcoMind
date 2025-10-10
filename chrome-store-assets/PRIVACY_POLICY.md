# Privacy Policy for EcoMind

**Last Updated: October 9, 2025**

## Overview

EcoMind is a Chrome extension that tracks your AI API usage and calculates the environmental impact (energy, water, CO₂). We are committed to protecting your privacy.

## Data Collection

### Local Data (Default Mode)
By default, EcoMind operates in **"Local Only"** mode:
- All usage data is stored locally in your browser using Chrome's storage API
- No data is sent to external servers
- Data includes: API call counts, provider names, model names, timestamps, and calculated environmental metrics
- You can clear this data at any time from the extension popup

### Optional Backend Mode
You may optionally enable backend telemetry by configuring:
- Base URL of your own backend server
- User ID for tracking
- When enabled, the extension sends:
  - Daily aggregated usage statistics (call counts, provider names, model names)
  - Calculated environmental metrics (kWh, water liters, CO₂ kg)
  - Date and user ID

**We do NOT collect:**
- Actual API request/response content
- Personal conversations or prompts
- API keys or credentials
- Browsing history beyond AI provider domains
- Any personally identifiable information (unless you provide a user ID)

## Data Storage

- **Local Mode**: Data stored in Chrome local storage (persists only on this device, does not sync)
- **Backend Mode**: Data sent to YOUR configured server (not controlled by EcoMind)

## Third-Party Services

EcoMind monitors requests to AI provider domains:
- OpenAI (api.openai.com, chatgpt.com)
- Anthropic (api.anthropic.com, claude.ai)
- Google AI (generativelanguage.googleapis.com)
- Replicate, Together.xyz, Cohere, Perplexity
- Custom domains you configure

We only observe request metadata (URLs, timing) - not content.

## Data Retention

- Local data persists until you manually clear it
- Backend data retention depends on your configured server

## Your Rights

You can:
- View all tracked data in the extension popup
- Clear today's data using the "Clear" button
- Disable telemetry in Settings
- Uninstall the extension to remove all local data

## Changes to This Policy

We will update this policy as needed. Check the "Last Updated" date above.

## Contact

For privacy questions or concerns, please contact us at:
support@ecomind.biz

