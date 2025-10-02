import { DailyUsage, TodayResponse } from '@/common/types';
import {
  createElement,
  createButton,
  createSection,
  createDataRow,
  createList,
  showLoading,
  showError,
  sendMessage,
  formatMetric,
  formatDate,
} from './components';

class PopupManager {
  private contentEl: HTMLElement;
  private refreshBtn: HTMLButtonElement;
  private optionsBtn: HTMLButtonElement;
  private clearBtn: HTMLButtonElement;

  constructor() {
    this.contentEl = document.getElementById('content')!;
    this.refreshBtn = document.getElementById('refreshBtn') as HTMLButtonElement;
    this.optionsBtn = document.getElementById('optionsBtn') as HTMLButtonElement;
    this.clearBtn = document.getElementById('clearBtn') as HTMLButtonElement;

    this.setupEventListeners();
    this.updateCurrentDate();
    this.loadData();
  }

  private setupEventListeners(): void {
    this.refreshBtn.addEventListener('click', () => this.loadData());
    this.optionsBtn.addEventListener('click', () => this.openOptions());
    this.clearBtn.addEventListener('click', () => this.clearToday());
  }

  private updateCurrentDate(): void {
    const dateEl = document.getElementById('currentDate');
    if (dateEl) {
      dateEl.textContent = formatDate(new Date().toISOString());
    }
  }

  private async loadData(): Promise<void> {
    showLoading(this.contentEl);

    try {
      // Get settings to check if backend is configured
      const settingsResult = await sendMessage('GET_SETTINGS');
      if (!settingsResult.success) {
        throw new Error('Failed to get settings');
      }

      const settings = settingsResult.data;
      const hasBackend =
        settings.telemetryEnabled &&
        !settings.privacyLocalOnly &&
        settings.baseUrl &&
        settings.userId;

      let data: DailyUsage | TodayResponse | null = null;
      let isBackendData = false;

      if (hasBackend) {
        try {
          const backendResult = await sendMessage('FETCH_TODAY_DATA', {
            baseUrl: settings.baseUrl,
            userId: settings.userId,
          });

          if (backendResult.success) {
            data = this.convertBackendResponse(backendResult.data);
            isBackendData = true;
          }
        } catch (error) {
          console.warn('Backend fetch failed, using local data:', error);
        }
      }

      // Fallback to local data
      if (!data) {
        const localResult = await sendMessage('GET_TODAY_USAGE');
        if (localResult.success) {
          data = localResult.data;
        }
      }

      this.renderData(data, isBackendData);
    } catch (error) {
      showError(this.contentEl, (error as Error).message);
    }
  }

  private convertBackendResponse(response: TodayResponse): DailyUsage {
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
      co2Kg: response.co2_kg,
    };
  }

  private renderData(data: DailyUsage | null, isBackendData: boolean): void {
    this.contentEl.innerHTML = '';

    if (!data || data.callCount === 0) {
      this.renderEmptyState();
      return;
    }

    // Data source indicator (if using backend data)
    if (isBackendData) {
      const sourceIndicator = createElement('div', 'data-source');
      sourceIndicator.textContent = '☁️ Synced with backend';
      sourceIndicator.style.fontSize = '0.8em';
      sourceIndicator.style.color = '#666';
      sourceIndicator.style.marginBottom = '8px';
      this.contentEl.appendChild(sourceIndicator);
    }

    // Call count
    const callCountEl = createElement('div', 'call-count', data.callCount.toString());
    this.contentEl.appendChild(callCountEl);

    // Environmental metrics
    const metricsSection = createSection('Environmental Impact');
    metricsSection.className += ' metrics';

    const metricsData = [
      { label: 'Energy', value: formatMetric(data.kwh, 'kWh') },
      { label: 'Water', value: formatMetric(data.waterLiters, 'L') },
      { label: 'CO₂', value: formatMetric(data.co2Kg, 'kg') },
    ];

    metricsData.forEach((metric) => {
      metricsSection.appendChild(createDataRow(metric.label, metric.value));
    });

    this.contentEl.appendChild(metricsSection);

    // Top providers
    if (Object.keys(data.providers).length > 0) {
      const providersSection = createSection('Top Providers');
      const providersData = Object.entries(data.providers)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 5)
        .map(([provider, count]) => ({
          label: provider,
          value: count.toString(),
        }));

      const providersList = createList(providersData);
      providersSection.appendChild(providersList);
      this.contentEl.appendChild(providersSection);
    }

    // Top models
    if (Object.keys(data.models).length > 0) {
      const modelsSection = createSection('Top Models');
      const modelsData = Object.entries(data.models)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 5)
        .map(([model, count]) => ({
          label: model === 'unknown' ? 'Unknown' : model,
          value: count.toString(),
        }));

      const modelsList = createList(modelsData);
      modelsSection.appendChild(modelsList);
      this.contentEl.appendChild(modelsSection);
    }

    // Data source indicator
    const sourceInfo = createElement(
      'div',
      'source-info',
      isBackendData ? '🌐 Backend data' : '💾 Local data'
    );
    this.contentEl.appendChild(sourceInfo);
  }

  private renderEmptyState(): void {
    const emptyState = createElement('div', 'empty-state');
    const title = createElement('h3', '', 'No API calls detected today');
    const subtitle = createElement(
      'p',
      '',
      'Start using AI services to see your usage tracking.'
    );

    emptyState.appendChild(title);
    emptyState.appendChild(subtitle);
    this.contentEl.appendChild(emptyState);
  }

  private openOptions(): void {
    chrome.runtime.openOptionsPage();
  }

  private async clearToday(): Promise<void> {
    if (confirm('Clear today\'s usage data? This action cannot be undone.')) {
      try {
        const result = await sendMessage('CLEAR_TODAY');
        if (result.success) {
          this.loadData();
        } else {
          alert('Failed to clear data: ' + result.error);
        }
      } catch (error) {
        alert('Error: ' + (error as Error).message);
      }
    }
  }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new PopupManager();
});