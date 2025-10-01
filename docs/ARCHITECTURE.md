# Ecomind Architecture

## System Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Browser   │────▶│   Gateway    │────▶│  Redpanda   │
│  Extension  │     │     (Go)     │     │   (Kafka)   │
└─────────────┘     └──────────────┘     └─────────────┘
                                                 │
┌─────────────┐     ┌──────────────┐            │
│  SDK (TS)   │────▶│   Gateway    │            │
└─────────────┘     └──────────────┘            ▼
                                         ┌──────────────┐
┌─────────────┐     ┌──────────────┐    │    Worker    │
│ SDK (Python)│────▶│   Gateway    │    │   (Python)   │
└─────────────┘     └──────────────┘    └──────────────┘
                                                 │
                                                 ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│     UI      │────▶│     API      │────▶│  PostgreSQL │
│  (Next.js)  │     │  (FastAPI)   │     │ (TimescaleDB)│
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    Redis    │
                    └─────────────┘
```

## Component Responsibilities

### Gateway (Go)
- High-throughput HTTP/gRPC ingestion
- Request validation (org_id, user_id, schema)
- HMAC/JWT auth
- Emit events to Kafka
- Rate limiting per org/plan
- Metrics: RPS, latency, error rate

### API (Python FastAPI)
- REST/gRPC for queries
- CRUD: orgs, users, teams, alerts, factors
- Auth: SSO (OIDC/SAML), API keys, JWT
- RBAC enforcement
- Audit log writes
- Async job creation (reports)
- OpenAPI spec

### Worker (Python)
- Kafka consumers (events.raw → events.enriched)
- Enrichment: model lookup, factor merge, grid intensity
- Compute: kWh, water_l, co2_kg
- Aggregation: daily rollups (org, user, provider, model)
- Alert evaluation and notification dispatch
- Report generation (PDF/CSV)

### UI (Next.js)
- Dashboard: charts (Recharts), tables
- Pages: orgs, users, teams, alerts, factors, reports, audits
- RBAC guards per route
- SSO login flow
- Settings management

### Extension (Chrome MV3)
- Intercept requests to AI provider domains
- Extract metadata (provider, model from URL)
- Local storage + badge count
- Optional telemetry to gateway
- Options page for config

### SDKs (TypeScript, Python)
- Thin wrappers around POST /v1/ingest
- Retry/backoff logic
- Helpers to wrap OpenAI/Anthropic clients

## Data Flow

1. **Ingest**: SDK/Extension → Gateway → Kafka (`events.raw`)
2. **Enrich**: Worker consumes `events.raw`, enriches, writes to `events.enriched` topic and DB
3. **Aggregate**: Worker consumes `events.enriched`, updates daily rollup tables
4. **Query**: UI/API query daily rollup tables for fast reads
5. **Alert**: Worker checks thresholds, sends notifications
6. **Report**: Async job queries aggregates, generates PDF/CSV, uploads to S3

## Database Schema

```sql
-- Core entities
orgs (id, name, plan, created_at)
users (id, org_id, email, name, role, created_at)
teams (id, org_id, name)
team_members (team_id, user_id)
api_keys (id, org_id, user_id, key_hash, scopes, created_at)

-- Events
events_raw (id, org_id, user_id, provider, model, tokens_in, tokens_out, region, ts, metadata)
events_enriched (id, org_id, user_id, provider, model, kwh, water_l, co2_kg, ts)

-- Aggregates (hypertables)
daily_org_agg (date, org_id, call_count, kwh, water_l, co2_kg)
daily_user_agg (date, org_id, user_id, call_count, kwh, water_l, co2_kg)
daily_provider_agg (date, org_id, provider, call_count, kwh, water_l, co2_kg)
daily_model_agg (date, org_id, provider, model, call_count, kwh, water_l, co2_kg)

-- Configuration
factors_defaults (provider, model, kwh_per_call, pue, water_l_per_kwh, co2_kg_per_kwh)
factors_overrides (id, org_id, provider, model, kwh_per_call, ...)
grid_intensity (region, date, gco2_per_kwh)

-- Alerts
alerts (id, org_id, metric, threshold, window, channel, webhook_url, created_at)
notifications (id, alert_id, ts, message, status)

-- Admin
audit_logs (id, org_id, user_id, action, resource, ts, details)
billing_customers (id, org_id, stripe_customer_id, plan, created_at)
invoices (id, org_id, stripe_invoice_id, amount, status, ts)
```

## Scalability Considerations

- **Gateway**: Horizontal scaling via load balancer; stateless
- **Worker**: Multiple consumers with Kafka consumer groups
- **API**: Horizontal scaling; Redis for session/cache
- **Postgres**: Read replicas for query endpoints; TimescaleDB compression
- **Kafka**: Partitioning by org_id for parallelism

## Security

- TLS everywhere
- JWT for user auth, HMAC for API keys
- Row-level security (RLS) in Postgres by org_id
- Secrets in AWS Secrets Manager
- Rate limiting per org

## Observability

- **Traces**: OpenTelemetry (OTLP) → Jaeger/Tempo
- **Metrics**: Prometheus scrape `/metrics`
- **Logs**: Structured JSON to stdout
- **Dashboards**: Grafana (pre-built)

## Deployment

- **Local**: docker-compose.dev.yml
- **Production**: Helm charts on EKS
- **Infra**: Terraform for AWS (VPC, EKS, RDS, MSK, S3)