import { S as STORAGE_KEYS, D as DEFAULT_SETTINGS, a as DEFAULT_PROVIDERS, A as ALARM_NAMES } from "../constants.js";
function getTodayDate() {
  return (/* @__PURE__ */ new Date()).toISOString().split("T")[0];
}
function generateId() {
  return Math.random().toString(36).substr(2, 9);
}
function extractDomainFromUrl(url) {
  try {
    const { hostname, port } = new URL(url);
    return port ? `${hostname}:${port}` : hostname;
  } catch {
    return "";
  }
}
function calculateFootprint(callCount, kwhPerCall, pue, waterLPerKwh, co2KgPerKwh) {
  const kwh = callCount * kwhPerCall * pue;
  return {
    kwh,
    waterLiters: kwh * waterLPerKwh,
    co2Kg: kwh * co2KgPerKwh
  };
}
function domainMatchesPattern(domain, pattern) {
  const [domainHost, domainPort] = domain.split(":");
  const [patternHost, patternPort] = pattern.split(":");
  if (patternPort && patternPort !== domainPort) {
    return false;
  }
  const hostPattern = patternHost.startsWith("*.") ? patternHost.slice(2) : patternHost;
  if (patternHost.startsWith("*.")) {
    return domainHost === hostPattern || domainHost.endsWith(`.${hostPattern}`);
  }
  return domainHost === hostPattern;
}
function shouldTrackDomain(domain, providerDomains) {
  return providerDomains.some(
    (pattern) => domainMatchesPattern(domain, pattern)
  );
}
async function retry(fn, maxRetries = 3, baseDelay = 1e3) {
  let lastError;
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (attempt === maxRetries)
        break;
      const delay = baseDelay * Math.pow(2, attempt);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }
  throw lastError;
}
class StorageManager {
  static getInstance() {
    if (!this.instance) {
      this.instance = new StorageManager();
    }
    return this.instance;
  }
  async getSettings() {
    const result = await chrome.storage.local.get(STORAGE_KEYS.SETTINGS);
    return { ...DEFAULT_SETTINGS, ...result[STORAGE_KEYS.SETTINGS] };
  }
  async saveSettings(settings) {
    await chrome.storage.local.set({
      [STORAGE_KEYS.SETTINGS]: settings
    });
  }
  async getTodayCount() {
    const result = await chrome.storage.local.get(STORAGE_KEYS.TODAY_COUNT);
    return result[STORAGE_KEYS.TODAY_COUNT] || 0;
  }
  async incrementTodayCount() {
    const current = await this.getTodayCount();
    const newCount = current + 1;
    await chrome.storage.local.set({
      [STORAGE_KEYS.TODAY_COUNT]: newCount
    });
    await chrome.action.setBadgeText({ text: newCount.toString() });
    await chrome.action.setBadgeBackgroundColor({ color: "#4CAF50" });
    return newCount;
  }
  async getDailyUsage() {
    const result = await chrome.storage.local.get(STORAGE_KEYS.DAILY_USAGE);
    return result[STORAGE_KEYS.DAILY_USAGE] || {};
  }
  async saveDailyUsage(dailyUsage) {
    await chrome.storage.local.set({
      [STORAGE_KEYS.DAILY_USAGE]: dailyUsage
    });
  }
  async getLastResetDate() {
    const result = await chrome.storage.local.get(STORAGE_KEYS.LAST_RESET_DATE);
    return result[STORAGE_KEYS.LAST_RESET_DATE] || getTodayDate();
  }
  async setLastResetDate(date) {
    await chrome.storage.local.set({
      [STORAGE_KEYS.LAST_RESET_DATE]: date
    });
  }
  async addUsageRecord(record) {
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
        co2Kg: 0
      };
    }
    const dayData = dailyUsage[record.date];
    dayData.callCount++;
    dayData.totalTokensIn += record.tokensIn;
    dayData.totalTokensOut += record.tokensOut;
    dayData.providers[record.provider] = (dayData.providers[record.provider] || 0) + 1;
    dayData.models[record.model] = (dayData.models[record.model] || 0) + 1;
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
  async getTodayUsage() {
    const today = getTodayDate();
    const dailyUsage = await this.getDailyUsage();
    return dailyUsage[today] || null;
  }
  async resetTodayCount() {
    await chrome.storage.local.set({
      [STORAGE_KEYS.TODAY_COUNT]: 0
    });
    await chrome.action.setBadgeText({ text: "" });
  }
  async clearTodayData() {
    const today = getTodayDate();
    const dailyUsage = await this.getDailyUsage();
    if (dailyUsage[today]) {
      delete dailyUsage[today];
      await this.saveDailyUsage(dailyUsage);
    }
    await this.resetTodayCount();
  }
  async archiveAndReset() {
    const today = getTodayDate();
    const lastResetDate = await this.getLastResetDate();
    if (today !== lastResetDate) {
      await this.resetTodayCount();
      await this.setLastResetDate(today);
    }
  }
}
class ProviderManager {
  constructor() {
    this.providers = [];
    this.providers = [...DEFAULT_PROVIDERS];
  }
  addCustomProvider(name, domains) {
    const existing = this.providers.find((p) => p.name === name);
    if (existing) {
      existing.domains = [.../* @__PURE__ */ new Set([...existing.domains, ...domains])];
    } else {
      this.providers.push({
        name,
        domains,
        modelExtractor: () => "unknown"
      });
    }
  }
  removeCustomProvider(name) {
    this.providers = this.providers.filter(
      (p) => p.name !== name || DEFAULT_PROVIDERS.find((dp) => dp.name === name)
    );
  }
  getAllDomains() {
    return this.providers.flatMap((p) => p.domains);
  }
  findProviderForUrl(url) {
    const domain = extractDomainFromUrl(url);
    if (!domain)
      return null;
    return this.providers.find(
      (provider) => shouldTrackDomain(domain, provider.domains)
    ) || null;
  }
  extractModel(url, body) {
    const provider = this.findProviderForUrl(url);
    if (!provider) {
      return { provider: "unknown", model: "unknown" };
    }
    const model = provider.modelExtractor ? provider.modelExtractor(url, body) : "unknown";
    return { provider: provider.name, model };
  }
  shouldTrackRequest(url) {
    return this.findProviderForUrl(url) !== null;
  }
  updateCustomProviders(customProviders) {
    this.providers = this.providers.filter(
      (p) => DEFAULT_PROVIDERS.find((dp) => dp.name === p.name)
    );
    customProviders.forEach((domain) => {
      if (domain.trim()) {
        this.addCustomProvider("custom", [domain.trim()]);
      }
    });
  }
}
class TelemetryManager {
  static getInstance() {
    if (!this.instance) {
      this.instance = new TelemetryManager();
    }
    return this.instance;
  }
  async sendTelemetry(baseUrl, payload) {
    if (!baseUrl || !payload.user_id) {
      return false;
    }
    try {
      await retry(async () => {
        const response = await fetch(`${baseUrl}/ingest`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        });
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      });
      return true;
    } catch (error) {
      console.warn("Failed to send telemetry:", error);
      return false;
    }
  }
  async fetchTodayData(baseUrl, userId) {
    if (!baseUrl || !userId) {
      throw new Error("Missing baseUrl or userId");
    }
    try {
      const response = await fetch(
        `${baseUrl}/today?user_id=${encodeURIComponent(userId)}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json"
          }
        }
      );
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.warn("Failed to fetch today data:", error);
      throw error;
    }
  }
  async testConnection(baseUrl) {
    if (!baseUrl) {
      return false;
    }
    try {
      const response = await fetch(`${baseUrl}/health`, {
        method: "GET",
        signal: AbortSignal.timeout(5e3)
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}
class TimeManager {
  constructor() {
    this.storageManager = StorageManager.getInstance();
  }
  static getInstance() {
    if (!this.instance) {
      this.instance = new TimeManager();
    }
    return this.instance;
  }
  async setupMidnightReset() {
    await chrome.alarms.clear(ALARM_NAMES.MIDNIGHT_RESET);
    const now = /* @__PURE__ */ new Date();
    const nextMidnight = new Date(now);
    nextMidnight.setHours(24, 0, 0, 0);
    await chrome.alarms.create(ALARM_NAMES.MIDNIGHT_RESET, {
      when: nextMidnight.getTime(),
      periodInMinutes: 24 * 60
      // Repeat every 24 hours
    });
  }
  async handleMidnightReset() {
    await this.storageManager.archiveAndReset();
  }
  async checkAndResetIfNeeded() {
    await this.storageManager.archiveAndReset();
  }
}
class ServiceWorker {
  constructor() {
    this.initialized = false;
    this.boundHandleWebRequest = this.handleWebRequest.bind(this);
    this.boundHandleAlarm = this.handleAlarm.bind(this);
    this.storageManager = StorageManager.getInstance();
    this.providerManager = new ProviderManager();
    this.telemetryManager = TelemetryManager.getInstance();
    this.timeManager = TimeManager.getInstance();
  }
  async initialize() {
    if (this.initialized)
      return;
    this.initialized = true;
    this.setupWebRequestListener();
    this.setupAlarmListener();
    await this.timeManager.setupMidnightReset();
    await this.timeManager.checkAndResetIfNeeded();
    const settings = await this.storageManager.getSettings();
    this.providerManager.updateCustomProviders(settings.customProviders);
  }
  setupWebRequestListener() {
    if (chrome.webRequest && chrome.webRequest.onBeforeRequest) {
      chrome.webRequest.onBeforeRequest.removeListener(this.boundHandleWebRequest);
      chrome.webRequest.onBeforeRequest.addListener(
        this.boundHandleWebRequest,
        {
          urls: ["<all_urls>"],
          types: ["xmlhttprequest"]
        },
        ["requestBody"]
      );
    }
  }
  setupAlarmListener() {
    chrome.alarms.onAlarm.removeListener(this.boundHandleAlarm);
    chrome.alarms.onAlarm.addListener(this.boundHandleAlarm);
  }
  async handleWebRequest(details) {
    try {
      if (!this.providerManager.shouldTrackRequest(details.url)) {
        return;
      }
      let requestBody;
      if (details.requestBody?.raw?.[0]?.bytes) {
        try {
          const decoder = new TextDecoder();
          requestBody = decoder.decode(details.requestBody.raw[0].bytes);
        } catch {
        }
      }
      const { provider, model } = this.providerManager.extractModel(
        details.url,
        requestBody
      );
      const record = {
        id: generateId(),
        provider,
        model,
        tokensIn: 0,
        // We don't extract token counts from request
        tokensOut: 0,
        timestamp: (/* @__PURE__ */ new Date()).toISOString(),
        date: getTodayDate()
      };
      await this.storageManager.addUsageRecord(record);
      await this.storageManager.incrementTodayCount();
      const settings = await this.storageManager.getSettings();
      if (settings.telemetryEnabled && !settings.privacyLocalOnly && settings.baseUrl && settings.userId) {
        await this.telemetryManager.sendTelemetry(settings.baseUrl, {
          user_id: settings.userId,
          provider: record.provider,
          model: record.model,
          tokens_in: record.tokensIn,
          tokens_out: record.tokensOut,
          ts: record.timestamp
        });
      }
    } catch (error) {
      console.warn("Error handling web request:", error);
    }
  }
  async handleAlarm(alarm) {
    if (alarm.name === ALARM_NAMES.MIDNIGHT_RESET) {
      await this.timeManager.handleMidnightReset();
    }
  }
  async updateProviders() {
    const settings = await this.storageManager.getSettings();
    this.providerManager.updateCustomProviders(settings.customProviders);
  }
}
const serviceWorker = new ServiceWorker();
chrome.runtime.onStartup.addListener(() => {
  serviceWorker.initialize();
});
chrome.runtime.onInstalled.addListener(() => {
  serviceWorker.initialize();
});
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      switch (message.type) {
        case "GET_TODAY_COUNT":
          const count = await serviceWorker.storageManager.getTodayCount();
          sendResponse({ success: true, data: count });
          break;
        case "GET_TODAY_USAGE":
          const usage = await serviceWorker.storageManager.getTodayUsage();
          sendResponse({ success: true, data: usage });
          break;
        case "CLEAR_TODAY":
          await serviceWorker.storageManager.clearTodayData();
          sendResponse({ success: true });
          break;
        case "UPDATE_PROVIDERS":
          await serviceWorker.updateProviders();
          sendResponse({ success: true });
          break;
        case "TEST_CONNECTION":
          const { baseUrl } = message;
          const isConnected = await serviceWorker.telemetryManager.testConnection(
            baseUrl
          );
          sendResponse({ success: true, data: isConnected });
          break;
        case "FETCH_TODAY_DATA":
          const { baseUrl: fetchBaseUrl, userId } = message;
          try {
            const data = await serviceWorker.telemetryManager.fetchTodayData(
              fetchBaseUrl,
              userId
            );
            sendResponse({ success: true, data });
          } catch (error) {
            sendResponse({ success: false, error: error.message });
          }
          break;
        case "GET_SETTINGS":
          const settings = await serviceWorker.storageManager.getSettings();
          sendResponse({ success: true, data: settings });
          break;
        case "SAVE_SETTINGS":
          const { settings: newSettings } = message;
          await serviceWorker.storageManager.saveSettings(newSettings);
          sendResponse({ success: true });
          break;
        default:
          sendResponse({ success: false, error: "Unknown message type" });
      }
    } catch (error) {
      sendResponse({ success: false, error: error.message });
    }
  })();
  return true;
});
serviceWorker.initialize();
