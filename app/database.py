# (empty)
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL


# Create SQLAlchemy engine with sensible pool settings for production (Render)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
	# sqlite needs check_same_thread disabled for SQLAlchemy in multithreaded apps
	connect_args = {"check_same_thread": False}

# Example pool sizing; Render provides its own connection limits so keep modest defaults
engine = create_engine(
	DATABASE_URL,
	pool_size=5,
	max_overflow=10,
	pool_pre_ping=True,
	connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

