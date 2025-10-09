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
    describe('OpenAI', () => {
      it('should extract model from API request body', () => {
        const body = JSON.stringify({ model: 'gpt-4', messages: [] });
        const result = providerManager.extractModel('https://api.openai.com/v1/chat', body);

        expect(result.provider).toBe('openai');
        expect(result.model).toBe('gpt-4');
      });

      it('should detect chatgpt-web from chatgpt.com URL (lowercase)', () => {
        const result = providerManager.extractModel('https://chatgpt.com/backend-api/conversation', undefined);

        expect(result.provider).toBe('openai');
        expect(result.model).toBe('chatgpt-web');
      });

      it('should detect chatgpt-web from chatgpt.com URL (mixed case)', () => {
        const result = providerManager.extractModel('https://ChatGPT.com/backend-api/conversation', undefined);

        expect(result.provider).toBe('openai');
        expect(result.model).toBe('chatgpt-web');
      });

      it('should detect chatgpt-web from www.chatgpt.com subdomain', () => {
        const result = providerManager.extractModel('https://www.chatgpt.com/api', undefined);

        expect(result.provider).toBe('openai');
        expect(result.model).toBe('chatgpt-web');
      });

      it('should detect chatgpt-web from chat.openai.com', () => {
        const result = providerManager.extractModel('https://chat.openai.com/backend-api/conversation', undefined);

        expect(result.provider).toBe('openai');
        expect(result.model).toBe('chatgpt-web');
      });

      it('should NOT detect chatgpt-web from fake domains', () => {
        const result = providerManager.extractModel('https://fakechatgpt.com/api', undefined);

        expect(result.provider).toBe('unknown');
        expect(result.model).toBe('unknown');
      });

      it('should prefer body model over URL fallback', () => {
        const body = JSON.stringify({ model: 'gpt-4-turbo', messages: [] });
        const result = providerManager.extractModel('https://chatgpt.com/api', body);

        expect(result.provider).toBe('openai');
        expect(result.model).toBe('gpt-4-turbo'); // Body wins
      });
    });

    describe('Anthropic', () => {
      it('should extract model from API request body', () => {
        const body = JSON.stringify({ model: 'claude-3-sonnet-20240229', messages: [] });
        const result = providerManager.extractModel('https://api.anthropic.com/v1/messages', body);

        expect(result.provider).toBe('anthropic');
        expect(result.model).toBe('claude-3-sonnet-20240229');
      });

      it('should detect claude-web from claude.ai URL', () => {
        const result = providerManager.extractModel('https://claude.ai/chat/new', undefined);

        expect(result.provider).toBe('anthropic');
        expect(result.model).toBe('claude-web');
      });

      it('should detect claude-web from claude.ai (mixed case)', () => {
        const result = providerManager.extractModel('https://Claude.AI/api', undefined);

        expect(result.provider).toBe('anthropic');
        expect(result.model).toBe('claude-web');
      });

      it('should NOT detect claude-web from fake domains', () => {
        const result = providerManager.extractModel('https://fakeclaude.ai/api', undefined);

        expect(result.provider).toBe('unknown');
        expect(result.model).toBe('unknown');
      });
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