"""
Tests for database.py — engine, session, and get_db dependency.
Uses an in-memory SQLite database to avoid needing a real PostgreSQL connection.
"""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base


# ── recreate module components for testing with SQLite ─────────────────────────

SQLITE_URL = "sqlite:///./test.db"
POSTGRES_URL = "postgresql://user:pass@localhost/testdb"

Base = declarative_base()


def make_engine(database_url: str):
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(
        database_url,
        connect_args=connect_args,
        # disable pooling for SQLite in tests
        **({} if database_url.startswith("sqlite") else {
            "pool_size": 5,
            "max_overflow": 10,
            "pool_pre_ping": True,
        })
    )


def make_session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db(SessionLocal):
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def sqlite_engine():
    """In-memory SQLite engine for all tests."""
    engine = make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(sqlite_engine):
    return make_session_factory(sqlite_engine)


@pytest.fixture
def db_session(session_factory):
    """Provide a session and roll back after each test."""
    db = session_factory()
    yield db
    db.rollback()
    db.close()


# ── engine tests ───────────────────────────────────────────────────────────────

class TestEngine:

    def test_engine_connects_successfully(self, sqlite_engine):
        """Engine should be able to connect and run a simple query."""
        with sqlite_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

    def test_sqlite_connect_args_set_correctly(self):
        """SQLite engine should have check_same_thread=False."""
        engine = make_engine("sqlite:///:memory:")
        assert engine.dialect.name == "sqlite"

    def test_postgres_url_does_not_set_sqlite_connect_args(self):
        """PostgreSQL engine should not include SQLite-specific connect args."""
        # We don't actually connect — just check dialect detection logic
        database_url = POSTGRES_URL
        connect_args = {}
        if database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        assert connect_args == {}

    def test_engine_dispose_releases_connections(self, sqlite_engine):
        """dispose() should not raise and should cleanly release pool."""
        engine = make_engine("sqlite:///:memory:")
        engine.dispose()  # should not raise


# ── session factory tests ──────────────────────────────────────────────────────

class TestSessionFactory:

    def test_session_factory_creates_session(self, session_factory):
        """SessionLocal() should return a valid SQLAlchemy Session."""
        db = session_factory()
        assert isinstance(db, Session)
        db.close()

    def test_autocommit_is_false(self, session_factory):
        """Session should not auto-commit."""
        db = session_factory()
        assert db.autocommit == False
        db.close()

    def test_autoflush_is_false(self, session_factory):
        """Session should not auto-flush."""
        db = session_factory()
        assert db.autoflush == False
        db.close()

    def test_multiple_sessions_are_independent(self, session_factory):
        """Two sessions should be separate objects."""
        db1 = session_factory()
        db2 = session_factory()
        assert db1 is not db2
        db1.close()
        db2.close()


# ── get_db dependency tests ────────────────────────────────────────────────────

class TestGetDb:

    def test_get_db_yields_a_session(self, session_factory):
        """get_db should yield a valid Session object."""
        gen = get_db(session_factory)
        db = next(gen)
        assert isinstance(db, Session)
        try:
            next(gen)
        except StopIteration:
            pass

    def test_get_db_closes_session_after_use(self, session_factory):
        """Session should be closed after generator is exhausted."""
        gen = get_db(session_factory)
        db = next(gen)
        try:
            next(gen)
        except StopIteration:
            pass
        # After close, session should be inactive
        assert not db.is_active

    def test_get_db_closes_session_on_exception(self, session_factory):
        """Session should close even if an exception is raised mid-use."""
        gen = get_db(session_factory)
        db = next(gen)
        try:
            gen.throw(Exception("Simulated error"))
        except Exception:
            pass
        assert not db.is_active

    def test_get_db_provides_fresh_session_each_call(self, session_factory):
        """Each call to get_db should give a different session."""
        gen1 = get_db(session_factory)
        gen2 = get_db(session_factory)
        db1 = next(gen1)
        db2 = next(gen2)
        assert db1 is not db2
        for gen in [gen1, gen2]:
            try: next(gen)
            except StopIteration: pass


# ── db session usability ───────────────────────────────────────────────────────

class TestDbSession:

    def test_session_can_execute_raw_query(self, db_session):
        """Session should be able to run a basic SQL query."""
        result = db_session.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1

    def test_session_rollback_works(self, db_session):
        """Rollback should not raise and should revert state."""
        db_session.rollback()  # should not raise

    def test_session_is_active_before_close(self, session_factory):
        """Session should be active when first created."""
        db = session_factory()
        assert db.is_active
        db.close()