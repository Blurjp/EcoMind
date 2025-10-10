# Privacy Policy – Ecomind Extension

**Effective Date**: January 1, 2025
**Last Updated**: January 1, 2025

---

## Introduction

Ecomind ("we", "our", or "the extension") is a Chrome browser extension that helps you track the environmental impact of AI API usage. This Privacy Policy explains what data we collect, how we use it, and your rights regarding your information.

---

## Data Collection

### What We Collect

Ecomind collects **only metadata** about your AI API usage. We **never** collect the actual content of your prompts or AI responses.

**Metadata collected includes**:
- Timestamp of API requests
- Provider name (e.g., "OpenAI", "Anthropic", "Google AI")
- Model identifier (e.g., "gpt-4o", "claude-3-opus")
- Token counts (when available from API response headers)
- Request domain (for custom provider tracking)

**Local storage only**:
- Your settings and preferences
- Daily usage counters
- Custom provider domains you configure
- Estimation parameters (kWh, water, CO₂ factors)

### What We DO NOT Collect

- ❌ **Prompts or input text** you send to AI services
- ❌ **Completions or responses** from AI models
- ❌ **Conversation history or chat logs**
- ❌ **Personal information** (name, email, address, etc.)
- ❌ **Browsing history** outside of AI API requests
- ❌ **Cookies or tracking identifiers**
- ❌ **IP addresses**
- ❌ **Authentication tokens or API keys**

---

## How We Use Your Data

### Local-Only Mode (Default)

By default, all tracking is **local-only**:
- Data is stored in Chrome's local storage on your device
- Nothing is transmitted to external servers
- You have complete control over your data

### Optional Telemetry Mode

If you enable telemetry and configure a backend URL:
- Metadata is sent to your specified backend server
- You control the backend (self-hosted or provided by your organization)
- We do not operate a centralized telemetry service

**Purpose of telemetry**:
- Aggregate usage statistics across teams/organizations
- Generate environmental impact reports
- Track sustainability metrics over time

---

## Data Storage

### Local Storage
- Settings: Stored in `chrome.storage.local`
- Daily metrics: Cleared automatically at midnight (configurable)
- No data leaves your device in local-only mode

### External Storage (Optional)
- If you configure a backend URL, data is sent via HTTPS
- Storage location depends on your backend configuration
- Retention policy set by your backend administrator

---

## Data Sharing

We **do not sell, rent, or share** your data with third parties.

**Exception**: If you enable telemetry and configure a backend URL, data is sent to that server. You are responsible for the privacy practices of your chosen backend.

---

## Your Rights

### Access
- View all stored data in the extension's options page
- Export data from local storage using browser developer tools

### Deletion
- Clear all data using the "Clear Today's Data" button in the popup
- Uninstall the extension to remove all local data
- Contact your backend administrator to delete server-side data (if applicable)

### Control
- Toggle telemetry on/off at any time
- Switch between local-only and telemetry modes
- Configure which providers to track
- Adjust environmental estimation parameters

---

## Security

### Data Protection
- All settings stored securely in Chrome's storage API
- No plaintext API keys or credentials stored
- XSS protection implemented in all UI components

### Network Security
- All external communications use HTTPS
- Content Security Policy enforced
- No third-party scripts or trackers

### Permissions Explained

**Storage**: Required to save your settings and daily metrics locally on your device.

**Web Request**: Required to detect API calls to AI providers for tracking purposes. We only monitor network requests to calculate usage statistics – we never access request/response content.

**Alarms**: Required to reset daily counters at midnight automatically.

**Host Permissions** (`<all_urls>`): Required to monitor requests to custom AI provider domains you configure. You can restrict this by only adding specific provider domains in settings.

---

## Compliance

### GDPR (European Users)
- **Right to Access**: View your data in the extension
- **Right to Deletion**: Clear data or uninstall
- **Right to Portability**: Export via browser tools
- **Data Minimization**: We collect only essential metadata
- **Purpose Limitation**: Data used only for usage tracking

### CCPA (California Users)
- We do not sell personal information
- You can delete all data at any time
- We collect only non-personal metadata

---

## Children's Privacy

Ecomind is not intended for users under 13 years of age. We do not knowingly collect data from children.

---

## Changes to This Policy

We may update this Privacy Policy from time to time. Changes will be reflected in the "Last Updated" date. Material changes will be communicated via:
- Extension update notes
- In-app notification
- GitHub repository announcements

---

## Third-Party Services

### AI Providers
Ecomind monitors requests to third-party AI services (OpenAI, Anthropic, Google, etc.). Your use of those services is governed by their respective privacy policies:
- OpenAI: https://openai.com/privacy
- Anthropic: https://www.anthropic.com/privacy
- Google AI: https://policies.google.com/privacy

We only observe metadata about requests; we do not interact with these services on your behalf.

---

## Open Source

Ecomind is open source software. You can review our code at:
- **GitHub**: https://github.com/[your-username]/ecomind
- **License**: MIT (or your chosen license)

---

## Contact Us

If you have questions about this Privacy Policy or your data:

- **Email**: support@ecomind.biz
- **GitHub Issues**: https://github.com/[your-username]/ecomind/issues
- **Support**: support@ecomind.biz

---

## Consent

By installing and using Ecomind, you consent to this Privacy Policy. If you do not agree, please do not install or use the extension.

---

**Summary**: Ecomind is privacy-first. We collect only metadata (no prompts/responses), store everything locally by default, and give you full control over your data.
