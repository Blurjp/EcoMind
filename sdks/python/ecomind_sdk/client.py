from datetime import datetime
from typing import Optional, Dict, Any

import httpx


class EcomindClient:
    """Python client for Ecomind API"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        org_id: str,
        user_id: str,
        timeout: float = 5.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.org_id = org_id
        self.user_id = user_id
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def track(
        self,
        provider: str,
        model: Optional[str] = None,
        tokens_in: int = 0,
        tokens_out: int = 0,
        region: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Track an AI API call event"""
        payload = {
            "org_id": self.org_id,
            "user_id": self.user_id,
            "provider": provider,
            "model": model or "",
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "region": region or "UNKNOWN",
            "ts": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {},
        }

        url = f"{self.base_url}/v1/ingest"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        resp = self.client.post(url, json=payload, headers=headers)
        resp.raise_for_status()

    def get_today(self) -> Dict[str, Any]:
        """Get today's aggregated data"""
        url = f"{self.base_url}/v1/today"
        params = {"org_id": self.org_id, "user_id": self.user_id}
        headers = {"Authorization": f"Bearer {self.api_key}"}

        resp = self.client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def close(self):
        """Close the HTTP client"""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()