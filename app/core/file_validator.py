import os
import re
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

# Magic bytes signature mapping
MAGIC_SIGNATURES = {
    "application/pdf": [b"%PDF-"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/jpeg": [b"\xff\xd8\xff"],
}

EXTENSION_TO_MIME = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
}

def sanitize_filename(filename: str) -> str:
    """Removes path traversals, special shell characters, and ensures safe basename."""
    basename = Path(filename).name
    # Replace dangerous characters with underscore
    safe = re.sub(r'[^a-zA-Z0-9._-]', '_', basename)
    return safe[:100]  # Limit length

async def validate_and_save_upload(file: UploadFile) -> Tuple[str, str, int, str]:
    """
    Validates uploaded file against size limits and header magic byte signatures.
    Returns: (stored_filename, safe_original_name, file_size_bytes, mime_type)
    """
    original_name = file.filename or "unknown_upload"
    safe_original = sanitize_filename(original_name)
    
    # 1. Extension check
    ext = safe_original.split(".")[-1].lower() if "." in safe_original else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '.{ext}'. Supported extensions: {settings.ALLOWED_EXTENSIONS}"
        )

    expected_mime = EXTENSION_TO_MIME.get(ext)
    
    # 2. Read initial chunk for magic bytes verification
    header = await file.read(16)
    if not header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    valid_signature = False
    for signature in MAGIC_SIGNATURES.get(expected_mime, []):
        if header.startswith(signature):
            valid_signature = True
            break

    if not valid_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File content signature does not match expected {expected_mime} format (magic byte validation failed)."
        )

    # 3. Read remaining contents and check size limit
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    rest = await file.read(max_bytes + 1024)
    file_bytes = header + rest
    file_size = len(file_bytes)

    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    # 4. Save to secure storage with UUID prefix
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    doc_uuid = str(uuid.uuid4())
    stored_filename = f"{doc_uuid}_{safe_original}"
    dest_path = upload_dir / stored_filename

    with open(dest_path, "wb") as f:
        f.write(file_bytes)

    return doc_uuid, safe_original, file_size, expected_mime
