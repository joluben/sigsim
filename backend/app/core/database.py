"""
Database configuration and session management
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from app.core.config import settings

# Create engine with appropriate configuration
engine_kwargs = {}

if "sqlite" in settings.database_url:
    # SQLite specific configuration
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
        "pool_pre_ping": True,
    })
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if 'sqlite' in str(dbapi_connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
else:
    # PostgreSQL/MySQL configuration
    engine_kwargs.update({
        "pool_size": settings.connection_pool_size,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    })

engine = create_engine(settings.database_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables (for development/testing)"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables (for testing)"""
    Base.metadata.drop_all(bind=engine)