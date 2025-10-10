# 🌱 Ecomind – Enterprise AI Environmental Monitoring Platform

> **Status**: Development - No CI/CD pipeline configured yet

**Centralized, multi-tenant monitoring for AI/compute usage with energy, water, and CO₂ footprint tracking.**

## Overview

Ecomind is an enterprise-grade platform that provides:

- **Centralized Monitoring**: Track AI API calls across your organization
- **Environmental Impact**: Convert usage to kWh, liters of water, and kgCO₂ using regional grid factors
- **Multi-Tenant**: Organizations, teams, users with RBAC
- **Privacy-First**: Never log prompts or completions, only metadata
- **Real-Time Alerts**: Slack/Teams/Webhook notifications for thresholds
- **ESG Reporting**: Generate PDF/CSV reports for compliance
- **SSO/SAML/OIDC**: Enterprise auth with audit logs
- **SDKs + Extension**: Easy integration via REST/gRPC, TypeScript/Python SDKs, and browser extension

## Architecture

**Monorepo** with:

- **Gateway** (Go) – High-throughput ingestion → Kafka/Redpanda
- **API** (Python FastAPI) – REST/gRPC for queries, admin, billing
- **Worker** (Python) – Event enrichment, aggregation, alerts
- **UI** (Next.js) – Dashboards, settings, reports
- **Extension** (Chrome MV3) – Browser tracking with optional backend sync
- **SDKs** (TypeScript, Python) – Client libraries
- **Infra** (Terraform + Helm) – AWS EKS, RDS, MSK, S3

**Data Plane**:
- Queue: Redpanda/Kafka
- DB: PostgreSQL + TimescaleDB
- Cache: Redis
- Storage: S3
- Observability: OpenTelemetry, Prometheus, Grafana

## Quick Start

### Local Development

**Prerequisites**: Docker, pnpm, Go 1.22+, Python 3.12+, Node 20+

```bash
# 1. Clone and install
git clone <repo>
cd ecomind
pnpm install

# 2. Start all services
make dev

# Services:
# - Gateway:  http://localhost:8080
# - API:      http://localhost:8000
# - UI:       http://localhost:3000
# - Postgres: localhost:5432
# - Redis:    localhost:6379
# - Redpanda: localhost:9092
```

### Seed Data

```bash
make seed
```

### Test Ingestion

```bash
curl -X POST http://localhost:8080/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "org_demo",
    "user_id": "user_alice",
    "provider": "openai",
    "model": "gpt-4o",
    "tokens_in": 100,
    "tokens_out": 50,
    "region": "US-CAISO",
    "ts": "2025-09-30T12:00:00Z"
  }'
```

### Query Aggregates

```bash
curl "http://localhost:8000/v1/today?org_id=org_demo&user_id=user_alice"
```

### Load UI

Open http://localhost:3000

## Project Structure

```
ecomind/
├── gateway/          # Go ingestion service
├── api/              # Python FastAPI (REST/gRPC)
├── worker/           # Python event consumers
├── ui/               # Next.js dashboard
├── ext-chrome/       # Chrome MV3 extension
├── sdks/
│   ├── ts/           # TypeScript SDK
│   └── python/       # Python SDK
├── infra/
│   ├── terraform/    # AWS infrastructure
│   └── helm/         # Kubernetes charts
├── ops/              # Runbooks, Grafana dashboards, load tests
├── docs/             # Architecture, API, Privacy, DPA
├── docker-compose.dev.yml
├── Makefile
├── pnpm-workspace.yaml
└── README.md
```

## APIs

### Ingestion

**POST /v1/ingest**
```json
{
  "org_id": "org_123",
  "user_id": "user_abc",
  "provider": "openai|anthropic|cohere|selfhost",
  "model": "gpt-4o",
  "tokens_in": 0,
  "tokens_out": 0,
  "region": "US-CAISO",
  "ts": "2025-09-30T12:00:00Z"
}
```

### Query

- `GET /v1/today?org_id=X&user_id=Y`
- `GET /v1/aggregate/daily?org_id=X&from=...&to=...&group_by=provider|model|user`
- `GET /v1/factors` – View merged default + override factors
- `POST /v1/reports/esg` – Generate async ESG report (PDF/CSV)

### Admin

- `POST /v1/orgs`, `POST /v1/orgs/{id}/users`, `POST /v1/teams`
- `POST /v1/factors/overrides` – Set org-specific factors
- `POST /v1/alerts` – Create threshold alerts
- `GET /v1/audits` – Audit logs

**Full API Docs**: See [docs/API.md](docs/API.md) and [OpenAPI spec](api/openapi.yaml)

## SDKs

### TypeScript

```bash
npm install @ecomind/sdk
```

```typescript
import { EcomindClient } from '@ecomind/sdk';

const client = new EcomindClient({
  apiKey: 'ek_...',
  baseUrl: 'https://api.ecomind.example.com',
  orgId: 'org_123',
  userId: 'user_abc'
});

await client.track({
  provider: 'openai',
  model: 'gpt-4o',
  tokensIn: 100,
  tokensOut: 50
});
```

