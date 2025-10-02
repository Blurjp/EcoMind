# Screenshot Guide for Chrome Web Store

**Required**: 1-5 screenshots (1280x800 or 640x400 recommended)
**Format**: PNG or JPEG
**Purpose**: Show key features and functionality

---

## Screenshot Requirements

### Chrome Web Store Guidelines

- **Minimum**: 1 screenshot (required)
- **Recommended**: 3-5 screenshots
- **Dimensions**: 1280x800, 640x400, or same aspect ratio
- **Format**: PNG (preferred) or JPEG
- **File Size**: < 2 MB each
- **Quality**: High-resolution, clear text, professional appearance

---

## Recommended Screenshots

### Screenshot 1: Popup Dashboard (Primary)
**Priority**: CRITICAL
**Caption**: "Daily metrics at a glance: API calls, energy consumption, carbon emissions, and water usage"

**How to Capture**:
1. Load extension in Chrome
2. Click extension icon to open popup
3. Make sure popup shows default state or simulated data
4. Use screenshot tool (macOS: Cmd+Shift+4, Windows: Snipping Tool)
5. Capture entire popup window
6. Ensure 1280x800 or proportional

**What to Show**:
- Extension name/title
- Today's usage metrics (even if zeros)
- kWh, water, CO₂ display
- Clear/Settings buttons
- Clean, professional appearance

**Tips**:
- If showing zeros, add caption: "Clean slate - ready to track your AI usage"
- Consider using browser dev tools to inject sample data for better visual

---

### Screenshot 2: Options Page - General Settings
**Priority**: HIGH
**Caption**: "Configure telemetry, privacy mode, and environmental estimation parameters"

**How to Capture**:
1. Right-click extension icon → Options
2. Scroll to show General Settings section
3. Capture showing:
   - Backend URL field
   - User ID field
   - Privacy toggle (local-only mode)
   - Telemetry toggle
4. Ensure all labels are readable

**What to Show**:
- Privacy-first design (local-only mode toggle)
- Optional telemetry configuration
- User-friendly form layout
- Clear labeling

---

### Screenshot 3: Options Page - Estimation Parameters
**Priority**: MEDIUM
**Caption**: "Customize environmental impact calculations with industry-standard or custom parameters"

**How to Capture**:
1. Scroll to Estimation Parameters section in options
2. Capture showing:
   - kWh per call input
   - PUE (Power Usage Effectiveness) input
   - Water L/kWh input
   - CO₂ kg/kWh input
3. Show default values filled in

**What to Show**:
- Customizable parameters
- Scientific metrics (kWh, PUE, L, kg CO₂)
- Professional environmental tracking

---

### Screenshot 4: Options Page - Custom Providers
**Priority**: MEDIUM
**Caption**: "Add custom AI provider domains to track internal or specialized APIs"

**How to Capture**:
1. Scroll to Custom Providers section
2. Ideally, add 1-2 sample custom providers first:
   - `api.custom.com`
   - `internal-ai.example.com`
3. Capture showing:
   - Default providers list (OpenAI, Anthropic, etc.)
   - Custom providers section
   - Add domain input field
   - Remove button for custom providers

**What to Show**:
- Extensibility (custom providers)
- Built-in provider support
- Easy management (add/remove)

---

### Screenshot 5: Privacy Mode Demonstration (Optional)
**Priority**: LOW
**Caption**: "Local-only mode keeps all data on your device - nothing sent to servers"

**How to Capture**:
1. Options page with privacy toggle ON
2. Show warning/info message about local-only mode
3. Highlight disabled telemetry fields

**What to Show**:
- Privacy focus
- Clear visual feedback
- User control over data

---

## Creating Sample Data (Optional)

If you want screenshots with realistic data instead of zeros, use Chrome DevTools:

### Inject Sample Data into Popup

```javascript
// Open popup, then in DevTools console:
chrome.storage.local.set({
  'today-2025-01-01': {
    count: 127,
    totalKwh: 0.508,
    totalWaterL: 2.032,
    totalCo2Kg: 0.254
  }
}, () => {
  // Reload popup to show data
  window.location.reload();
});
```

Then capture the popup with realistic numbers.

---

## Screenshot Preparation Workflow

