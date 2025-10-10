# Manual Tasks Before Chrome Web Store Submission

**Besides screenshots, here's what you need to do manually:**

---

## 1. Remove Debug Logging (5 min) ⚠️ CRITICAL

**File**: `ext-chrome/src/bg/service-worker.ts`

**Find and DELETE lines 62-69:**

```typescript
// DELETE THIS ENTIRE BLOCK:
if (details.url.toLowerCase().includes('x.ai') || details.url.toLowerCase().includes('perplexity')) {
  console.log('[EcoMind DEBUG] Request detected:', {
    url: details.url,
    tracked: this.providerManager.shouldTrackRequest(details.url),
    provider: this.providerManager.findProviderForUrl(details.url)
  });
}
```

**Why**: Chrome Web Store rejects extensions with debug/console logging in production code.

**After removing:**
```bash
cd ext-chrome
npm run build
npm test  # Should still show 73/73 passing
```

---

## 2. Host Privacy Policy (10 min) ⚠️ REQUIRED

Chrome Web Store **requires a publicly accessible URL** for your privacy policy.

**Option A: GitHub Pages (Recommended)**

1. Create docs folder:
   ```bash
   mkdir -p docs
   cp chrome-store-assets/PRIVACY_POLICY.md docs/privacy-policy.md
   ```

2. Enable GitHub Pages:
   - Go to: https://github.com/Blurjp/EcoMind/settings/pages
   - Source: "Deploy from a branch"
   - Branch: `main`
   - Folder: `/docs`
   - Click "Save"

3. Wait 1-2 minutes for deployment

4. Your privacy policy URL will be:
   ```
   https://blurjp.github.io/EcoMind/privacy-policy.html
   ```

**Option B: GitHub Gist (Faster, but less professional)**

1. Go to: https://gist.github.com
2. Click "New gist"
3. Copy content from `chrome-store-assets/PRIVACY_POLICY.md`
4. Paste into gist
5. Name it: `ecomind-privacy-policy.md`
6. Click "Create public gist"
7. Copy the gist URL

**Option C: Your Own Website**

Host the privacy policy at:
- `https://yourdomain.com/ecomind/privacy-policy`
- Any public URL that won't change

---

## 3. Set Up Support Email (5 min) ⚠️ REQUIRED

Chrome Web Store requires a support email for user inquiries.

**Options:**

1. **Create Gmail specifically for this**:
   - `support@ecomind.biz`
   - Easy to set up, free
   - Professional-looking

2. **Use your personal email**:
   - Your existing Gmail/email
   - Quick but less separation

3. **Business email** (if you have one):
   - `support@yourdomain.com`
   - Most professional

**You'll enter this email during Chrome Web Store submission.**

---

## 4. (Optional) Update Manifest Metadata (5 min)

**File**: `ext-chrome/manifest.json`

**Current state:**
```json
{
  "version": "1.0.0",
  "description": "Privacy-first AI sustainability tracker. Calculate carbon footprint, energy, and water usage for OpenAI, Anthropic, and custom APIs.",
  "author": "Ecomind Team",
  "homepage_url": "https://github.com/Blurjp/EcoMind"
}
```

**Consider updating:**

```json
{
  "version": "1.0.1",  // Increment if you made changes today
  "description": "Privacy-first AI sustainability tracker. Track environmental impact of ChatGPT, Claude, Grok, and 12+ AI providers. Monitor carbon footprint, energy, and water usage.",
  "author": "Your Name or Company",  // Update if needed
  "homepage_url": "https://youractualwebsite.com"  // Update if you have one
}
```

**Why increment version?**
- You made fixes today (HuggingFace, Grok web chat)
- Shows freshness to reviewers

---

## 5. Chrome Web Store Submission Form (10 min)

When submitting, you'll need to **manually fill out** these fields:

### Store Listing Tab

- **Name**: Ecomind - AI Sustainability Tracker
- **Summary**: Privacy-first AI sustainability tracker (132 char limit)
- **Description**: Copy/paste from `chrome-store-assets/STORE_LISTING.md`
- **Category**: Choose from dropdown → **Productivity** or **Developer Tools**
- **Language**: English

### Additional Info

- **Support Email**: [The email you set up in step 3]
- **Website**: https://github.com/Blurjp/EcoMind (or your website)
- **Privacy Policy URL**: [The URL from step 2]

### Privacy Practices

You'll need to **declare** what data you collect:

**If using local-only mode (default):**
- ☑ "This item does NOT collect or share user data"

**If telemetry is enabled (optional):**
- ☑ "This item collects user data"
- Data types: "User activity" (API call metadata)
- Purpose: "Analytics"
- Usage: "Data is NOT sold to third parties"
- ☑ "Disclosed in privacy policy"

**Permissions Justification** (you'll need to explain):
- `storage` → "Store usage statistics locally on user's device"
- `webRequest` → "Monitor AI API requests to calculate environmental impact"  
- `alarms` → "Reset daily statistics at midnight"
- `<all_urls>` → "Track requests to various AI providers (OpenAI, Anthropic, etc.)"

**Single Purpose** (required statement):
- "Track environmental impact of AI API usage"

---

## 6. (Optional) Create Promotional Tiles

These **increase visibility** but are not required for submission.

**Small Promo Tile**: 440x280px
- Use `ecomind_logo.png`
- Green background (#2D5F3F)
- Add text: "Track AI Impact"

**Tools**: Canva (free), Figma, Photoshop

**Skip this if you want to submit quickly** - you can add later.

---

## Summary: Required Manual Work

| Task | Time | Required? | Complexity |
|------|------|-----------|------------|
| 1. Remove debug logging | 5 min | ✅ YES | Easy |
| 2. Host privacy policy | 10 min | ✅ YES | Medium |
| 3. Support email | 5 min | ✅ YES | Easy |
| 4. Update manifest | 5 min | ⚠️ Optional | Easy |
| 5. Fill submission form | 10 min | ✅ YES | Easy |
| 6. Promo tiles | 30 min | ❌ Optional | Medium |

**Total Required Time**: ~30 minutes (without screenshots)
**Total with Screenshots**: ~45 minutes

---

## What's Automated?

✅ **Build process**: `npm run build`
✅ **Testing**: `npm test` (73/73 passing)
✅ **Packaging**: `./chrome-store-assets/create-submission-package.sh`
✅ **Store listing text**: Already written in `chrome-store-assets/STORE_LISTING.md`
✅ **Privacy policy**: Already written, just needs hosting

---

## Order of Operations

**Do this in order:**

1. ✅ Remove debug logging → Rebuild → Test
2. ✅ Host privacy policy (GitHub Pages or Gist)
3. ✅ Set up support email
4. ✅ Take screenshots (3-5 images)
5. ⚠️ (Optional) Update manifest version/description
6. ✅ Run packaging script
7. ✅ Go to Chrome Web Store and fill form

**Then wait 1-3 days for approval!**

---

## Need Help?

- **Debug logging location**: `ext-chrome/src/bg/service-worker.ts:62-69`
- **Privacy policy source**: `chrome-store-assets/PRIVACY_POLICY.md`
- **Store listing text**: `chrome-store-assets/STORE_LISTING.md`
- **Packaging script**: `chrome-store-assets/create-submission-package.sh`

**All the content is ready - you just need to host it and fill forms!**
