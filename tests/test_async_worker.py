import asyncio
import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db
from app.services.worker import process_document_task
from app.services.task_queue import task_queue

@pytest.mark.asyncio
async def test_async_task_lifecycle_and_status_tracking():
    await init_db()

    test_email = f"worker_test_{uuid.uuid4().hex[:8]}@pragatibharati.org"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register & Login
        await client.post("/api/v1/auth/register", json={
            "email": test_email,
            "password": "WorkerTestPassword123!",
            "full_name": "Worker Tester"
        })
        login_res = await client.post("/api/v1/auth/login/json", json={
            "email": test_email,
            "password": "WorkerTestPassword123!"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Upload valid PDF
        valid_pdf_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
        files = {"file": ("worker_exam.pdf", valid_pdf_content, "application/pdf")}
        data = {"role": "QUESTION_PAPER"}
        upload_res = await client.post("/api/v1/documents/upload", headers=headers, files=files, data=data)
        assert upload_res.status_code == 202
        doc_id = upload_res.json()["id"]

        # 3. Wait briefly for background task to execute
        await asyncio.sleep(0.5)

        # 4. Check Status (Should be COMPLETED or PROCESSING)
        status_res = await client.get(f"/api/v1/documents/{doc_id}/status", headers=headers)
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["id"] == doc_id
        assert status_data["status"] in ["PROCESSING", "COMPLETED"]
        assert status_data["progress"] > 0

        # Wait until COMPLETED
        for _ in range(10):
            if status_data["status"] == "COMPLETED":
                break
            await asyncio.sleep(0.2)
            status_res = await client.get(f"/api/v1/documents/{doc_id}/status", headers=headers)
            status_data = status_res.json()

        assert status_data["status"] == "COMPLETED"
        assert status_data["progress"] == 100

@pytest.mark.asyncio
async def test_worker_error_handling():
    await init_db()
    # Test processing non-existent document ID
    non_existent_id = str(uuid.uuid4())
    # Should not crash, will log error and return
    await process_document_task(non_existent_id)
