export interface UsageRecord {
  id: string;
  provider: string;
  model: string;
  tokensIn: number;
  tokensOut: number;
  timestamp: string;
  date: string; // YYYY-MM-DD format
}

export interface DailyUsage {
  date: string; // YYYY-MM-DD format
  callCount: number;
  totalTokensIn: number;
  totalTokensOut: number;
  providers: Record<string, number>; // provider -> count
  models: Record<string, number>; // model -> count
  kwh: number;
  waterLiters: number;
  co2Kg: number;
}

export interface ExtensionSettings {
  baseUrl: string;
  userId: string;
  telemetryEnabled: boolean;
  privacyLocalOnly: boolean;
  customProviders: string[];
  estimationParams: {
    kwhPerCall: number;
    pue: number;
    waterLPerKwh: number;
    co2KgPerKwh: number;
  };
}

export interface TelemetryPayload {
  user_id: string;
  provider: string;
  model: string;
  tokens_in: number;
  tokens_out: number;
  ts: string;
}

export interface TodayResponse {
  date: string;
  call_count: number;
  kwh: number;
  water_liters: number;
  co2_kg: number;
  top_providers: Array<{ provider: string; count: number }>;
  top_models: Array<{ model: string; count: number }>;
}

export interface ProviderConfig {
  name: string;
  domains: string[];
  modelExtractor?: (url: string, body?: string) => string;
}

export interface StorageData {
  settings: ExtensionSettings;
  dailyUsage: Record<string, DailyUsage>; // date -> usage
  todayCount: number;
  lastResetDate: string;
}