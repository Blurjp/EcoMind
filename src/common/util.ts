export function getTodayDate(): string {
  return new Date().toISOString().split('T')[0];
}

export function generateId(): string {
  return Math.random().toString(36).substr(2, 9);
}

export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

export function extractDomainFromUrl(url: string): string {
  try {
    const { hostname, port } = new URL(url);
    return port ? `${hostname}:${port}` : hostname;
  } catch {
    return '';
  }
}

export function calculateFootprint(
  callCount: number,
  kwhPerCall: number,
  pue: number,
  waterLPerKwh: number,
  co2KgPerKwh: number
) {
  const kwh = callCount * kwhPerCall * pue;
  return {
    kwh,
    waterLiters: kwh * waterLPerKwh,
    co2Kg: kwh * co2KgPerKwh,
  };
}

export function formatNumber(num: number, decimals = 2): string {
  return num.toFixed(decimals);
}

export function domainMatchesPattern(domain: string, pattern: string): boolean {
  const [domainHost, domainPort] = domain.split(':');
  const [patternHost, patternPort] = pattern.split(':');

  if (patternPort && patternPort !== domainPort) {
    return false;
  }

  const hostPattern = patternHost.startsWith('*.') ? patternHost.slice(2) : patternHost;
  if (patternHost.startsWith('*.')) {
    return domainHost === hostPattern || domainHost.endsWith(`.${hostPattern}`);
  }

  return domainHost === hostPattern;
}

export function shouldTrackDomain(
  domain: string,
  providerDomains: string[]
): boolean {
  return providerDomains.some((pattern) =>
    domainMatchesPattern(domain, pattern)
  );
}

export async function retry<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 1000
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (attempt === maxRetries) break;

      const delay = baseDelay * Math.pow(2, attempt);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  throw lastError!;
}