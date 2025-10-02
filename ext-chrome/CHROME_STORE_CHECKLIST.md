# Chrome Web Store Submission Checklist

**Extension**: Ecomind
**Version**: 1.0.0
**Status**: Pre-submission

---

## ✅ Completed Items

### 1. Code Quality
- [x] TypeScript strict mode compilation passes
- [x] All security fixes implemented (7 issues resolved)
- [x] XSS prevention in place
- [x] No hardcoded secrets or API keys
- [x] Build artifacts generated (`dist/` directory)

### 2. Manifest V3 Compliance
- [x] Using Manifest V3 (`manifest_version: 3`)
- [x] Service worker instead of background page
- [x] Appropriate permissions declared
- [x] Host permissions justified (`<all_urls>` for web request tracking)

### 3. Required Assets
- [x] Icons (16x16, 48x48, 128x128) ✅
- [x] Popup HTML (`dist/ui/popup.html`) ✅
- [x] Options page (`dist/ui/options.html`) ✅
- [x] Service worker bundle (`dist/bg/service-worker.js`) ✅

---

## 📋 Pre-Submission Tasks

### 1. Store Listing Materials

#### Required Screenshots (1280x800 or 640x400)
- [ ] Main dashboard/popup view showing metrics
- [ ] Options page with settings
- [ ] Example of tracking AI API usage
- [ ] Privacy settings demonstration
- [ ] (Optional) 3-5 total screenshots recommended

#### Promotional Images (Optional but Recommended)
- [ ] Small tile: 440x280 PNG
- [ ] Marquee: 1400x560 PNG (for featured listings)

#### Store Listing Text
- [ ] **Detailed description** (minimum 80 characters, recommended 500-1000)
- [ ] **Short description** (132 characters max) - for search results
- [ ] **Category**: Select appropriate category (Productivity suggested)
- [ ] **Language**: Primary language selection

**Suggested Short Description**:
```
Track environmental impact of AI API usage. Monitor energy, water, and carbon footprint across OpenAI, Anthropic, and custom providers.
```

**Suggested Detailed Description Template**:
```markdown
Ecomind helps you understand and reduce the environmental impact of AI API usage.

FEATURES:
• Real-time tracking of API calls across major providers (OpenAI, Anthropic, Google AI, etc.)
• Calculate energy consumption (kWh) and carbon emissions (CO₂)
• Water usage estimates for data center operations
• Privacy-first: Local-only mode available, no prompts logged
• Custom provider support for internal APIs
• Daily metrics and trend visualization

PRIVACY & SECURITY:
• No sensitive data collection - only metadata (timestamps, token counts)
• Optional telemetry to your own backend
• Open source and auditable
• GDPR/CCPA compliant design

PERFECT FOR:
• Developers monitoring AI integration costs
• Organizations tracking sustainability metrics
• ESG reporting and environmental accountability
• Conscious AI users wanting to reduce their footprint

PERMISSIONS EXPLAINED:
• Storage: Save settings and daily metrics locally
• Web Request: Detect API calls to supported providers
• Alarms: Reset daily counters at midnight

Learn more: [Your website/GitHub URL]
Support: [Your support email]
```

### 2. Legal & Privacy

#### Privacy Policy (REQUIRED)
- [ ] Create publicly accessible privacy policy URL
- [ ] Must explain data collection practices
- [ ] Must be hosted (GitHub Pages, website, etc.)

**Privacy Policy Essentials**:
```markdown
Required sections:
1. What data is collected (token counts, timestamps, provider names)
2. What is NOT collected (prompts, completions, personal data)
3. How data is stored (chrome.storage.local, optional backend)
4. Third-party data sharing (none, or specify backend)
5. User rights (data deletion, access)
6. Contact information
```

**Quick Start**: Reference `/docs/PRIVACY.md` as foundation

#### Additional Legal Documents
- [ ] **Terms of Service** (recommended but not required)
- [ ] **End User License Agreement** (if applicable)

### 3. Manifest Enhancements

#### Current Manifest Improvements Needed:

