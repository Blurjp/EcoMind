"""Alert evaluation and notification service"""
import httpx
from datetime import datetime


class AlertService:
    """Evaluates alerts and sends notifications"""

    def __init__(self, db_url: str):
        self.db_url = db_url

    async def evaluate_alerts(self):
        """
        Periodically check alert thresholds.
        For each alert:
        - Query aggregate data for the window
        - Compare to threshold
        - Send notification if threshold crossed
        """
        # TODO: Implement alert evaluation logic
        # Query alerts from DB
        # For each alert, check if threshold exceeded
        # Send notification via channel
        pass

    async def send_notification(self, channel: str, webhook_url: str, message: str):
        """Send notification to channel"""
        if channel == "slack":
            await self._send_slack(webhook_url, message)
        elif channel == "teams":
            await self._send_teams(webhook_url, message)
        elif channel == "webhook":
            await self._send_webhook(webhook_url, message)
        else:
            print(f"⚠️  Unsupported channel: {channel}")

    async def _send_slack(self, webhook_url: str, message: str):
        """Send to Slack webhook"""
        payload = {"text": message}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(webhook_url, json=payload, timeout=5.0)
                if resp.status_code == 200:
                    print(f"✅ Sent Slack notification")
                else:
                    print(f"❌ Slack notification failed: {resp.status_code}")
            except Exception as e:
                print(f"❌ Slack error: {e}")

    async def _send_teams(self, webhook_url: str, message: str):
        """Send to Microsoft Teams webhook"""
        payload = {"text": message}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(webhook_url, json=payload, timeout=5.0)
                if resp.status_code == 200:
                    print(f"✅ Sent Teams notification")
                else:
                    print(f"❌ Teams notification failed: {resp.status_code}")
            except Exception as e:
                print(f"❌ Teams error: {e}")

    async def _send_webhook(self, webhook_url: str, message: str):
        """Send to generic webhook"""
        payload = {"message": message, "ts": datetime.utcnow().isoformat() + "Z"}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(webhook_url, json=payload, timeout=5.0)
                if resp.status_code in [200, 201, 202]:
                    print(f"✅ Sent webhook notification")
                else:
                    print(f"❌ Webhook notification failed: {resp.status_code}")
            except Exception as e:
                print(f"❌ Webhook error: {e}")