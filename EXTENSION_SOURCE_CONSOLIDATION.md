# Extension Source Consolidation

**Date**: 2025-10-10
**Status**: ✅ COMPLETED

## Problem

Two separate `src/` directories existed:
- `./src/` - Root source (newer code with recent fixes)
- `./ext-chrome/src/` - Extension source (outdated, missing providers)

This caused confusion about which source to use for Chrome extension builds.

## Solution: Single Source of Truth

**Decision**: Use `ext-chrome/` as the canonical extension source.

**Reasoning**:
1. Documentation explicitly points to `ext-chrome/` for Chrome extension
2. `ext-chrome/` has complete package structure (manifest.json, package.json, dist/)
3. Follows monorepo pattern (separate workspaces for different components)

## Actions Taken

1. ✅ **Synced all files** from `./src/` → `./ext-chrome/src/`
   - `common/constants.ts` - HuggingFace regex fix + all provider updates
   - `common/types.ts`, `common/util.ts`
   - `bg/*` - Background service worker files
   - `ui/*` - Popup and options UI files

2. ✅ **Synced test files** from `./tests/` → `./ext-chrome/tests/`
   - All HuggingFace test cases included
   - Tests passing: 68/68 ✅

3. ✅ **Built extension**
   - Production build successful
   - Output: `ext-chrome/dist/`

4. ✅ **Verified integrity**
   - All tests pass in `ext-chrome/`
   - Build produces valid extension bundle

## For Chrome Web Store

**Use this folder for all Chrome extension work:**

```bash
cd ext-chrome
npm install
npm run build
```

**Load in Chrome:**
1. Go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select: `ext-chrome/dist/`

**For Chrome Web Store submission:**
- Package: `ext-chrome/dist/` (zip the contents, not the folder itself)
- Manifest: `ext-chrome/manifest.json`
- Source: `ext-chrome/src/`

## Root `./src/` Status

The root `./src/` is now **redundant**. Recommendations:

**Option 1: Remove** (recommended)
```bash
rm -rf ./src/ ./tests/ ./dist/
```

**Option 2: Mark as deprecated**
```bash
mv src src.deprecated
echo "DEPRECATED: Use ext-chrome/src/ instead" > src.deprecated/README.md
```

**Option 3: Create symlinks** (for workspace compatibility)
```bash
rm -rf src
ln -s ext-chrome/src src
```

## Files Modified Today

**ext-chrome/src/common/constants.ts**:
- HuggingFace regex: `/\/models\/([^\/\?]+(?:\/[^\/\?]+)?)/`
- Supports both single-segment (`gpt2`) and owner/model (`mistralai/Mixtral-8x7B`)
- Fixed regression from previous 2-segment-only pattern

**ext-chrome/tests/providers.test.ts**:
- Updated test: "should extract single-segment model IDs"
- New test: "should stop at additional path segments"
- All 68 tests passing

## Verification Checklist

- ✅ All source files synced to `ext-chrome/src/`
- ✅ All tests synced to `ext-chrome/tests/`
- ✅ Tests pass: 68/68
- ✅ Build successful
- ✅ HuggingFace regex fix included
- ✅ All recent provider updates included (xAI, Mistral, HuggingFace, OpenRouter, Groq)
- ✅ Production-ready dist bundle generated

## Next Steps

1. **Remove or deprecate root `./src/`** to prevent future confusion
2. **Update CI/CD** if it references `./src/` instead of `ext-chrome/src/`
3. **Test extension** in Chrome with real HuggingFace API calls
4. **Submit to Chrome Web Store** using `ext-chrome/dist/`
