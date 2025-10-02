import json
import logging
import os
import signal
import sys
from datetime import datetime

from kafka import KafkaConsumer
from worker.services.enrichment import EnrichmentService
from worker.services.factors import FactorsService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

running = True


def signal_handler(sig, frame):
    global running
    logger.info("Received shutdown signal, stopping worker...")
    running = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def main():
    kafka_brokers = os.getenv("KAFKA_BROKERS", "localhost:9092").split(",")
    db_url = os.getenv("DATABASE_URL", "postgresql://ecomind:ecomind_dev_pass@localhost:5432/ecomind")

    logger.info(f"🚀 Starting worker, connecting to Kafka: {kafka_brokers}")

    # Load factors
    factors_service = FactorsService()
    factors_service.load_defaults()

    # Create enrichment service
    enrichment_service = EnrichmentService(factors_service, db_url)

    # Kafka consumer
    consumer = KafkaConsumer(
        "events.raw",
        bootstrap_servers=kafka_brokers,
        group_id="ecomind-worker",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    logger.info("✅ Worker ready, listening for events...")

    try:
        while running:
            msg_pack = consumer.poll(timeout_ms=1000)
            for topic_partition, messages in msg_pack.items():
                for message in messages:
                    try:
                        event = message.value
                        logger.info(
                            f"Processing event: org={event.get('org_id')}, "
                            f"provider={event.get('provider')}"
                        )
                        enriched = enrichment_service.enrich(event)
                        enrichment_service.store_enriched(enriched)
                        logger.info(f"Enriched: kWh={enriched['kwh']:.6f}, "
                                    f"CO2={enriched['co2_kg']:.6f}")
                    except Exception as e:
                        logger.error(f"Error processing event: {e}", exc_info=True)
    finally:
        consumer.close()
        logger.info("🛑 Worker stopped")


if __name__ == "__main__":
    main()