### Python

```bash
pip install ecomind-sdk
```

```python
from ecomind_sdk import EcomindClient

client = EcomindClient(
    api_key="ek_...",
    base_url="https://api.ecomind.example.com",
    org_id="org_123",
    user_id="user_abc"
)

client.track(
    provider="anthropic",
    model="claude-3-sonnet",
    tokens_in=200,
    tokens_out=100
)
```

## Browser Extension

Located in `ext-chrome/`. See [ext-chrome/README.md](ext-chrome/README.md).

**Install**:
1. `cd ext-chrome && npm install && npm run build`
2. Load unpacked from `ext-chrome/dist/` in Chrome

**Features**:
- Local tracking or backend sync
- Privacy-first (no prompt logging)
- Custom provider domains
- Configurable environmental factors

## RBAC & Auth

**Roles** (per org):
- **Owner**: Full control
- **Admin**: Manage users, teams, factors, alerts
- **Analyst**: View dashboards, reports
- **Viewer**: Read-only
- **Billing**: Manage billing

**SSO**: OIDC/SAML via Auth0/Okta (configurable). Fallback: magic link.

**API Keys**: HMAC or PAT for server-to-server.

## Alerts

Configure thresholds:
```json
{
  "org_id": "org_123",
  "metric": "co2_kg",
  "threshold": 10.0,
  "window": "1d",
  "channel": "slack",
  "webhook_url": "https://hooks.slack.com/..."
}
```

Supported channels: Slack, Teams, Webhook, Email.

## Environmental Factors

**Defaults** (global):
- kWh per call, PUE, water L/kWh, CO₂ kg/kWh per provider/model

**Overrides** (org-level):
- Custom factors for specific models or regions
- Grid intensity by region code (e.g., `US-CAISO`, `EU-DE`)

**Data sources**:
- Model energy: Research papers, provider specs
- Grid CO₂: Real-time APIs (e.g., ElectricityMaps) or static tables

## Reports

Generate ESG reports:
```bash
curl -X POST http://localhost:8000/v1/reports/esg \
  -H "Authorization: Bearer ek_..." \
  -d '{"org_id":"org_123","from":"2025-01-01","to":"2025-12-31","format":"pdf"}'
```

Returns: `{"job_id":"...", "status":"pending"}`

Poll or webhook when ready → download from S3.

## Observability

- **Traces**: OpenTelemetry → Jaeger/Tempo
- **Metrics**: Prometheus (scrape `/metrics`)
- **Logs**: JSON to stdout
- **Dashboards**: Grafana (pre-built in `ops/grafana/`)

## Infrastructure

**AWS** (via Terraform):
- EKS cluster
- RDS PostgreSQL (TimescaleDB)
- MSK or Redpanda self-managed
- ElastiCache Redis
- S3 for exports
- CloudFront for UI

**Deploy**:
```bash
cd infra/terraform
terraform init
terraform apply
```

**Helm** (Kubernetes):
```bash
cd infra/helm
helm install ecomind ./ecomind-chart
```

## CI/CD

GitHub Actions workflows in `.github/workflows/`:
- `test.yml` – Run tests on PRs
- `build.yml` – Build Docker images
- `deploy.yml` – Deploy to dev/stage/prod

## Development

### Commands

```bash
make dev        # Start local stack
make build      # Build all services
make test       # Run tests
make lint       # Lint code
make seed       # Seed DB
make loadtest   # k6 load tests
make clean      # Clean up
```

### Environment Variables

Copy `.env.example` to `.env` and configure:
- `DATABASE_URL`
- `KAFKA_BROKERS`
- `REDIS_URL`
- `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`
- `STRIPE_SECRET_KEY`
- `S3_BUCKET`

## Testing

```bash
# Unit tests
cd api && pytest
cd worker && pytest
cd gateway && go test ./...

# Integration tests (requires docker-compose up)
pytest tests/integration/

# Load tests
make loadtest
```

## Security

- HTTPS/TLS everywhere
- JWT for auth
- HMAC for API keys
- Row-level security (RLS) in Postgres
- Secrets via AWS Secrets Manager
- Audit logs for all admin actions
- CSP headers on UI

## Privacy

- **No prompt/completion logging**
- Metadata only: timestamps, provider, model, token counts
- Local-only mode in extension
- Data retention policies (configurable per org)
- GDPR/DPA templates in `docs/`

See [PRIVACY.md](docs/PRIVACY.md) for full policy.

## Billing

Stripe integration:
- Plans: Free (10k calls/mo), Pro (1M calls/mo), Enterprise (custom)
- Rate limits per plan
- Webhooks for payment events
- Admin UI for plan management

## Roadmap

- [ ] Real-time streaming dashboards
- [ ] Mobile apps (React Native)
- [ ] More cloud providers (Azure, GCP)
- [ ] Carbon credit purchase integration
- [ ] Team-level budgets and quotas

## License

Proprietary – All rights reserved

## Support

For support inquiries, please contact:
- Email: support@ecomind.biz
- Website: https://ecomind.ai

---

**Built with ❤️ for a sustainable AI future.**