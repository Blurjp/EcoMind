# Gateway Service (Go)

High-throughput ingestion service for Ecomind events.

## Endpoints

- `GET /health` – Health check (kafka + redis)
- `POST /v1/ingest` – Ingest event

## Environment Variables

- `PORT` (default: 8080)
- `KAFKA_BROKERS` (default: localhost:9092)
- `REDIS_ADDR` (default: localhost:6379)

## Build

```bash
go build -o bin/gateway ./cmd/gateway
```

## Run

```bash
./bin/gateway
```

## Docker

```bash
docker build -t ecomind-gateway .
docker run -p 8080:8080 ecomind-gateway
```

## Test

```bash
curl -X POST http://localhost:8080/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "org_test",
    "user_id": "user_test",
    "provider": "openai",
    "model": "gpt-4o",
    "tokens_in": 100,
    "tokens_out": 50
  }'
```