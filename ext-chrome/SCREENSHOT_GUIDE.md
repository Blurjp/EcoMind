# Chrome Web Store Screenshot Guide

**Date**: October 2, 2025

---

## Requirements

Chrome Web Store requires **at least 1 screenshot** (maximum 5):
- **Size**: 1280×800 or 640×400 pixels
- **Format**: PNG or JPEG
- **Content**: Show key extension features

---

## Recommended Screenshots (5 total)

### 1. Extension Badge & Popup - Daily Metrics ⭐ PRIMARY
**Purpose**: Show the core tracking feature

**Steps to Capture**:
1. Load extension in Chrome (`chrome://extensions` → Load unpacked → `ext-chrome/dist`)
2. Visit ChatGPT or Claude and make 3-5 queries
3. Wait for badge to update (shows count like "5")
4. Click extension icon to open popup
5. Take screenshot showing:
   - Browser with extension badge visible
   - Popup open showing today's metrics
   - Clean browser chrome (no extra tabs)

**What Should Be Visible**:
- 🌱 Ecomind header
- Today's date (e.g., "Oct 2, 2025")
- Call count (e.g., "Calls: 5")
- Energy (e.g., "Energy: 0.005 kWh")
- CO₂ (e.g., "CO₂: 0.002 kg")
- Water (e.g., "Water: 0.01 L")
- Three buttons: Refresh, Options, Clear Today

**Screenshot Dimensions**: 1280×800
**Filename**: `screenshot-1-popup.png`
**Caption for Store**: "Real-time AI usage tracking with environmental impact metrics"

---

### 2. Options Page - Privacy Settings ⭐ PRIVACY FOCUS
**Purpose**: Highlight privacy-first design

**Steps to Capture**:
1. Click "Options" button in popup (or right-click extension icon → Options)
2. Options page opens in new tab
3. Scroll to show these sections together:
   - 🌐 Backend Configuration
   - 🔒 Privacy Settings
4. Take screenshot of options page

**What Should Be Visible**:
- "🌱 Ecomind Settings" header
- Backend URL field (empty or example: `https://api.example.com`)
- User ID field
- "Local-only mode" checkbox
- "Enable telemetry" checkbox
- Help text: "When enabled, all data stays on your device..."
- Privacy warning (if local mode is ON)

**Screenshot Dimensions**: 1280×800
**Filename**: `screenshot-2-privacy.png`
**Caption for Store**: "Privacy-first: Local-only mode keeps all data on your device"

---

### 3. Options Page - Provider Tracking
**Purpose**: Show supported providers + custom domain feature

**Steps to Capture**:
1. Stay on Options page
2. Scroll to "🎯 Tracking Providers" section
3. (Optional) Add 1-2 custom providers for demo:
   - Enter `api.custom-ai.com` → Click Add
   - Enter `internal.example.com` → Click Add
4. Take screenshot showing providers section

**What Should Be Visible**:
- Default providers with checkboxes:
  - OpenAI (api.openai.com)
  - Anthropic (api.anthropic.com)
  - Google (generativelanguage.googleapis.com)
  - Perplexity, Mistral, etc.
- Custom Providers section
- Input field: "api.custom-ai.com"
- "Add" button
- Listed custom providers (if you added any)

**Screenshot Dimensions**: 1280×800
**Filename**: `screenshot-3-providers.png`
**Caption for Store**: "Track OpenAI, Anthropic, Google AI, and custom domains"

---

### 4. Options Page - Environmental Parameters
**Purpose**: Show customizable estimation settings

**Steps to Capture**:
1. Scroll to "🌍 Environmental Estimation" section
2. Make sure all parameter fields show default values:
   - kWh per API call: 0.001
   - Power Usage Effectiveness (PUE): 1.2
   - Water (L per kWh): 0.4
   - CO₂ (kg per kWh): 0.5
3. Take screenshot of this section

**What Should Be Visible**:
- Section title: "🌍 Environmental Estimation"
- Description text
- Four input fields with labels and values
- Help text under each field
- "Reset to Defaults" button
- "Save Settings" button (optionally with "✓ Saved" indicator)

**Screenshot Dimensions**: 1280×800
**Filename**: `screenshot-4-environment.png`
**Caption for Store**: "Customize environmental impact calculations with industry-standard parameters"

---

### 5. Extension Badge in Action
**Purpose**: Show real-time tracking during AI usage

**Steps to Capture**:
1. Open ChatGPT or Claude in a tab
2. Make sure extension badge shows a count (e.g., "12")
3. Take screenshot showing:
   - AI service tab (ChatGPT/Claude)
   - Extension badge with count visible in toolbar
   - Clean browser view

**What Should Be Visible**:
- AI service website (ChatGPT or Claude interface)
- Extension icon with badge counter (e.g., "12")
- Minimal browser chrome (just enough to see extension)

**Screenshot Dimensions**: 1280×800
**Filename**: `screenshot-5-tracking.png`
**Caption for Store**: "Automatically tracks API calls to AI services in real-time"

---

## How to Take Screenshots

### macOS (Recommended)
```bash
# Press Cmd+Shift+4
# Click and drag to select area
# File saves to Desktop as "Screenshot YYYY-MM-DD at HH.MM.SS.png"
```

