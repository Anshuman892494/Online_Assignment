from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from enum import Enum

class DocumentRole(str, Enum):
    QUESTION_PAPER = "QUESTION_PAPER"
    ANSWER_KEY = "ANSWER_KEY"
    COMBINED = "COMBINED"

class DocumentStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    role: str
    status: str
    progress: int
    message: str

class DocumentStatusResponse(BaseModel):
    id: str
    filename: str
    role: str
    status: str
    progress: int
    total_pages: int
    extracted_questions_count: int
    review_required_count: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentDetailResponse(BaseModel):
    id: str
    user_id: int
    filename: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    role: str
    status: str
    progress: int
    total_pages: int
    metadata_json: Dict[str, Any]
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
