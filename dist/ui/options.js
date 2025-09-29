import { D as DEFAULT_SETTINGS, a as DEFAULT_PROVIDERS } from "../constants.js";
import { a as sendMessage } from "../components.js";
class OptionsManager {
  constructor() {
    this.settings = { ...DEFAULT_SETTINGS };
    this.elements = {};
    this.initializeElements();
    this.setupEventListeners();
    this.loadSettings();
  }
  initializeElements() {
    const ids = [
      "baseUrl",
      "userId",
      "privacyLocalOnly",
      "telemetryEnabled",
      "kwhPerCall",
      "pue",
      "waterLPerKwh",
      "co2KgPerKwh",
      "connectionStatus",
      "privacyWarning",
      "providersList",
      "customProvidersList",
      "customProviderInput",
      "addProviderBtn",
      "testConnectionBtn",
      "resetBtn",
      "saveBtn",
      "savedIndicator"
    ];
    ids.forEach((id) => {
      this.elements[id] = document.getElementById(id);
    });
  }
  setupEventListeners() {
    this.elements.baseUrl.addEventListener(
      "input",
      this.handleInputChange.bind(this)
    );
    this.elements.userId.addEventListener(
      "input",
      this.handleInputChange.bind(this)
    );
    this.elements.privacyLocalOnly.addEventListener(
      "change",
      this.handlePrivacyChange.bind(this)
    );
    this.elements.telemetryEnabled.addEventListener(
      "change",
      this.handleInputChange.bind(this)
    );
    ["kwhPerCall", "pue", "waterLPerKwh", "co2KgPerKwh"].forEach((id) => {
      this.elements[id].addEventListener(
        "input",
        this.handleInputChange.bind(this)
      );
    });
    this.elements.addProviderBtn.addEventListener(
      "click",
      this.addCustomProvider.bind(this)
    );
    this.elements.customProviderInput.addEventListener(
      "keypress",
      (e) => {
        if (e.key === "Enter") {
          this.addCustomProvider();
        }
      }
    );
    this.elements.testConnectionBtn.addEventListener(
      "click",
      this.testConnection.bind(this)
    );
    this.elements.resetBtn.addEventListener(
      "click",
      this.resetToDefaults.bind(this)
    );
    this.elements.saveBtn.addEventListener(
      "click",
      this.saveSettings.bind(this)
    );
  }
  async loadSettings() {
    try {
      const result = await sendMessage("GET_SETTINGS");
      if (result.success && result.data) {
        this.settings = { ...DEFAULT_SETTINGS, ...result.data };
        this.populateForm();
        this.renderProviders();
        this.updateConnectionStatus();
      }
    } catch (error) {
      console.error("Failed to load settings:", error);
    }
  }
  populateForm() {
    this.elements.baseUrl.value = this.settings.baseUrl;
    this.elements.userId.value = this.settings.userId;
    this.elements.privacyLocalOnly.checked = this.settings.privacyLocalOnly;
    this.elements.telemetryEnabled.checked = this.settings.telemetryEnabled;
    this.elements.kwhPerCall.value = this.settings.estimationParams.kwhPerCall.toString();
    this.elements.pue.value = this.settings.estimationParams.pue.toString();
    this.elements.waterLPerKwh.value = this.settings.estimationParams.waterLPerKwh.toString();
    this.elements.co2KgPerKwh.value = this.settings.estimationParams.co2KgPerKwh.toString();
    this.updatePrivacyWarning();
  }
  renderProviders() {
    const providersList = this.elements.providersList;
    providersList.innerHTML = "";
    DEFAULT_PROVIDERS.forEach((provider) => {
      const item = document.createElement("div");
      item.className = "provider-item";
      item.innerHTML = `
        <div>
          <div class="provider-name">${provider.name}</div>
          <div class="provider-domains">${provider.domains.join(", ")}</div>
        </div>
        <span>Default</span>
      `;
      providersList.appendChild(item);
    });
    this.renderCustomProviders();
  }
  renderCustomProviders() {
    const customList = this.elements.customProvidersList;
    customList.innerHTML = "";
    if (this.settings.customProviders.length === 0) {
      customList.innerHTML = '<div style="text-align: center; color: #666; padding: 12px;">No custom providers added</div>';
      return;
    }
    this.settings.customProviders.forEach((domain, index) => {
      const item = document.createElement("div");
      item.className = "provider-item";
      item.innerHTML = `
        <div>
          <div class="provider-name">${domain}</div>
          <div class="provider-domains">Custom domain</div>
        </div>
        <button class="btn btn-danger btn-small" type="button">Remove</button>
      `;
      item.querySelector("button")?.addEventListener("click", () => this.removeCustomProvider(index));
      customList.appendChild(item);
    });
  }
  handleInputChange() {
    this.collectFormData();
    this.updateConnectionStatus();
  }
  handlePrivacyChange() {
    this.collectFormData();
    this.updatePrivacyWarning();
    this.updateConnectionStatus();
  }
  collectFormData() {
    this.settings.baseUrl = this.elements.baseUrl.value.trim();
    this.settings.userId = this.elements.userId.value.trim();
    this.settings.privacyLocalOnly = this.elements.privacyLocalOnly.checked;
    this.settings.telemetryEnabled = this.elements.telemetryEnabled.checked;
    this.settings.estimationParams.kwhPerCall = parseFloat(
      this.elements.kwhPerCall.value
    ) || DEFAULT_SETTINGS.estimationParams.kwhPerCall;
    this.settings.estimationParams.pue = parseFloat(
      this.elements.pue.value
    ) || DEFAULT_SETTINGS.estimationParams.pue;
    this.settings.estimationParams.waterLPerKwh = parseFloat(
      this.elements.waterLPerKwh.value
    ) || DEFAULT_SETTINGS.estimationParams.waterLPerKwh;
    this.settings.estimationParams.co2KgPerKwh = parseFloat(
      this.elements.co2KgPerKwh.value
    ) || DEFAULT_SETTINGS.estimationParams.co2KgPerKwh;
  }
  updatePrivacyWarning() {
    const warning = this.elements.privacyWarning;
    const telemetryInput = this.elements.telemetryEnabled;
    if (this.settings.privacyLocalOnly) {
      warning.style.display = "block";
      telemetryInput.disabled = true;
    } else {
      warning.style.display = "none";
      telemetryInput.disabled = false;
    }
  }
  updateConnectionStatus() {
    const status = this.elements.connectionStatus;
    this.settings.baseUrl && this.settings.userId && this.settings.telemetryEnabled && !this.settings.privacyLocalOnly;
    if (!this.settings.baseUrl || !this.settings.userId) {
      status.className = "status-indicator disabled";
      status.innerHTML = '<div class="status-dot"></div>Not configured';
    } else if (this.settings.privacyLocalOnly) {
      status.className = "status-indicator disabled";
      status.innerHTML = '<div class="status-dot"></div>Privacy mode';
    } else if (!this.settings.telemetryEnabled) {
      status.className = "status-indicator disabled";
      status.innerHTML = '<div class="status-dot"></div>Telemetry disabled';
    } else {
      status.className = "status-indicator disconnected";
      status.innerHTML = '<div class="status-dot"></div>Ready to test';
    }
  }
  addCustomProvider() {
    const input = this.elements.customProviderInput;
    const domain = input.value.trim();
    if (!domain)
      return;
    if (!/^(\*\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(domain)) {
      alert("Please enter a valid domain (e.g., api.example.com or *.example.com)");
      return;
    }
    if (this.settings.customProviders.includes(domain)) {
      alert("This domain is already added");
      return;
    }
    this.settings.customProviders.push(domain);
    input.value = "";
    this.renderCustomProviders();
  }
  removeCustomProvider(index) {
    this.settings.customProviders.splice(index, 1);
    this.renderCustomProviders();
  }
  async testConnection() {
    if (!this.settings.baseUrl) {
      alert("Please enter a backend URL first");
      return;
    }
    const btn = this.elements.testConnectionBtn;
    const originalText = btn.textContent;
    btn.textContent = "Testing...";
    btn.disabled = true;
    try {
      const result = await sendMessage("TEST_CONNECTION", {
        baseUrl: this.settings.baseUrl
      });
      const status = this.elements.connectionStatus;
      if (result.success && result.data) {
        status.className = "status-indicator connected";
        status.innerHTML = '<div class="status-dot"></div>Connected';
        alert("Connection successful!");
      } else {
        status.className = "status-indicator disconnected";
        status.innerHTML = '<div class="status-dot"></div>Connection failed';
        alert("Connection failed. Please check your backend URL.");
      }
    } catch (error) {
      alert("Error testing connection: " + error.message);
    } finally {
      btn.textContent = originalText;
      btn.disabled = false;
    }
  }
  async saveSettings() {
    try {
      const result = await sendMessage("SAVE_SETTINGS", { settings: this.settings });
      if (result.success) {
        await sendMessage("UPDATE_PROVIDERS");
        const indicator = this.elements.savedIndicator;
        indicator.classList.add("show");
        setTimeout(() => {
          indicator.classList.remove("show");
        }, 2e3);
      } else {
        alert("Failed to save settings: " + result.error);
      }
    } catch (error) {
      alert("Error saving settings: " + error.message);
    }
  }
  async resetToDefaults() {
    if (confirm("Reset all settings to defaults? This action cannot be undone.")) {
      this.settings = { ...DEFAULT_SETTINGS };
      this.populateForm();
      this.renderProviders();
      this.updateConnectionStatus();
    }
  }
}
document.addEventListener("DOMContentLoaded", () => {
  new OptionsManager();
});
