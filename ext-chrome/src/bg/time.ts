import { ALARM_NAMES } from '@/common/constants';
import { StorageManager } from './storage';

export class TimeManager {
  private static instance: TimeManager;
  private storageManager: StorageManager;

  constructor() {
    this.storageManager = StorageManager.getInstance();
  }

  static getInstance(): TimeManager {
    if (!this.instance) {
      this.instance = new TimeManager();
    }
    return this.instance;
  }

  async setupMidnightReset(): Promise<void> {
    // Clear any existing alarm
    await chrome.alarms.clear(ALARM_NAMES.MIDNIGHT_RESET);

    // Calculate next midnight
    const now = new Date();
    const nextMidnight = new Date(now);
    nextMidnight.setHours(24, 0, 0, 0);

    // Set alarm for next midnight
    await chrome.alarms.create(ALARM_NAMES.MIDNIGHT_RESET, {
      when: nextMidnight.getTime(),
      periodInMinutes: 24 * 60, // Repeat every 24 hours
    });
  }

  async handleMidnightReset(): Promise<void> {
    await this.storageManager.archiveAndReset();
  }

  async checkAndResetIfNeeded(): Promise<void> {
    await this.storageManager.archiveAndReset();
  }
}