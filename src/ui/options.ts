import { ExtensionSettings } from '@/common/types';
import { DEFAULT_SETTINGS, DEFAULT_PROVIDERS } from '@/common/constants';
import { sendMessage } from './components';

class OptionsManager {
  private settings: ExtensionSettings = {
    ...DEFAULT_SETTINGS,
    estimationParams: { ...DEFAULT_SETTINGS.estimationParams },
  };
  private elements: { [key: string]: HTMLElement } = {};

  constructor() {
    this.initializeElements();
    this.setupEventListeners();
    this.loadSettings();
  }

  private initializeElements(): void {
    const ids = [
      'baseUrl',
      'userId',
      'privacyLocalOnly',
      'telemetryEnabled',
      'kwhPerCall',
      'pue',
      'waterLPerKwh',
      'co2KgPerKwh',
      'connectionStatus',
      'privacyWarning',
      'providersList',
      'customProvidersList',
      'customProviderInput',
      'addProviderBtn',
      'testConnectionBtn',
      'resetBtn',
      'saveBtn',
      'savedIndicator',
    ];

    ids.forEach((id) => {
      this.elements[id] = document.getElementById(id)!;
    });
  }

  private setupEventListeners(): void {
    // Form inputs
    (this.elements.baseUrl as HTMLInputElement).addEventListener(
      'input',
      this.handleInputChange.bind(this)
    );
    (this.elements.userId as HTMLInputElement).addEventListener(
      'input',
      this.handleInputChange.bind(this)
    );

    // Checkboxes
    (this.elements.privacyLocalOnly as HTMLInputElement).addEventListener(
      'change',
      this.handlePrivacyChange.bind(this)
    );
    (this.elements.telemetryEnabled as HTMLInputElement).addEventListener(
      'change',
      this.handleInputChange.bind(this)
    );

    // Estimation parameters
    ['kwhPerCall', 'pue', 'waterLPerKwh', 'co2KgPerKwh'].forEach((id) => {
      (this.elements[id] as HTMLInputElement).addEventListener(
        'input',
        this.handleInputChange.bind(this)
      );
    });

    // Custom providers
    (this.elements.addProviderBtn as HTMLButtonElement).addEventListener(
      'click',
      this.addCustomProvider.bind(this)
    );
    (this.elements.customProviderInput as HTMLInputElement).addEventListener(
      'keypress',
      (e) => {
        if (e.key === 'Enter') {
          this.addCustomProvider();
        }
      }
    );

    // Action buttons
    (this.elements.testConnectionBtn as HTMLButtonElement).addEventListener(
      'click',
      this.testConnection.bind(this)
    );
    (this.elements.resetBtn as HTMLButtonElement).addEventListener(
      'click',
      this.resetToDefaults.bind(this)
    );
    (this.elements.saveBtn as HTMLButtonElement).addEventListener(
      'click',
      this.saveSettings.bind(this)
    );
  }

