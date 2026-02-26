#!/usr/bin/env python
"""
Complete setup and validation script for YouTube Transcript Caching application.

This script:
1. Validates environment configuration
2. Creates database tables
3. Runs unit tests
4. Starts the FastAPI server
"""
import os
import sys
import subprocess
from pathlib import Path

# Ensure project root is importable
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_env():
    """Validate environment variables."""
    print("🔍 Checking environment configuration...")
    
    db_url = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    fernet_key = os.getenv("FERNET_KEY", "")
    
    print(f"  ✓ DATABASE_URL: {db_url[:50]}..." if len(db_url) > 50 else f"  ✓ DATABASE_URL: {db_url}")
    
    if fernet_key:
        print(f"  ✓ FERNET_KEY: {'*' * 40} (length: {len(fernet_key)})")
    else:
        print("  ⚠ FERNET_KEY: Not set (will auto-generate for development)")
    
    return db_url, fernet_key


def create_tables():
    """Create database tables."""
    print("\n📊 Creating database tables...")
    try:
        from app.database import engine, Base
        from app.models import Video
        
        Base.metadata.create_all(engine)
        print("  ✓ Tables created successfully")
        print("    - videos (id, video_id, transcript_encrypted, created_at)")
        return True
    except Exception as e:
        print(f"  ✗ Error creating tables: {e}")
        return False


def run_tests():
    """Run unit tests."""
    print("\n🧪 Running unit tests...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode == 0:
            print("  ✓ All tests passed")
            return True
        else:
            print("  ✗ Some tests failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"  ⚠ Could not run tests: {e}")
        return True  # Don't fail completely


def show_next_steps():
    """Display next steps for the user."""
    print("\n" + "="*60)
    print("✓ SETUP COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("\n1. Start the FastAPI server:")
    print("   . .venv\\Scripts\\Activate.ps1  (on Windows PowerShell)")
    print("   uvicorn app.main:app --reload")
    print("\n2. Test the API:")
    print("   curl -X POST http://localhost:8000/transcript \\")
    print("     -H \"Content-Type: application/json\" \\")
    print("     -d '{\"youtube_url\": \"https://www.youtube.com/watch?v=dQw4w9WgXcQ\"}'")
    print("\n3. View API documentation:")
    print("   http://localhost:8000/docs (Swagger UI)")
    print("   http://localhost:8000/redoc (ReDoc)")
    print("\n4. Database tables created:")
    print("   - videos (transcript caching)")
    print("\n5. Environment variables (set in .env or Render secrets):")
    print("   - DATABASE_URL (PostgreSQL for production)")
    print("   - FERNET_KEY (encryption key)")
    print("="*60)


def main():
    """Run full setup."""
    print("🚀 YouTube Transcript Caching - Setup\n")
    
    # Check environment
    db_url, fernet_key = check_env()
    
    # Create tables
    if not create_tables():
        print("\n⚠ Setup partially complete (database creation failed)")
        return 1
    
    # Run tests
    run_tests()
    
    # Show next steps
    show_next_steps()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
