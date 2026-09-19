import logging
from typing import Dict, Any, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.document import Document
from app.models.question import Question
from app.models.answer_key import AnswerKey
from app.models.relationship import DocumentRelationship
from app.services.confidence_service import confidence_scorer

logger = logging.getLogger("document_intelligence.answer_key")

class AnswerKeyService:
    async def associate_answer_key_document(
        self,
        parent_document_id: str,
        answer_key_document_id: str,
        user_id: int,
        db: AsyncSession
    ) -> Tuple[int, int]:
        """
        Associates a separate Answer Key document with a Question Paper document.
        Matches questions by question_number, updates answers, recalculates confidence,
        and flags unmatched or ambiguous questions for review.
        """
        # 1. Verify Parent Document ownership
        stmt_parent = select(Document).where(Document.id == parent_document_id, Document.user_id == user_id)
        res_parent = await db.execute(stmt_parent)
        parent_doc = res_parent.scalars().first()
        if not parent_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent document '{parent_document_id}' not found or unauthorized."
            )

        # 2. Verify Answer Key Document ownership
        stmt_ak = select(Document).where(Document.id == answer_key_document_id, Document.user_id == user_id)
        res_ak = await db.execute(stmt_ak)
        ak_doc = res_ak.scalars().first()
        if not ak_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Answer key document '{answer_key_document_id}' not found or unauthorized."
            )

        # 3. Retrieve Answer Key data from answer_keys table
        stmt_key = select(AnswerKey).where(AnswerKey.document_id == answer_key_document_id)
        res_key = await db.execute(stmt_key)
        ak_record = res_key.scalars().first()

        key_data: Dict[str, str] = {}
        if ak_record and ak_record.raw_key_data:
            key_data = {str(k): str(v).strip().upper() for k, v in ak_record.raw_key_data.items()}
        else:
            # Check if answer key doc has questions with answers
            stmt_q = select(Question).where(Question.document_id == answer_key_document_id)
            res_q = await db.execute(stmt_q)
            for q in res_q.scalars().all():
                if q.answer:
                    key_data[str(q.question_number)] = q.answer.strip().upper()

        if not key_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No structured answer keys could be detected from the specified answer key document."
            )

        # 4. Update questions in Parent Document
        stmt_parent_q = select(Question).where(Question.document_id == parent_document_id)
        res_parent_q = await db.execute(stmt_parent_q)
        parent_questions = res_parent_q.scalars().all()

        matched_count = 0
        unmatched_count = 0

        for q in parent_questions:
            q_num = str(q.question_number)
            if q_num in key_data:
                matched_ans = key_data[q_num]
                q.answer = matched_ans
                matched_count += 1
            else:
                unmatched_count += 1

            # Recalculate confidence & review reasons
            score, review_req, reasons = confidence_scorer.evaluate_question(
                question_number=q.question_number,
                question_text=q.question_text,
                question_type=q.question_type,
                options=q.options,
                answer=q.answer,
                source_pages=q.source_pages
            )
            q.confidence_score = score
            q.review_required = review_req
            q.review_reasons = reasons

        # 5. Persist Document Relationship
        rel_stmt = select(DocumentRelationship).where(
            DocumentRelationship.parent_document_id == parent_document_id,
            DocumentRelationship.related_document_id == answer_key_document_id
        )
        rel_res = await db.execute(rel_stmt)
        existing_rel = rel_res.scalars().first()
        if not existing_rel:
            new_rel = DocumentRelationship(
                parent_document_id=parent_document_id,
                related_document_id=answer_key_document_id,
                relation_type="ANSWER_KEY_FOR"
            )
            db.add(new_rel)

        await db.commit()
        logger.info(f"Associated answer key doc {answer_key_document_id} with {parent_document_id}: {matched_count} matched, {unmatched_count} unmatched.")
        return matched_count, unmatched_count

answer_key_service = AnswerKeyService()
