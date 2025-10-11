# Chrome Web Store Privacy Practices Responses

## Single Purpose Description

**Single Purpose:**
Track and measure the environmental impact (CO2 emissions, energy, and water usage) of AI model usage across multiple AI service providers to help users make more sustainable choices.

---

## Permission Justifications

### 1. Alarms Permission
**Why this permission is needed:**
The extension uses the `alarms` permission to schedule daily data aggregation tasks. This processes accumulated AI usage statistics at midnight each day to calculate total environmental impact metrics (CO2, energy, water). The alarm ensures accurate daily tracking without requiring the extension to run continuously, which would consume more resources.

**User benefit:**
Enables automatic daily environmental impact reporting without draining system resources.

---

### 2. Host Permissions (`<all_urls>`)
**Why this permission is needed:**
The extension needs to monitor network requests to 12+ different AI service providers (OpenAI, Anthropic, Google AI, Perplexity, xAI, Cohere, Mistral, Meta, DeepSeek, HuggingFace, Groq, Replicate) to track AI model usage. Each provider has different domains:
- api.openai.com
- api.anthropic.com
- generativelanguage.googleapis.com
- api.perplexity.ai / perplexity.ai
- api.x.ai
- api.cohere.ai
- api.mistral.ai
- graph.facebook.com
- api.deepseek.com
- api-inference.huggingface.co
- api.groq.com
- api.replicate.com

The extension uses pattern matching to detect requests to these specific domains only. No other websites are monitored or accessed.

**User benefit:**
Enables comprehensive tracking across all major AI providers without requiring users to manually configure each service.

---

### 3. Remote Code
**Why this permission is needed:**
This extension does NOT use remote code. All code is bundled within the extension package. We do not execute any remotely hosted scripts, load external JavaScript, or use eval() with external content.

**Certification:**
N/A - No remote code is used.

---

### 4. Storage Permission
**Why this permission is needed:**
The extension uses Chrome's `storage.local` API to store:
1. **AI usage history**: Timestamps, provider names, model names, and request counts
2. **Environmental impact data**: Calculated CO2, energy, and water usage metrics
3. **User preferences**: Display settings and estimation parameters

All data is stored locally on the user's device and never synchronized or transmitted to external servers. Storage is essential for:
- Maintaining historical usage records
- Calculating cumulative environmental impact
- Persisting user preferences

**User benefit:**
Provides historical tracking and personalized environmental impact reports. All data remains private and local to the user's device.

---

### 5. WebRequest Permission
**Why this permission is needed:**
The extension uses `webRequest` API to:
1. **Detect AI API calls**: Monitor outgoing requests to known AI provider endpoints
2. **Extract model information**: Read request bodies to identify which AI model was used (e.g., "gpt-4", "claude-3-opus")
3. **Count requests**: Track the number of AI interactions for environmental calculations

The extension operates in **read-only** mode - it never modifies, blocks, or intercepts requests. It only observes requests to the specific AI provider domains listed above to gather usage statistics.

**User benefit:**
Enables automatic, transparent tracking of AI usage without requiring manual input or API key integration.

---

## Data Usage Certification

### Does this item collect or transmit user data?
**Answer:** NO

**Explanation:**
- All tracking happens locally in the browser
- No data is sent to external servers
- No user account or sign-up required
- No analytics, telemetry, or crash reporting
- Users can clear all data at any time from the extension popup

### Privacy Policy URL
https://blurjp.github.io/EcoMind/privacy-policy.md

---

## Compliance Checklist

✅ Single purpose is clearly defined
✅ All permissions are justified with specific use cases
✅ No remote code is used
✅ No user data is collected or transmitted
✅ Privacy policy is publicly accessible
✅ All data processing happens locally
✅ Users have full control over their data

---

## Additional Notes

**Transparency:**
- The extension icon shows a badge counter when tracking is active
- Users can view all tracked data in the popup
- Settings page clearly explains privacy-first design
- Source code is available on GitHub for audit

**User Control:**
- "Clear Today" button removes current day's data
- All data stored locally can be cleared via browser tools
- No persistent user identifiers are created
- No cross-site tracking occurs

**Minimal Data Collection:**
The extension only stores:
- Provider name (e.g., "openai")
- Model name (e.g., "gpt-4")
- Timestamp of request
- Request count

It does NOT store:
- Request content or prompts
- Response data
- User credentials or API keys
- Personal information
- Browsing history beyond AI service requests
