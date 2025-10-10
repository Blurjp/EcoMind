# GitHub Pages Setup for Privacy Policy

**Goal**: Host `PRIVACY_POLICY.md` at a public URL for Chrome Web Store submission

**Your Repository**: https://github.com/Blurjp/EcoMind

---

## Option 1: GitHub Pages (Recommended - Free & Easy)

### Method A: Use Docs Folder (Simplest)

**Step 1: Create docs folder and copy privacy policy**

```bash
cd /Users/jianphua/projects/EcoMind

# Create docs folder in repo root
mkdir -p docs

# Copy privacy policy
cp ext-chrome/PRIVACY_POLICY.md docs/privacy-policy.md

# Create a simple index page (optional)
cat > docs/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ecomind - Privacy Policy</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .highlight { background: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Ecomind - Privacy Policy</h1>
    <div class="highlight">
        <p><strong>View our Privacy Policy:</strong> <a href="privacy-policy.html">Privacy Policy</a></p>
    </div>
    <p>Ecomind is a privacy-first Chrome extension for tracking AI API environmental impact.</p>
    <ul>
        <li><a href="https://github.com/Blurjp/EcoMind">GitHub Repository</a></li>
        <li><a href="privacy-policy.html">Privacy Policy</a></li>
        <li><a href="mailto:support@ecomind.biz">Support</a></li>
    </ul>
</body>
</html>
EOF

# Convert markdown to HTML (we'll use a simple converter)
cat > docs/privacy-policy.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - Ecomind</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; border-bottom: 1px solid #ecf0f1; padding-bottom: 5px; }
        h3 { color: #7f8c8d; margin-top: 20px; }
        ul { padding-left: 20px; }
        .highlight { background: #e8f4f8; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }
        .negative { color: #e74c3c; font-weight: 600; }
        hr { border: none; border-top: 1px solid #ecf0f1; margin: 40px 0; }
        a { color: #3498db; }
    </style>
</head>
<body>
    <!-- Content will be added below -->
</body>
</html>
EOF
```

**Step 2: Commit and push to GitHub**

```bash
cd /Users/jianphua/projects/EcoMind

git add docs/
git commit -m "Add GitHub Pages with privacy policy for Chrome Web Store"
git push origin main
```

**Step 3: Enable GitHub Pages**

1. Go to https://github.com/Blurjp/EcoMind/settings/pages
2. Under "Build and deployment":
   - **Source**: Select "Deploy from a branch"
   - **Branch**: Select `main`
   - **Folder**: Select `/docs`
3. Click "Save"
4. Wait 2-3 minutes for deployment
5. GitHub will show your site URL: `https://blurjp.github.io/EcoMind/`

**Your Privacy Policy URL will be**:
```
https://blurjp.github.io/EcoMind/privacy-policy.html
```

---

### Method B: Use gh-pages Branch (Alternative)

**Step 1: Create gh-pages branch**

```bash
cd /Users/jianphua/projects/EcoMind

# Create orphan branch for GitHub Pages
git checkout --orphan gh-pages

# Remove all files
git rm -rf .

# Copy privacy policy
cp ext-chrome/PRIVACY_POLICY.md privacy-policy.md

# Create index
echo "# Ecomind Privacy Policy" > index.md
echo "" >> index.md
echo "[View Privacy Policy](privacy-policy.md)" >> index.md

# Commit
git add .
git commit -m "Initial GitHub Pages setup"
git push origin gh-pages

# Switch back to main
git checkout main
```

**Step 2: Enable GitHub Pages**
1. Go to https://github.com/Blurjp/EcoMind/settings/pages
2. Select branch: `gh-pages`, folder: `/ (root)`
3. Save

**Privacy Policy URL**:
```
https://blurjp.github.io/EcoMind/privacy-policy
```

---

## Option 2: Use GitHub Gist (Quick Alternative)

**Step 1: Create a Gist**

1. Go to https://gist.github.com/
2. Click "+" (New gist)
3. **Filename**: `ecomind-privacy-policy.md`
4. **Content**: Paste contents of `ext-chrome/PRIVACY_POLICY.md`
5. Select "Create public gist"

