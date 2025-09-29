const DEFAULT_SETTINGS = {
  baseUrl: "",
  userId: "",
  telemetryEnabled: false,
  privacyLocalOnly: true,
  customProviders: [],
  estimationParams: {
    kwhPerCall: 3e-4,
    pue: 1.5,
    waterLPerKwh: 1.8,
    co2KgPerKwh: 0.4
  }
};
const DEFAULT_PROVIDERS = [
  {
    name: "openai",
    domains: ["api.openai.com"],
    modelExtractor: (url, body) => {
      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || "unknown";
        } catch {
        }
      }
      return "unknown";
    }
  },
  {
    name: "anthropic",
    domains: ["api.anthropic.com"],
    modelExtractor: (url, body) => {
      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || "unknown";
        } catch {
        }
      }
      return "unknown";
    }
  },
  {
    name: "replicate",
    domains: ["api.replicate.com"],
    modelExtractor: (url) => {
      const match = url.match(/\/models\/([^\/]+\/[^\/]+)/);
      return match ? match[1] : "unknown";
    }
  },
  {
    name: "together",
    domains: ["api.together.xyz"],
    modelExtractor: (url, body) => {
      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || "unknown";
        } catch {
        }
      }
      return "unknown";
    }
  },
  {
    name: "cohere",
    domains: ["api.cohere.ai"],
    modelExtractor: (url, body) => {
      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || "unknown";
        } catch {
        }
      }
      return "unknown";
    }
  },
  {
    name: "perplexity",
    domains: ["api.perplexity.ai"],
    modelExtractor: (url, body) => {
      if (body) {
        try {
          const parsed = JSON.parse(body);
          return parsed.model || "unknown";
        } catch {
        }
      }
      return "unknown";
    }
  },
  {
    name: "google",
    domains: ["generativelanguage.googleapis.com", "ai.google.dev"],
    modelExtractor: (url, body) => {
      if (body) {
        try {
          const parsed = JSON.parse(body);
          if (parsed.model)
            return parsed.model;
        } catch {
        }
      }
      const match = url.match(/\/models\/([^\/\?]+)/);
      return match ? match[1] : "unknown";
    }
  }
];
const STORAGE_KEYS = {
  SETTINGS: "ecomind_settings",
  DAILY_USAGE: "ecomind_daily_usage",
  TODAY_COUNT: "ecomind_today_count",
  LAST_RESET_DATE: "ecomind_last_reset_date"
};
const ALARM_NAMES = {
  MIDNIGHT_RESET: "midnight_reset"
};
export {
  ALARM_NAMES as A,
  DEFAULT_SETTINGS as D,
  STORAGE_KEYS as S,
  DEFAULT_PROVIDERS as a
};
