#!/usr/bin/env python
"""
Database initialization script - creates all tables defined in ORM models.

Run this after setting up DATABASE_URL environment variable.
"""
import sys
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, Base
from app.models import Video


def create_tables():
    """Create all tables based on ORM models."""
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    print("✓ Database tables created successfully")
    print("\nCreated tables:")
    print("  - videos (id, video_id, transcript_encrypted, created_at)")


if __name__ == "__main__":
    try:
        create_tables()
        print("\n✓ Database initialization complete")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        sys.exit(1)
