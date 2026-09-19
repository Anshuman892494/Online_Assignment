import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
from PIL import Image
from pydantic import BaseModel
from app.core.config import settings

logger = logging.getLogger("document_intelligence.preprocessor")

class PageArtifact(BaseModel):
    page_number: int  # 1-indexed
    text: str
    image_path: str
    has_digital_text: bool
    width: float
    height: float

class DocumentPreprocessedData(BaseModel):
    document_id: str
    total_pages: int
    is_pdf: bool
    pages: List[PageArtifact]
    full_digital_text: str

class DocumentPreprocessor:
    """
    High-Performance Document Ingestion & Page Normalizer.
    Converts PDFs and images into structured page text and high-resolution vision images.
    """
    def __init__(self, output_dir: str = settings.EXTRACTED_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process(self, document_id: str, file_path: str) -> DocumentPreprocessedData:
        path = Path(file_path)
        doc_dir = self.output_dir / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)

        pages: List[PageArtifact] = []
        is_pdf = path.suffix.lower() == ".pdf"
        full_text_parts = []

        if is_pdf:
            pdf_doc = fitz.open(str(path))
            total_pages = len(pdf_doc)

            for page_idx in range(total_pages):
                page = pdf_doc[page_idx]
                page_num = page_idx + 1

                # 1. Extract digital text
                page_text = page.get_text("text").strip()
                has_digital = len(page_text) > 20
                if page_text:
                    full_text_parts.append(f"--- PAGE {page_num} ---\n{page_text}")

                # 2. Render high-resolution page image (300 DPI for crystal clear OCR & diagram understanding)
                pix = page.get_pixmap(dpi=200)
                img_path = doc_dir / f"page_{page_num}.png"
                pix.save(str(img_path))

                rect = page.rect
                pages.append(
                    PageArtifact(
                        page_number=page_num,
                        text=page_text,
                        image_path=str(img_path),
                        has_digital_text=has_digital,
                        width=rect.width,
                        height=rect.height
                    )
                )

            pdf_doc.close()
        else:
            # Single Image (PNG / JPEG / JPG)
            total_pages = 1
            img = Image.open(str(path))
            img_path = doc_dir / "page_1.png"
            img.convert("RGB").save(str(img_path))
            
            w, h = img.size
            pages.append(
                PageArtifact(
                    page_number=1,
                    text="",
                    image_path=str(img_path),
                    has_digital_text=False,
                    width=float(w),
                    height=float(h)
                )
            )

        return DocumentPreprocessedData(
            document_id=document_id,
            total_pages=total_pages,
            is_pdf=is_pdf,
            pages=pages,
            full_digital_text="\n\n".join(full_text_parts)
        )

preprocessor = DocumentPreprocessor()
