# Phase 4: Monitoring, Alerting & Integration Testing

**Phase ID**: P004
**Duration**: 2 weeks (10 business days)
**Priority**: MEDIUM (PRODUCTION RECOMMENDED)
**Owner**: Backend + QA Teams
**Status**: Design Review
**Dependencies**: P001, P002, P003 (requires complete infrastructure)

---

## 1. Executive Summary

Implement comprehensive monitoring, alerting, and integration testing to ensure system reliability, performance, and early detection of issues in production.

**Problem Statement:**
- **No Prometheus metrics exported** (gateway/cmd/gateway/main.go:191 missing `/metrics` route)
- No distributed tracing (no OpenTelemetry integration)
- No error aggregation (no Sentry/Datadog)
- No integration tests for backend services
- No SLO/SLA monitoring
- Blind to production issues (no real-time alerts)

**Success Criteria:**
- ✅ Prometheus metrics exported from all services
- ✅ Grafana dashboards for key metrics
- ✅ Alerts for critical issues (downtime, errors, performance)
- ✅ Integration tests covering 80%+ of API endpoints
- ✅ End-to-end tests (extension → gateway → kafka → worker → api)
- ✅ < 5 minutes MTTD (Mean Time To Detect) for critical issues
- ✅ Synthetic monitoring (uptime checks)

---

## 2. Technical Architecture

### 2.1 Current State Analysis

**Evidence from codebase:**

**File**: `gateway/cmd/gateway/main.go:191-192`
```go
r.Get("/health", gateway.HealthHandler)
r.Post("/v1/ingest", gateway.IngestHandler)
// NO /metrics route
```

**Missing**: Prometheus exporter

**File**: `gateway/internal/metrics.go` (referenced in `ENTERPRISE_SETUP.md:556-566`)
```markdown
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
```

**Status**: File exists but metrics not wired up.

**File**: `api/app/main.py:1-51`
```python
from fastapi import FastAPI

app = FastAPI(
    title="Ecomind API",
    version="0.1.0",
)
# NO Prometheus middleware
```

**Missing**: Metrics export, no instrumentation.

### 2.2 Proposed Architecture

#### 2.2.1 Monitoring Stack

```
┌────────────────────────────────────────────────────────────────┐
│                   Observability Architecture                   │
└────────────────────────────────────────────────────────────────┘

EcoMind Services
   ├─> Gateway (Go) ──────┐
   ├─> API (FastAPI) ─────┤
   ├─> Worker (Python) ───┤
   └─> UI (Next.js) ──────┤
                          │
                          ├──> Prometheus
                          │    (Metrics Collection)
                          │       │
                          │       └──> Grafana
                          │            (Dashboards)
                          │
                          ├──> Jaeger
                          │    (Distributed Tracing)
                          │
                          ├──> Sentry
                          │    (Error Tracking)
                          │
                          └──> Loki
                               (Log Aggregation)

Alerting
   ├─> Alertmanager (Prometheus)
   ├─> PagerDuty (Critical alerts)
   ├─> Slack (Notifications)
   └─> Email (Weekly reports)

Synthetic Monitoring
   ├─> UptimeRobot (Uptime checks)
   └─> Pingdom (Performance checks)
```

#### 2.2.2 Metrics to Track

**Gateway Metrics:**
```go
// Counters
ecomind_gateway_requests_total{status="200|400|500"}
ecomind_gateway_kafka_writes_total
ecomind_gateway_kafka_errors_total

// Histograms
ecomind_gateway_request_duration_seconds{endpoint="/v1/ingest"}
ecomind_gateway_kafka_write_duration_seconds

// Gauges
ecomind_gateway_kafka_connection_status{broker="1|2|3"}
ecomind_gateway_redis_connection_status
```

**API Metrics:**
```python
# Counters
ecomind_api_requests_total{method="GET|POST", endpoint="/v1/today", status="200|500"}
ecomind_api_db_queries_total

# Histograms
ecomind_api_request_duration_seconds{endpoint="/v1/today"}
ecomind_api_db_query_duration_seconds

# Gauges
ecomind_api_db_connection_pool_size
ecomind_api_db_connection_pool_available
```

**Worker Metrics:**
```python
# Counters
ecomind_worker_events_processed_total
ecomind_worker_events_failed_total

# Histograms
ecomind_worker_event_processing_duration_seconds

# Gauges
ecomind_worker_kafka_lag{topic="events.raw", partition="0"}
```