**Step 2: Get public URL**

Your Gist URL will be something like:
```
https://gist.github.com/Blurjp/[gist-id]
```

**Drawback**: Gist URLs look less professional. GitHub Pages is preferred.

---

## Option 3: Use a Free Hosting Service

### Netlify Drop

1. Go to https://app.netlify.com/drop
2. Create a simple HTML file locally:
   ```bash
   cd /tmp
   mkdir ecomind-privacy
   cd ecomind-privacy

   # Copy and convert privacy policy to HTML
   cp /Users/jianphua/projects/EcoMind/ext-chrome/PRIVACY_POLICY.md .

   # Create index.html (manual conversion or use online tool)
   # Upload to Netlify
   ```
3. Drag folder to Netlify Drop
4. Get URL: `https://[random-name].netlify.app/privacy-policy.html`

---

## Recommended: Automated GitHub Pages Setup

I'll create a script to set this up automatically:

**Run this command**:

```bash
cd /Users/jianphua/projects/EcoMind

# Create docs folder
mkdir -p docs

# Copy privacy policy as markdown
cp ext-chrome/PRIVACY_POLICY.md docs/privacy-policy.md

# Create HTML version with embedded markdown rendering
cat > docs/privacy-policy.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - Ecomind Extension</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        h2 {
            color: #34495e;
            margin-top: 35px;
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 8px;
        }
        h3 { color: #7f8c8d; margin-top: 25px; }
        ul { padding-left: 25px; }
        li { margin: 8px 0; }
        .highlight {
            background: #e8f4f8;
            padding: 20px;
            border-left: 4px solid #3498db;
            margin: 25px 0;
            border-radius: 4px;
        }
        .no-collect {
            color: #e74c3c;
            font-weight: 600;
        }
        hr {
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 40px 0;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover { text-decoration: underline; }
        .meta {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 30px;
        }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <h1>Privacy Policy – Ecomind Extension</h1>

    <p class="meta">
        <strong>Effective Date:</strong> January 1, 2025<br>
        <strong>Last Updated:</strong> January 1, 2025
    </p>

    <hr>

    <h2>Introduction</h2>
    <p>Ecomind ("we", "our", or "the extension") is a Chrome browser extension that helps you track the environmental impact of AI API usage. This Privacy Policy explains what data we collect, how we use it, and your rights regarding your information.</p>

    <hr>

    <h2>Data Collection</h2>

    <h3>What We Collect</h3>
    <p>Ecomind collects <strong>only metadata</strong> about your AI API usage. We <strong>never</strong> collect the actual content of your prompts or AI responses.</p>

    <p><strong>Metadata collected includes:</strong></p>
    <ul>
        <li>Timestamp of API requests</li>
        <li>Provider name (e.g., "OpenAI", "Anthropic", "Google AI")</li>
        <li>Model identifier (e.g., "gpt-4o", "claude-3-opus")</li>
        <li>Token counts (when available from API response headers)</li>
        <li>Request domain (for custom provider tracking)</li>
    </ul>

    <p><strong>Local storage only:</strong></p>
    <ul>
        <li>Your settings and preferences</li>
        <li>Daily usage counters</li>
        <li>Custom provider domains you configure</li>
        <li>Estimation parameters (kWh, water, CO₂ factors)</li>
    </ul>

    <h3>What We DO NOT Collect</h3>
    <div class="highlight">
        <ul>
            <li class="no-collect">❌ Prompts or input text you send to AI services</li>
            <li class="no-collect">❌ Completions or responses from AI models</li>
            <li class="no-collect">❌ Conversation history or chat logs</li>
            <li class="no-collect">❌ Personal information (name, email, address, etc.)</li>
            <li class="no-collect">❌ Browsing history outside of AI API requests</li>
            <li class="no-collect">❌ Cookies or tracking identifiers</li>
            <li class="no-collect">❌ IP addresses</li>
            <li class="no-collect">❌ Authentication tokens or API keys</li>
        </ul>
    </div>

    <hr>

    <h2>How We Use Your Data</h2>

    <h3>Local-Only Mode (Default)</h3>
    <p>By default, all tracking is <strong>local-only</strong>:</p>
    <ul>
        <li>Data is stored in Chrome's local storage on your device</li>
        <li>Nothing is transmitted to external servers</li>
        <li>You have complete control over your data</li>
    </ul>

    <h3>Optional Telemetry Mode</h3>
    <p>If you enable telemetry and configure a backend URL:</p>
    <ul>
        <li>Metadata is sent to your specified backend server</li>
        <li>You control the backend (self-hosted or provided by your organization)</li>
        <li>We do not operate a centralized telemetry service</li>
    </ul>

    <p><strong>Purpose of telemetry:</strong></p>
    <ul>
        <li>Aggregate usage statistics across teams/organizations</li>
        <li>Generate environmental impact reports</li>
        <li>Track sustainability metrics over time</li>
    </ul>

    <hr>

    <h2>Data Storage</h2>

    <h3>Local Storage</h3>
    <ul>
        <li>Settings: Stored in <code>chrome.storage.local</code></li>
        <li>Daily metrics: Cleared automatically at midnight (configurable)</li>
        <li>No data leaves your device in local-only mode</li>
    </ul>

    <h3>External Storage (Optional)</h3>
    <ul>
        <li>If you configure a backend URL, data is sent via HTTPS</li>
        <li>Storage location depends on your backend configuration</li>
        <li>Retention policy set by your backend administrator</li>
    </ul>

    <hr>

    <h2>Data Sharing</h2>
    <p>We <strong>do not sell, rent, or share</strong> your data with third parties.</p>
    <p><strong>Exception:</strong> If you enable telemetry and configure a backend URL, data is sent to that server. You are responsible for the privacy practices of your chosen backend.</p>

    <hr>

    <h2>Your Rights</h2>

    <h3>Access</h3>
    <ul>
        <li>View all stored data in the extension's options page</li>
        <li>Export data from local storage using browser developer tools</li>
    </ul>

    <h3>Deletion</h3>
    <ul>
        <li>Clear all data using the "Clear Today's Data" button in the popup</li>
        <li>Uninstall the extension to remove all local data</li>
        <li>Contact your backend administrator to delete server-side data (if applicable)</li>
    </ul>

    <h3>Control</h3>
    <ul>
        <li>Toggle telemetry on/off at any time</li>
        <li>Switch between local-only and telemetry modes</li>
        <li>Configure which providers to track</li>
        <li>Adjust environmental estimation parameters</li>
    </ul>

    <hr>

    <h2>Security</h2>

    <h3>Data Protection</h3>
    <ul>
        <li>All settings stored securely in Chrome's storage API</li>
        <li>No plaintext API keys or credentials stored</li>
        <li>XSS protection implemented in all UI components</li>
    </ul>

    <h3>Network Security</h3>
    <ul>
        <li>All external communications use HTTPS</li>
        <li>Content Security Policy enforced</li>
        <li>No third-party scripts or trackers</li>
    </ul>

    <h3>Permissions Explained</h3>
    <p><strong>Storage:</strong> Required to save your settings and daily metrics locally on your device.</p>
    <p><strong>Web Request:</strong> Required to detect API calls to AI providers for tracking purposes. We only monitor network requests to calculate usage statistics – we never access request/response content.</p>
    <p><strong>Alarms:</strong> Required to reset daily counters at midnight automatically.</p>
    <p><strong>Host Permissions (<code>&lt;all_urls&gt;</code>):</strong> Required to monitor requests to custom AI provider domains you configure. You can restrict this by only adding specific provider domains in settings.</p>

    <hr>

    <h2>Compliance</h2>

    <h3>GDPR (European Users)</h3>
    <ul>
        <li><strong>Right to Access:</strong> View your data in the extension</li>
        <li><strong>Right to Deletion:</strong> Clear data or uninstall</li>
        <li><strong>Right to Portability:</strong> Export via browser tools</li>
        <li><strong>Data Minimization:</strong> We collect only essential metadata</li>
        <li><strong>Purpose Limitation:</strong> Data used only for usage tracking</li>
    </ul>

    <h3>CCPA (California Users)</h3>
    <ul>
        <li>We do not sell personal information</li>
        <li>You can delete all data at any time</li>
        <li>We collect only non-personal metadata</li>
    </ul>

    <hr>

    <h2>Children's Privacy</h2>
    <p>Ecomind is not intended for users under 13 years of age. We do not knowingly collect data from children.</p>

    <hr>

    <h2>Changes to This Policy</h2>
    <p>We may update this Privacy Policy from time to time. Changes will be reflected in the "Last Updated" date. Material changes will be communicated via:</p>
    <ul>
        <li>Extension update notes</li>
        <li>In-app notification</li>
        <li>GitHub repository announcements</li>
    </ul>

    <hr>

    <h2>Third-Party Services</h2>

    <h3>AI Providers</h3>
    <p>Ecomind monitors requests to third-party AI services (OpenAI, Anthropic, Google, etc.). Your use of those services is governed by their respective privacy policies:</p>
    <ul>
        <li>OpenAI: <a href="https://openai.com/privacy" target="_blank">https://openai.com/privacy</a></li>
        <li>Anthropic: <a href="https://www.anthropic.com/privacy" target="_blank">https://www.anthropic.com/privacy</a></li>
        <li>Google AI: <a href="https://policies.google.com/privacy" target="_blank">https://policies.google.com/privacy</a></li>
    </ul>
    <p>We only observe metadata about requests; we do not interact with these services on your behalf.</p>

    <hr>

    <h2>Open Source</h2>
    <p>Ecomind is open source software. You can review our code at:</p>
    <ul>
        <li><strong>GitHub:</strong> <a href="https://github.com/Blurjp/EcoMind" target="_blank">https://github.com/Blurjp/EcoMind</a></li>
        <li><strong>License:</strong> MIT</li>
    </ul>

    <hr>

    <h2>Contact Us</h2>
    <p>If you have questions about this Privacy Policy or your data:</p>
    <ul>
        <li><strong>Email:</strong> <a href="mailto:support@ecomind.biz">support@ecomind.biz</a></li>
        <li><strong>GitHub Issues:</strong> <a href="https://github.com/Blurjp/EcoMind/issues" target="_blank">https://github.com/Blurjp/EcoMind/issues</a></li>
        <li><strong>Support:</strong> <a href="mailto:support@ecomind.biz">support@ecomind.biz</a></li>
    </ul>

    <hr>

    <h2>Consent</h2>
    <p>By installing and using Ecomind, you consent to this Privacy Policy. If you do not agree, please do not install or use the extension.</p>

    <hr>

    <div class="highlight">
        <p><strong>Summary:</strong> Ecomind is privacy-first. We collect only metadata (no prompts/responses), store everything locally by default, and give you full control over your data.</p>
    </div>

    <hr>

    <p style="text-align: center; color: #7f8c8d; margin-top: 50px;">
        <a href="https://github.com/Blurjp/EcoMind">Back to Ecomind Repository</a>
    </p>
</body>
</html>
HTMLEOF

# Create simple index page
cat > docs/index.html << 'INDEXEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ecomind - AI Sustainability Tracker</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .tagline {
            color: #7f8c8d;
            font-size: 1.2em;
            margin-bottom: 30px;
        }
        .card {
            background: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        .card h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .links {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin: 30px 0;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 600;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #2980b9;
        }
        .btn-secondary {
            background: #95a5a6;
        }
        .btn-secondary:hover {
            background: #7f8c8d;
        }
        ul {
            padding-left: 20px;
        }
        li {
            margin: 10px 0;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 Ecomind</h1>
        <p class="tagline">Track the environmental impact of your AI API usage</p>

        <div class="card">
            <h3>Privacy-First AI Sustainability Tracker</h3>
            <p>Monitor energy consumption, carbon emissions, and water usage across OpenAI, Anthropic, Google AI, and custom providers.</p>
        </div>

        <div class="links">
            <a href="privacy-policy.html" class="btn">📄 Privacy Policy</a>
            <a href="https://github.com/Blurjp/EcoMind" class="btn btn-secondary">💻 GitHub Repository</a>
        </div>

        <h2>Features</h2>
        <ul>
            <li>🔒 <strong>Privacy-First:</strong> Local-only mode, no data collection</li>
            <li>📊 <strong>Real-Time Tracking:</strong> Monitor API calls and environmental impact</li>
            <li>⚡ <strong>Energy Metrics:</strong> Calculate kWh with data center efficiency (PUE)</li>
            <li>💧 <strong>Water Usage:</strong> Track cooling and operational water consumption</li>
            <li>🌱 <strong>Carbon Footprint:</strong> Estimate CO₂ emissions with regional grid data</li>
            <li>🔧 <strong>Customizable:</strong> Add custom providers and adjust parameters</li>
        </ul>

        <h2>Installation</h2>
        <p>Available on <strong>Chrome Web Store</strong> (coming soon)</p>
        <p>Or install from source: <a href="https://github.com/Blurjp/EcoMind#installation">GitHub Installation Guide</a></p>

        <h2>Documentation</h2>
        <ul>
            <li><a href="privacy-policy.html">Privacy Policy</a></li>
            <li><a href="https://github.com/Blurjp/EcoMind#usage">Usage Guide</a></li>
            <li><a href="https://github.com/Blurjp/EcoMind/issues">Report Issues</a></li>
        </ul>

        <h2>Support</h2>
        <p>Need help? Contact us:</p>
        <ul>
            <li>📧 Email: <a href="mailto:support@ecomind.biz">support@ecomind.biz</a></li>
            <li>🐛 GitHub Issues: <a href="https://github.com/Blurjp/EcoMind/issues">Report a Bug</a></li>
        </ul>

        <hr style="margin: 40px 0; border: none; border-top: 1px solid #ecf0f1;">

        <p style="text-align: center; color: #7f8c8d;">
            Made with 💚 for a sustainable AI future
        </p>
    </div>
</body>
</html>
INDEXEOF

echo "✅ GitHub Pages files created in docs/ folder"
echo ""
echo "Next steps:"
echo "1. git add docs/"
echo "2. git commit -m 'Add GitHub Pages with privacy policy'"
echo "3. git push origin main"
echo "4. Enable GitHub Pages at: https://github.com/Blurjp/EcoMind/settings/pages"
echo "5. Select: Source = 'Deploy from a branch', Branch = 'main', Folder = '/docs'"
echo "6. Your privacy policy will be at: https://blurjp.github.io/EcoMind/privacy-policy.html"
```

