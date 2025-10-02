# Ecomind - Quick Start Guide

**Enterprise AI Environmental Monitoring Platform**

All 12 phases complete! Here's how to get started.

---

## Prerequisites

- Docker + Docker Compose
- Go 1.22+
- Python 3.12+
- Node 20+
- pnpm (for workspace management)

---

## 1. Start Infrastructure

```bash
# Start Postgres, Redis, Redpanda
docker-compose -f docker-compose.dev.yml up postgres redis redpanda -d

# Verify services are healthy
docker-compose -f docker-compose.dev.yml ps
```

---

## 2. Seed Database

```bash
cd api
pip install uv
uv pip install -e .
python -m app.seed
```

Expected output:
```
🌱 Creating database schema...
✅ Schema created
✅ Seeded:
  - Org: org_demo (Demo Organization)
  - User: user_alice (alice@demo.ecomind.example, ADMIN)
  - User: user_bob (bob@demo.ecomind.example, ANALYST)
```

---

## 3. Start Gateway (Terminal 1)

```bash
cd gateway
go mod download
go build -o bin/gateway ./cmd/gateway

export KAFKA_BROKERS=localhost:9092
export REDIS_ADDR=localhost:6379
./bin/gateway
```

Gateway runs on **http://localhost:8080**

---

## 4. Start API (Terminal 2)

```bash
cd api
uv pip install -e .

export DATABASE_URL=postgresql://ecomind:ecomind_dev_pass@localhost:5432/ecomind
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API runs on **http://localhost:8000**

Docs: **http://localhost:8000/docs** (Swagger UI)

---

## 5. Start Worker (Terminal 3)

```bash
cd worker
uv pip install -e .

export KAFKA_BROKERS=localhost:9092
export DATABASE_URL=postgresql://ecomind:ecomind_dev_pass@localhost:5432/ecomind
python -m worker.main
```

Worker listens to Kafka, enriches events, writes to DB.

---

## 6. Start UI (Terminal 4)

```bash
cd ui
npm install

export NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

UI runs on **http://localhost:3000**

---

## 7. Test Ingestion

**Send test event:**

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
    "region": "US-CAISO"
  }'
```

**Expected Response** (202 Accepted):
```json
{
  "status": "accepted",
  "ts": "2025-09-30T12:34:56Z"
}
```

**Check Worker Logs** (Terminal 3):
```
Processing event: org=org_demo, provider=openai
✅ Stored: org_demo/user_alice, openai/gpt-4o, kWh=0.000750, CO2=0.000165
```

---

## 8. Query Data

**Today's aggregates:**

```bash
curl "http://localhost:8000/v1/today?org_id=org_demo&user_id=user_alice"
```

**Response:**
```json
{
  "date": "2025-09-30",
  "org_id": "org_demo",
  "user_id": "user_alice",
  "call_count": 1,
  "kwh": 0.00075,
  "water_liters": 0.00135,
  "co2_kg": 0.000165,
  "top_providers": [{"provider": "openai", "count": 1}],
  "top_models": [{"model": "gpt-4o", "count": 1}]
}
```

---

## 9. View Dashboard

Open **http://localhost:3000** in browser.

Dashboard shows:
- API calls today
- Energy (kWh)
- Water (L)
- CO₂ (kg)
- Top providers/models
- 7-day trend chart

---

## 10. Use SDKs

### TypeScript

```typescript
import { EcomindClient } from '@ecomind/sdk';

const client = new EcomindClient({
  apiKey: 'demo',
  baseUrl: 'http://localhost:8080',
  orgId: 'org_demo',
  userId: 'user_alice',
});

await client.track({
  provider: 'anthropic',
  model: 'claude-3-sonnet',
  tokensIn: 200,
  tokensOut: 100,
});
```

### Python

```python
from ecomind_sdk import EcomindClient

with EcomindClient(
    api_key="demo",
    base_url="http://localhost:8080",
    org_id="org_demo",
    user_id="user_alice",
) as client:
    client.track(
        provider="openai",
        model="gpt-4o",
        tokens_in=150,
        tokens_out=75,
        region="US-CAISO",
    )
```

---

## 11. Build Extension

```bash
cd ext-chrome
npm install
npm run build

