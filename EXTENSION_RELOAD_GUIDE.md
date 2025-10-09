# Extension Reload Guide

## Why Reload?

Chrome extensions cache their service worker code. After rebuilding (`npm run build`), you must manually reload the extension for changes to take effect.

## Step-by-Step Instructions

### 1. Reload the Extension

1. Open Chrome and navigate to: `chrome://extensions/`
2. Find "Ecomind" in the list
3. Click the **circular reload icon** (🔄) on the Ecomind card
4. Verify the "Service Worker" shows **"Active"** status

### 2. Clear Old Data (Important!)

The "Unknown" models you're seeing were recorded BEFORE the fix. To see new data:

**Option A: Clear All Data (Recommended)**
1. Click the Ecomind extension icon in Chrome toolbar
2. Click **"Clear Today"** button
3. Confirm the action

**Option B: Wait Until Tomorrow**
- The extension auto-resets at midnight
- Tomorrow's data will use the new detection logic

### 3. Test the Fix

1. Visit [https://chatgpt.com](https://chatgpt.com)
2. Send a message to ChatGPT
3. Click the Ecomind extension icon
4. Check **"Top Models"** section
5. ✅ Should now show **"chatgpt-web"** instead of "Unknown"

### 4. Verify Build is Latest

If still seeing "Unknown", verify you have the latest build:

```bash
# Check dist/constants.js contains the fix
grep "chatgpt-web" dist/constants.js
# Should output: return "chatgpt-web";

# If not found, rebuild:
npm run build
```

Then repeat steps 1-3 above.

## What Changed?

### Before (Commit: dd9addc)
```typescript
modelExtractor: (url: string, body?: string) => {
  if (body) {
    try {
      const parsed = JSON.parse(body);
      return parsed.model || 'unknown';
    } catch { }
  }
  return 'unknown';  // ← Always returned 'unknown' for web UIs
}
```

### After (Commit: a4a7735)
```typescript
modelExtractor: (url: string, body?: string) => {
  // Try body parsing first
  if (body) {
    try {
      const parsed = JSON.parse(body);
      return parsed.model || 'unknown';
    } catch { }
  }
  // MV3 fallback: URL-based detection when body unavailable
  if (url.includes('chatgpt.com') || url.includes('chat.openai.com')) {
    return 'chatgpt-web';  // ← NEW: Detects ChatGPT web UI
  }
  return 'unknown';
}
```

## Expected Results After Fix

| Service | URL Pattern | Model Name |
|---------|------------|------------|
| ChatGPT Web | chatgpt.com, chat.openai.com | **chatgpt-web** ✅ |
| Claude Web | claude.ai | **claude-web** ✅ |
| OpenAI API | api.openai.com | **unknown** (MV3 limitation) |
| Anthropic API | api.anthropic.com | **unknown** (MV3 limitation) |

## Troubleshooting

### Still Seeing "Unknown" After Reload?

1. **Hard Reload Extension**:
   - Go to `chrome://extensions/`
   - Toggle Ecomind **OFF** then **ON**
   - Click reload icon again

2. **Check Service Worker Console**:
   - Go to `chrome://extensions/`
   - Under Ecomind, click **"Service Worker"** (blue link)
   - DevTools opens - check Console for errors
   - In Console, type: `chrome.runtime.reload()`

3. **Verify Request URL**:
   - Open ChatGPT: https://chatgpt.com
   - Open Chrome DevTools (F12)
   - Go to **Network** tab
   - Send a message in ChatGPT
   - Look for requests to domains like:
     - `chatgpt.com/backend-api/conversation`
     - `chat.openai.com/backend-api/conversation`
   - These should now be detected as "chatgpt-web"

4. **Check Extension Logs**:
   ```javascript
   // In Service Worker console:
   chrome.storage.local.get('ecomind_daily_usage', (data) => {
     console.log(JSON.stringify(data, null, 2));
   });
   ```
   Look for recent entries - they should have `"model": "chatgpt-web"`

### Chrome Version Issues

If using **Chrome Dev/Canary**, service worker behavior may differ. Try:
- Restarting Chrome completely
- Using Chrome Stable instead

## Next Steps

After verifying the fix works:
1. Use ChatGPT normally throughout the day
2. Check the popup regularly to see "chatgpt-web" incrementing
3. If you use Claude web UI (claude.ai), it should show "claude-web"

## Known Limitations

- **Direct API calls** (via code/Postman to api.openai.com) will still show "unknown"
- This is a Chrome Manifest V3 security restriction
- See `codex_reviews/auto_fix_20251009_133920.md` for details and workarounds
