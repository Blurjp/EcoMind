# Production Readiness Checklist

**Last Updated**: 2025-10-10  
**Extension Version**: 1.0.0  
**Status**: Ready for Chrome Web Store Submission

---

## ✅ Code Quality & Testing

- [x] **All tests passing**: 73/73 tests ✅
  - 4 test suites (providers, storage, util, domain-validation)
  - HuggingFace model extraction (9 tests)
  - xAI Grok support (5 tests)
  - OpenAI, Anthropic, and other providers

- [x] **Production build successful**
  ```bash
  cd ext-chrome
  npm run build  # ✅ Clean build
  ```

- [x] **No TypeScript errors**: Clean compilation
- [x] **No console errors**: Service worker runs cleanly

---

## ✅ Core Functionality

### Provider Support
- [x] OpenAI (API + ChatGPT web UI)
- [x] Anthropic (API + Claude.ai web UI)
- [x] xAI Grok (API + grok.com web chat) ⭐ Just added
- [x] HuggingFace (single-segment + owner/model) ⭐ Just fixed
- [x] Replicate
- [x] Together
- [x] Cohere
- [x] Perplexity
- [x] Google Gemini
- [x] Mistral
- [x] OpenRouter
- [x] Groq

### Key Features
- [x] Real-time request tracking (webRequest API)
- [x] Environmental impact calculations (kWh, water, CO₂)
- [x] Daily usage tracking with midnight reset
- [x] Privacy-first (local-only mode by default)
- [x] Optional backend telemetry sync
- [x] Custom provider domains support
- [x] Popup UI with usage statistics
- [x] Options page for settings

---

## ✅ Code Cleanup & Quality

- [x] **Single source of truth**: ext-chrome/ only
- [x] **Removed duplicates**: Deleted root src/, tests/, dist/
- [x] **Pre-commit hook**: Prevents duplicate source files
- [x] **Git protection**: .gitignore blocks root extension files
- [x] **Documentation**: README_EXTENSION.md, CLEANUP_COMPLETE.md

---

## ⚠️ TODO: Chrome Web Store Requirements

### 1. Remove Debug Logging (REQUIRED before submission)

**File**: `ext-chrome/src/bg/service-worker.ts:62-69`

Currently has diagnostic logging:
```typescript
if (details.url.toLowerCase().includes('x.ai') || details.url.toLowerCase().includes('perplexity')) {
  console.log('[EcoMind DEBUG] Request detected:', {...});
}
```

**Action**: Remove or comment out before final build

---

### 2. Screenshots (3-5 required)

Create and save to `chrome-store-assets/screenshots/`:

- [ ] **Main popup with usage data** (640x400px min)
  - Show call count, providers, environmental metrics
  
- [ ] **Top providers & models section**
  - Display tracked AI services
  
- [ ] **Settings/Options page**
  - Privacy settings, telemetry toggle
  
- [ ] **Empty state** (optional)
  - "No API calls detected today"

**How to create**:
1. Use extension with real data
2. Cmd+Shift+4 (Mac) or browser screenshot tool
3. Ensure 1280x800px or 640x400px minimum

---

### 3. Promotional Images (Optional but recommended)

- [ ] **Small promo tile**: 440x280px
  - Green theme (#2D5F3F)
  - "Track AI Impact" text
  - Use `ecomind_logo.png`

- [ ] **Large promo tile**: 920x680px (increases visibility)
- [ ] **Marquee**: 1400x560px (for featured placement)

**Tools**: Figma, Canva, or Photoshop

---

### 4. Privacy Policy Hosting (REQUIRED)

Chrome Web Store requires a **publicly accessible URL** for privacy policy.

**Current**: `chrome-store-assets/PRIVACY_POLICY.md` (not accessible)

**Options**:
1. **GitHub Pages** (free):
   ```bash
   # Enable GitHub Pages in repo settings
   # URL: https://blurjp.github.io/EcoMind/privacy-policy.html
   ```

2. **Your website**: 
   - Host at `https://yourdomain.com/privacy-policy`

3. **Google Sites** (free):
   - Create simple page with privacy policy text

**Action**: Host privacy policy and update manifest.json with URL

---

### 5. Support Email (REQUIRED)

Chrome Web Store requires a support email for users.

**Options**:
- `support@ecomind.biz`
- `support@ecomind.biz`
- Your personal/business email

---

### 6. Manifest Updates

**Current version**: `1.0.0`

**Optional improvements**:
```json
{
  "version": "1.0.1",  // Increment for any changes
  "description": "Updated with Grok support...",  // Update if needed
  "homepage_url": "https://your-actual-website.com"  // Update from GitHub
}
```

---

## 🚀 Submission Process

### Step 1: Final Preparation

```bash
cd ext-chrome

# 1. Remove debug logging from service-worker.ts
# 2. Update version in manifest.json (optional)
# 3. Final build
npm run build

# 4. Run tests one more time
npm test  # Should see 73/73 passing
```

### Step 2: Create Submission Package

```bash
cd /Users/jianphua/projects/EcoMind
./chrome-store-assets/create-submission-package.sh
# Creates: ecomind-submission.zip
```

### Step 3: Chrome Web Store Developer Console

1. **Create Account** (if needed):
   - Visit: https://chrome.google.com/webstore/devconsole
   - Pay $5 one-time registration fee

2. **Upload Extension**:
   - Click "New Item"
   - Upload `ecomind-submission.zip`

3. **Store Listing**:
   - Copy from `chrome-store-assets/STORE_LISTING.md`
   - Upload 3-5 screenshots
   - Upload promotional images (if created)

4. **Privacy Settings**:
   - Privacy policy URL: [Your hosted URL]
   - Data handling: Declare "storage" permission use
   - Remote code: No
   - Analytics: Optional telemetry (disclosed in privacy policy)

5. **Distribution**:
   - Visibility: Public
   - Regions: All
   - Pricing: Free

6. **Submit for Review**:
   - Review time: 1-3 business days
   - Watch email for approval/feedback

---

## 📊 Current Status Summary

### ✅ Ready
- Code quality (tests, build, no errors)
- Core functionality (12 AI providers)
- Recent fixes (HuggingFace, Grok web chat)
- Source cleanup (single source of truth)
- Documentation

### ⚠️ Needs Action
1. **Remove debug logging** (5 min)
2. **Create screenshots** (15 min)
3. **Host privacy policy** (10 min)
4. **Get support email** (5 min)
5. **Create promotional images** (30 min - optional)

**Total time to submission-ready**: ~45 minutes (without promo images)

---

## 🔄 Post-Submission

Once approved:
- Extension will be live on Chrome Web Store
- Users can install with one click
- You'll get a store URL: `https://chrome.google.com/webstore/detail/{extension-id}`

**Future updates**:
1. Increment `version` in manifest.json
2. Rebuild: `npm run build`
3. Create new ZIP
4. Upload to existing listing (triggers new review)

---

## 📞 Need Help?

**Documentation**:
- Chrome Web Store: https://developer.chrome.com/docs/webstore/
- Submission guide: chrome-store-assets/SUBMISSION_CHECKLIST.md
- Privacy policy: chrome-store-assets/PRIVACY_POLICY.md

**Common Issues**:
- Missing screenshots → Take 3-5 screenshots before submission
- Privacy policy URL → Must be publicly accessible (not GitHub raw URL)
- Debug logging → Remove before final build
- Version conflicts → Increment version for each submission

---

**Ready to submit in ~45 minutes!** 🚀
