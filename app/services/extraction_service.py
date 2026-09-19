import logging
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.document import Document
from app.services.task_queue import task_queue

logger = logging.getLogger("document_intelligence.extraction")

class ExtractionEngine:
    async def process_document(self, document_id: str, file_path: str, doc_role: str):
        """Processes document pages and computes metadata."""
        path = Path(file_path)
        total_pages = 1

        if path.suffix.lower() == ".pdf":
            try:
                doc = fitz.open(str(path))
                total_pages = len(doc)
                doc.close()
            except Exception as e:
                logger.warning(f"Could not open PDF with PyMuPDF: {e}")
        elif path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            total_pages = 1

        await task_queue.update_progress(
            document_id=document_id,
            progress=60,
            status="PROCESSING",
            total_pages=total_pages
        )

extraction_engine = ExtractionEngine()
