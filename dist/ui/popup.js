import { f as formatDate, s as showLoading, a as sendMessage, b as showError, c as createElement, d as createSection, e as formatMetric, g as createDataRow, h as createList } from "../components.js";
class PopupManager {
  constructor() {
    this.contentEl = document.getElementById("content");
    this.refreshBtn = document.getElementById("refreshBtn");
    this.optionsBtn = document.getElementById("optionsBtn");
    this.clearBtn = document.getElementById("clearBtn");
    this.setupEventListeners();
    this.updateCurrentDate();
    this.loadData();
  }
  setupEventListeners() {
    this.refreshBtn.addEventListener("click", () => this.loadData());
    this.optionsBtn.addEventListener("click", () => this.openOptions());
    this.clearBtn.addEventListener("click", () => this.clearToday());
  }
  updateCurrentDate() {
    const dateEl = document.getElementById("currentDate");
    if (dateEl) {
      dateEl.textContent = formatDate((/* @__PURE__ */ new Date()).toISOString());
    }
  }
  async loadData() {
    showLoading(this.contentEl);
    try {
      const settingsResult = await sendMessage("GET_SETTINGS");
      if (!settingsResult.success) {
        throw new Error("Failed to get settings");
      }
      const settings = settingsResult.data;
      const hasBackend = settings.telemetryEnabled && !settings.privacyLocalOnly && settings.baseUrl && settings.userId;
      let data = null;
      let isBackendData = false;
      if (hasBackend) {
        try {
          const backendResult = await sendMessage("FETCH_TODAY_DATA", {
            baseUrl: settings.baseUrl,
            userId: settings.userId
          });
          if (backendResult.success) {
            data = this.convertBackendResponse(backendResult.data);
            isBackendData = true;
          }
        } catch (error) {
          console.warn("Backend fetch failed, using local data:", error);
        }
      }
      if (!data) {
        const localResult = await sendMessage("GET_TODAY_USAGE");
        if (localResult.success) {
          data = localResult.data;
        }
      }
      this.renderData(data, isBackendData);
    } catch (error) {
      showError(this.contentEl, error.message);
    }
  }
  convertBackendResponse(response) {
    return {
      date: response.date,
      callCount: response.call_count,
      totalTokensIn: 0,
      totalTokensOut: 0,
      providers: Object.fromEntries(
        response.top_providers.map((p) => [p.provider, p.count])
      ),
      models: Object.fromEntries(
        response.top_models.map((m) => [m.model, m.count])
      ),
      kwh: response.kwh,
      waterLiters: response.water_liters,
      co2Kg: response.co2_kg
    };
  }
  renderData(data, isBackendData) {
    this.contentEl.innerHTML = "";
    if (!data || data.callCount === 0) {
      this.renderEmptyState();
      return;
    }
    const callCountEl = createElement("div", "call-count", data.callCount.toString());
    this.contentEl.appendChild(callCountEl);
    const metricsSection = createSection("Environmental Impact");
    metricsSection.className += " metrics";
    const metricsData = [
      { label: "Energy", value: formatMetric(data.kwh, "kWh") },
      { label: "Water", value: formatMetric(data.waterLiters, "L") },
      { label: "CO₂", value: formatMetric(data.co2Kg, "kg") }
    ];
    metricsData.forEach((metric) => {
      metricsSection.appendChild(createDataRow(metric.label, metric.value));
    });
    this.contentEl.appendChild(metricsSection);
    if (Object.keys(data.providers).length > 0) {
      const providersSection = createSection("Top Providers");
      const providersData = Object.entries(data.providers).sort(([, a], [, b]) => b - a).slice(0, 5).map(([provider, count]) => ({
        label: provider,
        value: count.toString()
      }));
      const providersList = createList(providersData);
      providersSection.appendChild(providersList);
      this.contentEl.appendChild(providersSection);
    }
    if (Object.keys(data.models).length > 0) {
      const modelsSection = createSection("Top Models");
      const modelsData = Object.entries(data.models).sort(([, a], [, b]) => b - a).slice(0, 5).map(([model, count]) => ({
        label: model === "unknown" ? "Unknown" : model,
        value: count.toString()
      }));
      const modelsList = createList(modelsData);
      modelsSection.appendChild(modelsList);
      this.contentEl.appendChild(modelsSection);
    }
    const sourceInfo = createElement(
      "div",
      "source-info",
      isBackendData ? "🌐 Backend data" : "💾 Local data"
    );
    this.contentEl.appendChild(sourceInfo);
  }
  renderEmptyState() {
    const emptyState = createElement("div", "empty-state");
    const title = createElement("h3", "", "No API calls detected today");
    const subtitle = createElement(
      "p",
      "",
      "Start using AI services to see your usage tracking."
    );
    emptyState.appendChild(title);
    emptyState.appendChild(subtitle);
    this.contentEl.appendChild(emptyState);
  }
  openOptions() {
    chrome.runtime.openOptionsPage();
  }
  async clearToday() {
    if (confirm("Clear today's usage data? This action cannot be undone.")) {
      try {
        const result = await sendMessage("CLEAR_TODAY");
        if (result.success) {
          this.loadData();
        } else {
          alert("Failed to clear data: " + result.error);
        }
      } catch (error) {
        alert("Error: " + error.message);
      }
    }
  }
}
document.addEventListener("DOMContentLoaded", () => {
  new PopupManager();
});