# Load unpacked extension in Chrome:
# 1. Go to chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select ext-chrome/dist/
```

Extension tracks AI API calls in browser and sends to backend.

---

## 12. Run with Docker Compose (All Services)

```bash
# Build and start everything
make dev

# Or manually:
docker-compose -f docker-compose.dev.yml up --build
```

All services run together:
- Gateway: localhost:8080
- API: localhost:8000
- UI: localhost:3000
- Postgres: localhost:5432
- Redis: localhost:6379
- Redpanda: localhost:9092

---

## 13. Create Alerts

```bash
curl -X POST http://localhost:8000/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "org_demo",
    "name": "High CO2 Alert",
    "metric": "co2_kg",
    "threshold": 1.0,
    "window": "1d",
    "channel": "slack",
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }'
```

---

## 14. Generate Report

```bash
curl -X POST http://localhost:8000/v1/reports \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "org_demo",
    "report_type": "esg",
    "format": "csv",
    "from_date": "2025-09-01",
    "to_date": "2025-09-30"
  }'
```

Returns job ID. Poll `/v1/reports/{id}` for status.

---

## 15. Load Testing

```bash
# Install k6
brew install k6  # macOS
# or download from https://k6.io

# Run load test
k6 run ops/scripts/loadtest.js

# Target 100 concurrent users, measure RPS and latency
```

---

## Project Structure

```
ecomind/
├── gateway/         # Go HTTP/gRPC ingestion service
├── api/             # Python FastAPI (REST/gRPC)
├── worker/          # Python Kafka consumer (enrichment)
├── ui/              # Next.js dashboard
├── ext-chrome/      # Chrome MV3 extension
├── sdks/            # TypeScript & Python SDKs
│   ├── ts/
│   └── python/
├── infra/           # Terraform (AWS) + Helm (K8s)
├── ops/             # Grafana dashboards, Prom config, load tests
├── docs/            # API, Architecture, Privacy, DPA
├── docker-compose.dev.yml
├── Makefile
└── README.md
```

---

## Key Endpoints

| Service | Endpoint | Purpose |
|---------|----------|---------|
| Gateway | POST /v1/ingest | Ingest events |
| API | GET /v1/today | Today's usage |
| API | GET /v1/aggregate/daily | Daily aggregates |
| API | POST /v1/orgs | Create organization |
| API | POST /v1/users | Create user |
| API | POST /v1/alerts | Create alert |
| API | POST /v1/reports | Generate report |
| API | GET /v1/audits | Audit logs |
| UI | http://localhost:3000 | Dashboard |

---

## Troubleshooting

**Gateway won't start:**
- Check Kafka/Redis are running: `docker-compose ps`
- Verify ports not in use: `lsof -i :8080`

**Worker not processing:**
- Check Kafka topic exists: `docker exec -it <redpanda_container> rpk topic list`
- Create topic if missing: `rpk topic create events.raw`

**UI shows no data:**
- Verify API is accessible: `curl http://localhost:8000/health`
- Check browser console for CORS errors
- Ensure `NEXT_PUBLIC_API_URL` is set

**Database errors:**
- Run seed again: `python -m app.seed`
- Check Postgres logs: `docker logs <postgres_container>`

---

## Next Steps

1. **Configure SSO**: Update `api/app/auth.py` with Auth0/Okta credentials
2. **Add Observability**: Implement Prometheus metrics in gateway/API/worker
3. **Deploy to AWS**: Use `infra/terraform` and `infra/helm`
4. **Enable Alerts**: Add Slack/Teams webhook URLs
5. **Generate Reports**: Implement PDF generation in worker
6. **Write Tests**: Add unit and integration tests

---

## Documentation

- **API**: [docs/API.md](docs/API.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Privacy**: [docs/PRIVACY.md](docs/PRIVACY.md)
- **DPA**: [docs/DPA_TEMPLATE.md](docs/DPA_TEMPLATE.md)
- **Build Status**: [docs/BUILD_STATUS.md](docs/BUILD_STATUS.md)

---

## Support

- GitHub: [github.com/ecomind/ecomind](https://github.com/ecomind/ecomind)
- Issues: [github.com/ecomind/ecomind/issues](https://github.com/ecomind/ecomind/issues)
- Email: support@ecomind.example.com

---

**Built with ❤️ for a sustainable AI future.**