**manifest.json updates**:
```json
{
  "name": "Ecomind - AI Sustainability Tracker",  // More descriptive
  "short_name": "Ecomind",
  "version": "1.0.0",
  "description": "Track environmental impact of AI API usage: energy, water, and carbon footprint monitoring",  // More detailed (132 char max)
  "author": "Your Name/Organization",  // Add this
  "homepage_url": "https://github.com/yourorg/ecomind",  // Add this

  // Consider if you truly need <all_urls> - be specific if possible
  "host_permissions": [
    "https://api.openai.com/*",
    "https://api.anthropic.com/*",
    "https://generativelanguage.googleapis.com/*",
    // ... or keep <all_urls> with justification in listing
  ],

  // Optional but recommended
  "commands": {
    "_execute_action": {
      "suggested_key": {
        "default": "Ctrl+Shift+E"
      }
    }
  }
}
```

- [ ] Update `description` to be more descriptive
- [ ] Add `author` field
- [ ] Add `homepage_url` (GitHub or website)
- [ ] Consider narrowing `host_permissions` or justify `<all_urls>`

### 4. Testing Requirements

#### Manual Testing Checklist
- [ ] Fresh install in Chrome (Load unpacked from `dist/`)
- [ ] Test popup displays correctly
- [ ] Test options page saves settings
- [ ] Verify API call tracking works (test with OpenAI/Anthropic)
- [ ] Test privacy mode (local-only)
- [ ] Test telemetry connection (if applicable)
- [ ] Verify daily counter reset at midnight
- [ ] Test custom provider addition/removal
- [ ] Test "Reset to Defaults" functionality
- [ ] Verify all links work (if any)
- [ ] Check console for errors

#### Cross-Browser Testing (Optional for Chrome Store)
- [ ] Test in Edge (uses Chrome extensions)
- [ ] Test in Brave (uses Chrome extensions)

### 5. Package for Submission

#### Create Distribution ZIP
```bash
cd /Users/jianphua/projects/EcoMind/ext-chrome

# Option 1: Package entire dist folder
zip -r ecomind-v1.0.0.zip dist/ manifest.json

# Option 2: Package only necessary files (recommended)
zip -r ecomind-v1.0.0.zip \
  manifest.json \
  dist/bg/ \
  dist/ui/ \
  dist/icons/ \
  dist/*.js
```

**Important**:
- [ ] Verify zip is under 20 MB (current build is ~34 KB, well under limit)
- [ ] Do NOT include `node_modules/`, `src/`, `.git/`, or test files
- [ ] Only include production build artifacts

### 6. Developer Account Setup

#### Chrome Web Store Developer Account
- [ ] Register at https://chrome.google.com/webstore/devconsole
- [ ] Pay one-time $5 registration fee
- [ ] Verify developer email
- [ ] Complete developer profile

### 7. Content Compliance Review

#### Chrome Web Store Program Policies
- [ ] **Deceptive Installation Tactics**: None (✓)
- [ ] **User Data Privacy**: Privacy policy required (pending)
- [ ] **Prohibited Products**: Not applicable (✓)
- [ ] **Spam & Placement**: No keyword stuffing (✓)
- [ ] **Functionality**: Extension does what description says (✓)
- [ ] **Permissions Justification**: Document why you need each permission

**Permission Justifications to Include in Listing**:
```
PERMISSIONS EXPLAINED:
• Storage: Required to save your settings and daily usage metrics locally
• Web Request: Needed to detect API calls to AI providers for tracking
• Alarms: Used to reset daily counters at midnight automatically
• Host Permissions (<all_urls>): Required to monitor requests to custom AI provider domains you configure
```

### 8. Post-Submission Preparation

#### Support Infrastructure
- [ ] Set up support email (required in listing)
- [ ] Create GitHub Issues page (optional but recommended)
- [ ] Prepare FAQ document
- [ ] Set up monitoring for user feedback

#### Update Strategy
- [ ] Plan for versioning (semantic versioning)
- [ ] Set up changelog documentation
- [ ] Prepare update communication plan

---

## 🚀 Submission Process

### Step-by-Step Submission

1. **Navigate to Developer Dashboard**
   - Go to https://chrome.google.com/webstore/devconsole
   - Click "New Item"

2. **Upload ZIP Package**
   - Upload `ecomind-v1.0.0.zip`
   - Wait for automatic analysis

