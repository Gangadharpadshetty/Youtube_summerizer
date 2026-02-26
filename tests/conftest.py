import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db


# -----------------------------
# TEST DATABASE CONFIG
# -----------------------------

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# -----------------------------
# CREATE / DROP TABLES
# -----------------------------

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
    Create tables before test session
    Drop after session ends
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

    # Remove test.db file after tests
    if os.path.exists("test.db"):
        os.remove("test.db")


# -----------------------------
# OVERRIDE get_db DEPENDENCY
# -----------------------------

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# -----------------------------
# TEST CLIENT FIXTURE
# -----------------------------

@pytest.fixture()
def client():
    """
    Provides FastAPI TestClient
    """
    with TestClient(app) as c:
        yield c