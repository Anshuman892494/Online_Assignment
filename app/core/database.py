import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.models.base import Base

logger = logging.getLogger("document_intelligence.database")

import socket

def is_postgres_available(host="localhost", port=5432, timeout=0.3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, ConnectionRefusedError):
        return False

_engine = None
_sessionmaker = None
_using_fallback = False

def get_engine():
    global _engine, _using_fallback
    if _engine is None:
        if is_postgres_available():
            _engine = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                future=True,
                pool_pre_ping=True
            )
        else:
            logger.info(f"PostgreSQL not reachable at localhost:5432. Using SQLite fallback: {settings.SQLITE_FALLBACK_URL}")
            _using_fallback = True
            _engine = create_async_engine(
                settings.SQLITE_FALLBACK_URL,
                echo=False,
                future=True
            )
    return _engine

def get_sessionmaker():
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    return _sessionmaker

class DynamicAsyncSessionLocal:
    """Dynamic session factory proxy that gracefully tracks engine switching."""
    def __call__(self) -> AsyncSession:
        sm = get_sessionmaker()
        return sm()

AsyncSessionLocal = DynamicAsyncSessionLocal()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for injecting database sessions into API endpoints."""
    sm = get_sessionmaker()
    async with sm() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initializes database tables. Falls back seamlessly to SQLite if PostgreSQL is unreachable."""
    global _engine, _sessionmaker, _using_fallback
    eng = get_engine()
    try:
        # Test PostgreSQL connection
        async with eng.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Successfully connected to primary PostgreSQL database.")
    except Exception as exc:
        logger.warning(
            f"PostgreSQL connection failed ({exc}). Switching to zero-config SQLite mode at {settings.SQLITE_FALLBACK_URL}."
        )
        _using_fallback = True
        _engine = create_async_engine(
            settings.SQLITE_FALLBACK_URL,
            echo=False,
            future=True
        )
        _sessionmaker = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
        eng = _engine

    # Create tables if not exist
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schemas and tables verified/created.")
