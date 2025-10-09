import {
  matchesDomain,
  getTodayDate,
  generateId,
  isValidUrl,
  extractDomainFromUrl,
  calculateFootprint,
  formatNumber,
  domainMatchesPattern,
  shouldTrackDomain,
} from '../src/common/util';

describe('Utility Functions', () => {
  describe('matchesDomain', () => {
    it('should match exact domain (lowercase)', () => {
      expect(matchesDomain('https://chatgpt.com/api', 'chatgpt.com')).toBe(true);
      expect(matchesDomain('https://claude.ai/chat', 'claude.ai')).toBe(true);
    });

    it('should match exact domain (mixed case)', () => {
      expect(matchesDomain('https://ChatGPT.com/api', 'chatgpt.com')).toBe(true);
      expect(matchesDomain('https://CHATGPT.COM/api', 'chatgpt.com')).toBe(true);
      expect(matchesDomain('https://Claude.AI/chat', 'claude.ai')).toBe(true);
    });

    it('should match subdomains', () => {
      expect(matchesDomain('https://www.chatgpt.com/api', 'chatgpt.com')).toBe(true);
      expect(matchesDomain('https://api.chatgpt.com/v1', 'chatgpt.com')).toBe(true);
      expect(matchesDomain('https://subdomain.claude.ai/chat', 'claude.ai')).toBe(true);
    });

    it('should reject fake domains', () => {
      expect(matchesDomain('https://fakechatgpt.com', 'chatgpt.com')).toBe(false);
      expect(matchesDomain('https://notchatgpt.com', 'chatgpt.com')).toBe(false);
      expect(matchesDomain('https://mychatgpt.com', 'chatgpt.com')).toBe(false);
      expect(matchesDomain('https://chatgpt.com.example.com', 'chatgpt.com')).toBe(false);
    });

    it('should reject query param tricks', () => {
      expect(matchesDomain('https://evil.com?url=chatgpt.com', 'chatgpt.com')).toBe(false);
      expect(matchesDomain('https://phishing.net?redirect=claude.ai', 'claude.ai')).toBe(false);
    });

    it('should reject subdomain attacks', () => {
      expect(matchesDomain('https://chatgpt.com.evil.net', 'chatgpt.com')).toBe(false);
      expect(matchesDomain('https://claude.ai.phishing.com', 'claude.ai')).toBe(false);
    });

    it('should handle invalid URLs', () => {
      expect(matchesDomain('not-a-url', 'chatgpt.com')).toBe(false);
      expect(matchesDomain('', 'chatgpt.com')).toBe(false);
      expect(matchesDomain('javascript:alert(1)', 'chatgpt.com')).toBe(false);
    });

    it('should handle URLs with ports', () => {
      expect(matchesDomain('https://chatgpt.com:443/api', 'chatgpt.com')).toBe(true);
      expect(matchesDomain('http://localhost:3000', 'localhost')).toBe(true);
    });

    it('should handle URLs with paths and fragments', () => {
      expect(matchesDomain('https://chatgpt.com/backend-api/conversation', 'chatgpt.com')).toBe(true);
      expect(matchesDomain('https://claude.ai/chat/new#model', 'claude.ai')).toBe(true);
    });
  });

  describe('getTodayDate', () => {
    it('should return date in YYYY-MM-DD format', () => {
      const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
      expect(getTodayDate()).toMatch(dateRegex);
    });
  });

  describe('generateId', () => {
    it('should generate a string id', () => {
      const id = generateId();
      expect(typeof id).toBe('string');
      expect(id.length).toBeGreaterThan(0);
    });

    it('should generate unique ids', () => {
      const id1 = generateId();
      const id2 = generateId();
      expect(id1).not.toBe(id2);
    });
  });

  describe('isValidUrl', () => {
    it('should return true for valid URLs', () => {
      expect(isValidUrl('https://api.openai.com')).toBe(true);
      expect(isValidUrl('http://localhost:3000')).toBe(true);
      expect(isValidUrl('https://api.example.com/v1/chat')).toBe(true);
    });

    it('should return false for invalid URLs', () => {
      expect(isValidUrl('not-a-url')).toBe(false);
      expect(isValidUrl('')).toBe(false);
      expect(isValidUrl('ftp://')).toBe(false);
    });
  });

  describe('extractDomainFromUrl', () => {
    it('should extract domain from valid URLs', () => {
      expect(extractDomainFromUrl('https://api.openai.com/v1/chat')).toBe('api.openai.com');
      expect(extractDomainFromUrl('http://localhost:3000')).toBe('localhost:3000');
      expect(extractDomainFromUrl('https://subdomain.example.com:8080/path')).toBe('subdomain.example.com:8080');
      expect(extractDomainFromUrl('https://example.com/path')).toBe('example.com');
    });

    it('should return empty string for invalid URLs', () => {
      expect(extractDomainFromUrl('not-a-url')).toBe('');
      expect(extractDomainFromUrl('')).toBe('');
    });
  });

  describe('calculateFootprint', () => {
    it('should calculate environmental footprint correctly', () => {
      const result = calculateFootprint(100, 0.001, 1.5, 2.0, 0.5);
      
      expect(result.kwh).toBeCloseTo(0.15, 10); // 100 * 0.001 * 1.5
      expect(result.waterLiters).toBeCloseTo(0.3, 10); // 0.15 * 2.0
      expect(result.co2Kg).toBeCloseTo(0.075, 10); // 0.15 * 0.5
    });

    it('should handle zero values', () => {
      const result = calculateFootprint(0, 0.001, 1.5, 2.0, 0.5);
      
      expect(result.kwh).toBe(0);
      expect(result.waterLiters).toBe(0);
      expect(result.co2Kg).toBe(0);
    });
  });

  describe('formatNumber', () => {
    it('should format numbers with default decimals', () => {
      expect(formatNumber(1.23456)).toBe('1.23');
      expect(formatNumber(0.001)).toBe('0.00');
    });

    it('should format numbers with custom decimals', () => {
      expect(formatNumber(1.23456, 3)).toBe('1.235');
      expect(formatNumber(1.23456, 0)).toBe('1');
    });
  });

  describe('domainMatchesPattern', () => {
    it('should match exact domains', () => {
      expect(domainMatchesPattern('api.openai.com', 'api.openai.com')).toBe(true);
      expect(domainMatchesPattern('example.com', 'example.com')).toBe(true);
    });

    it('should match wildcard patterns', () => {
      expect(domainMatchesPattern('api.openai.com', '*.openai.com')).toBe(true);
      expect(domainMatchesPattern('subdomain.example.com', '*.example.com')).toBe(true);
      expect(domainMatchesPattern('example.com', '*.example.com')).toBe(true);
    });

    it('should handle ports correctly', () => {
      expect(domainMatchesPattern('localhost:3000', 'localhost:3000')).toBe(true);
      expect(domainMatchesPattern('localhost:3000', 'localhost:8080')).toBe(false);
      expect(domainMatchesPattern('localhost:3000', 'localhost')).toBe(true); // Pattern without port matches any port;
      expect(domainMatchesPattern('api.example.com:8080', '*.example.com:8080')).toBe(true);
      expect(domainMatchesPattern('api.example.com:8080', '*.example.com')).toBe(true); // Pattern without port matches any port;
    });

    it('should not match incorrect patterns', () => {
      expect(domainMatchesPattern('api.openai.com', 'openai.com')).toBe(false);
      expect(domainMatchesPattern('example.com', '*.different.com')).toBe(false);
      expect(domainMatchesPattern('notexample.com', '*.example.com')).toBe(false);
    });
  });

  describe('shouldTrackDomain', () => {
    it('should return true if domain matches any pattern', () => {
      const domains = ['api.openai.com', '*.replicate.com', 'localhost:3000'];
      
      expect(shouldTrackDomain('api.openai.com', domains)).toBe(true);
      expect(shouldTrackDomain('api.replicate.com', domains)).toBe(true);
      expect(shouldTrackDomain('localhost:3000', domains)).toBe(true);
    });

    it('should return false if domain does not match any pattern', () => {
      const domains = ['api.openai.com', '*.replicate.com', 'localhost:3000'];
      
      expect(shouldTrackDomain('api.anthropic.com', domains)).toBe(false);
      expect(shouldTrackDomain('example.com', domains)).toBe(false);
      expect(shouldTrackDomain('localhost:8080', domains)).toBe(false);
    });
  });
});