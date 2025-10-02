# Enterprise Mode Setup Guide

**Goal**: Send usage metrics from all employees to a centralized dashboard

---

## Architecture Overview

```
┌─────────────────────┐
│  Employee Browser   │
│  (Chrome Extension) │
│                     │
│  ┌───────────────┐  │
│  │ Local Count:  │  │     HTTP POST
│  │     Badge     │  │────────────────┐
│  └───────────────┘  │                │
│                     │                ▼
│  ┌───────────────┐  │    ┌──────────────────────┐
│  │ Telemetry:    │  │    │   Your Backend API   │
│  │   Enabled     │  │    │  (Gateway/FastAPI)   │
│  └───────────────┘  │    └──────────┬───────────┘
└─────────────────────┘               │
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │    Kafka/Redpanda    │
                          │  (Event Streaming)   │
                          └──────────┬───────────┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │   Worker (Python)    │
                          │  (Aggregation)       │
                          └──────────┬───────────┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │  PostgreSQL/Redis    │
                          │  (Centralized Data)  │
                          └──────────┬───────────┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │   Dashboard (UI)     │
                          │  (Grafana/Next.js)   │
                          └──────────────────────┘
```

---

## Part 1: Extension Configuration (End Users)

### Option A: Pre-configured Extension (Recommended for Enterprise)

**For IT Admins**: Deploy pre-configured extension to all employees

1. **Edit manifest.json** before deployment:
```json
{
  "name": "Ecomind - YourCompany",
  "default_settings": {
    "baseUrl": "https://ecomind.yourcompany.com",
    "telemetryEnabled": true,
    "privacyLocalOnly": false
  }
}
```

2. **Create managed policy** (Chrome Enterprise):
```json
// managed_storage.json
{
  "ecomind_settings": {
    "baseUrl": "https://ecomind.yourcompany.com",
    "userId": "{employee_email}",  // Auto-populated from AD/SSO
    "telemetryEnabled": true,
    "privacyLocalOnly": false,
    "customProviders": ["internal-ai.yourcompany.com"]
  }
}
```

3. **Deploy via Chrome Enterprise**:
   - Go to Google Admin Console
   - Apps → Web and Mobile Apps → Chrome Web Store
   - Add Ecomind extension
   - Configure managed settings (auto-applies to all users)

### Option B: Manual Configuration (Small Teams)

**Each employee configures**:

1. Install Ecomind extension
2. Right-click extension icon → Options
3. Configure:
   - **Backend URL**: `https://ecomind.yourcompany.com`
   - **User ID**: `employee.email@company.com`
   - **Enable Telemetry**: ✓ ON
   - **Local-only Mode**: ✗ OFF
4. Click "Test Connection" → Should show "✓ Connected"
5. Click "Save Settings"

---

## Part 2: Backend Setup (IT/DevOps)

### Quick Start (Docker Compose)

**Already built!** The monorepo includes full backend:

```bash
# Clone the repo
git clone https://github.com/Blurjp/EcoMind.git
cd EcoMind

# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Services running:
# - Gateway (Go): http://localhost:8080
# - API (FastAPI): http://localhost:8000
# - Worker (Python): background processing
# - PostgreSQL: localhost:5432
# - Redpanda (Kafka): localhost:9092
# - Redis: localhost:6379
# - UI Dashboard: http://localhost:3000
```

**That's it!** Backend is running.

### Production Deployment

#### Option 1: AWS (Terraform - Automated)

```bash
cd infra/terraform

# Configure
cp terraform.tfvars.example terraform.tfvars
# Edit: domain, region, instance sizes

# Deploy
terraform init
terraform plan
terraform apply

# Outputs:
# - gateway_url: https://api.ecomind.yourcompany.com
# - dashboard_url: https://dashboard.ecomind.yourcompany.com
# - database_endpoint: <RDS endpoint>
```

**Provisions**:
- EKS cluster (Kubernetes)
- RDS PostgreSQL (with TimescaleDB)
- MSK (Kafka) or EC2 with Redpanda
- ElastiCache Redis
- S3 for exports
- CloudFront for UI
- ALB with TLS

#### Option 2: Kubernetes (Helm - Any Cloud)

```bash
cd infra/helm

# Configure
cp values.yaml values-prod.yaml
# Edit: domain, ingress, resource limits

# Deploy
helm install ecomind ./ecomind-chart \
  --namespace ecomind \
  --create-namespace \
  -f values-prod.yaml

# Get ingress URL
kubectl get ingress -n ecomind
```

