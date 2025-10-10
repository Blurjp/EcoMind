# Quick Chrome Web Store Submission Guide

**Ready to submit in 45 minutes!**

---

## 📋 Pre-Flight Checklist

✅ **Code is ready**:
- 73/73 tests passing
- 12 AI providers supported (including Grok web chat!)
- Clean build with no errors
- HuggingFace & Grok fixes deployed

⚠️ **Need to do before submission**:
1. Remove debug logging (5 min)
2. Take screenshots (15 min)
3. Host privacy policy (10 min)
4. Set up support email (5 min)

---

## 🚀 Action Items (In Order)

### 1. Remove Debug Logging (5 min)

```bash
cd /Users/jianphua/projects/EcoMind/ext-chrome
```

**Edit**: `src/bg/service-worker.ts` - Remove lines 62-69:
```typescript
// DELETE THESE LINES:
if (details.url.toLowerCase().includes('x.ai') || details.url.toLowerCase().includes('perplexity')) {
  console.log('[EcoMind DEBUG] Request detected:', {
    url: details.url,
    tracked: this.providerManager.shouldTrackRequest(details.url),
    provider: this.providerManager.findProviderForUrl(details.url)
  });
}
```

Then rebuild:
```bash
npm run build
npm test  # Verify still 73/73 passing
```

---

### 2. Take Screenshots (15 min)

**Open extension and take 3-5 screenshots**:

1. **Make some test API calls** to populate data:
   - Use ChatGPT, Claude, or any supported AI service
   - Let extension track a few requests

2. **Screenshot 1: Main Popup** (REQUIRED)
   - Click extension icon in toolbar
   - Screenshot showing:
     - Call count
     - Environmental metrics (kWh, water, CO₂)
     - Top providers/models
   - Save as `screenshot-1-popup.png`

3. **Screenshot 2: Options Page** (REQUIRED)
   - Click gear icon in popup OR right-click extension → Options
   - Screenshot showing:
     - Privacy settings
     - Telemetry toggle
     - Custom providers
   - Save as `screenshot-2-options.png`

4. **Screenshot 3: Providers View** (REQUIRED)
   - Screenshot of providers/models section in popup
   - Save as `screenshot-3-providers.png`

**Save to**: `chrome-store-assets/screenshots/`

**Requirements**:
- Minimum size: 640x400px
- Recommended: 1280x800px
- Format: PNG or JPEG

---

### 3. Host Privacy Policy (10 min)

**Easiest option: GitHub Pages**

```bash
# 1. Create docs folder in repo
mkdir -p /Users/jianphua/projects/EcoMind/docs

# 2. Convert privacy policy to HTML
cp chrome-store-assets/PRIVACY_POLICY.md docs/privacy-policy.md

# 3. Enable GitHub Pages:
# - Go to: https://github.com/Blurjp/EcoMind/settings/pages
# - Source: Deploy from a branch
# - Branch: main
# - Folder: /docs
# - Click Save

# 4. Your privacy policy URL will be:
# https://blurjp.github.io/EcoMind/privacy-policy
```

**Alternative: Use GitHub Gist** (faster):
1. Go to https://gist.github.com
2. Create new gist
3. Paste privacy policy content
4. Save as public
5. Use the gist URL

---

### 4. Set Support Email (5 min)

Choose one:
- Use: `support@ecomind.biz`
- Or use your personal email
- Or business email if you have one

**You'll enter this during Chrome Web Store submission.**

---

### 5. Final Build & Package (5 min)

```bash
cd /Users/jianphua/projects/EcoMind

# Run the packaging script
./chrome-store-assets/create-submission-package.sh

# This creates: ecomind-submission.zip
```

---

## 🌐 Chrome Web Store Submission

### Step 1: Create Developer Account

1. Visit: https://chrome.google.com/webstore/devconsole
2. Sign in with Google account
3. Pay $5 one-time registration fee
4. Accept developer agreement

### Step 2: Upload Extension

1. Click **"New Item"** button
2. Upload `ecomind-submission.zip`
3. Wait for upload to complete

### Step 3: Fill Store Listing

**Store Listing Tab**:
- **Name**: Ecomind - AI Sustainability Tracker
- **Summary**: Privacy-first AI sustainability tracker
- **Description**: Copy from `chrome-store-assets/STORE_LISTING.md`
- **Category**: Productivity
- **Language**: English

**Graphic Assets**:
- Upload 3-5 screenshots (from step 2)
- Small tile: 440x280px (optional - can skip for now)

**Additional Fields**:
- **Support Email**: [Your email from step 4]
- **Website**: https://github.com/Blurjp/EcoMind
- **Privacy Policy**: [Your hosted URL from step 3]

### Step 4: Privacy Practices

**Data Handling**:
- [ ] Does NOT handle user data (if using local-only mode)
- OR
- [x] Collects usage data (if telemetry enabled)
  - Check: "User activity"
  - Purpose: "Analytics"
  - Disclosed in privacy policy

**Permissions Justification**:
- `storage`: Store usage statistics locally
- `webRequest`: Monitor AI API calls
- `alarms`: Reset daily statistics at midnight

**Remote Code**: No

### Step 5: Distribution

- **Visibility**: Public
- **Regions**: All regions
- **Pricing**: Free
- **Mature Content**: No

### Step 6: Submit for Review

1. Click **"Submit for Review"**
2. Review time: 1-3 business days
3. Check email for approval/rejection
4. If rejected, fix issues and resubmit

---

## ⏱️ Time Estimate

- Remove debug logging: **5 min**
- Take screenshots: **15 min**
- Host privacy policy: **10 min**
- Set up email: **5 min**
- Package extension: **5 min**
- Fill store listing: **10 min**
- **Total: ~50 minutes**

---

## ✅ After Approval

Once approved (1-3 days):
- You'll get an email notification
- Extension will be live on Chrome Web Store
- Store URL: `https://chrome.google.com/webstore/detail/{extension-id}`
- Share the URL for users to install!

---

## 🔄 Future Updates

To update the extension later:

```bash
# 1. Make code changes
# 2. Update version
cd ext-chrome
# Edit manifest.json: "version": "1.0.1" → "1.0.2"

# 3. Rebuild
npm run build
npm test

# 4. Create new package
cd ..
./chrome-store-assets/create-submission-package.sh

# 5. Upload to Chrome Web Store
# - Go to developer console
# - Click your extension
# - Click "Package" → "Upload new package"
# - Submit for review
```

---

## 📞 Support

**Issues?**
- Chrome Web Store Help: https://support.google.com/chrome_webstore
- Developer Docs: https://developer.chrome.com/docs/webstore/
- GitHub Issues: https://github.com/Blurjp/EcoMind/issues

**Common Problems**:
- "Privacy policy not accessible" → Make sure URL is public (not GitHub raw)
- "Screenshots required" → Need at least 3 screenshots
- "Debug code detected" → Remove console.log statements

---

**Ready to launch! 🚀**

Start with step 1 (remove debug logging) and work through the list.
