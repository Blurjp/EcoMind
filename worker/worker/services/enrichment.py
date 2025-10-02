from datetime import datetime
from typing import Dict, Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class EnrichmentService:
    """Service for enriching raw events with environmental impact."""

    def __init__(self, factors_service, db_url: str):
        self.factors = factors_service
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def enrich(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich event with kWh, water, CO2.

        Formula:
        - kwh_base = kwh_per_call (from provider/model lookup)
        - kwh = kwh_base * pue
        - water_l = kwh * water_l_per_kwh
        - co2_kg = kwh * (grid_intensity / 1000) OR kwh * co2_kg_per_kwh
        """
        provider = event.get("provider", "unknown")
        model = event.get("model", "")
        region = event.get("region", "UNKNOWN")

        # Get factors
        kwh_base = self.factors.get_kwh_per_call(provider, model)
        pue = self.factors.get_pue()
        water_per_kwh = self.factors.get_water_per_kwh()

        # Compute
        kwh = kwh_base * pue
        water_l = kwh * water_per_kwh

        # CO2: use grid intensity if region known, else default
        if region and region != "UNKNOWN":
            grid_gco2 = self.factors.get_grid_intensity(region)
            co2_kg = (kwh * grid_gco2) / 1000.0  # gCO2 → kgCO2
        else:
            co2_kg_per_kwh = self.factors.get_co2_per_kwh()
            co2_kg = kwh * co2_kg_per_kwh

        enriched = {
            **event,
            "kwh": kwh,
            "water_l": water_l,
            "co2_kg": co2_kg,
            "enriched_at": datetime.utcnow().isoformat() + "Z",
        }

        return enriched

    def store_enriched(self, enriched: Dict[str, Any]):
        """Store enriched event and update daily aggregates"""
        db = self.SessionLocal()
        try:
            # Parse timestamp
            ts_str = enriched.get("ts")
            if ts_str:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            else:
                ts = datetime.utcnow()

            event_date = ts.date()
            org_id = enriched["org_id"]
            user_id = enriched["user_id"]
            provider = enriched["provider"]
            model = enriched.get("model", "unknown")
            kwh = enriched["kwh"]
            water_l = enriched["water_l"]
            co2_kg = enriched["co2_kg"]

            # Insert into events_enriched
            db.execute(
                text("""
                    INSERT INTO events_enriched
                    (id, org_id, user_id, provider, model, tokens_in, tokens_out,
                     node_type, region, kwh, water_l, co2_kg, ts, source, metadata, created_at)
                    VALUES
                    (gen_random_uuid()::text, :org_id, :user_id, :provider, :model, :tokens_in, :tokens_out,
                     :node_type, :region, :kwh, :water_l, :co2_kg, :ts, :source, :metadata::jsonb, now())
                """),
                {
                    "org_id": org_id,
                    "user_id": user_id,
                    "provider": provider,
                    "model": model,
                    "tokens_in": enriched.get("tokens_in", 0),
                    "tokens_out": enriched.get("tokens_out", 0),
                    "node_type": enriched.get("node_type"),
                    "region": enriched.get("region"),
                    "kwh": kwh,
                    "water_l": water_l,
                    "co2_kg": co2_kg,
                    "ts": ts,
                    "source": enriched.get("source", "gateway"),
                    "metadata": str(enriched.get("metadata", {})),
                }
            )

            # Update daily_org_agg
            db.execute(
                text("""
                    INSERT INTO daily_org_agg (date, org_id, call_count, kwh, water_l, co2_kg)
                    VALUES (:date, :org_id, 1, :kwh, :water_l, :co2_kg)
                    ON CONFLICT (date, org_id) DO UPDATE SET
                        call_count = daily_org_agg.call_count + 1,
                        kwh = daily_org_agg.kwh + EXCLUDED.kwh,
                        water_l = daily_org_agg.water_l + EXCLUDED.water_l,
                        co2_kg = daily_org_agg.co2_kg + EXCLUDED.co2_kg
                """),
                {"date": event_date, "org_id": org_id, "kwh": kwh, "water_l": water_l, "co2_kg": co2_kg}
            )

            # Update daily_user_agg
            db.execute(
                text("""
                    INSERT INTO daily_user_agg (date, org_id, user_id, call_count, kwh, water_l, co2_kg)
                    VALUES (:date, :org_id, :user_id, 1, :kwh, :water_l, :co2_kg)
                    ON CONFLICT (date, org_id, user_id) DO UPDATE SET
                        call_count = daily_user_agg.call_count + 1,
                        kwh = daily_user_agg.kwh + EXCLUDED.kwh,
                        water_l = daily_user_agg.water_l + EXCLUDED.water_l,
                        co2_kg = daily_user_agg.co2_kg + EXCLUDED.co2_kg
                """),
                {"date": event_date, "org_id": org_id, "user_id": user_id, "kwh": kwh, "water_l": water_l, "co2_kg": co2_kg}
            )

            # Update daily_provider_agg
            db.execute(
                text("""
                    INSERT INTO daily_provider_agg (date, org_id, provider, call_count, kwh, water_l, co2_kg)
                    VALUES (:date, :org_id, :provider, 1, :kwh, :water_l, :co2_kg)
                    ON CONFLICT (date, org_id, provider) DO UPDATE SET
                        call_count = daily_provider_agg.call_count + 1,
                        kwh = daily_provider_agg.kwh + EXCLUDED.kwh,
                        water_l = daily_provider_agg.water_l + EXCLUDED.water_l,
                        co2_kg = daily_provider_agg.co2_kg + EXCLUDED.co2_kg
                """),
                {"date": event_date, "org_id": org_id, "provider": provider, "kwh": kwh, "water_l": water_l, "co2_kg": co2_kg}
            )

            # Update daily_model_agg
            db.execute(
                text("""
                    INSERT INTO daily_model_agg (date, org_id, provider, model, call_count, kwh, water_l, co2_kg)
                    VALUES (:date, :org_id, :provider, :model, 1, :kwh, :water_l, :co2_kg)
                    ON CONFLICT (date, org_id, provider, model) DO UPDATE SET
                        call_count = daily_model_agg.call_count + 1,
                        kwh = daily_model_agg.kwh + EXCLUDED.kwh,
                        water_l = daily_model_agg.water_l + EXCLUDED.water_l,
                        co2_kg = daily_model_agg.co2_kg + EXCLUDED.co2_kg
                """),
                {"date": event_date, "org_id": org_id, "provider": provider, "model": model, "kwh": kwh, "water_l": water_l, "co2_kg": co2_kg}
            )

            db.commit()
            print(f"✅ Stored: {org_id}/{user_id}, {provider}/{model}, kWh={kwh:.6f}, CO2={co2_kg:.6f}")

        except Exception as e:
            db.rollback()
            print(f"❌ DB error: {e}")
            raise
        finally:
            db.close()