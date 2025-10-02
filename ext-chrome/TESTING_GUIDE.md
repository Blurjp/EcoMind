# Extension Testing Guide

**Version**: 1.0.0
**Date**: January 1, 2025

---

## Fresh Install Testing

### Step 1: Load Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select the `dist/` folder: `/Users/jianphua/projects/EcoMind/ext-chrome/dist/`
5. Verify extension appears with:
   - Name: "Ecomind - AI Sustainability Tracker"
   - Version: 1.0.0
   - Icon: Green leaf icon (if visible)

### Step 2: Verify Permissions

Check that these permissions are requested:
- [x] Storage
- [x] Web Request
- [x] Alarms
- [x] Host Permissions: `<all_urls>`

---

## Functional Testing Checklist

### Popup Tests

1. **Open Popup**
   - Click extension icon in toolbar
   - Verify popup opens (should show default state with 0 calls)

2. **Default State**
   - [ ] "Today's Usage" heading visible
   - [ ] Shows 0 API calls
   - [ ] Shows 0.000 kWh
   - [ ] Shows 0.000 L water
   - [ ] Shows 0.000 kg CO₂
   - [ ] "Clear Today's Data" button visible
   - [ ] "View Settings" button visible

3. **Navigation**
   - [ ] Click "View Settings" → Opens options page in new tab
   - [ ] Click "Clear Today's Data" → Confirms data cleared (stays at 0)

### Options Page Tests

4. **Open Options**
   - Right-click extension icon → "Options"
   - OR click "View Settings" from popup
   - Verify options page loads

5. **General Settings**
   - [ ] Backend URL field visible (default: empty or placeholder)
   - [ ] User ID field visible (default: empty)
   - [ ] Privacy toggle: "Local-only mode" (default: ON/checked)
   - [ ] Telemetry toggle: "Enable telemetry" (default: OFF/unchecked)

6. **Estimation Parameters**
   - [ ] kWh per call: default value visible
   - [ ] PUE: default value visible
   - [ ] Water L/kWh: default value visible
   - [ ] CO₂ kg/kWh: default value visible

7. **Custom Providers**
   - [ ] "Default Providers" section shows built-in providers (OpenAI, Anthropic, etc.)
   - [ ] "Custom Providers" section visible
   - [ ] "Add Custom Provider" input field
   - [ ] Domain validation works (try invalid domain → error)
   - [ ] Add valid domain (e.g., `api.custom.com`) → appears in list
   - [ ] Remove custom provider → disappears from list

8. **Settings Persistence**
   - [ ] Change settings → Click "Save Settings" → Success message
   - [ ] Close and reopen options page → Settings still changed
   - [ ] Click "Reset to Defaults" → All settings revert

### Privacy Mode Tests

9. **Local-Only Mode (Default)**
   - [ ] Privacy toggle is ON by default
   - [ ] Warning message about telemetry disabled visible
   - [ ] Backend URL and User ID fields disabled/grayed out

10. **Telemetry Mode**
    - [ ] Uncheck "Local-only mode"
    - [ ] Backend URL and User ID fields become enabled
    - [ ] Enter backend URL (e.g., `http://localhost:8000`)
    - [ ] Enter User ID (e.g., `test-user`)
    - [ ] Click "Test Connection" → Should attempt connection (may fail if backend not running)

### Edge Cases

11. **Zero Value Handling**
    - [ ] Set kWh per call to `0` → Save → Reopen → Still shows `0` (not reverted to default)
    - [ ] Set water L/kWh to `0` → Save → Reopen → Still shows `0`

12. **Port in Domain**
    - [ ] Add custom domain `localhost:3000` → Accepted (no validation error)
    - [ ] Add custom domain `api.example.com:8080` → Accepted

13. **Case-Insensitive Domains**
    - [ ] Add custom domain `ChatGPT.com` → Saves
    - [ ] Test that tracking works for requests to `chatgpt.com` (lowercase)

14. **Deep Clone Settings**
    - [ ] Add custom provider → Save
    - [ ] Reset to defaults → Custom provider removed
    - [ ] Add same custom provider again → Works (defaults not polluted)

---

## Simulated Usage Testing

### Test API Call Tracking

Since we're testing without actual AI API calls, we'll verify the architecture is correct:

15. **Service Worker**
    - [ ] Open `chrome://extensions/` → Find Ecomind → Click "Service worker"
    - [ ] Check console for errors (should be none)
    - [ ] Type `chrome.runtime.getManifest()` → Verify manifest loads

