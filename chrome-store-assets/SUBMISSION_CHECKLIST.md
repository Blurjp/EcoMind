# Chrome Web Store Submission Checklist

## ✅ Assets Ready

### Icons (Already created in `dist/icons/`)
- [x] 16x16 icon
- [x] 48x48 icon
- [x] 128x128 icon

### Documents Created
- [x] Privacy Policy: `chrome-store-assets/PRIVACY_POLICY.md`
- [x] Store Listing Text: `chrome-store-assets/STORE_LISTING.md`

## 📸 Screenshots Needed

You need to create 3-5 screenshots (1280x800px or 640x400px). Recommended:

1. **Main popup with usage data**
   - Open extension popup while you have some usage data
   - Take screenshot showing call count, environmental metrics

2. **Top Providers & Models**
   - Screenshot showing the providers and models sections

3. **Settings page**
   - Open options page (click gear icon)
   - Screenshot showing privacy and telemetry settings

4. **Empty state**
   - Clear today's data
   - Screenshot showing "No API calls detected today"

5. **Backend data mode** (optional)
   - Screenshot with "🌐 Backend data" indicator

**How to take screenshots:**
1. Open extension in Chrome
2. Use browser's built-in screenshot tool or press Cmd+Shift+4 (Mac)
3. Save to `chrome-store-assets/screenshots/`
4. Ensure they're at least 640x400px

## 🎨 Promotional Images Needed

### Required:
- **Small promo tile**: 440x280px
  - Use green background with leaf/circuit logo
  - Add text: "Track AI Impact"

### Optional (increases visibility):
- **Large promo tile**: 920x680px
- **Marquee**: 1400x560px

You can create these using:
- Figma, Canva, or Photoshop
- Use the existing logo (`ecomind_logo.png`)
- Match the green theme (#2D5F3F)

## 📦 Package for Submission

Once screenshots are ready, run:

```bash
cd /Users/jianphua/projects/EcoMind
./chrome-store-assets/create-submission-package.sh
```

This will create `ecomind-submission.zip` with:
- dist/ (extension files)
- manifest.json
- All assets in proper structure

## 🚀 Submission Steps

1. **Create Developer Account**
   - Go to: https://chrome.google.com/webstore/devconsole
   - Pay $5 one-time registration fee

2. **Upload Package**
   - Click "New Item"
   - Upload `ecomind-submission.zip`

3. **Fill Store Listing**
   - Copy text from `STORE_LISTING.md`
   - Upload screenshots (3-5 images)
   - Upload promotional tiles (if created)

4. **Set Privacy**
   - Privacy policy URL: [You need to host PRIVACY_POLICY.md on your website]
   - Declare data collection practices
   - Check "Uses remote code: No"

5. **Distribution**
   - Visibility: Public
   - Geographic distribution: All regions
   - Pricing: Free

6. **Submit for Review**
   - Review takes 1-3 business days
   - Check email for approval/rejection

## 📝 Notes

- **Version**: Currently 1.0.0 (from manifest.json)
- **Support email**: Provide during submission (e.g., support@ecomind.ai)
- **Homepage URL**: Your website or product page
- **Privacy Policy**: Must be publicly accessible URL (not GitHub)

## 🔄 After Approval

To update the extension:
1. Increment version in `manifest.json`
2. Rebuild: `npm run build`
3. Create new ZIP package
4. Upload to existing listing (will trigger new review)
