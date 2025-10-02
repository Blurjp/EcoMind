import { ProviderManager } from '../src/bg/providers';

describe('ProviderManager', () => {
  let providerManager: ProviderManager;

  beforeEach(() => {
    providerManager = new ProviderManager();
  });

  describe('findProviderForUrl', () => {
    it('should find provider for known URLs', () => {
      const provider = providerManager.findProviderForUrl('https://api.openai.com/v1/chat');
      expect(provider).not.toBeNull();
      expect(provider?.name).toBe('openai');
    });

    it('should return null for unknown URLs', () => {
      const provider = providerManager.findProviderForUrl('https://unknown-api.com/v1/chat');
      expect(provider).toBeNull();
    });

    it('should find provider for wildcard domains', () => {
      const provider = providerManager.findProviderForUrl('https://api.replicate.com/v1/predictions');
      expect(provider).not.toBeNull();
      expect(provider?.name).toBe('replicate');
    });
  });

  describe('extractModel', () => {
    it('should extract model from OpenAI request', () => {
      const body = JSON.stringify({ model: 'gpt-4', messages: [] });
      const result = providerManager.extractModel('https://api.openai.com/v1/chat', body);
      
      expect(result.provider).toBe('openai');
      expect(result.model).toBe('gpt-4');
    });

    it('should extract model from Anthropic request', () => {
      const body = JSON.stringify({ model: 'claude-3-sonnet-20240229', messages: [] });
      const result = providerManager.extractModel('https://api.anthropic.com/v1/messages', body);
      
      expect(result.provider).toBe('anthropic');
      expect(result.model).toBe('claude-3-sonnet-20240229');
    });

    it('should extract model from Replicate URL', () => {
      const result = providerManager.extractModel('https://api.replicate.com/v1/models/meta/llama-2-70b-chat/predictions');
      
      expect(result.provider).toBe('replicate');
      expect(result.model).toBe('meta/llama-2-70b-chat');
    });

    it('should return unknown for invalid JSON body', () => {
      const result = providerManager.extractModel('https://api.openai.com/v1/chat', 'invalid json');
      
      expect(result.provider).toBe('openai');
      expect(result.model).toBe('unknown');
    });

    it('should return unknown for unknown provider', () => {
      const result = providerManager.extractModel('https://unknown-api.com/v1/chat');
      
      expect(result.provider).toBe('unknown');
      expect(result.model).toBe('unknown');
    });
  });

  describe('shouldTrackRequest', () => {
    it('should track requests to known providers', () => {
      expect(providerManager.shouldTrackRequest('https://api.openai.com/v1/chat')).toBe(true);
      expect(providerManager.shouldTrackRequest('https://api.anthropic.com/v1/messages')).toBe(true);
    });

    it('should not track requests to unknown providers', () => {
      expect(providerManager.shouldTrackRequest('https://unknown-api.com/v1/chat')).toBe(false);
      expect(providerManager.shouldTrackRequest('https://example.com')).toBe(false);
    });
  });

  describe('custom providers', () => {
    it('should add custom provider', () => {
      providerManager.addCustomProvider('custom', ['api.custom.com']);
      expect(providerManager.shouldTrackRequest('https://api.custom.com/v1/test')).toBe(true);
    });

    it('should update custom providers from settings', () => {
      const customDomains = ['api.custom1.com', '*.custom2.com', 'localhost:3000'];
      providerManager.updateCustomProviders(customDomains);
      
      expect(providerManager.shouldTrackRequest('https://api.custom1.com/test')).toBe(true);
      expect(providerManager.shouldTrackRequest('https://api.custom2.com/test')).toBe(true);
      expect(providerManager.shouldTrackRequest('https://sub.custom2.com/test')).toBe(true);
      expect(providerManager.shouldTrackRequest('http://localhost:3000/test')).toBe(true);
    });

    it('should handle empty custom domains', () => {
      providerManager.updateCustomProviders(['', '  ', 'api.valid.com']);
      expect(providerManager.shouldTrackRequest('https://api.valid.com/test')).toBe(true);
    });
  });

  describe('getAllDomains', () => {
    it('should return all provider domains', () => {
      const domains = providerManager.getAllDomains();
      expect(domains).toContain('api.openai.com');
      expect(domains).toContain('api.anthropic.com');
      expect(domains.length).toBeGreaterThan(5);
    });

    it('should include custom domains', () => {
      providerManager.addCustomProvider('test', ['api.test.com']);
      const domains = providerManager.getAllDomains();
      expect(domains).toContain('api.test.com');
    });
  });
});