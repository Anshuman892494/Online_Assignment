from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.question import Question
from app.schemas.question import QuestionResponse, QuestionListResponse

router = APIRouter(prefix="/documents", tags=["Questions & Extraction API"])

class QuestionUpdateSchema(BaseModel):
    question_text: Optional[str] = None
    options: Optional[List[Dict[str, str]]] = None
    answer: Optional[str] = None
    answer_explanation: Optional[str] = None
    review_required: Optional[bool] = None

class StandardExportQuestion(BaseModel):
    id: str
    question_number: str
    question: str
    question_type: str
    options: Optional[List[Dict[str, str]]] = None
    answer: Optional[str] = None
    source_pages: List[int]
    confidence: float
    review_required: bool
    review_reasons: List[str]

class StandardDocumentExportResponse(BaseModel):
    document_id: str
    filename: str
    total_questions: int
    review_required_count: int
    questions: List[StandardExportQuestion]

@router.get("/{document_id}/questions", response_model=QuestionListResponse)
async def get_document_questions(
    document_id: str,
    page: Optional[int] = Query(None, description="Filter by source page number"),
    review_required: Optional[bool] = Query(None, description="Filter by review flag"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence threshold"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves extracted questions for a document with optional filtering:
    - by source page
    - by review status
    - by minimum confidence score
    """
    # Verify access
    doc_stmt = select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    doc_res = await db.execute(doc_stmt)
    doc = doc_res.scalars().first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or unauthorized.")

    stmt = select(Question).where(Question.document_id == document_id)
    if review_required is not None:
        stmt = stmt.where(Question.review_required == review_required)
    if min_confidence is not None:
        stmt = stmt.where(Question.confidence_score >= min_confidence)

    # Order by question_number
    stmt = stmt.order_by(Question.question_number).offset(offset).limit(limit)
    res = await db.execute(stmt)
    questions = res.scalars().all()

    # If page filter requested, filter in-memory for JSON column compatibility across SQLite & Postgres
    if page is not None:
        questions = [q for q in questions if page in (q.source_pages or [])]

    # Total count
    count_stmt = select(func.count(Question.id)).where(Question.document_id == document_id)
    count_res = await db.execute(count_stmt)
    total_count = count_res.scalar() or 0

    return QuestionListResponse(
        document_id=document_id,
        total_count=total_count,
        questions=[QuestionResponse.model_validate(q) for q in questions]
    )

@router.get("/{document_id}/questions/{question_id}", response_model=QuestionResponse)
async def get_single_question(
    document_id: str,
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves individual question details and source metadata."""
    # Verify doc access
    doc_stmt = select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    doc_res = await db.execute(doc_stmt)
    if not doc_res.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or unauthorized.")

    stmt = select(Question).where(Question.id == question_id, Question.document_id == document_id)
    res = await db.execute(stmt)
    q = res.scalars().first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")

    return QuestionResponse.model_validate(q)

@router.patch("/{document_id}/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    document_id: str,
    question_id: str,
    update_data: QuestionUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Allows a human reviewer to edit text, verify answers, and approve questions."""
    doc_stmt = select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    doc_res = await db.execute(doc_stmt)
    if not doc_res.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or unauthorized.")

    stmt = select(Question).where(Question.id == question_id, Question.document_id == document_id)
    res = await db.execute(stmt)
    q = res.scalars().first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")

    if update_data.question_text is not None:
        q.question_text = update_data.question_text
    if update_data.options is not None:
        q.options = update_data.options
    if update_data.answer is not None:
        q.answer = update_data.answer
    if update_data.answer_explanation is not None:
        q.answer_explanation = update_data.answer_explanation
    if update_data.review_required is not None:
        q.review_required = update_data.review_required
        if not update_data.review_required:
            q.review_reasons = []
            q.confidence_score = 1.0

    await db.commit()
    await db.refresh(q)
    return QuestionResponse.model_validate(q)

@router.get("/{document_id}/export", response_model=StandardDocumentExportResponse)
async def export_document_structured_json(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Standardized, System-Independent JSON Export conforming to Assignment Section 7.
    Can be seamlessly consumed by downstream examination platforms.
    """
    # Verify doc access
    doc_stmt = select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    doc_res = await db.execute(doc_stmt)
    doc = doc_res.scalars().first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or unauthorized.")

    q_stmt = select(Question).where(Question.document_id == document_id).order_by(Question.question_number)
    q_res = await db.execute(q_stmt)
    questions = q_res.scalars().all()

    export_items: List[StandardExportQuestion] = []
    review_count = 0

    for q in questions:
        if q.review_required:
            review_count += 1
        export_items.append(
            StandardExportQuestion(
                id=q.id,
                question_number=q.question_number,
                question=q.question_text,
                question_type=q.question_type,
                options=q.options,
                answer=q.answer,
                source_pages=q.source_pages or [1],
                confidence=q.confidence_score,
                review_required=q.review_required,
                review_reasons=q.review_reasons or []
            )
        )

    return StandardDocumentExportResponse(
        document_id=doc.id,
        filename=doc.original_filename,
        total_questions=len(export_items),
        review_required_count=review_count,
        questions=export_items
    )