  private async loadSettings(): Promise<void> {
    try {
      const result = await sendMessage('GET_SETTINGS');
      if (result.success && result.data) {
        // Deep clone to prevent mutation of DEFAULT_SETTINGS
        this.settings = {
          ...DEFAULT_SETTINGS,
          ...result.data,
          estimationParams: {
            ...DEFAULT_SETTINGS.estimationParams,
            ...(result.data?.estimationParams || {}),
          },
        };
        this.populateForm();
        this.renderProviders();
        this.updateConnectionStatus();
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  }

  private populateForm(): void {
    (this.elements.baseUrl as HTMLInputElement).value = this.settings.baseUrl;
    (this.elements.userId as HTMLInputElement).value = this.settings.userId;
    (this.elements.privacyLocalOnly as HTMLInputElement).checked =
      this.settings.privacyLocalOnly;
    (this.elements.telemetryEnabled as HTMLInputElement).checked =
      this.settings.telemetryEnabled;
    (this.elements.kwhPerCall as HTMLInputElement).value =
      this.settings.estimationParams.kwhPerCall.toString();
    (this.elements.pue as HTMLInputElement).value =
      this.settings.estimationParams.pue.toString();
    (this.elements.waterLPerKwh as HTMLInputElement).value =
      this.settings.estimationParams.waterLPerKwh.toString();
    (this.elements.co2KgPerKwh as HTMLInputElement).value =
      this.settings.estimationParams.co2KgPerKwh.toString();

    this.updatePrivacyWarning();
  }

  private renderProviders(): void {
    // Default providers
    const providersList = this.elements.providersList;
    providersList.innerHTML = '';

    DEFAULT_PROVIDERS.forEach((provider) => {
      const item = document.createElement('div');
      item.className = 'provider-item';
      item.innerHTML = `
        <div>
          <div class="provider-name">${provider.name}</div>
          <div class="provider-domains">${provider.domains.join(', ')}</div>
        </div>
        <span>Default</span>
      `;
      providersList.appendChild(item);
    });

    // Custom providers
    this.renderCustomProviders();
  }

  private renderCustomProviders(): void {
    const customList = this.elements.customProvidersList;
    customList.innerHTML = '';

    if (this.settings.customProviders.length === 0) {
      customList.innerHTML = '<div style="text-align: center; color: #666; padding: 12px;">No custom providers added</div>';
      return;
    }

    this.settings.customProviders.forEach((domain, index) => {
      const item = document.createElement('div');
      item.className = 'provider-item';
      item.innerHTML = `
        <div>
          <div class="provider-name">${domain}</div>
          <div class="provider-domains">Custom domain</div>
        </div>
        <button class="btn btn-danger btn-small" type="button">Remove</button>
      `;
      
      item
        .querySelector('button')
        ?.addEventListener('click', () => this.removeCustomProvider(index));
      
      customList.appendChild(item);
    });
  }

  private handleInputChange(): void {
    this.collectFormData();
    this.updateConnectionStatus();
  }

  private handlePrivacyChange(): void {
    this.collectFormData();
    this.updatePrivacyWarning();
    this.updateConnectionStatus();
  }

  private collectFormData(): void {
    this.settings.baseUrl = (this.elements.baseUrl as HTMLInputElement).value.trim();
    this.settings.userId = (this.elements.userId as HTMLInputElement).value.trim();
    this.settings.privacyLocalOnly = (this.elements.privacyLocalOnly as HTMLInputElement).checked;
    this.settings.telemetryEnabled = (this.elements.telemetryEnabled as HTMLInputElement).checked;

    this.settings.estimationParams.kwhPerCall = parseFloat(
      (this.elements.kwhPerCall as HTMLInputElement).value
    ) || DEFAULT_SETTINGS.estimationParams.kwhPerCall;
    this.settings.estimationParams.pue = parseFloat(
      (this.elements.pue as HTMLInputElement).value
    ) || DEFAULT_SETTINGS.estimationParams.pue;
    this.settings.estimationParams.waterLPerKwh = parseFloat(
      (this.elements.waterLPerKwh as HTMLInputElement).value
    ) || DEFAULT_SETTINGS.estimationParams.waterLPerKwh;
    this.settings.estimationParams.co2KgPerKwh = parseFloat(
      (this.elements.co2KgPerKwh as HTMLInputElement).value
    ) || DEFAULT_SETTINGS.estimationParams.co2KgPerKwh;
  }

  private updatePrivacyWarning(): void {
    const warning = this.elements.privacyWarning;
    const telemetryInput = this.elements.telemetryEnabled as HTMLInputElement;
    
    if (this.settings.privacyLocalOnly) {
      warning.style.display = 'block';
      telemetryInput.disabled = true;
    } else {
      warning.style.display = 'none';
      telemetryInput.disabled = false;
    }
  }

  private updateConnectionStatus(): void {
    const status = this.elements.connectionStatus;
    const canConnect = this.settings.baseUrl && this.settings.userId && 
                       this.settings.telemetryEnabled && !this.settings.privacyLocalOnly;

    if (!this.settings.baseUrl || !this.settings.userId) {
      status.className = 'status-indicator disabled';
      status.innerHTML = '<div class="status-dot"></div>Not configured';
    } else if (this.settings.privacyLocalOnly) {
      status.className = 'status-indicator disabled';
      status.innerHTML = '<div class="status-dot"></div>Privacy mode';
    } else if (!this.settings.telemetryEnabled) {
      status.className = 'status-indicator disabled';
      status.innerHTML = '<div class="status-dot"></div>Telemetry disabled';
    } else {
      status.className = 'status-indicator disconnected';
      status.innerHTML = '<div class="status-dot"></div>Ready to test';
    }
  }

  private addCustomProvider(): void {
    const input = this.elements.customProviderInput as HTMLInputElement;
    const domain = input.value.trim();

    if (!domain) return;

    // Basic domain validation (allow ports for localhost and custom setups)
    if (!/^(\*\.)?[a-zA-Z0-9.-]+(:[0-9]+)?(\.[a-zA-Z]{2,}|$)/.test(domain)) {
      alert('Please enter a valid domain (e.g., api.example.com, *.example.com, or localhost:3000)');
      return;
    }

    if (this.settings.customProviders.includes(domain)) {
      alert('This domain is already added');
      return;
    }

    this.settings.customProviders.push(domain);
    input.value = '';
    this.renderCustomProviders();
  }

  private removeCustomProvider(index: number): void {
    this.settings.customProviders.splice(index, 1);
    this.renderCustomProviders();
  }

  private async testConnection(): Promise<void> {
    if (!this.settings.baseUrl) {
      alert('Please enter a backend URL first');
      return;
    }

    const btn = this.elements.testConnectionBtn as HTMLButtonElement;
    const originalText = btn.textContent;
    btn.textContent = 'Testing...';
    btn.disabled = true;

    try {
      const result = await sendMessage('TEST_CONNECTION', {
        baseUrl: this.settings.baseUrl,
      });

      const status = this.elements.connectionStatus;
      if (result.success && result.data) {
        status.className = 'status-indicator connected';
        status.innerHTML = '<div class="status-dot"></div>Connected';
        alert('Connection successful!');
      } else {
        status.className = 'status-indicator disconnected';
        status.innerHTML = '<div class="status-dot"></div>Connection failed';
        alert('Connection failed. Please check your backend URL.');
      }
    } catch (error) {
      alert('Error testing connection: ' + (error as Error).message);
    } finally {
      btn.textContent = originalText;
      btn.disabled = false;
    }
  }

  private async saveSettings(): Promise<void> {
    try {
      // Save settings
      const result = await sendMessage('SAVE_SETTINGS', { settings: this.settings });
      
      if (result.success) {
        // Update providers in background script
        await sendMessage('UPDATE_PROVIDERS');
        
        // Show saved indicator
        const indicator = this.elements.savedIndicator;
        indicator.classList.add('show');
        setTimeout(() => {
          indicator.classList.remove('show');
        }, 2000);
      } else {
        alert('Failed to save settings: ' + result.error);
      }
    } catch (error) {
      alert('Error saving settings: ' + (error as Error).message);
    }
  }

  private async resetToDefaults(): Promise<void> {
    if (confirm('Reset all settings to defaults? This action cannot be undone.')) {
      this.settings = {
        ...DEFAULT_SETTINGS,
        estimationParams: { ...DEFAULT_SETTINGS.estimationParams },
      };
      this.populateForm();
      this.renderProviders();
      this.updateConnectionStatus();
    }
  }
}

// Initialize options page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new OptionsManager();
});