### Windows
```bash
# Press Win+Shift+S (Snipping Tool)
# Select area
# Save as PNG
```

### Linux
```bash
gnome-screenshot -a  # Area screenshot
# Or use Spectacle, Flameshot, etc.
```

---

## Resize Screenshots (if needed)

### macOS Preview
1. Open screenshot in Preview
2. Tools → Adjust Size
3. Set Width: 1280, Height: 800
4. Uncheck "Scale proportionally"
5. Save

### ImageMagick (all platforms)
```bash
brew install imagemagick  # macOS
# or apt install imagemagick (Linux)

convert screenshot.png -resize 1280x800! screenshot-resized.png
```

---

## Create Sample Data (Optional)

If you want realistic numbers instead of zeros, inject sample data:

### Open Extension Popup Console
1. Click extension icon to open popup
2. Right-click popup → Inspect
3. Go to Console tab
4. Paste this code:

```javascript
const today = new Date().toISOString().split('T')[0];
chrome.storage.local.set({
  ecomind_daily_usage: {
    [today]: {
      callCount: 47,
      totalKwh: 0.047,
      totalWaterL: 0.019,
      totalCo2Kg: 0.024,
      providers: {
        openai: { count: 28, models: { 'gpt-4': 28 } },
        anthropic: { count: 19, models: { 'claude-3-5-sonnet': 19 } }
      }
    }
  }
}, () => {
  chrome.action.setBadgeText({ text: '47' });
  window.location.reload();
});
```

5. Popup will reload with sample data
6. Take screenshot

---

## Screenshot Preparation Workflow

### 1. Build Extension
```bash
cd /Users/jianphua/projects/EcoMind/ext-chrome
npm run build
```

### 2. Load in Chrome
```
1. Open chrome://extensions
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select /Users/jianphua/projects/EcoMind/ext-chrome/dist
```

### 3. Generate Usage Data
```
- Visit https://chatgpt.com
- Make 3-5 queries (or inject sample data via console)
- Badge should show count
```

### 4. Capture Screenshots
```
- Screenshot 1: Popup with badge visible
- Screenshot 2: Options → Privacy section
- Screenshot 3: Options → Providers section
- Screenshot 4: Options → Environment section
- Screenshot 5: Badge in action
```

### 5. Save to Directory
```bash
mkdir -p screenshots
mv ~/Desktop/Screenshot*.png screenshots/
cd screenshots
# Rename files:
mv Screenshot1.png screenshot-1-popup.png
mv Screenshot2.png screenshot-2-privacy.png
# etc.
```

---

## Screenshot Checklist

Before uploading to Chrome Web Store:

- [ ] All screenshots are 1280×800 (or 640×400 minimum)
- [ ] PNG format (preferred over JPEG)
- [ ] File sizes under 2 MB each
- [ ] Text is readable and clear
- [ ] No personal/sensitive information visible
- [ ] Professional appearance (no errors, broken layouts)
- [ ] Captions prepared for each screenshot:
  - Screenshot 1: "Real-time AI usage tracking with environmental impact metrics"
  - Screenshot 2: "Privacy-first: Local-only mode keeps all data on your device"
  - Screenshot 3: "Track OpenAI, Anthropic, Google AI, and custom domains"
  - Screenshot 4: "Customize environmental impact calculations with industry-standard parameters"
  - Screenshot 5: "Automatically tracks API calls to AI services in real-time"
- [ ] At least 1 screenshot captured (recommended 5)

---

## Tips for Great Screenshots

1. **Clean Background**: Plain browser interface
2. **Readable Text**: Ensure all labels/numbers are clear
3. **Highlight Features**: Show key functionality
4. **Consistent Style**: Use same zoom level/window size
5. **No Clutter**: Hide unnecessary browser elements (bookmarks bar, extra tabs)
6. **Professional**: No debug info, console errors, or test data

---

## What NOT to Include

- ❌ Personal information or email addresses
- ❌ Console errors or debug messages
- ❌ Unfinished features or placeholder text
- ❌ Copyrighted content (actual AI conversation content)
- ❌ Low-resolution or blurry images

---

## Where to Save

```bash
mkdir -p /Users/jianphua/projects/EcoMind/ext-chrome/screenshots
cd screenshots
# Save files as:
# - screenshot-1-popup.png
# - screenshot-2-privacy.png
# - screenshot-3-providers.png
# - screenshot-4-environment.png
# - screenshot-5-tracking.png
```

---

## Upload to Chrome Web Store

1. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
2. Create new item or edit existing
3. Under "Store listing" → "Graphic assets" → Screenshots:
   - Click "Choose file"
   - Upload PNG files (up to 5)
   - Add captions from checklist above
   - Drag to reorder (first screenshot shows prominently)
4. Save draft

---

## Quick Reference

**Minimum Viable**:
- Screenshot 1: Popup dashboard (REQUIRED)

**Recommended Set** (all 5):
1. Popup with badge visible
2. Options - Privacy settings
3. Options - Provider tracking
4. Options - Environmental parameters
5. Badge in action on AI service

**Time Estimate**: 15-30 minutes for all 5 screenshots

---

**Status**: Ready to capture screenshots
**Next Action**: Follow "Screenshot Preparation Workflow" above to capture all 5 screenshots
