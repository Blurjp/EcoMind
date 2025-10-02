# ecomind-sdk (Python)

Official Python SDK for Ecomind API.

## Installation

```bash
pip install ecomind-sdk
```

## Usage

```python
from ecomind_sdk import EcomindClient

client = EcomindClient(
    api_key="ek_...",
    base_url="https://api.ecomind.example.com",
    org_id="org_123",
    user_id="user_abc",
)

# Track event
client.track(
    provider="anthropic",
    model="claude-3-sonnet",
    tokens_in=200,
    tokens_out=100,
    region="US-CAISO",
)

# Get today's data
today = client.get_today()
print(f"kWh: {today['kwh']}, CO2: {today['co2_kg']} kg")

client.close()
```

## Context Manager

```python
with EcomindClient(...) as client:
    client.track(...)
```

## Development

```bash
pip install -e '.[dev]'
pytest
```