### Step 1: Set Up Extension
```bash
cd /Users/jianphua/projects/EcoMind/ext-chrome
npm run build
# Load dist/ in Chrome as unpacked extension
```

### Step 2: Open Extension
- Click extension icon (popup)
- Right-click → Options (options page)

### Step 3: Capture Screenshots
- macOS: `Cmd + Shift + 4` → Drag to select area
- Windows: Snipping Tool or `Win + Shift + S`
- Linux: `gnome-screenshot -a` or Screenshot tool

### Step 4: Resize/Optimize (if needed)
- Use Preview (macOS), Paint (Windows), or GIMP (all platforms)
- Target dimensions: 1280x800 or 640x400
- Save as PNG
- Verify file size < 2 MB

### Step 5: Name Files
```
screenshot-1-popup-dashboard.png
screenshot-2-options-general.png
screenshot-3-options-parameters.png
screenshot-4-options-providers.png
screenshot-5-privacy-mode.png
```

---

## Screenshot Checklist

Before uploading to Chrome Web Store:

- [ ] All screenshots are 1280x800 or 640x400 (or same aspect ratio)
- [ ] PNG format (preferred over JPEG)
- [ ] File sizes under 2 MB each
- [ ] Text is readable and clear
- [ ] No personal/sensitive information visible
- [ ] No browser chrome/toolbars (just extension UI)
- [ ] Professional appearance (no errors, broken layouts)
- [ ] Captions prepared for each screenshot
- [ ] At least 1 screenshot (recommended 3-5)

---

## Alternative: Use Mockups

If you prefer polished marketing screenshots:

1. **Design Tool**: Figma, Sketch, or Canva
2. **Template**: Chrome extension screenshot template
3. **Add**: Extension screenshots + marketing text
4. **Export**: 1280x800 PNG

This is optional - actual screenshots are perfectly acceptable.

---

## Tips for Great Screenshots

1. **Clean Background**: Plain white or light gray
2. **Readable Text**: Ensure all labels/numbers are clear
3. **Highlight Features**: Show key functionality
4. **Consistent Style**: Use same zoom level/window size
5. **No Clutter**: Hide unnecessary browser elements
6. **Professional**: No debug info, console errors, or test data

---

## What NOT to Include

- ❌ Browser address bar or tabs (unless necessary)
- ❌ Personal information or email addresses
- ❌ Console errors or debug messages
- ❌ Unfinished features or placeholder text
- ❌ Copyrighted content (e.g., actual AI prompts from services)
- ❌ Low-resolution or blurry images

---

## After Screenshots Are Ready

1. **Upload to Chrome Web Store Developer Console**:
   - Go to Store Listing → Graphic Assets
   - Upload each screenshot
   - Add captions
   - Reorder if needed (drag and drop)

2. **Preview**:
   - Check how screenshots appear in store listing
   - Verify captions display correctly
   - Test on different screen sizes

3. **Iterate**:
   - If screenshots don't convey value, retake
   - Get feedback from team/users
   - Update before final submission

---

## Example Caption Templates

Use these or customize:

**Popup**:
- "Monitor your AI usage: calls, energy, water, and carbon footprint"
- "Real-time environmental impact tracking"
- "See your daily AI sustainability metrics at a glance"

**Options - General**:
- "Privacy-first design with local-only mode"
- "Choose between local tracking or team telemetry"
- "Configure backend integration (optional)"

**Options - Parameters**:
- "Customize environmental calculations"
- "Industry-standard metrics with full control"
- "Adjust kWh, PUE, water, and CO₂ factors"

**Options - Providers**:
- "Track OpenAI, Anthropic, Google AI, and more"
- "Add custom domains for internal APIs"
- "Extensible provider support"

**Privacy Mode**:
- "Your data stays on your device"
- "No external tracking by default"
- "Full transparency and control"

---

## Quick Reference

**Minimum Viable Screenshots**:
1. Popup dashboard (REQUIRED)
2. Options page general view (RECOMMENDED)
3. Custom providers section (RECOMMENDED)

**Ideal Set**:
1. Popup with data
2. Options - General settings
3. Options - Estimation parameters
4. Options - Custom providers
5. Privacy mode highlight

**Time Estimate**: 30-60 minutes for all screenshots

---

**Status**: Ready to capture screenshots
**Next Action**: Load extension in Chrome and follow capture guide above
