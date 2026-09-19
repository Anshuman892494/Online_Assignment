import asyncio
import logging
import socket
from typing import Callable, Coroutine, Any, Optional
from urllib.parse import urlparse
import redis.asyncio as aioredis
from sqlalchemy import select, update
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.document import Document

logger = logging.getLogger("document_intelligence.task_queue")

def is_redis_available(redis_url: str = settings.REDIS_URL, timeout: float = 0.3) -> bool:
    """Fast check to verify if Redis server is reachable on the configured host/port."""
    try:
        parsed = urlparse(redis_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6379
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, ConnectionRefusedError):
        return False

class TaskQueueManager:
    """
    Dual-Mode Asynchronous Task Dispatcher:
    - Mode A: Distributed Redis Queue when Redis service is reachable.
    - Mode B: Zero-config asyncio Background Task Pool when running standalone.
    """
    def __init__(self):
        self._redis_client: Optional[aioredis.Redis] = None
        self._has_redis: Optional[bool] = None

    def has_redis(self) -> bool:
        if self._has_redis is None:
            self._has_redis = is_redis_available()
            if self._has_redis:
                logger.info("Connected to Redis asynchronous task broker.")
            else:
                logger.info("Redis not detected. Operating in high-performance in-process async worker mode.")
        return self._has_redis

    async def get_redis(self) -> Optional[aioredis.Redis]:
        if self.has_redis():
            if self._redis_client is None:
                self._redis_client = aioredis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
            return self._redis_client
        return None

    async def update_progress(
        self,
        document_id: str,
        progress: int,
        status: str = "PROCESSING",
        total_pages: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """Updates document progress in persistent database and distributed cache."""
        async with AsyncSessionLocal() as session:
            stmt = select(Document).where(Document.id == document_id)
            res = await session.execute(stmt)
            doc = res.scalars().first()
            if doc:
                doc.progress = progress
                doc.status = status
                if total_pages is not None:
                    doc.total_pages = total_pages
                if error_message is not None:
                    doc.error_message = error_message
                await session.commit()

        # Update Redis state if active
        redis_client = await self.get_redis()
        if redis_client:
            try:
                await redis_client.hset(
                    f"doc:{document_id}",
                    mapping={
                        "status": status,
                        "progress": str(progress),
                        "error_message": error_message or ""
                    }
                )
            except Exception as e:
                logger.warning(f"Redis state update failed: {e}")

    async def enqueue_document_job(self, document_id: str, pipeline_coro: Callable[[str], Coroutine[Any, Any, None]]):
        """Enqueues document extraction job asynchronously without blocking HTTP response."""
        redis_client = await self.get_redis()
        if redis_client:
            try:
                # Push document ID to Redis queue list
                await redis_client.rpush("queue:document_extraction", document_id)
                await self.update_progress(document_id, progress=5, status="QUEUED")
                # Also launch consumer trigger
                asyncio.create_task(pipeline_coro(document_id))
                return
            except Exception as e:
                logger.warning(f"Failed to dispatch to Redis: {e}. Falling back to async loop.")

        # In-process asynchronous task dispatch
        asyncio.create_task(pipeline_coro(document_id))

task_queue = TaskQueueManager()
