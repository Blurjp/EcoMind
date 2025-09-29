import { TelemetryPayload } from '@/common/types';
import { retry } from '@/common/util';

export class TelemetryManager {
  private static instance: TelemetryManager;

  static getInstance(): TelemetryManager {
    if (!this.instance) {
      this.instance = new TelemetryManager();
    }
    return this.instance;
  }

  async sendTelemetry(
    baseUrl: string,
    payload: TelemetryPayload
  ): Promise<boolean> {
    if (!baseUrl || !payload.user_id) {
      return false;
    }

    try {
      await retry(async () => {
        const response = await fetch(`${baseUrl}/ingest`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      });

      return true;
    } catch (error) {
      console.warn('Failed to send telemetry:', error);
      return false;
    }
  }

  async fetchTodayData(baseUrl: string, userId: string) {
    if (!baseUrl || !userId) {
      throw new Error('Missing baseUrl or userId');
    }

    try {
      const response = await fetch(
        `${baseUrl}/today?user_id=${encodeURIComponent(userId)}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.warn('Failed to fetch today data:', error);
      throw error;
    }
  }

  async testConnection(baseUrl: string): Promise<boolean> {
    if (!baseUrl) {
      return false;
    }

    try {
      const response = await fetch(`${baseUrl}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });

      return response.ok;
    } catch {
      return false;
    }
  }
}