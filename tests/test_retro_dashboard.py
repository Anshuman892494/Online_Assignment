import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db

@pytest.mark.asyncio
async def test_retro_dashboard_serves_html_and_assets():
    await init_db()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test Root Dashboard Route
        res = await client.get("/")
        assert res.status_code == 200
        assert "text/html" in res.headers.get("content-type", "")
        assert "Document Intelligence & Question Extraction Workbench" in res.text
        assert "sys-window" in res.text

        # 2. Test Modern CSS file
        css_res = await client.get("/static/css/retro-system.css")
        assert css_res.status_code == 200
        assert "--wb-canvas: #f8fafc" in css_res.text
        assert "--wb-border: #e2e8f0" in css_res.text

        # 3. Test Retro JS Controller
        js_res = await client.get("/static/js/workbench.js")
        assert js_res.status_code == 200
        assert "CLASSIC RETRO WORKBENCH CONTROLLER" in js_res.text