**Works on**:
- AWS EKS
- Google GKE
- Azure AKS
- On-premise Kubernetes

#### Option 3: Manual VMs (Traditional)

**Requirements**: 4 VMs or 1 large server

**VM 1: Gateway** (Go)
```bash
# Install Go 1.21+
cd gateway
go build -o /usr/local/bin/ecomind-gateway ./cmd/gateway
systemctl start ecomind-gateway
```

**VM 2: API** (Python)
```bash
# Install Python 3.11+
cd api
pip install -e .
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**VM 3: Worker** (Python)
```bash
cd worker
pip install -e .
python -m worker.main
```

**VM 4: Infrastructure**
```bash
# PostgreSQL with TimescaleDB
docker run -d -p 5432:5432 timescale/timescaledb:latest-pg15

# Redpanda (Kafka)
docker run -d -p 9092:9092 vectorized/redpanda:latest

# Redis
docker run -d -p 6379:6379 redis:alpine
```

---

## Part 3: Configure Extension to Send Data

### Extension Settings (Per User)

**After backend is running**, configure extension:

1. **Backend URL**: `https://ecomind.yourcompany.com` (or `http://localhost:8080` for testing)
2. **User ID**: Employee's email or ID
3. **Enable Telemetry**: ✓ ON
4. **Privacy Mode**: ✗ OFF (allow sending to backend)

### What Gets Sent

**Extension sends on each API call**:

```json
POST https://ecomind.yourcompany.com/v1/ingest
Content-Type: application/json

{
  "user_id": "alice@company.com",
  "org_id": "yourcompany",  // Derived from backend
  "provider": "openai",
  "model": "gpt-4",
  "tokens_in": 0,   // Not captured in extension
  "tokens_out": 0,
  "region": "US",
  "ts": "2025-10-01T12:34:56Z"
}
```

**Privacy**: NO prompts, NO responses, only metadata!

---

## Part 4: Dashboard Setup

### Option A: Pre-built Next.js Dashboard

**Already included in the monorepo!**

```bash
cd ui
npm install
npm run build
npm start

# Open: http://localhost:3000
```