**Business Metrics:**
```
# Counters
ecomind_events_ingested_total{org_id="org_acme", provider="openai"}
ecomind_api_calls_total{org_id="org_acme", model="gpt-4"}

# Gauges
ecomind_daily_active_orgs
ecomind_daily_active_users
ecomind_total_kwh_today
ecomind_total_co2_kg_today
```

#### 2.2.3 SLO/SLA Definitions

| Service | SLI (Indicator) | SLO (Objective) | SLA (Agreement) |
|---------|----------------|-----------------|-----------------|
| Gateway | Availability | 99.9% uptime | 99.5% (money-back) |
| Gateway | Latency (p95) | < 100ms | < 200ms |
| API | Availability | 99.9% uptime | 99.5% |
| API | Latency (p95) | < 200ms | < 500ms |
| Worker | Event processing lag | < 10 seconds | < 60 seconds |
| Database | Query latency (p95) | < 50ms | < 100ms |

---

## 3. Implementation Plan

### 3.1 Week 1: Metrics & Dashboards

#### Day 1-2: Gateway Metrics

**Tasks:**

1. Update `gateway/internal/metrics.go`
   ```go
   package internal

   import (
       "github.com/prometheus/client_golang/prometheus"
       "github.com/prometheus/client_golang/prometheus/promauto"
   )

   var (
       RequestsTotal = promauto.NewCounterVec(
           prometheus.CounterOpts{
               Name: "ecomind_gateway_requests_total",
               Help: "Total HTTP requests",
           },
           []string{"status"},
       )

       RequestDuration = promauto.NewHistogramVec(
           prometheus.HistogramOpts{
               Name:    "ecomind_gateway_request_duration_seconds",
               Help:    "HTTP request duration",
               Buckets: prometheus.DefBuckets,
           },
           []string{"endpoint"},
       )

       KafkaWritesTotal = promauto.NewCounter(
           prometheus.CounterOpts{
               Name: "ecomind_gateway_kafka_writes_total",
               Help: "Total Kafka writes",
           },
       )

       KafkaErrorsTotal = promauto.NewCounter(
           prometheus.CounterOpts{
               Name: "ecomind_gateway_kafka_errors_total",
               Help: "Total Kafka errors",
           },
       )
   )
   ```

2. Update `gateway/cmd/gateway/main.go`
   ```go
   import (
       "github.com/prometheus/client_golang/prometheus/promhttp"
       "ecomind/gateway/internal"
   )

   func (g *Gateway) IngestHandler(w http.ResponseWriter, r *http.Request) {
       start := time.Now()
       defer func() {
           duration := time.Since(start).Seconds()
           internal.RequestDuration.WithLabelValues("/v1/ingest").Observe(duration)
       }()

       var event Event
       if err := json.NewDecoder(r.Body).Decode(&event); err != nil {
           internal.RequestsTotal.WithLabelValues("400").Inc()
           http.Error(w, "invalid JSON", http.StatusBadRequest)
           return
       }

       // ... validation

       if err := g.kafkaWriter.WriteMessages(ctx, msg); err != nil {
           internal.KafkaErrorsTotal.Inc()
           internal.RequestsTotal.WithLabelValues("500").Inc()
           http.Error(w, "failed to write event", http.StatusInternalServerError)
           return
       }

       internal.KafkaWritesTotal.Inc()
       internal.RequestsTotal.WithLabelValues("202").Inc()

       w.WriteHeader(http.StatusAccepted)
       json.NewEncoder(w).Encode(map[string]interface{}{
           "status": "accepted",
       })
   }

   func main() {
       // ... existing setup

       r.Get("/health", gateway.HealthHandler)
       r.Get("/metrics", promhttp.Handler())  // NEW: Metrics endpoint
       r.Post("/v1/ingest", gateway.IngestHandler)

       // ... rest of main
   }
   ```

**Deliverables:**
- ✅ Gateway metrics exported at `/metrics`

#### Day 3-4: API & Worker Metrics

**Tasks:**

1. Install Prometheus client for Python
   ```bash
   cd api
   pip install prometheus-client prometheus-fastapi-instrumentator
   ```

2. Update `api/app/main.py`
   ```python
   from prometheus_fastapi_instrumentator import Instrumentator

   app = FastAPI(title="Ecomind API", version="0.1.0")

   # Instrument with Prometheus
   Instrumentator().instrument(app).expose(app, endpoint="/metrics")
   ```

