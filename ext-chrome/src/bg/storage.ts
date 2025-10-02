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
  private updateQueue: Promise<void> = Promise.resolve();
  private inMemoryCache: {
    dailyUsage: Record<string, DailyUsage> | null;
    lastFetch: number;
  } = {
    dailyUsage: null,
    lastFetch: 0,
  };
  private readonly CACHE_TTL = 1000; // 1 second cache to reduce storage reads

  static getInstance(): StorageManager {
    if (!this.instance) {
      this.instance = new StorageManager();
    }
    return this.instance;
  }

  /**
   * Serialize all storage update operations to prevent race conditions
   */
  private async queueOperation<T>(operation: () => Promise<T>): Promise<T> {
    const previousOperation = this.updateQueue;
    let resolver: (value: T) => void;
    let rejecter: (error: any) => void;

    const currentOperation = new Promise<T>((resolve, reject) => {
      resolver = resolve;
      rejecter = reject;
    });

    this.updateQueue = previousOperation
      .then(() => operation())
      .then(resolver!)
      .catch(rejecter!);

    return currentOperation;
  }

  async getSettings(): Promise<ExtensionSettings> {
    const result = await chrome.storage.local.get(STORAGE_KEYS.SETTINGS);
    const saved = result[STORAGE_KEYS.SETTINGS] || {};

    // Deep merge to prevent undefined nested properties
    // Create a fresh copy of DEFAULT_SETTINGS to avoid mutation
    return {
      baseUrl: saved.baseUrl ?? DEFAULT_SETTINGS.baseUrl,
      userId: saved.userId ?? DEFAULT_SETTINGS.userId,
      telemetryEnabled: saved.telemetryEnabled ?? DEFAULT_SETTINGS.telemetryEnabled,
      privacyLocalOnly: saved.privacyLocalOnly ?? DEFAULT_SETTINGS.privacyLocalOnly,
      customProviders: Array.isArray(saved.customProviders)
        ? [...saved.customProviders]
        : [...DEFAULT_SETTINGS.customProviders],
      estimationParams: {
        kwhPerCall: saved.estimationParams?.kwhPerCall ?? DEFAULT_SETTINGS.estimationParams.kwhPerCall,
        pue: saved.estimationParams?.pue ?? DEFAULT_SETTINGS.estimationParams.pue,
        waterLPerKwh: saved.estimationParams?.waterLPerKwh ?? DEFAULT_SETTINGS.estimationParams.waterLPerKwh,
        co2KgPerKwh: saved.estimationParams?.co2KgPerKwh ?? DEFAULT_SETTINGS.estimationParams.co2KgPerKwh,
      },
    };
  }

  async saveSettings(settings: ExtensionSettings): Promise<void> {
    await chrome.storage.local.set({
      [STORAGE_KEYS.SETTINGS]: settings,
    });
  }

  async getTodayCount(): Promise<number> {
    // Use DailyUsage as single source of truth
    const today = getTodayDate();
    const dailyUsage = await this.getDailyUsage();
    return dailyUsage[today]?.callCount || 0;
  }

  /**
   * @deprecated Use addUsageRecord() instead - it handles count and badge updates
   */
  async incrementTodayCount(): Promise<number> {
    // This method is deprecated but kept for backward compatibility
    // The badge is now updated directly in addUsageRecord()
    return this.getTodayCount();
  }

  async getDailyUsage(): Promise<Record<string, DailyUsage>> {
    // Use in-memory cache to reduce storage reads during bursts
    const now = Date.now();
    if (this.inMemoryCache.dailyUsage && now - this.inMemoryCache.lastFetch < this.CACHE_TTL) {
      return { ...this.inMemoryCache.dailyUsage }; // Return copy to prevent mutations
    }

    const result = await chrome.storage.local.get(STORAGE_KEYS.DAILY_USAGE);
    const dailyUsage = result[STORAGE_KEYS.DAILY_USAGE] || {};

    // Update cache
    this.inMemoryCache.dailyUsage = dailyUsage;
    this.inMemoryCache.lastFetch = now;

    return { ...dailyUsage };
  }

  async saveDailyUsage(
    dailyUsage: Record<string, DailyUsage>
  ): Promise<void> {
    await chrome.storage.local.set({
      [STORAGE_KEYS.DAILY_USAGE]: dailyUsage,
    });

    // Update cache
    this.inMemoryCache.dailyUsage = dailyUsage;
    this.inMemoryCache.lastFetch = Date.now();
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
    // Queue this operation to prevent race conditions
    return this.queueOperation(async () => {
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

      // Update badge with the accurate count (single source of truth)
      if (record.date === getTodayDate()) {
        await chrome.action.setBadgeText({ text: dayData.callCount.toString() });
        await chrome.action.setBadgeBackgroundColor({ color: '#4CAF50' });
      }
    });
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