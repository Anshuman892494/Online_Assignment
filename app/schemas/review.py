from typing import List, Optional
from pydantic import BaseModel
from app.schemas.question import QuestionResponse

class AssociateAnswerKeyRequest(BaseModel):
    answer_key_document_id: str

class AssociateAnswerKeyResponse(BaseModel):
    message: str
    parent_document_id: str
    answer_key_document_id: str
    matched_questions_count: int
    unmatched_answers_count: int

class ReviewQueueResponse(BaseModel):
    document_id: str
    total_review_items: int
    items: List[QuestionResponse]

class AnswerKeyResponse(BaseModel):
    document_id: str
    answer_keys: dict
    detection_confidence: float
    source_document_id: Optional[str] = None
