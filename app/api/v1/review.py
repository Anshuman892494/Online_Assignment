from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.question import Question
from app.models.answer_key import AnswerKey
from app.schemas.question import QuestionResponse
from app.schemas.review import (
    AssociateAnswerKeyRequest, AssociateAnswerKeyResponse,
    ReviewQueueResponse, AnswerKeyResponse
)
from app.services.answer_key_service import answer_key_service

router = APIRouter(prefix="/documents", tags=["Review & Answer Key"])

@router.get("/{document_id}/answer-key", response_model=AnswerKeyResponse)
async def get_document_answer_key(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves detected answer-key information for a document."""
    # Verify access
    stmt = select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    res = await db.execute(stmt)
    doc = res.scalars().first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or unauthorized.")

    # Retrieve answer key record
    ak_stmt = select(AnswerKey).where(AnswerKey.document_id == document_id)
    ak_res = await db.execute(ak_stmt)
    ak = ak_res.scalars().first()

    keys = ak.raw_key_data if ak else {}
    confidence = ak.detection_confidence if ak else 0.0

    return AnswerKeyResponse(
        document_id=document_id,
        answer_keys=keys,
        detection_confidence=confidence,
        source_document_id=document_id
    )

@router.post("/{document_id}/associate-answer-key", response_model=AssociateAnswerKeyResponse)
async def associate_answer_key(
    document_id: str,
    request: AssociateAnswerKeyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Associates an external Answer Key document with the question paper.
    Matches answers by question number and re-evaluates question confidence.
    """
    matched, unmatched = await answer_key_service.associate_answer_key_document(
        parent_document_id=document_id,
        answer_key_document_id=request.answer_key_document_id,
        user_id=current_user.id,
        db=db
    )

    return AssociateAnswerKeyResponse(
        message=f"Answer key associated successfully. {matched} questions matched, {unmatched} questions unmatched.",
        parent_document_id=document_id,
        answer_key_document_id=request.answer_key_document_id,
        matched_questions_count=matched,
        unmatched_answers_count=unmatched
    )

@router.get("/{document_id}/review-items", response_model=ReviewQueueResponse)
async def get_review_items(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Human Review Queue.
    Retrieves questions flagged with extraction warnings, missing options,
    uncertain answers, or multi-page boundary splits for human verification.
    """
    # Verify access
    stmt = select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    res = await db.execute(stmt)
    doc = res.scalars().first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or unauthorized.")

    # Fetch review items
    q_stmt = select(Question).where(
        Question.document_id == document_id,
        Question.review_required == True
    ).order_by(Question.question_number)
    q_res = await db.execute(q_stmt)
    review_questions = q_res.scalars().all()

    return ReviewQueueResponse(
        document_id=document_id,
        total_review_items=len(review_questions),
        items=[QuestionResponse.model_validate(q) for q in review_questions]
    )
