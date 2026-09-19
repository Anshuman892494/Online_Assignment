import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from app.main import app
from app.core.database import init_db, AsyncSessionLocal
from app.models.document import Document
from app.models.question import Question
from app.models.answer_key import AnswerKey

@pytest.mark.asyncio
async def test_answer_key_and_review_workflow():
    await init_db()

    test_email = f"review_test_{uuid.uuid4().hex[:8]}@pragatibharati.org"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register & Login
        await client.post("/api/v1/auth/register", json={
            "email": test_email,
            "password": "ReviewTestPassword123!",
            "full_name": "Review Tester"
        })
        login_res = await client.post("/api/v1/auth/login/json", json={
            "email": test_email,
            "password": "ReviewTestPassword123!"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get User ID
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        user_id = me_res.json()["id"]

        # 2. Create Question Paper document in DB
        qp_id = str(uuid.uuid4())
        ak_doc_id = str(uuid.uuid4())

        async with AsyncSessionLocal() as session:
            qp_doc = Document(
                id=qp_id,
                user_id=user_id,
                filename="exam_paper.pdf",
                original_filename="exam_paper.pdf",
                file_type="application/pdf",
                file_size_bytes=1024,
                storage_path="./storage/uploads/exam_paper.pdf",
                role="QUESTION_PAPER",
                status="COMPLETED",
                progress=100,
                total_pages=1,
                metadata_json={}
            )
            ak_doc = Document(
                id=ak_doc_id,
                user_id=user_id,
                filename="answer_key.pdf",
                original_filename="answer_key.pdf",
                file_type="application/pdf",
                file_size_bytes=512,
                storage_path="./storage/uploads/answer_key.pdf",
                role="ANSWER_KEY",
                status="COMPLETED",
                progress=100,
                total_pages=1,
                metadata_json={}
            )
            session.add_all([qp_doc, ak_doc])

            # Add Questions to Question Paper (Q1 with no answer, Q2 with incomplete options)
            q1 = Question(
                document_id=qp_id,
                question_number="1",
                question_text="What is the capital of India?",
                question_type="multiple_choice",
                options=[
                    {"label": "A", "text": "Mumbai"},
                    {"label": "B", "text": "New Delhi"},
                    {"label": "C", "text": "Kolkata"},
                    {"label": "D", "text": "Chennai"}
                ],
                answer=None,  # Unmatched
                confidence_score=0.80,
                review_required=True,
                review_reasons=["UNMATCHED_ANSWER"],
                source_pages=[1]
            )
            q2 = Question(
                document_id=qp_id,
                question_number="2",
                question_text="Which planet is known as the Red Planet?",
                question_type="multiple_choice",
                options=[
                    {"label": "A", "text": "Venus"},
                    {"label": "B", "text": "Mars"}  # Incomplete options (only 2)
                ],
                answer=None,
                confidence_score=0.60,
                review_required=True,
                review_reasons=["INCOMPLETE_MCQ_OPTIONS", "UNMATCHED_ANSWER"],
                source_pages=[1]
            )
            session.add_all([q1, q2])

            # Add Answer Key record to Answer Key Document
            ak_record = AnswerKey(
                document_id=ak_doc_id,
                raw_key_data={"1": "B", "2": "B"},
                detection_confidence=0.98,
                is_associated=False
            )
            session.add(ak_record)
            await session.commit()

        # 3. Check Review Items Endpoint
        rev_res = await client.get(f"/api/v1/documents/{qp_id}/review-items", headers=headers)
        assert rev_res.status_code == 200
        rev_data = rev_res.json()
        assert rev_data["total_review_items"] == 2

        # 4. Associate Separate Answer Key Document
        assoc_res = await client.post(
            f"/api/v1/documents/{qp_id}/associate-answer-key",
            headers=headers,
            json={"answer_key_document_id": ak_doc_id}
        )
        assert assoc_res.status_code == 200
        assoc_data = assoc_res.json()
        assert assoc_data["matched_questions_count"] == 2
        assert assoc_data["unmatched_answers_count"] == 0

        # 5. Verify Q1 now has answer='B' and review_required=False
        async with AsyncSessionLocal() as session:
            stmt = select(Question).where(Question.document_id == qp_id, Question.question_number == "1")
            res = await session.execute(stmt)
            updated_q1 = res.scalars().first()
            assert updated_q1.answer == "B"
            assert updated_q1.review_required is False
            assert updated_q1.confidence_score >= 0.95

            # Q2 should now have answer='B', but still review_required=True because it only has 2 options!
            stmt2 = select(Question).where(Question.document_id == qp_id, Question.question_number == "2")
            res2 = await session.execute(stmt2)
            updated_q2 = res2.scalars().first()
            assert updated_q2.answer == "B"
            assert updated_q2.review_required is True  # Still flagged due to missing options!
            assert any("MISSING_OPTION" in r or "FEWER" in r for r in updated_q2.review_reasons)