3. Create custom metrics in `api/app/metrics.py`
   ```python
   from prometheus_client import Counter, Histogram, Gauge

   db_queries_total = Counter(
       'ecomind_api_db_queries_total',
       'Total database queries',
       ['query_type']
   )

   db_query_duration = Histogram(
       'ecomind_api_db_query_duration_seconds',
       'Database query duration',
       ['query_type']
   )

   db_connection_pool_size = Gauge(
       'ecomind_api_db_connection_pool_size',
       'Database connection pool size'
   )
   ```

4. Update `worker/worker/main.py`
   ```python
   from prometheus_client import Counter, Histogram, start_http_server

   events_processed = Counter('ecomind_worker_events_processed_total', 'Events processed')
   events_failed = Counter('ecomind_worker_events_failed_total', 'Events failed')
   processing_duration = Histogram('ecomind_worker_event_processing_duration_seconds', 'Processing duration')

   def main():
       # Start Prometheus HTTP server on port 8000
       start_http_server(8000)

       # ... existing worker logic

       while running:
           msg_pack = consumer.poll(timeout_ms=1000)
           for topic_partition, messages in msg_pack.items():
               for message in messages:
                   start = time.time()
                   try:
                       event = message.value
                       enriched = enrichment_service.enrich(event)
                       enrichment_service.store_enriched(enriched)
                       events_processed.inc()
                   except Exception as e:
                       events_failed.inc()
                       logger.error(f"Error: {e}")
                   finally:
                       processing_duration.observe(time.time() - start)
   ```

**Deliverables:**
- ✅ API metrics at `/metrics`
- ✅ Worker metrics at `:8000/metrics`

#### Day 5: Grafana Dashboards

**Tasks:**

1. Create `ops/grafana/dashboard-overview.json`
   ```json
   {
     "dashboard": {
       "title": "EcoMind Overview",
       "panels": [
         {
           "title": "Gateway Request Rate",
           "targets": [{
             "expr": "rate(ecomind_gateway_requests_total[5m])"
           }],
           "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
         },
         {
           "title": "Gateway Error Rate",
           "targets": [{
             "expr": "rate(ecomind_gateway_requests_total{status=~\"5..\"}[5m])"
           }],
           "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
         },
         {
           "title": "API Latency (p95)",
           "targets": [{
             "expr": "histogram_quantile(0.95, rate(ecomind_api_request_duration_seconds_bucket[5m]))"
           }],
           "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8}
         },
         {
           "title": "Worker Event Processing Rate",
           "targets": [{
             "expr": "rate(ecomind_worker_events_processed_total[5m])"
           }],
           "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8}
         },
         {
           "title": "Daily Active Organizations",
           "targets": [{
             "expr": "count(count by (org_id) (ecomind_events_ingested_total))"
           }],
           "gridPos": {"x": 0, "y": 16, "w": 6, "h": 8}
         },
         {
           "title": "Total CO2 Today (kg)",
           "targets": [{
             "expr": "sum(ecomind_total_co2_kg_today)"
           }],
           "gridPos": {"x": 6, "y": 16, "w": 6, "h": 8}
         }
       ]
     }
   }
   ```

2. Deploy Grafana via Helm
   ```bash
   helm install grafana grafana/grafana \
     --namespace monitoring \
     --set adminPassword=admin \
     --set datasources."datasources\.yaml".apiVersion=1 \
     --set datasources."datasources\.yaml".datasources[0].name=Prometheus \
     --set datasources."datasources\.yaml".datasources[0].type=prometheus \
     --set datasources."datasources\.yaml".datasources[0].url=http://prometheus:9090
   ```

3. Import dashboard JSON via Grafana UI or ConfigMap

**Deliverables:**
- ✅ Grafana dashboard showing key metrics

### 3.2 Week 2: Alerting & Testing

#### Day 6-7: Alerting Rules

**Tasks:**

