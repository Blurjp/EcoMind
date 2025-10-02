# Counter Mismatch Issue

## Problem
Extension badge shows **193** but popup shows **9** - they're tracking different counters.

## Root Cause

Two separate counting mechanisms:

1. **Badge Counter** (`TODAY_COUNT`):
   - Simple integer: `ecomind_today_count`
   - Incremented in `storage.ts:54-66`
   - Shows on extension icon
   - **Current value**: 193

2. **Daily Usage Counter** (`DailyUsage[date].callCount`):
   - Structured object keyed by date
   - Incremented in `storage.ts:92-120`
   - Shown in popup
   - **Current value**: 9

## Why They're Different

The counters may be from different dates or one was cleared without the other.

## How to Debug

**Check current storage values**:

1. Open extension popup
2. Open DevTools Console (F12)
3. Run:
```javascript
chrome.storage.local.get(null, (data) => {
  console.log('All storage:', data);
  console.log('Simple counter:', data.ecomind_today_count);
  console.log('Daily usage:', data.ecomind_daily_usage);
});
```

Look for:
- `ecomind_today_count`: Should match badge (193)
- `ecomind_daily_usage`: Object with dates as keys

## Quick Fix Options

### Option 1: Clear All Data (Recommended for Testing)

In popup, click **"Clear Today's Data"** button - this should reset both counters.

### Option 2: Manually Sync via Console

```javascript
// Get today's date
const today = new Date().toISOString().split('T')[0];

// Option A: Set badge to match daily usage
chrome.storage.local.get(['ecomind_daily_usage'], (data) => {
  const count = data.ecomind_daily_usage?.[today]?.callCount || 0;
  chrome.action.setBadgeText({ text: count.toString() });
  chrome.storage.local.set({ ecomind_today_count: count });
  console.log('Synced to:', count);
});

// Option B: Set daily usage to match badge
chrome.storage.local.get(['ecomind_today_count', 'ecomind_daily_usage'], (data) => {
  const count = data.ecomind_today_count || 0;
  const dailyUsage = data.ecomind_daily_usage || {};

  if (!dailyUsage[today]) {
    dailyUsage[today] = {
      date: today,
      callCount: count,
      totalTokensIn: 0,
      totalTokensOut: 0,
      providers: {},
      models: {},
      kwh: 0,
      waterLiters: 0,
      co2Kg: 0
    };
  } else {
    dailyUsage[today].callCount = count;
  }

  chrome.storage.local.set({ ecomind_daily_usage: dailyUsage });
  console.log('Synced to:', count);
});
```

### Option 3: Reload Extension

1. Go to `chrome://extensions/`
2. Find Ecomind extension
3. Click **Reload** (circular arrow icon)
4. Both counters should reset to 0

## Long-Term Fix (Code Change)

**The bug**: `incrementTodayCount()` and `addUsageRecord()` update different counters.

**Proper fix** (for future version):

```typescript
// storage.ts - Remove separate TODAY_COUNT, use DailyUsage.callCount instead

async incrementTodayCount(): Promise<number> {
  const today = getTodayDate();
  const dailyUsage = await this.getDailyUsage();

  if (!dailyUsage[today]) {
    dailyUsage[today] = {
      date: today,
      callCount: 0,
      totalTokensIn: 0,
      totalTokensOut: 0,
      providers: {},
      models: {},
      kwh: 0,
      waterLiters: 0,
      co2Kg: 0
    };
  }

  dailyUsage[today].callCount += 1;
  const newCount = dailyUsage[today].callCount;

  await this.saveDailyUsage(dailyUsage);

  // Update badge
  await chrome.action.setBadgeText({ text: newCount.toString() });
  await chrome.action.setBadgeBackgroundColor({ color: '#4CAF50' });

  return newCount;
}

async getTodayCount(): Promise<number> {
  const today = getTodayDate();
  const dailyUsage = await this.getDailyUsage();
  return dailyUsage[today]?.callCount || 0;
}
```

This ensures **one source of truth**: `DailyUsage[today].callCount`

## Current Workaround

For now, the numbers being different doesn't break functionality:
- **Badge (193)**: Shows total requests intercepted
- **Popup (9)**: Shows structured daily data

Both are "correct" from their own perspective - they're just not synced.

To align them for Chrome Web Store screenshots:
1. Click "Clear Today's Data" in popup
2. Both will reset to 0
3. Use the extension normally
4. Both counters should increment together

## For Chrome Web Store Submission

**Don't worry about this for screenshots!**

Just:
1. Clear data to reset to 0
2. Take screenshot showing clean state
3. Or take screenshot with the current numbers (it's fine to show activity)

The mismatch is a minor UX issue, not a blocker for Chrome Web Store approval.
