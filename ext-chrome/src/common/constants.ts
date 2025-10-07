import { ExtensionSettings, ProviderConfig } from './types';

export const DEFAULT_SETTINGS: ExtensionSettings = {
  baseUrl: '',
  userId: '',
  telemetryEnabled: false,
  privacyLocalOnly: true,
  customProviders: [],
  estimationParams: {
    kwhPerCall: 0.0003,
    pue: 1.5,
    waterLPerKwh: 1.8,
    co2KgPerKwh: 0.4,
  },
};

export const DEFAULT_PROVIDERS: ProviderConfig[] = [
  {
    name: 'openai',
    domains: ['api.openai.com', 'chatgpt.com', 'chat.openai.com'],
    modelExtractor: (url: string, body?: string) => {
      // Try URL extraction for ChatGPT web UI
      if (url.includes('chatgpt.com')) {
        // ChatGPT web UI uses /backend-api/conversation endpoint
        if (url.includes('/backend-api/conversation')) {
          return 'chatgpt-web';
        }
        // GPT-4 model selector in URL params
        const modelMatch = url.match(/[?&]model=([^&]+)/);
        if (modelMatch) {
          return decodeURIComponent(modelMatch[1]);
        }
      }

      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || 'unknown';
        } catch {
          // Ignore parsing errors
        }
      }
      return 'unknown';
    },
  },
  {
    name: 'anthropic',
    domains: ['api.anthropic.com', 'claude.ai'],
    modelExtractor: (url: string, body?: string) => {
      // Try URL extraction for Claude web UI
      if (url.includes('claude.ai')) {
        // Claude web UI organization URLs sometimes include model hints
        const modelMatch = url.match(/[?&]model=([^&]+)/);
        if (modelMatch) {
          return decodeURIComponent(modelMatch[1]);
        }
        // Generic indicator for Claude web interface
        if (url.includes('/api/organizations/')) {
          return 'claude-web';
        }
      }

      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || 'unknown';
        } catch {
          // Ignore parsing errors
        }
      }
      return 'unknown';
    },
  },
  {
    name: 'replicate',
    domains: ['api.replicate.com'],
    modelExtractor: (url: string) => {
      const match = url.match(/\/models\/([^\/]+\/[^\/]+)/);
      return match ? match[1] : 'unknown';
    },
  },
  {
    name: 'together',
    domains: ['api.together.xyz'],
    modelExtractor: (url: string, body?: string) => {
      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || 'unknown';
        } catch {
          // Ignore parsing errors
        }
      }
      return 'unknown';
    },
  },
  {
    name: 'cohere',
    domains: ['api.cohere.ai'],
    modelExtractor: (url: string, body?: string) => {
      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || 'unknown';
        } catch {
          // Ignore parsing errors
        }
      }
      return 'unknown';
    },
  },
  {
    name: 'perplexity',
    domains: ['api.perplexity.ai'],
    modelExtractor: (url: string, body?: string) => {
      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || 'unknown';
        } catch {
          // Ignore parsing errors
        }
      }
      return 'unknown';
    },
  },
  {
    name: 'google',
    domains: ['generativelanguage.googleapis.com', 'ai.google.dev'],
    modelExtractor: (url: string, body?: string) => {
      // Try body first if available
      if (body) {
        try {
          const parsed = JSON.parse(body);
          if (parsed.model) return parsed.model;
        } catch {
          // Ignore parsing errors
        }
      }
      // Fall back to URL extraction (works well for Gemini)
      const match = url.match(/\/models\/([^\/\?:]+)/);
      return match ? match[1] : 'unknown';
    },
  },
];

export const STORAGE_KEYS = {
  SETTINGS: 'ecomind_settings',
  DAILY_USAGE: 'ecomind_daily_usage',
  TODAY_COUNT: 'ecomind_today_count',
  LAST_RESET_DATE: 'ecomind_last_reset_date',
} as const;

export const ALARM_NAMES = {
  MIDNIGHT_RESET: 'midnight_reset',
} as const;