1. Create `ops/prometheus/alert-rules.yml`
   ```yaml
   groups:
     - name: ecomind_alerts
       rules:
         # High error rate
         - alert: HighErrorRate
           expr: rate(ecomind_gateway_requests_total{status=~"5.."}[5m]) > 0.05
           for: 5m
           labels:
             severity: critical
           annotations:
             summary: "High error rate in Gateway"
             description: "Error rate is {{ $value }} requests/sec"

         # High latency
         - alert: HighLatency
           expr: histogram_quantile(0.95, rate(ecomind_api_request_duration_seconds_bucket[5m])) > 0.5
           for: 5m
           labels:
             severity: warning
           annotations:
             summary: "High API latency"
             description: "p95 latency is {{ $value }} seconds"

         # Kafka lag
         - alert: HighKafkaLag
           expr: ecomind_worker_kafka_lag > 1000
           for: 10m
           labels:
             severity: warning
           annotations:
             summary: "High Kafka consumer lag"
             description: "Lag is {{ $value }} messages"

         # Database connection pool exhausted
         - alert: DatabasePoolExhausted
           expr: ecomind_api_db_connection_pool_available == 0
           for: 2m
           labels:
             severity: critical
           annotations:
             summary: "Database connection pool exhausted"

         # Service down
         - alert: ServiceDown
           expr: up{job=~"ecomind-.*"} == 0
           for: 1m
           labels:
             severity: critical
           annotations:
             summary: "Service {{ $labels.job }} is down"
   ```

2. Configure Alertmanager
   ```yaml
   # ops/prometheus/alertmanager.yml
   global:
     resolve_timeout: 5m
     slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

   route:
     receiver: 'default'
     group_by: ['alertname', 'severity']
     group_wait: 10s
     group_interval: 10s
     repeat_interval: 12h
     routes:
       - match:
           severity: critical
         receiver: 'pagerduty'
       - match:
           severity: warning
         receiver: 'slack'

   receivers:
     - name: 'default'
       slack_configs:
         - channel: '#ecomind-alerts'
           title: 'EcoMind Alert'
           text: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ .Annotations.description }}\n{{ end }}'

     - name: 'pagerduty'
       pagerduty_configs:
         - service_key: 'YOUR_PAGERDUTY_KEY'

     - name: 'slack'
       slack_configs:
         - channel: '#ecomind-alerts'
   ```

**Deliverables:**
- ✅ Alert rules configured
- ✅ Alertmanager routing to Slack/PagerDuty

#### Day 8-9: Integration Tests

**Tasks:**

1. Create `api/tests/integration/test_e2e_flow.py`
   ```python
   import pytest
   import requests
   import time
   from kafka import KafkaConsumer

   @pytest.fixture
   def setup_test_org(db_session):
       # Create test org and user
       org = Organization(org_id="test_org", name="Test Org")
       user = User(user_id="test_user", org_id="test_org", email="test@test.com")
       db_session.add(org)
       db_session.add(user)
       db_session.commit()
       yield
       # Cleanup
       db_session.delete(user)
       db_session.delete(org)
       db_session.commit()

   def test_end_to_end_ingestion(setup_test_org):
       """Test: Gateway → Kafka → Worker → Database → API"""

       # Step 1: Send event to Gateway
       event = {
           "org_id": "test_org",
           "user_id": "test_user",
           "provider": "openai",
           "model": "gpt-4",
           "tokens_in": 100,
           "tokens_out": 50,
       }
       response = requests.post("http://localhost:8080/v1/ingest", json=event)
       assert response.status_code == 202

       # Step 2: Wait for worker to process (up to 10 seconds)
       time.sleep(10)

       # Step 3: Query API to verify event was processed
       response = requests.get("http://localhost:8000/v1/today?org_id=test_org")
       assert response.status_code == 200
       data = response.json()
       assert data["call_count"] >= 1
       assert data["kwh"] > 0

   def test_authentication_flow():
       """Test: Login → Get token → Access protected route"""

       # Step 1: Login
       response = requests.post("http://localhost:8000/v1/auth/login", json={
           "email": "test@test.com",
           "password": "password123"
       })
       assert response.status_code == 200
       token = response.json()["access_token"]

       # Step 2: Access protected route with token
       headers = {"Authorization": f"Bearer {token}"}
       response = requests.get("http://localhost:8000/v1/today?org_id=test_org", headers=headers)
       assert response.status_code == 200

       # Step 3: Access without token should fail
       response = requests.get("http://localhost:8000/v1/today?org_id=test_org")
       assert response.status_code == 401

   def test_rbac_permissions():
       """Test: Viewer cannot access org-wide data"""

       # Login as viewer
       viewer_token = login_as("viewer@test.com", "password")

       # Try to access org-wide data
       response = requests.get(
           "http://localhost:8000/v1/today?org_id=test_org",
           headers={"Authorization": f"Bearer {viewer_token}"}
       )
       assert response.status_code == 403
   ```

