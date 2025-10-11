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
      'kwhPerCall',
      'pue',
      'waterLPerKwh',
      'co2KgPerKwh',
      'providersList',
      'customProvidersList',
      'customProviderInput',
      'addProviderBtn',
      'resetBtn',
      'saveBtn',
      'savedIndicator',
    ];

    ids.forEach((id) => {
      this.elements[id] = document.getElementById(id)!;
    });
  }

  private setupEventListeners(): void {
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
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  }

  private populateForm(): void {
    (this.elements.kwhPerCall as HTMLInputElement).value =
      this.settings.estimationParams.kwhPerCall.toString();
    (this.elements.pue as HTMLInputElement).value =
      this.settings.estimationParams.pue.toString();
    (this.elements.waterLPerKwh as HTMLInputElement).value =
      this.settings.estimationParams.waterLPerKwh.toString();
    (this.elements.co2KgPerKwh as HTMLInputElement).value =
      this.settings.estimationParams.co2KgPerKwh.toString();
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
  }

  private collectFormData(): void {
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
    }
  }
}

// Initialize options page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new OptionsManager();
});