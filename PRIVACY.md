# Privacy Policy - Ecomind Extension

*Last updated: September 2023*

## Our Privacy Commitment

Ecomind is built with privacy as the foundational principle. We believe you should have complete control over your data while still being able to track and understand your AI usage patterns.

## What We DON'T Collect

**We never access, store, or transmit:**
- Prompt text or questions you send to AI services
- Responses or outputs from AI models
- Personal conversations or content
- Cookies or tracking identifiers
- Usage analytics or behavioral data
- Any personally identifiable information beyond what you explicitly configure

## What We DO Collect (Locally)

**When using the extension, we store locally on your device:**
- Timestamps of API requests
- Provider names (e.g., "openai", "anthropic")
- Model names when detectable (e.g., "gpt-4", "claude-3-sonnet")
- Call counts and usage statistics
- Environmental impact estimates based on your configured parameters

**All this data is:**
- Stored only in your browser's local storage
- Never transmitted anywhere by default
- Completely under your control
- Automatically deleted when you uninstall the extension

## Optional Backend Reporting

**If you explicitly configure and enable backend reporting:**
- Only the minimal metadata listed above is sent to your configured backend URL
- No prompt text or AI responses are ever transmitted
- You control the backend URL and can disable this feature at any time
- Data is sent only to the endpoint you specify
- You can enable "Local-only mode" to disable all network requests

## Data You Control

**User ID**: If you configure a User ID for backend reporting, this is entirely your choice and under your control.

**Backend URL**: If you configure a backend URL, you control where (if anywhere) data is sent.

**Custom Providers**: Any custom domains you add for tracking are stored locally and only used to identify relevant API requests.

## How We Detect AI Usage

The extension monitors network requests to known AI API domains using Chrome's `webRequest` API. We only:
1. Check if a request matches a known AI provider domain
2. Extract the provider name from the URL
3. Attempt to extract the model name from the URL or request metadata
4. Count the request and update local statistics

**We do not:**
- Read request bodies containing prompts
- Access response data from AI services
- Store or transmit conversation content
- Track any user behavior beyond API request counts

## Local-Only Mode

You can enable "Local-only mode" in the options, which:
- Prevents all network requests from the extension
- Keeps all data on your local device
- Disables backend reporting regardless of other settings
- Provides a privacy-first experience with zero data transmission

## Data Storage

**Local Storage**: All data is stored in Chrome's `chrome.storage.local` API, which:
- Is isolated to your browser profile
- Is not accessible to websites
- Is removed when you uninstall the extension
- Can be cleared through Chrome's extension settings

**No External Storage**: We do not use any external databases, cloud storage, or third-party services to store your data.

## Third-Party Services

**AI Providers**: We monitor requests to AI service providers (OpenAI, Anthropic, etc.) but only to count usage. We do not store or access the actual data you exchange with these services.

**Backend Services**: If you configure a backend URL, data is sent only to that endpoint. We do not provide or recommend any specific backend services.

## Data Retention

**Local Data**: Kept until you clear it manually or uninstall the extension.

**Backend Data**: If you use backend reporting, data retention is controlled by your backend service, not by us.

## Children's Privacy

This extension is not intended for children under 13. We do not knowingly collect data from children.

## Changes to Privacy Policy

We may update this privacy policy occasionally. Significant changes will be noted in the extension update notes.

## Contact

For privacy questions or concerns, please open an issue on our GitHub repository.

## Summary

Ecomind is designed to give you insights into your AI usage while maintaining complete privacy. We never access your conversations with AI services, and all tracking is focused solely on aggregate usage patterns that you control and can keep entirely local to your device.

**Key principles:**
- ✅ Privacy by design
- ✅ Local-first data storage
- ✅ User control over all data sharing
- ✅ No content or conversation logging
- ✅ Minimal metadata collection
- ✅ Transparent about what we do and don't collect