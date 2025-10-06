describe('Domain Validation', () => {
  // Test the regex pattern used in options UI
  // Updated: Prevent trailing dots, double dots, leading/trailing hyphens
  // Explanation: [a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])? ensures segments start/end with alphanumeric
  // (\.[...])* allows multiple dot-separated segments, (\.[a-zA-Z]{2,})? allows optional TLD
  const domainRegex = /^(\*\.)?[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*(\.[a-zA-Z]{2,})?(:[0-9]{1,5})?$/;

  describe('Custom domain validation', () => {
    it('should accept standard domains', () => {
      expect('api.example.com').toMatch(domainRegex);
      expect('subdomain.api.example.com').toMatch(domainRegex);
      expect('api-v2.example.org').toMatch(domainRegex);
    });

    it('should accept wildcard domains', () => {
      expect('*.example.com').toMatch(domainRegex);
      expect('*.api.example.org').toMatch(domainRegex);
    });

    it('should accept domains with ports', () => {
      expect('localhost:3000').toMatch(domainRegex);
      expect('api.example.com:8080').toMatch(domainRegex);
      expect('127.0.0.1:5000').toMatch(domainRegex);
      expect('*.example.com:9000').toMatch(domainRegex);
    });

    it('should accept localhost variations', () => {
      expect('localhost').toMatch(domainRegex);
      expect('localhost:3000').toMatch(domainRegex);
      expect('127.0.0.1').toMatch(domainRegex);
      expect('192.168.1.100:8000').toMatch(domainRegex);
    });

    it('should reject invalid formats', () => {
      expect('').not.toMatch(domainRegex);
      expect('example .com').not.toMatch(domainRegex);
      expect('http://example.com').not.toMatch(domainRegex);
      expect('example@com').not.toMatch(domainRegex);
      expect('*.').not.toMatch(domainRegex);
    });

    it('should handle edge cases', () => {
      expect('a.co').toMatch(domainRegex); // Minimum valid domain
      expect('very-long-subdomain.very-long-domain.example.com').toMatch(domainRegex);
      expect('test.localhost').toMatch(domainRegex);
    });
  });
});