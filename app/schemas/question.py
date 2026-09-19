from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    MULTI_SELECT = "multi_select"
    TRUE_FALSE = "true_false"
    NUMERICAL = "numerical"
    SHORT_ANSWER = "short_answer"

class QuestionOption(BaseModel):
    label: str = Field(..., description="Option label e.g. 'A', 'B', '1', 'i'")
    text: str = Field(..., description="Option textual content")

class QuestionBase(BaseModel):
    question_number: str
    question_text: str
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    options: Optional[List[QuestionOption]] = None
    answer: Optional[str] = None
    answer_explanation: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction reliability score")
    review_required: bool = False
    review_reasons: List[str] = Field(default_factory=list)
    source_pages: List[int] = Field(default_factory=list, description="Original page number(s) from document")
    has_diagram_or_table: bool = False

class QuestionResponse(BaseModel):
    """Standardized, system-independent structured question format conforming to Assignment Section 7."""
    id: str
    document_id: str
    question_number: str
    question_text: str
    question_type: str
    options: Optional[List[Dict[str, str]]] = None
    answer: Optional[str] = None
    answer_explanation: Optional[str] = None
    source_pages: List[int] = Field(default_factory=list)
    confidence: float
    review_required: bool
    review_reasons: List[str] = Field(default_factory=list)
    has_diagram_or_table: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class QuestionListResponse(BaseModel):
    document_id: str
    total_count: int
    questions: List[QuestionResponse]
