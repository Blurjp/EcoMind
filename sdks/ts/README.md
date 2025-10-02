# @ecomind/sdk (TypeScript)

Official TypeScript SDK for Ecomind API.

## Installation

```bash
npm install @ecomind/sdk
```

## Usage

```typescript
import { EcomindClient } from '@ecomind/sdk';

const client = new EcomindClient({
  apiKey: 'ek_...',
  baseUrl: 'https://api.ecomind.example.com',
  orgId: 'org_123',
  userId: 'user_abc',
});

// Track event
await client.track({
  provider: 'openai',
  model: 'gpt-4o',
  tokensIn: 100,
  tokensOut: 50,
  region: 'US-CAISO',
});

// Get today's data
const today = await client.getToday();
console.log(today.kwh, today.co2_kg);
```

## Development

```bash
npm run build
npm test
```