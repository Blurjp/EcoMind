# API Service (Python FastAPI)

REST/gRPC API for Ecomind queries, admin, and configuration.

## Endpoints

- `GET /health` – Health check
- `GET /v1/today` – Today's usage
- `GET /v1/aggregate/daily` – Daily aggregates
- (More to come: orgs, users, alerts, factors, reports, audits)

## Environment Variables

- `DATABASE_URL` – Postgres connection string
- `REDIS_URL` – Redis connection string
- `PORT` (default: 8000)

## Development

```bash
# Install deps (using uv for speed)
pip install uv
uv pip install -e .

# Run
uvicorn app.main:app --reload --port 8000
```

## Docker

```bash
docker build -t ecomind-api .
docker run -p 8000:8000 ecomind-api
```

## Test

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/v1/today?org_id=org_demo&user_id=user_alice"
```