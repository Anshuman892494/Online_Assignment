from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.file_validator import validate_and_save_upload
from app.core.config import settings
from app.models.user import User
from app.models.document import Document
from app.models.question import Question
from app.models.relationship import DocumentRelationship
from app.schemas.document import (
    DocumentUploadResponse, DocumentStatusResponse, DocumentDetailResponse, DocumentRole
)

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(..., description="PDF or Image file (Max 25MB)"),
    role: DocumentRole = Form(DocumentRole.QUESTION_PAPER, description="Document type: QUESTION_PAPER, ANSWER_KEY, or COMBINED"),
    related_document_id: Optional[str] = Form(None, description="Optional ID of related question paper or answer key"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Secure Document Ingestion Gateway.
    - Validates MIME type via file header magic bytes
    - Enforces 25MB size limit
    - Sanitizes and stores file securely
    - Queues document for asynchronous processing (HTTP 202 Accepted)
    """
    # 1. Validate magic bytes, size, and save securely
    doc_id, safe_name, file_size, mime_type = await validate_and_save_upload(file)
    stored_path = str(Path(settings.UPLOAD_DIR) / f"{doc_id}_{safe_name}")

    # 2. Persist Document record
    document = Document(
        id=doc_id,
        user_id=current_user.id,
        filename=f"{doc_id}_{safe_name}",
        original_filename=safe_name,
        file_type=mime_type,
        file_size_bytes=file_size,
        storage_path=stored_path,
        role=role.value,
        status="QUEUED",
        progress=0,
        total_pages=1,
        metadata_json={
            "uploader": current_user.email,
            "original_filename": safe_name
        }
    )
    db.add(document)

    # 3. Create relationship if related_document_id is provided
    if related_document_id:
        stmt = select(Document).where(Document.id == related_document_id, Document.user_id == current_user.id)
        res = await db.execute(stmt)
        related_doc = res.scalars().first()
        if related_doc:
            rel = DocumentRelationship(
                parent_document_id=related_document_id,
                related_document_id=doc_id,
                relation_type="ANSWER_KEY_FOR" if role == DocumentRole.ANSWER_KEY else "SUPPLEMENT_TO"
            )
            db.add(rel)

    await db.commit()
    await db.refresh(document)

    # 4. Enqueue Asynchronous Processing Task (Redis or async background loop)
    from app.services.task_queue import task_queue
    from app.services.worker import process_document_task
    await task_queue.enqueue_document_job(document.id, process_document_task)

    return DocumentUploadResponse(
        id=document.id,
        filename=document.original_filename,
        role=document.role,
        status=document.status,
        progress=document.progress,
        message="Document accepted and queued for asynchronous intelligence extraction."
    )

@router.get("", response_model=List[DocumentStatusResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all documents uploaded by the authenticated user."""
    stmt = select(Document).where(Document.user_id == current_user.id).order_by(Document.created_at.desc())
    result = await db.execute(stmt)
    documents = result.scalars().all()

    response_list = []
    for doc in documents:
        # Count questions and review items
        q_count_res = await db.execute(select(func.count(Question.id)).where(Question.document_id == doc.id))
        total_q = q_count_res.scalar() or 0

        rev_count_res = await db.execute(
            select(func.count(Question.id)).where(Question.document_id == doc.id, Question.review_required == True)
        )
        total_rev = rev_count_res.scalar() or 0

        response_list.append(
            DocumentStatusResponse(
                id=doc.id,
                filename=doc.original_filename,
                role=doc.role,
                status=doc.status,
                progress=doc.progress,
                total_pages=doc.total_pages,
                extracted_questions_count=total_q,
                review_required_count=total_rev,
                error_message=doc.error_message,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )
        )
    return response_list

@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Tracks asynchronous processing status and progress for a document."""
    stmt = select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    result = await db.execute(stmt)
    doc = result.scalars().first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access unauthorized."
        )

    q_count_res = await db.execute(select(func.count(Question.id)).where(Question.document_id == doc.id))
    total_q = q_count_res.scalar() or 0

    rev_count_res = await db.execute(
        select(func.count(Question.id)).where(Question.document_id == doc.id, Question.review_required == True)
    )
    total_rev = rev_count_res.scalar() or 0

    return DocumentStatusResponse(
        id=doc.id,
        filename=doc.original_filename,
        role=doc.role,
        status=doc.status,
        progress=doc.progress,
        total_pages=doc.total_pages,
        extracted_questions_count=total_q,
        review_required_count=total_rev,
        error_message=doc.error_message,
        created_at=doc.created_at,
        updated_at=doc.updated_at
    )

@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document_detail(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves detailed metadata for a specific document."""
    stmt = select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    result = await db.execute(stmt)
    doc = result.scalars().first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access unauthorized."
        )
    return doc

import shutil
from sqlalchemy import delete

@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deletes a document, cascading associated questions, answer keys, and disk files."""
    stmt = select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    result = await db.execute(stmt)
    doc = result.scalars().first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access unauthorized."
        )

    # Clean relationships
    await db.execute(
        delete(DocumentRelationship).where(
            (DocumentRelationship.parent_document_id == document_id) |
            (DocumentRelationship.related_document_id == document_id)
        )
    )

    # Clean physical files on disk
    if doc.storage_path and Path(doc.storage_path).exists():
        try:
            Path(doc.storage_path).unlink(missing_ok=True)
        except Exception:
            pass

    extracted_folder = Path(settings.EXTRACTED_DIR) / document_id
    if extracted_folder.exists():
        try:
            shutil.rmtree(extracted_folder, ignore_errors=True)
        except Exception:
            pass

    # Delete Document (cascades questions and answer keys)
    await db.delete(doc)
    await db.commit()

    return {"status": "SUCCESS", "message": f"Document {document_id} deleted successfully."}

@router.delete("", status_code=status.HTTP_200_OK)
async def clear_all_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deletes all documents and extracted data for the currently authenticated user."""
    stmt = select(Document).where(Document.user_id == current_user.id)
    result = await db.execute(stmt)
    docs = result.scalars().all()

    count = len(docs)
    for doc in docs:
        # Clean relationships
        await db.execute(
            delete(DocumentRelationship).where(
                (DocumentRelationship.parent_document_id == doc.id) |
                (DocumentRelationship.related_document_id == doc.id)
            )
        )
        # Clean files
        if doc.storage_path and Path(doc.storage_path).exists():
            try:
                Path(doc.storage_path).unlink(missing_ok=True)
            except Exception:
                pass
        extracted_folder = Path(settings.EXTRACTED_DIR) / doc.id
        if extracted_folder.exists():
            try:
                shutil.rmtree(extracted_folder, ignore_errors=True)
            except Exception:
                pass
        await db.delete(doc)

    await db.commit()
    return {"status": "SUCCESS", "message": f"Successfully cleared {count} documents from archive."}
