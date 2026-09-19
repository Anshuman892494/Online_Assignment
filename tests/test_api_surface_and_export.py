import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db, AsyncSessionLocal
from app.models.document import Document
from app.models.question import Question

@pytest.mark.asyncio
async def test_questions_api_and_standard_export():
    await init_db()

    test_email = f"api_test_{uuid.uuid4().hex[:8]}@pragatibharati.org"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register & Login
        await client.post("/api/v1/auth/register", json={
            "email": test_email,
            "password": "ApiTestPassword123!",
            "full_name": "API Tester"
        })
        login_res = await client.post("/api/v1/auth/login/json", json={
            "email": test_email,
            "password": "ApiTestPassword123!"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get User ID
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        user_id = me_res.json()["id"]

        # 2. Seed Document & Questions
        doc_id = str(uuid.uuid4())
        q1_id = str(uuid.uuid4())
        q2_id = str(uuid.uuid4())

        async with AsyncSessionLocal() as session:
            doc = Document(
                id=doc_id,
                user_id=user_id,
                filename="physics_exam.pdf",
                original_filename="Physics_Exam_2026.pdf",
                file_type="application/pdf",
                file_size_bytes=2048,
                storage_path="./storage/uploads/physics_exam.pdf",
                role="QUESTION_PAPER",
                status="COMPLETED",
                progress=100,
                total_pages=2,
                metadata_json={"subject": "Physics"}
            )
            session.add(doc)

            q1 = Question(
                id=q1_id,
                document_id=doc_id,
                question_number="1",
                question_text="What is the speed of light in vacuum?",
                question_type="multiple_choice",
                options=[
                    {"label": "A", "text": "3 x 10^8 m/s"},
                    {"label": "B", "text": "3 x 10^6 m/s"},
                    {"label": "C", "text": "3 x 10^5 km/s"},
                    {"label": "D", "text": "Both A and C"}
                ],
                answer="D",
                confidence_score=0.98,
                review_required=False,
                review_reasons=[],
                source_pages=[1]
            )
            q2 = Question(
                id=q2_id,
                document_id=doc_id,
                question_number="2",
                question_text="Define Newton's Second Law of Motion.",
                question_type="short_answer",
                options=None,
                answer=None,
                confidence_score=0.70,
                review_required=True,
                review_reasons=["UNMATCHED_ANSWER", "SHORT_ANSWER_SUBJECTIVE"],
                source_pages=[1, 2]
            )
            session.add_all([q1, q2])
            await session.commit()

        # 3. Test GET /documents/{id}/questions
        res = await client.get(f"/api/v1/documents/{doc_id}/questions", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total_count"] == 2
        assert len(data["questions"]) == 2

        # 4. Test Filter ?review_required=true
        res_filter = await client.get(f"/api/v1/documents/{doc_id}/questions?review_required=true", headers=headers)
        assert res_filter.status_code == 200
        filtered = res_filter.json()["questions"]
        assert len(filtered) == 1
        assert filtered[0]["id"] == q2_id

        # 5. Test Single Question GET /documents/{id}/questions/{q_id}
        res_single = await client.get(f"/api/v1/documents/{doc_id}/questions/{q1_id}", headers=headers)
        assert res_single.status_code == 200
        assert res_single.json()["question_number"] == "1"
        assert res_single.json()["answer"] == "D"

        # 6. Test PATCH /documents/{id}/questions/{q_id} (Human Review Approval)
        patch_res = await client.patch(
            f"/api/v1/documents/{doc_id}/questions/{q2_id}",
            headers=headers,
            json={"answer": "F = ma", "review_required": False}
        )
        assert patch_res.status_code == 200
        patched = patch_res.json()
        assert patched["answer"] == "F = ma"
        assert patched["review_required"] is False
        assert patched["confidence"] == 1.0

        # 7. Test Standard Export /documents/{id}/export (Conforming to Section 7)
        export_res = await client.get(f"/api/v1/documents/{doc_id}/export", headers=headers)
        assert export_res.status_code == 200
        exp_data = export_res.json()
        assert exp_data["document_id"] == doc_id
        assert exp_data["filename"] == "Physics_Exam_2026.pdf"
        assert exp_data["total_questions"] == 2
        assert exp_data["review_required_count"] == 0  # Because Q2 was approved
        assert len(exp_data["questions"]) == 2
        assert "source_pages" in exp_data["questions"][0]
        assert "confidence" in exp_data["questions"][0]

        # 8. Test DELETE /documents/{id}
        del_res = await client.delete(f"/api/v1/documents/{doc_id}", headers=headers)
        assert del_res.status_code == 200
        assert del_res.json()["status"] == "SUCCESS"

        # Verify Document no longer exists
        get_res = await client.get(f"/api/v1/documents/{doc_id}", headers=headers)
        assert get_res.status_code == 404

        # 9. Test DELETE /documents (Clear All)
        clear_res = await client.delete("/api/v1/documents", headers=headers)
        assert clear_res.status_code == 200
        assert clear_res.json()["status"] == "SUCCESS"
