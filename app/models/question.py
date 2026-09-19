import uuid
from typing import List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document

class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    
    question_number: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Question Type: 'multiple_choice', 'multi_select', 'true_false', 'numerical', 'short_answer'
    question_type: Mapped[str] = mapped_column(String(50), default="multiple_choice", nullable=False)
    
    # Options: list of {"label": "A", "text": "..."}
    options: Mapped[List[Dict[str, str]] | None] = mapped_column(JSON, nullable=True)
    
    # Answer & Explanation
    answer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    answer_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Confidence & Human Review Flagging
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    review_required: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    review_reasons: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    
    # Source Page Relationship (Preserves cross-page origins e.g. [1, 2])
    source_pages: Mapped[List[int]] = mapped_column(JSON, default=list, nullable=False)
    
    # Bounding Box / Diagram reference
    bounding_box: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    has_diagram_or_table: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    raw_extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="questions")
