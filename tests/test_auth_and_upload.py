import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db

@pytest.mark.asyncio
async def test_auth_and_upload_lifecycle():
    await init_db()

    test_email = f"phase2_{uuid.uuid4().hex[:8]}@pragatibharati.org"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "HEALTHY"

        # 2. Register user
        register_payload = {
            "email": test_email,
            "password": "StrongPassword123!",
            "full_name": "Phase2 Tester"
        }
        res = await client.post("/api/v1/auth/register", json=register_payload)
        assert res.status_code == 201

        # 3. Login
        login_payload = {
            "email": test_email,
            "password": "StrongPassword123!"
        }
        res = await client.post("/api/v1/auth/login/json", json=login_payload)
        assert res.status_code == 200
        token_data = res.json()
        assert "access_token" in token_data
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 4. Verify /me
        res = await client.get("/api/v1/auth/me", headers=headers)
        assert res.status_code == 200
        assert res.json()["email"] == test_email

        # 5. Test Invalid File Upload (Spoofed magic bytes: .pdf extension with plain text content)
        fake_pdf_content = b"This is not a real PDF file, just malicious plain text."
        files = {"file": ("malicious.pdf", fake_pdf_content, "application/pdf")}
        data = {"role": "QUESTION_PAPER"}
        res = await client.post("/api/v1/documents/upload", headers=headers, files=files, data=data)
        assert res.status_code == 400
        assert "magic byte validation failed" in res.json()["detail"]

        # 6. Test Valid PDF Upload (Proper %PDF- header)
        valid_pdf_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
        files = {"file": ("sample_exam.pdf", valid_pdf_content, "application/pdf")}
        res = await client.post("/api/v1/documents/upload", headers=headers, files=files, data=data)
        assert res.status_code == 202
        upload_resp = res.json()
        assert upload_resp["status"] == "QUEUED"
        doc_id = upload_resp["id"]

        # 7. Check Status Endpoint
        res = await client.get(f"/api/v1/documents/{doc_id}/status", headers=headers)
        assert res.status_code == 200
        status_resp = res.json()
        assert status_resp["id"] == doc_id
        assert status_resp["status"] in ["QUEUED", "PROCESSING"]

        # 8. List documents
        res = await client.get("/api/v1/documents", headers=headers)
        assert res.status_code == 200
        docs = res.json()
        assert any(d["id"] == doc_id for d in docs)
