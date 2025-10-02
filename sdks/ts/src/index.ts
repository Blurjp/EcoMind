export interface EcomindConfig {
  apiKey: string;
  baseUrl: string;
  orgId: string;
  userId: string;
}

export interface TrackEvent {
  provider: string;
  model?: string;
  tokensIn?: number;
  tokensOut?: number;
  region?: string;
  metadata?: Record<string, any>;
}

export class EcomindClient {
  private config: EcomindConfig;

  constructor(config: EcomindConfig) {
    this.config = config;
  }

  async track(event: TrackEvent): Promise<void> {
    const payload = {
      org_id: this.config.orgId,
      user_id: this.config.userId,
      provider: event.provider,
      model: event.model || "",
      tokens_in: event.tokensIn || 0,
      tokens_out: event.tokensOut || 0,
      region: event.region || "UNKNOWN",
      ts: new Date().toISOString(),
      metadata: event.metadata,
    };

    const url = `${this.config.baseUrl}/v1/ingest`;
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.config.apiKey}`,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Failed to track event: ${response.statusText}`);
    }
  }

  async getToday(): Promise<any> {
    const url = `${this.config.baseUrl}/v1/today?org_id=${this.config.orgId}&user_id=${this.config.userId}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${this.config.apiKey}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get today's data: ${response.statusText}`);
    }

    return response.json();
  }
}