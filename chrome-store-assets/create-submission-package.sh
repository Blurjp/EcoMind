#!/bin/bash

# Chrome Web Store Submission Package Creator
# Creates a ZIP file ready for Chrome Web Store upload

set -e

echo "🎯 Creating Chrome Web Store submission package..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Check required files exist
if [ ! -f "manifest.json" ]; then
  echo "❌ Error: manifest.json not found"
  exit 1
fi

if [ ! -d "dist" ]; then
  echo "❌ Error: dist/ directory not found. Run 'npm run build' first."
  exit 1
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
PACKAGE_NAME="ecomind-submission"

echo "📦 Copying extension files..."

# Copy required files
cp -r dist "$TEMP_DIR/"
cp manifest.json "$TEMP_DIR/"

# Copy README if exists
if [ -f "README.md" ]; then
  cp README.md "$TEMP_DIR/"
fi

# Create ZIP
echo "🗜️  Creating ZIP package..."
cd "$TEMP_DIR"
zip -r "$PACKAGE_NAME.zip" . -x "*.DS_Store" -x "__MACOSX/*"

# Move to project root
mv "$PACKAGE_NAME.zip" "$OLDPWD/"

# Cleanup
cd "$OLDPWD"
rm -rf "$TEMP_DIR"

# Show size
SIZE=$(du -h "$PACKAGE_NAME.zip" | cut -f1)

echo "✅ Package created: $PACKAGE_NAME.zip ($SIZE)"
echo ""
echo "Next steps:"
echo "1. Take screenshots of the extension in action"
echo "2. Create promotional images (440x280px minimum)"
echo "3. Host PRIVACY_POLICY.md on your website"
echo "4. Go to: https://chrome.google.com/webstore/devconsole"
echo "5. Upload $PACKAGE_NAME.zip"
echo "6. Use text from chrome-store-assets/STORE_LISTING.md"
echo "7. Set privacy policy URL (must be publicly accessible)"
echo ""
echo "📖 See chrome-store-assets/SUBMISSION_CHECKLIST.md for full instructions"