2. Create `tests/e2e/test_chrome_extension_flow.py`
   ```python
   def test_extension_to_backend_flow():
       """Test: Extension → Gateway → API"""

       # Simulate extension sending telemetry
       payload = {
           "user_id": "alice@acme.com",
           "org_id": "acme",
           "provider": "openai",
           "model": "gpt-4",
           "tokens_in": 0,
           "tokens_out": 0,
           "ts": "2025-10-07T12:00:00Z"
       }

       # Send to Gateway
       response = requests.post(
           "http://localhost:8080/v1/ingest",
           json=payload,
           headers={"Content-Type": "application/json"}
       )
       assert response.status_code == 202

       # Wait for processing
       time.sleep(10)

       # Verify data in API
       response = requests.get("http://localhost:8000/v1/today?org_id=acme")
       assert response.status_code == 200
   ```

3. Run tests
   ```bash
   cd api
   pytest tests/integration/ -v
   ```

**Deliverables:**
- ✅ 15+ integration tests passing

#### Day 10: Synthetic Monitoring

**Tasks:**

1. Set up UptimeRobot
   - Monitor https://api.ecomind.acme.com/health (5-minute checks)
   - Alert on 2 consecutive failures

2. Set up Pingdom
   - Performance monitoring (page load time)
   - Alert if > 3 seconds

3. Create `ops/synthetic-tests/gateway_health_check.sh`
   ```bash
   #!/bin/bash
   set -e

   GATEWAY_URL="https://api.ecomind.acme.com"

   # Health check
   response=$(curl -s -o /dev/null -w "%{http_code}" $GATEWAY_URL/health)
   if [ $response -ne 200 ]; then
     echo "ERROR: Gateway health check failed (HTTP $response)"
     exit 1
   fi

   # Latency check
   latency=$(curl -s -o /dev/null -w "%{time_total}" $GATEWAY_URL/health)
   if (( $(echo "$latency > 0.5" | bc -l) )); then
     echo "WARNING: Gateway latency is high ($latency seconds)"
   fi

   echo "✅ Gateway is healthy (latency: ${latency}s)"
   ```

4. Schedule synthetic tests in CI
   ```yaml
   # .github/workflows/synthetic-tests.yml
   name: Synthetic Tests

   on:
     schedule:
       - cron: '*/15 * * * *'  # Every 15 minutes

   jobs:
     health_check:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3

         - name: Gateway Health Check
           run: ./ops/synthetic-tests/gateway_health_check.sh

         - name: API Health Check
           run: curl -f https://api.ecomind.acme.com/health || exit 1
   ```

**Deliverables:**
- ✅ Synthetic monitoring configured
- ✅ Health checks running every 15 minutes

---

## 4. Risk Analysis

### 4.1 Medium Risks

**Risk 1: Alert Fatigue**
- **Likelihood**: Medium
- **Impact**: Medium (missed critical alerts)
- **Mitigation**:
  - Tune alert thresholds carefully
  - Use severity levels (critical/warning/info)
  - Weekly review of alert frequency
  - Silence non-actionable alerts

**Risk 2: Monitoring Overhead**
- **Likelihood**: Low
- **Impact**: Low (performance degradation)
- **Mitigation**:
  - Use sampling for high-volume metrics
  - Optimize Prometheus queries
  - Monitor monitoring system itself

---

## 5. Success Metrics

**Quantitative:**
- ✅ < 5 minutes MTTD (Mean Time To Detect)
- ✅ < 100ms metrics collection overhead
- ✅ 80%+ code coverage (integration tests)
- ✅ 0 false positive alerts per day

**Qualitative:**
- ✅ Team trusts monitoring data
- ✅ Incidents detected before user reports
- ✅ Clear runbooks for all alerts

---

## 6. Dependencies

**Upstream (Blockers):**
- P003: Infrastructure (needs production environment)

**Downstream:**
- None (final phase)

---

## 7. Acceptance Criteria

- [ ] Prometheus metrics exported from all services
- [ ] Grafana dashboards for Gateway, API, Worker, Business metrics
- [ ] Alert rules configured (high error rate, latency, lag, downtime)
- [ ] Alertmanager routing to Slack/PagerDuty
- [ ] 15+ integration tests passing
- [ ] End-to-end test (extension → backend) passing
- [ ] Synthetic monitoring (UptimeRobot/Pingdom) configured
- [ ] Documentation complete (`MONITORING.md`, `RUNBOOK.md`)
- [ ] < 5 minutes MTTD for critical issues in staging

---

**Design Status**: Ready for Codex Review
**Next Step**: Codex review → Implementation → Testing → Production deployment