**Features**:
- Real-time metrics (today's usage)
- 7-day trends
- Provider/model breakdown
- Environmental impact (kWh, CO₂, water)
- Organization-wide view
- User drill-down

**Deploy**:
```bash
# Build for production
npm run build

# Deploy to Vercel/Netlify
vercel deploy

# Or Docker
docker build -t ecomind-ui .
docker run -p 3000:3000 ecomind-ui
```

### Option B: Grafana (Advanced Analytics)

**Pre-built dashboard included**: `ops/grafana/dashboard-overview.json`

```bash
# Start Grafana
docker run -d -p 3000:3000 grafana/grafana

# Add PostgreSQL data source:
# - Host: your-db-host:5432
# - Database: ecomind
# - User: ecomind_user
# - Password: <from setup>

# Import dashboard:
# 1. Go to Dashboards → Import
# 2. Upload ops/grafana/dashboard-overview.json
# 3. Select PostgreSQL data source
```

**Panels included**:
- Total API calls (gauge)
- Calls by provider (pie chart)
- Calls over time (time series)
- Top users (table)
- Environmental impact (bar chart)
- Cost estimation (calculated metric)

---

## Part 5: Database Schema (Already Created)

**The backend automatically creates these tables**:

### Core Tables

**organizations** - Company/team info
```sql
org_id VARCHAR PRIMARY KEY
name VARCHAR
plan_type VARCHAR (free/pro/enterprise)
created_at TIMESTAMP
```

**users** - Employee accounts
```sql
user_id VARCHAR PRIMARY KEY
org_id VARCHAR REFERENCES organizations
email VARCHAR
role VARCHAR (owner/admin/analyst/viewer)
```

**events** - Raw API call events
```sql
id BIGSERIAL PRIMARY KEY
org_id VARCHAR
user_id VARCHAR
provider VARCHAR (openai/anthropic/google)
model VARCHAR (gpt-4/claude-3-opus)
tokens_in INTEGER
tokens_out INTEGER
region VARCHAR
timestamp TIMESTAMPTZ
```

**daily_aggregates** - Pre-computed metrics
```sql
date DATE
org_id VARCHAR
user_id VARCHAR (optional)
call_count INTEGER
total_kwh FLOAT
total_water_l FLOAT
total_co2_kg FLOAT
PRIMARY KEY (date, org_id, user_id)
```

### Query Examples

**Today's company-wide usage**:
```sql
SELECT
  SUM(call_count) as total_calls,
  SUM(total_kwh) as total_kwh,
  SUM(total_co2_kg) as total_co2_kg
FROM daily_aggregates
WHERE org_id = 'yourcompany'
  AND date = CURRENT_DATE;
```

**Top users this week**:
```sql
SELECT
  user_id,
  SUM(call_count) as total_calls
FROM daily_aggregates
WHERE org_id = 'yourcompany'
  AND date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY user_id
ORDER BY total_calls DESC
LIMIT 10;
```

**Provider breakdown**:
```sql
SELECT
  provider,
  COUNT(*) as call_count
FROM events
WHERE org_id = 'yourcompany'
  AND timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY provider;
```

---

## Part 6: API Endpoints (Already Implemented)

### Ingest Endpoint (For Extension)

**POST /v1/ingest**
```bash
curl -X POST http://localhost:8080/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "yourcompany",
    "user_id": "alice@company.com",
    "provider": "openai",
    "model": "gpt-4",
    "tokens_in": 100,
    "tokens_out": 50,
    "region": "US-CAISO"
  }'
```

### Query Endpoints (For Dashboard)

**GET /v1/today?org_id=yourcompany**
```json
{
  "date": "2025-10-01",
  "call_count": 1247,
  "kwh": 0.623,
  "water_liters": 1.121,
  "co2_kg": 0.249,
  "top_providers": [
    {"provider": "openai", "count": 823},
    {"provider": "anthropic", "count": 312}
  ],
  "top_models": [
    {"model": "gpt-4", "count": 456},
    {"model": "claude-3-opus", "count": 234}
  ]
}
```

**GET /v1/aggregate/daily?org_id=yourcompany&days=7**
```json
{
  "aggregates": [
    {
      "date": "2025-10-01",
      "call_count": 1247,
      "kwh": 0.623,
      "co2_kg": 0.249
    },
    // ... 6 more days
  ]
}
```

**GET /v1/users?org_id=yourcompany**
```json
{
  "users": [
    {
      "user_id": "alice@company.com",
      "role": "admin",
      "today_calls": 145
    },
    // ... more users
  ]
}
```

---

## Part 7: Security & Compliance

### Authentication (Already Implemented)

**JWT Tokens**:
```python
# api/app/auth.py
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials):
    # Validate JWT token
    # Check org_id scope
    # Return user context
```

**API Key Auth** (Alternative):
```bash
curl -H "X-API-Key: your-org-api-key" \
  http://localhost:8000/v1/today?org_id=yourcompany
```

### RBAC (Already Implemented)

**Roles** (`api/app/models/user.py`):
- **Owner**: Full access, billing
- **Admin**: User management, settings
- **Analyst**: Read all data, export
- **Viewer**: Read own data only
- **Billing**: Invoices, usage reports

**Enforcement**:
```python
@app.get("/v1/users")
async def list_users(
    org_id: str,
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["owner", "admin"]:
        raise HTTPException(403, "Insufficient permissions")
    # ... return users
```

### Audit Logs (Already Implemented)

**All admin actions logged** (`api/app/models/audit.py`):
```sql
CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  org_id VARCHAR,
  user_id VARCHAR,
  action VARCHAR,  -- 'user.created', 'settings.updated'
  resource_type VARCHAR,
  resource_id VARCHAR,
  metadata JSONB,
  ip_address VARCHAR,
  timestamp TIMESTAMPTZ
);
```

---

## Part 8: Monitoring & Alerts

### Prometheus Metrics (Placeholders Exist)

**Gateway metrics** (`gateway/internal/metrics.go`):
```go
var (
  ingestTotal = prometheus.NewCounter(...)
  ingestDuration = prometheus.NewHistogram(...)
  kafkaErrors = prometheus.NewCounter(...)
)

// Expose at /metrics
http.Handle("/metrics", promhttp.Handler())
```

**Scrape config** (`ops/prom/prometheus.yml`):
```yaml
scrape_configs:
  - job_name: 'gateway'
    static_configs:
      - targets: ['gateway:8080']
  - job_name: 'api'
    static_configs:
      - targets: ['api:8000']
```

### Alert Rules (Create These)

**High error rate**:
```yaml
# alerts.yml
groups:
  - name: ecomind
    rules:
      - alert: HighIngestErrors
        expr: rate(ingest_errors_total[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High ingestion error rate"
```

### Notification Channels (Already Implemented)

**Slack/Teams webhooks** (`worker/worker/services/alerts.py`):
```python
async def send_alert(alert: Alert, channel: NotificationChannel):
    if channel.type == "slack":
        await post_to_slack(channel.webhook_url, {
            "text": f"🚨 Alert: {alert.name}",
            "attachments": [{
                "color": "danger",
                "text": f"Threshold exceeded: {alert.threshold}"
            }]
        })
```

---

## Part 9: Cost & Scaling

### Infrastructure Costs (Estimated)

**Small Team (10-50 users, ~10k calls/day)**:
- AWS t3.small instances (4x): $50/month
- RDS PostgreSQL (db.t3.small): $30/month
- ElastiCache Redis: $15/month
- Data transfer: $10/month
- **Total**: ~$105/month

**Medium Enterprise (100-500 users, ~100k calls/day)**:
- AWS t3.medium instances (4x): $150/month
- RDS PostgreSQL (db.t3.medium): $70/month
- MSK (Kafka): $200/month
- ElastiCache Redis: $30/month
- Data transfer: $50/month
- **Total**: ~$500/month

**Large Enterprise (1000+ users, ~1M calls/day)**:
- AWS c5.xlarge instances (8x): $1,200/month
- RDS PostgreSQL (db.r5.xlarge): $400/month
- MSK (Kafka): $500/month
- ElastiCache Redis (cache.r5.large): $150/month
- Data transfer: $200/month
- **Total**: ~$2,450/month

### Scaling Guidelines

**Gateway (10k RPS target)**:
- Horizontal: Add more instances behind ALB
- Auto-scale: CPU > 70% → add instance
- Kafka: Partition by org_id for parallel processing

**Database**:
- Read replicas for dashboard queries
- TimescaleDB compression for old data
- Partition tables by month (> 1B events)

**Worker**:
- Scale Kafka consumers (1 per partition)
- Async job queues for reports
- Redis for rate limiting

---

## Part 10: Quick Start Commands

### 1. Local Testing (Your Machine)

```bash
# Terminal 1: Start infrastructure
cd /path/to/EcoMind
docker-compose -f docker-compose.dev.yml up postgres redis redpanda -d

# Terminal 2: Start API
cd api
pip install -e .
python -m app.seed  # Create demo org
uvicorn app.main:app --port 8000 --reload

# Terminal 3: Start Gateway
cd gateway
go run ./cmd/gateway

# Terminal 4: Start Worker
cd worker
pip install -e .
python -m worker.main

# Terminal 5: Start UI
cd ui
npm install
npm run dev

# Configure extension:
# - Backend URL: http://localhost:8080
# - User ID: user_alice
# - Enable telemetry: ON
# - Privacy mode: OFF
```

### 2. Production Deployment (AWS)

```bash
# One-command deploy
cd infra/terraform
terraform init
terraform apply -auto-approve

# Get outputs
terraform output gateway_url     # → Configure in extension
terraform output dashboard_url   # → Share with team
```

### 3. Test Ingestion

```bash
# Send test event
curl -X POST http://localhost:8080/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "yourcompany",
    "user_id": "test@company.com",
    "provider": "openai",
    "model": "gpt-4",
    "tokens_in": 100,
    "tokens_out": 50
  }'

# Check dashboard
curl http://localhost:8000/v1/today?org_id=yourcompany
```

---

## Summary: Enterprise Mode Checklist

### Backend Setup
- [ ] Deploy infrastructure (Docker/K8s/Terraform)
- [ ] Configure database (PostgreSQL + TimescaleDB)
- [ ] Set up message queue (Kafka/Redpanda)
- [ ] Start services (Gateway, API, Worker, UI)
- [ ] Create organization: `POST /v1/orgs`
- [ ] Get backend URL (e.g., `https://ecomind.yourcompany.com`)

### Extension Configuration
- [ ] Set backend URL in extension options
- [ ] Set user ID (email or employee ID)
- [ ] Enable telemetry (turn ON)
- [ ] Disable privacy mode (turn OFF local-only)
- [ ] Test connection (should show ✓ Connected)
- [ ] Save settings

### Dashboard Access
- [ ] Open dashboard URL
- [ ] View real-time metrics
- [ ] Check aggregations
- [ ] Export reports

### Security
- [ ] Configure HTTPS/TLS
- [ ] Enable authentication (JWT/API keys)
- [ ] Set up RBAC roles
- [ ] Enable audit logging
- [ ] Configure alerts

**You're done!** All employee metrics now flow to centralized dashboard. 🎉

---

## Support

**Need help?**
- Architecture: See `/docs/ARCHITECTURE.md`
- API docs: See `/docs/API.md`
- Privacy: See `/docs/PRIVACY.md`
- Issues: https://github.com/Blurjp/EcoMind/issues
