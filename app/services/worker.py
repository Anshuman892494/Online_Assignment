import asyncio
import logging
from pathlib import Path
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.document import Document
from app.services.task_queue import task_queue

logger = logging.getLogger("document_intelligence.worker")

async def process_document_task(document_id: str):
    """
    Asynchronous Document Processing Task Orchestrator.
    Handles lifecycle: QUEUED -> PROCESSING (progress steps) -> COMPLETED or FAILED.
    """
    logger.info(f"Worker picked up document task: {document_id}")
    try:
        # 1. Transition to PROCESSING
        await task_queue.update_progress(document_id, progress=10, status="PROCESSING")

        # 2. Retrieve document metadata
        async with AsyncSessionLocal() as session:
            stmt = select(Document).where(Document.id == document_id)
            res = await session.execute(stmt)
            document = res.scalars().first()
            if not document:
                logger.error(f"Document {document_id} not found in database.")
                return
            file_path = document.storage_path
            doc_role = document.role

        await task_queue.update_progress(document_id, progress=30, status="PROCESSING")

        # 3. Process Document
        from app.services.extraction_service import extraction_engine
        await extraction_engine.process_document(document_id, file_path, doc_role)

        # 4. Completion
        await task_queue.update_progress(document_id, progress=100, status="COMPLETED")
        logger.info(f"Document {document_id} successfully processed and marked COMPLETED.")

    except Exception as exc:
        logger.exception(f"Processing failed for document {document_id}: {exc}")
        await task_queue.update_progress(
            document_id,
            progress=0,
            status="FAILED",
            error_message=str(exc)
        )
