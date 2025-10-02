import {
  StorageData,
  ExtensionSettings,
  DailyUsage,
  UsageRecord,
} from '@/common/types';
import { DEFAULT_SETTINGS, STORAGE_KEYS } from '@/common/constants';
import { getTodayDate, calculateFootprint } from '@/common/util';

export class StorageManager {
  private static instance: StorageManager;

  static getInstance(): StorageManager {
    if (!this.instance) {
      this.instance = new StorageManager();
    }
    return this.instance;
  }

  async getSettings(): Promise<ExtensionSettings> {
    const result = await chrome.storage.local.get(STORAGE_KEYS.SETTINGS);
    const saved = result[STORAGE_KEYS.SETTINGS] || {};
    
    // Deep merge to prevent undefined nested properties
    return {
      ...DEFAULT_SETTINGS,
      ...saved,
      estimationParams: {
        ...DEFAULT_SETTINGS.estimationParams,
        ...(saved.estimationParams || {}),
      },
    };
  }

  async saveSettings(settings: ExtensionSettings): Promise<void> {
    await chrome.storage.local.set({
      [STORAGE_KEYS.SETTINGS]: settings,
    });
  }

  async getTodayCount(): Promise<number> {
    const result = await chrome.storage.local.get(STORAGE_KEYS.TODAY_COUNT);
    return result[STORAGE_KEYS.TODAY_COUNT] || 0;
  }

  async incrementTodayCount(): Promise<number> {
    const current = await this.getTodayCount();
    const newCount = current + 1;
    await chrome.storage.local.set({
      [STORAGE_KEYS.TODAY_COUNT]: newCount,
    });
    
    // Update badge
    await chrome.action.setBadgeText({ text: newCount.toString() });
    await chrome.action.setBadgeBackgroundColor({ color: '#4CAF50' });
    
    return newCount;
  }

  async getDailyUsage(): Promise<Record<string, DailyUsage>> {
    const result = await chrome.storage.local.get(STORAGE_KEYS.DAILY_USAGE);
    return result[STORAGE_KEYS.DAILY_USAGE] || {};
  }

  async saveDailyUsage(
    dailyUsage: Record<string, DailyUsage>
  ): Promise<void> {
    await chrome.storage.local.set({
      [STORAGE_KEYS.DAILY_USAGE]: dailyUsage,
    });
  }

  async getLastResetDate(): Promise<string> {
    const result = await chrome.storage.local.get(STORAGE_KEYS.LAST_RESET_DATE);
    return result[STORAGE_KEYS.LAST_RESET_DATE] || getTodayDate();
  }

  async setLastResetDate(date: string): Promise<void> {
    await chrome.storage.local.set({
      [STORAGE_KEYS.LAST_RESET_DATE]: date,
    });
  }

  async addUsageRecord(record: UsageRecord): Promise<void> {
    const dailyUsage = await this.getDailyUsage();
    const settings = await this.getSettings();
    
    if (!dailyUsage[record.date]) {
      dailyUsage[record.date] = {
        date: record.date,
        callCount: 0,
        totalTokensIn: 0,
        totalTokensOut: 0,
        providers: {},
        models: {},
        kwh: 0,
        waterLiters: 0,
        co2Kg: 0,
      };
    }

    const dayData = dailyUsage[record.date];
    dayData.callCount++;
    dayData.totalTokensIn += record.tokensIn;
    dayData.totalTokensOut += record.tokensOut;
    dayData.providers[record.provider] =
      (dayData.providers[record.provider] || 0) + 1;
    dayData.models[record.model] = (dayData.models[record.model] || 0) + 1;

    // Recalculate footprint
    const footprint = calculateFootprint(
      dayData.callCount,
      settings.estimationParams.kwhPerCall,
      settings.estimationParams.pue,
      settings.estimationParams.waterLPerKwh,
      settings.estimationParams.co2KgPerKwh
    );
    
    dayData.kwh = footprint.kwh;
    dayData.waterLiters = footprint.waterLiters;
    dayData.co2Kg = footprint.co2Kg;

    await this.saveDailyUsage(dailyUsage);
  }

  async getTodayUsage(): Promise<DailyUsage | null> {
    const today = getTodayDate();
    const dailyUsage = await this.getDailyUsage();
    return dailyUsage[today] || null;
  }

  async resetTodayCount(): Promise<void> {
    await chrome.storage.local.set({
      [STORAGE_KEYS.TODAY_COUNT]: 0,
    });
    await chrome.action.setBadgeText({ text: '' });
  }

  async clearTodayData(): Promise<void> {
    const today = getTodayDate();
    const dailyUsage = await this.getDailyUsage();
    
    if (dailyUsage[today]) {
      delete dailyUsage[today];
      await this.saveDailyUsage(dailyUsage);
    }
    
    await this.resetTodayCount();
  }

  async archiveAndReset(): Promise<void> {
    const today = getTodayDate();
    const lastResetDate = await this.getLastResetDate();
    
    if (today !== lastResetDate) {
      await this.resetTodayCount();
      await this.setLastResetDate(today);
    }
  }
}