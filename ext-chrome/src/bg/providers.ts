import { ProviderConfig } from '@/common/types';
import { DEFAULT_PROVIDERS } from '@/common/constants';
import { extractDomainFromUrl, shouldTrackDomain } from '@/common/util';

export class ProviderManager {
  private providers: ProviderConfig[] = [];

  constructor() {
    this.providers = [...DEFAULT_PROVIDERS];
  }

  addCustomProvider(name: string, domains: string[]): void {
    const existing = this.providers.find((p) => p.name === name);
    if (existing) {
      existing.domains = [...new Set([...existing.domains, ...domains])];
    } else {
      this.providers.push({
        name,
        domains,
        modelExtractor: () => 'unknown',
      });
    }
  }

  removeCustomProvider(name: string): void {
    this.providers = this.providers.filter(
      (p) => p.name !== name || DEFAULT_PROVIDERS.find((dp) => dp.name === name)
    );
  }

  getAllDomains(): string[] {
    return this.providers.flatMap((p) => p.domains);
  }

  findProviderForUrl(url: string): ProviderConfig | null {
    const domain = extractDomainFromUrl(url);
    if (!domain) return null;

    return (
      this.providers.find((provider) =>
        shouldTrackDomain(domain, provider.domains)
      ) || null
    );
  }

  extractModel(url: string, body?: string): { provider: string; model: string } {
    const provider = this.findProviderForUrl(url);
    if (!provider) {
      return { provider: 'unknown', model: 'unknown' };
    }

    const model = provider.modelExtractor
      ? provider.modelExtractor(url, body)
      : 'unknown';

    return { provider: provider.name, model };
  }

  shouldTrackRequest(url: string): boolean {
    return this.findProviderForUrl(url) !== null;
  }

  updateCustomProviders(customProviders: string[]): void {
    // Remove existing custom providers
    this.providers = this.providers.filter((p) =>
      DEFAULT_PROVIDERS.find((dp) => dp.name === p.name)
    );

    // Add new custom providers
    customProviders.forEach((domain) => {
      if (domain.trim()) {
        this.addCustomProvider('custom', [domain.trim()]);
      }
    });
  }
}