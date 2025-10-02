# Worker Service (Python)

Kafka consumer for event enrichment and aggregation.

## Responsibilities

- Consume `events.raw` from Kafka
- Enrich with kWh, water, CO₂ using factors + grid intensity
- Store to `events_enriched` and update daily aggregates
- Evaluate alerts (future)
- Generate reports (future)

## Environment Variables

- `KAFKA_BROKERS` (default: localhost:9092)
- `DATABASE_URL` – Postgres connection
- `REDIS_URL` – Redis connection

## Development

```bash
# Install
pip install uv
uv pip install -e .

# Run
python -m worker.main
```

## Docker

```bash
docker build -t ecomind-worker .
docker run ecomind-worker
```

## Test

Send event via gateway, watch worker logs.