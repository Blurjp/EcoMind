# Justification for Broad Host Permissions

## Why `<all_urls>` is Required

### Extension Purpose
Ecomind tracks environmental impact (CO2, energy, water) of AI model usage across **12+ different AI service providers**. This requires monitoring API requests to multiple domains.

### Why activeTab Cannot Work
The `activeTab` permission is **incompatible** with our use case because:
1. **Background monitoring required**: AI API requests happen in the background via JavaScript, not user clicks on visible tabs
2. **No user gesture**: Users don't click our extension before using AI services - they use ChatGPT, Claude, etc. directly
3. **Automatic detection needed**: The extension must passively observe API traffic without user intervention

### Why Specific Domains Cannot Work
We **cannot** use specific `host_permissions` like `["https://api.openai.com/*"]` because:

1. **Dynamic provider ecosystem**: New AI providers launch frequently (Perplexity, xAI, DeepSeek added in recent months)
2. **Multiple subdomains**: Some providers use various subdomains:
   - Perplexity: `api.perplexity.ai` AND `perplexity.ai` (web interface)
   - Google: `generativelanguage.googleapis.com` AND `ai.google.dev`
   - HuggingFace: `api-inference.huggingface.co` AND `huggingface.co`

3. **User flexibility**: Users should be able to track any AI service, including:
   - Self-hosted AI models (custom domains)
   - Enterprise AI deployments (corporate domains)
   - Emerging AI providers (new services)

### Current Providers Monitored (12+)
```
api.openai.com
api.anthropic.com
generativelanguage.googleapis.com
api.perplexity.ai, perplexity.ai
api.x.ai
api.cohere.ai
api.mistral.ai
graph.facebook.com
api.deepseek.com
api-inference.huggingface.co
api.groq.com
api.replicate.com
```

### Security Safeguards

**1. Read-Only Access**
- Uses `webRequest` in **observer mode only**
- Never modifies, blocks, or intercepts requests
- Only reads request URLs and bodies

**2. Domain Filtering**
- Code explicitly checks against known AI provider patterns
- Ignores all non-AI-related traffic
- Source code: `src/common/constants.ts` (line 13-220)

**3. No Data Transmission**
- All data stored locally (`storage.local`)
- No external servers contacted
- No telemetry or analytics

**4. Transparent Operation**
- Badge shows when tracking is active
- Users can view all tracked data in popup
- Open source on GitHub for audit

### Code Reference
```typescript
// src/common/constants.ts
export const AI_PROVIDERS: ProviderConfig[] = [
  {
    name: 'openai',
    domains: ['api.openai.com', 'openai.com'],
    // ...
  },
  // ... 11+ more providers
];

// Only monitors these specific domains
public shouldTrackRequest(url: string): boolean {
  return this.findProviderForUrl(url) !== null;
}
```

### Alternative Considered: Specific Permissions
We evaluated requesting specific permissions like:
```json
{
  "host_permissions": [
    "https://api.openai.com/*",
    "https://api.anthropic.com/*",
    "https://generativelanguage.googleapis.com/*",
    // ... 20+ more patterns
  ]
}
```

**Why this is worse:**
1. **Same security profile**: Still monitors multiple domains
2. **Less flexible**: Cannot track new providers without extension update
3. **More confusing**: Users see 20+ permission warnings instead of 1
4. **Maintenance burden**: Requires update for every new AI service

### Conclusion
`<all_urls>` is the **most appropriate permission** for this use case because:
- ✅ Extension purpose requires monitoring multiple AI services
- ✅ Domain list is dynamic and growing
- ✅ Code implements strict filtering to only AI providers
- ✅ Read-only access with no modifications
- ✅ All data processing is local
- ✅ Open source and auditable

This is a **legitimate use case** for broad host permissions, similar to other productivity/monitoring extensions like RescueTime, WakaTime, or carbon footprint trackers.