---

## Quick Start (Copy-Paste Commands)

```bash
# Navigate to repo
cd /Users/jianphua/projects/EcoMind

# Run the automated script above (create docs folder and files)
# Then:

# Commit and push
git add docs/
git commit -m "Add GitHub Pages with privacy policy for Chrome Web Store submission"
git push origin main

# Then enable GitHub Pages in browser:
# 1. Go to https://github.com/Blurjp/EcoMind/settings/pages
# 2. Source: Deploy from a branch
# 3. Branch: main
# 4. Folder: /docs
# 5. Click Save
```

**Wait 2-3 minutes**, then visit:
```
https://blurjp.github.io/EcoMind/privacy-policy.html
```

This is your **public privacy policy URL** for Chrome Web Store!

---

## Update Extension Manifest

After GitHub Pages is live, update your manifest:

```bash
cd /Users/jianphua/projects/EcoMind/ext-chrome

# Update manifest.json with real URLs
# Replace homepage_url with your actual repo
# Then rebuild
npm run build

# Recreate distribution ZIP
zip -r ecomind-v1.0.0.zip manifest.json dist/ -x "*.DS_Store"
```

---

## Summary

**Easiest Method**:
1. Run script above to create `docs/` folder
2. Commit and push to GitHub
3. Enable GitHub Pages at repo settings
4. Privacy policy URL: `https://blurjp.github.io/EcoMind/privacy-policy.html`

**Time**: 5-10 minutes (including GitHub Pages deployment)