16. **Storage Inspection**
    - [ ] In service worker console, run:
    ```javascript
    chrome.storage.local.get(null, (data) => console.log(data));
    ```
    - [ ] Verify settings object exists
    - [ ] Check that customProviders is an array

17. **Message Passing**
    - [ ] Open popup
    - [ ] In service worker console, check for message handler logs
    - [ ] Verify `GET_TODAY_COUNT` and `GET_TODAY_USAGE` messages work

---

## Visual/UI Tests

18. **Popup UI**
    - [ ] No layout issues (text overflow, misalignment)
    - [ ] All text readable and appropriately sized
    - [ ] Buttons are clickable and styled correctly
    - [ ] Numbers display with correct precision (3 decimals)

19. **Options Page UI**
    - [ ] All sections properly spaced
    - [ ] Form inputs aligned and sized correctly
    - [ ] Toggle switches work (visual feedback)
    - [ ] Provider cards display properly
    - [ ] No console errors related to UI rendering

20. **Icons**
    - [ ] Extension icon appears in toolbar (16x16)
    - [ ] Popup shows icon if referenced (48x48)
    - [ ] Options page shows icon if referenced (128x128)
    - [ ] All icons are clear and recognizable

---

## Security Tests

21. **XSS Prevention**
    - [ ] Add custom provider with name `<script>alert('xss')</script>`
    - [ ] Verify script does NOT execute (should display as plain text)

22. **Content Security Policy**
    - [ ] Check console for CSP violations (should be none)
    - [ ] Verify no inline scripts or unsafe-eval

23. **No Sensitive Data Exposure**
    - [ ] Open Network tab → Perform actions → Verify no unexpected requests
    - [ ] In local-only mode, verify zero external requests

---

## Performance Tests

24. **Load Time**
    - [ ] Popup opens in < 1 second
    - [ ] Options page loads in < 1 second
    - [ ] No lag when typing in input fields

25. **Memory Usage**
    - [ ] Open Chrome Task Manager (`Shift+Esc`)
    - [ ] Find Ecomind extension
    - [ ] Memory usage should be < 50 MB
    - [ ] No memory leaks after repeated popup open/close

---

## Cross-Browser Testing (Optional)

26. **Edge (Chromium-based)**
    - [ ] Load extension in Edge
    - [ ] Verify all functionality works identically

27. **Brave**
    - [ ] Load extension in Brave
    - [ ] Verify all functionality works

---

## Regression Tests (After Each Update)

28. **TypeScript Compilation**
    - [ ] Run `npm run build` → No errors
    - [ ] Check dist/ files are generated

29. **Security Fixes Intact**
    - [ ] Public accessors used in service worker
    - [ ] Array cloning in all settings locations
    - [ ] Number.isFinite() for numeric inputs
    - [ ] Case-insensitive domain matching

---

## Known Limitations (Expected Behavior)

- **No Real API Tracking**: Without actual API calls, counters remain at 0
- **Backend Connection**: Test connection fails if no backend running (expected)
- **Midnight Reset**: Requires extension to be active at midnight (may need manual test)

---

## Test Results Template

```
DATE: _____________
TESTER: ___________
VERSION: 1.0.0

SUMMARY:
- Functional Tests: ___/29 passed
- UI Tests: ___/3 passed
- Security Tests: ___/3 passed
- Performance Tests: ___/2 passed

ISSUES FOUND:
1. _____________________
2. _____________________
3. _____________________

OVERALL STATUS: [ ] PASS  [ ] FAIL  [ ] NEEDS WORK

NOTES:
_____________________
_____________________
```

---

## Next Steps After Testing

1. **If All Tests Pass**:
   - [ ] Mark testing complete
   - [ ] Proceed with Chrome Web Store submission
   - [ ] Take screenshots for store listing

2. **If Issues Found**:
   - [ ] Document issues in GitHub Issues
   - [ ] Fix critical bugs
   - [ ] Rebuild and retest
   - [ ] Update version number if changes made

3. **For Store Submission**:
   - [ ] Create screenshots from tested extension
   - [ ] Verify ZIP package (`ecomind-v1.0.0.zip`)
   - [ ] Prepare privacy policy URL
   - [ ] Complete Chrome Web Store Developer Console form

---

## Testing Automation (Future)

Consider adding:
- Unit tests for utility functions (util.ts)
- Integration tests for storage operations
- E2E tests with Puppeteer/Playwright
- Automated visual regression tests

Current coverage: Manual testing only (acceptable for v1.0.0)

---

**Testing Status**: Ready for manual testing
**Next Action**: Load extension and complete checklist above
