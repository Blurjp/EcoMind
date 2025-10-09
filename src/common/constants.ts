import { ExtensionSettings, ProviderConfig } from './types';
import { matchesDomain } from './util';

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
    domains: ['api.openai.com', 'chatgpt.com', '*.chatgpt.com', 'chat.openai.com', '*.chat.openai.com'],
    modelExtractor: (url: string, body?: string) => {
      // Try body parsing first (preserves accuracy when body available)
      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || 'unknown';
        } catch {
          // Ignore parsing errors
        }
      }
      // MV3 fallback: URL-based detection when body unavailable
      if (matchesDomain(url, 'chatgpt.com') || matchesDomain(url, 'chat.openai.com')) {
        return 'chatgpt';
      }
      // Final fallback: OpenAI API (body empty, not web UI)
      return 'openai-api';
    },
  },
  {
    name: 'anthropic',
    domains: ['api.anthropic.com', 'claude.ai', '*.claude.ai'],
    modelExtractor: (url: string, body?: string) => {
      // Try body parsing first (preserves accuracy when body available)
      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || 'unknown';
        } catch {
          // Ignore parsing errors
        }
      }
      // MV3 fallback: URL-based detection when body unavailable
      if (matchesDomain(url, 'claude.ai')) {
        return 'claude';
      }
      // Final fallback: Anthropic API (body empty, not web UI)
      return 'anthropic-api';
    },
  },
  {
    name: 'replicate',
    domains: ['api.replicate.com'],
    modelExtractor: (url: string) => {
      const match = url.match(/\/models\/([^\/]+\/[^\/]+)/);
      return match ? match[1] : 'replicate-api';
    },
  },
  {
    name: 'together',
    domains: ['api.together.xyz'],
    modelExtractor: (url: string, body?: string) => {
      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || 'together-api';
        } catch {
          // Ignore parsing errors
        }
      }
      return 'together-api';
    },
  },
  {
    name: 'cohere',
    domains: ['api.cohere.ai'],
    modelExtractor: (url: string, body?: string) => {
      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || 'cohere-api';
        } catch {
          // Ignore parsing errors
        }
      }
      return 'cohere-api';
    },
  },
  {
    name: 'perplexity',
    domains: ['api.perplexity.ai'],
    modelExtractor: (url: string, body?: string) => {
      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || 'perplexity-api';
        } catch {
          // Ignore parsing errors
        }
      }
      return 'perplexity-api';
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
      // Fall back to URL extraction
      const match = url.match(/\/models\/([^\/\?]+)/);
      return match ? match[1] : 'google-api';
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