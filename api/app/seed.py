"""Seed database with default data"""
import sys
from datetime import datetime, date

from app.db import engine, Base, SessionLocal
from app.models import Org, User, PlanType, Role

def seed_database():
    print("🌱 Creating database schema...")
    Base.metadata.create_all(bind=engine)
    print("✅ Schema created")

    db = SessionLocal()
    try:
        # Check if demo org exists
        existing = db.query(Org).filter_by(id="org_demo").first()
        if existing:
            print("⚠️  Demo data already exists, skipping seed")
            return

        # Create demo org
        demo_org = Org(
            id="org_demo",
            name="Demo Organization",
            plan=PlanType.PRO,
        )
        db.add(demo_org)

        # Create demo users
        alice = User(
            id="user_alice",
            org_id="org_demo",
            email="alice@demo.ecomind.example",
            name="Alice Johnson",
            role=Role.ADMIN,
        )
        bob = User(
            id="user_bob",
            org_id="org_demo",
            email="bob@demo.ecomind.example",
            name="Bob Smith",
            role=Role.ANALYST,
        )

        db.add(alice)
        db.add(bob)
        db.commit()

        print("✅ Seeded:")
        print("  - Org: org_demo (Demo Organization)")
        print("  - User: user_alice (alice@demo.ecomind.example, ADMIN)")
        print("  - User: user_bob (bob@demo.ecomind.example, ANALYST)")

    except Exception as e:
        print(f"❌ Seed failed: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