3. **Fill Store Listing**
   - **Product Details**:
     - Language
     - Name: "Ecomind - AI Sustainability Tracker"
     - Summary (short description, 132 chars)
     - Category: Productivity (or Developer Tools)

   - **Graphic Assets**:
     - Icon (128x128) - auto-populated from manifest
     - Screenshots (1-5 images)
     - Promotional images (optional)

   - **Additional Details**:
     - Detailed description
     - Privacy policy URL (**REQUIRED**)
     - Homepage URL
     - Support email/URL

   - **Privacy Practices** (New requirement):
     - Do you collect personal data? (No, or Yes with justification)
     - Is data used for purposes unrelated to functionality? (No)
     - Do you sell user data? (No)
     - Privacy policy certification

4. **Distribution Options**
   - Public (anyone can install)
   - Unlisted (only those with link)
   - Private (specific Google Workspace domains)

5. **Submit for Review**
   - Review takes 1-3 days typically
   - May take longer for first submission
   - Be responsive to reviewer questions

---

## ⚠️ Common Rejection Reasons (Avoid These)

1. **Missing Privacy Policy** - Most common! Create before submitting
2. **Excessive Permissions** - Justify `<all_urls>` or narrow scope
3. **Poor Screenshots** - Must clearly show functionality
4. **Vague Description** - Be specific about what extension does
5. **Broken Functionality** - Test thoroughly before submission
6. **Misleading Metadata** - Name/description must match actual function
7. **Minified/Obfuscated Code** - Reviewers need readable code
   - **Current status**: ✅ Vite builds are acceptable, use source maps

---

## 📊 Pre-Launch Optimization

### SEO & Discoverability

**Keywords to Target** (include naturally in description):
- AI sustainability
- Environmental impact
- Carbon footprint
- API monitoring
- Energy tracking
- OpenAI tracking
- Anthropic monitoring
- Developer tools

### Analytics Preparation
- [ ] Set up Google Analytics (optional, privacy-compliant)
- [ ] Plan metrics to track (installs, active users, uninstalls)
- [ ] Create feedback collection mechanism

---

## 🎯 Immediate Next Steps (Priority Order)

### Critical (Required for Submission)
1. **Create Privacy Policy** - Host publicly accessible URL
2. **Take 3-5 Screenshots** - Demonstrate key features
3. **Write Store Listing Copy** - Short + detailed descriptions
4. **Update manifest.json** - Add author, homepage_url, improve description
5. **Create Distribution ZIP** - Package only production files
6. **Register Developer Account** - Pay $5 fee if not done

### Important (Highly Recommended)
7. **Test Fresh Install** - Verify everything works from clean slate
8. **Set Up Support Email** - Create dedicated address
9. **Justify Permissions** - Document why each permission is needed
10. **Review Content Policy** - Ensure 100% compliance

### Optional (Improves Success)
11. **Create Promotional Graphics** - 440x280 tile, 1400x560 marquee
12. **Prepare FAQ** - Common questions about tracking/privacy
13. **Set Up GitHub Issues** - For user feedback
14. **Add Terms of Service** - Legal protection

---

## 📝 Quick Action Template

```bash
# 1. Create privacy policy (use docs/PRIVACY.md as base)
# Host on GitHub Pages or your website

# 2. Take screenshots
# Open extension in Chrome, capture:
#   - Popup with metrics
#   - Options page
#   - Custom provider setup

# 3. Build distribution package
cd /Users/jianphua/projects/EcoMind/ext-chrome
npm run build
zip -r ecomind-v1.0.0.zip manifest.json dist/

# 4. Register & Submit
# https://chrome.google.com/webstore/devconsole
```

---

## ✅ Final Pre-Submission Checklist

Before clicking "Submit for Review":

- [ ] Privacy policy URL is live and accessible
- [ ] All screenshots uploaded (minimum 1, recommended 3-5)
- [ ] Store listing text is complete and accurate
- [ ] Support email is set and monitored
- [ ] Extension has been tested fresh install
- [ ] ZIP package contains only necessary files
- [ ] Manifest description is detailed (132 char max)
- [ ] Permissions are justified in listing
- [ ] No console errors in extension
- [ ] Version number is correct (1.0.0)

---

**Estimated Time to Store-Ready**: 2-4 hours
**Review Time**: 1-3 business days
**Total Time to Published**: ~1 week from now

Good luck! 🚀
