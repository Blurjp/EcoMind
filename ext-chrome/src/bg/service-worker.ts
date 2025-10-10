import { UsageRecord } from '@/common/types';
import { ALARM_NAMES } from '@/common/constants';
import { getTodayDate, generateId } from '@/common/util';
import { StorageManager } from './storage';
import { ProviderManager } from './providers';
import { TelemetryManager } from './telemetry';
import { TimeManager } from './time';

class ServiceWorker {
  private storageManager: StorageManager;
  private providerManager: ProviderManager;
  private telemetryManager: TelemetryManager;
  private timeManager: TimeManager;
  private initialized = false;
  private readonly boundHandleWebRequest = this.handleWebRequest.bind(this);
  private readonly boundHandleAlarm = this.handleAlarm.bind(this);

  constructor() {
    this.storageManager = StorageManager.getInstance();
    this.providerManager = new ProviderManager();
    this.telemetryManager = TelemetryManager.getInstance();
    this.timeManager = TimeManager.getInstance();
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;
    this.initialized = true;
    
    this.setupWebRequestListener();
    this.setupAlarmListener();
    await this.timeManager.setupMidnightReset();
    await this.timeManager.checkAndResetIfNeeded();

    // Load custom providers from settings
    const settings = await this.storageManager.getSettings();
    this.providerManager.updateCustomProviders(settings.customProviders);
  }

  private setupWebRequestListener(): void {
    if (chrome.webRequest && chrome.webRequest.onBeforeRequest) {
      chrome.webRequest.onBeforeRequest.removeListener(this.boundHandleWebRequest);
      chrome.webRequest.onBeforeRequest.addListener(
        this.boundHandleWebRequest,
        {
          urls: ['<all_urls>'],
          types: ['xmlhttprequest'],
        },
        ['requestBody']
      );
    }
  }

  private setupAlarmListener(): void {
    chrome.alarms.onAlarm.removeListener(this.boundHandleAlarm);
    chrome.alarms.onAlarm.addListener(this.boundHandleAlarm);
  }

  private async handleWebRequest(
    details: chrome.webRequest.WebRequestBodyDetails
  ): Promise<void> {
    try {
      if (!this.providerManager.shouldTrackRequest(details.url)) {
        return;
      }

      // In MV3 without webRequestBlocking, request body is often empty
      // We'll extract what we can from the URL and fall back to "unknown" for model
      let requestBody: string | undefined;
      if (details.requestBody?.raw?.[0]?.bytes) {
        try {
          const decoder = new TextDecoder();
          requestBody = decoder.decode(details.requestBody.raw[0].bytes);
        } catch {
          // Ignore decoding errors - common in MV3
        }
      }

      // Extract provider and model (model will often be "unknown" in MV3)
      const { provider, model } = this.providerManager.extractModel(
        details.url,
        requestBody
      );

      // Create usage record
      const record: UsageRecord = {
        id: generateId(),
        provider,
        model,
        tokensIn: 0, // We don't extract token counts from request
        tokensOut: 0,
        timestamp: new Date().toISOString(),
        date: getTodayDate(),
      };

      // Store locally
      await this.storageManager.addUsageRecord(record);
      await this.storageManager.incrementTodayCount();

      // Send telemetry if enabled
      const settings = await this.storageManager.getSettings();
      if (
        settings.telemetryEnabled &&
        !settings.privacyLocalOnly &&
        settings.baseUrl &&
        settings.userId
      ) {
        await this.telemetryManager.sendTelemetry(settings.baseUrl, {
          user_id: settings.userId,
          provider: record.provider,
          model: record.model,
          tokens_in: record.tokensIn,
          tokens_out: record.tokensOut,
          ts: record.timestamp,
        });
      }
    } catch (error) {
      console.warn('Error handling web request:', error);
    }
  }

  private async handleAlarm(alarm: chrome.alarms.Alarm): Promise<void> {
    if (alarm.name === ALARM_NAMES.MIDNIGHT_RESET) {
      await this.timeManager.handleMidnightReset();
    }
  }

  async updateProviders(): Promise<void> {
    const settings = await this.storageManager.getSettings();
    this.providerManager.updateCustomProviders(settings.customProviders);
  }
}

// Initialize service worker
const serviceWorker = new ServiceWorker();

// Handle extension startup
chrome.runtime.onStartup.addListener(() => {
  serviceWorker.initialize();
});

chrome.runtime.onInstalled.addListener(() => {
  serviceWorker.initialize();
});

// Handle messages from popup/options
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      switch (message.type) {
        case 'GET_TODAY_COUNT':
          const count = await serviceWorker.storageManager.getTodayCount();
          sendResponse({ success: true, data: count });
          break;

        case 'GET_TODAY_USAGE':
          const usage = await serviceWorker.storageManager.getTodayUsage();
          sendResponse({ success: true, data: usage });
          break;

        case 'CLEAR_TODAY':
          await serviceWorker.storageManager.clearTodayData();
          sendResponse({ success: true });
          break;

        case 'UPDATE_PROVIDERS':
          await serviceWorker.updateProviders();
          sendResponse({ success: true });
          break;

        case 'TEST_CONNECTION':
          const { baseUrl } = message;
          const isConnected = await serviceWorker.telemetryManager.testConnection(
            baseUrl
          );
          sendResponse({ success: true, data: isConnected });
          break;

        case 'FETCH_TODAY_DATA':
          const { baseUrl: fetchBaseUrl, userId } = message;
          try {
            const data = await serviceWorker.telemetryManager.fetchTodayData(
              fetchBaseUrl,
              userId
            );
            sendResponse({ success: true, data });
          } catch (error) {
            sendResponse({ success: false, error: (error as Error).message });
          }
          break;

        case 'GET_SETTINGS':
          const settings = await serviceWorker.storageManager.getSettings();
          sendResponse({ success: true, data: settings });
          break;

        case 'SAVE_SETTINGS':
          const { settings: newSettings } = message;
          await serviceWorker.storageManager.saveSettings(newSettings);
          sendResponse({ success: true });
          break;

        default:
          sendResponse({ success: false, error: 'Unknown message type' });
      }
    } catch (error) {
      sendResponse({ success: false, error: (error as Error).message });
    }
  })();

  return true; // Keep message channel open for async response
});

// Initialize immediately
serviceWorker.initialize();