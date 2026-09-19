import pytest
import shutil
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def cleanup_storage_after_tests():
    """Automatically cleans up temporary test artifacts from storage after test suite runs."""
    yield
    base_dir = Path(__file__).resolve().parent.parent
    extracted_dir = base_dir / "storage" / "extracted"
    uploads_dir = base_dir / "storage" / "uploads"

    if extracted_dir.exists():
        for p in extracted_dir.iterdir():
            if p.name != ".gitkeep":
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    p.unlink(missing_ok=True)

    if uploads_dir.exists():
        for p in uploads_dir.iterdir():
            if p.name != ".gitkeep":
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    p.unlink(missing_ok=True)
