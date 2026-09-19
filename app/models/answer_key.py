import uuid
from datetime import datetime, timezone
from typing import Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.document import Document

class AnswerKey(Base):
    __tablename__ = "answer_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # Raw extracted answers dictionary e.g. {"1": "A", "2": "C"}
    raw_key_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    
    detection_confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_associated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="answer_keys")
