import uuid
from typing import List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Integer, BigInteger, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.question import Question
    from app.models.answer_key import AnswerKey

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Document Role: 'QUESTION_PAPER', 'ANSWER_KEY', 'COMBINED'
    role: Mapped[str] = mapped_column(String(50), default="QUESTION_PAPER", nullable=False)
    
    # Status: 'QUEUED', 'PROCESSING', 'COMPLETED', 'FAILED'
    status: Mapped[str] = mapped_column(String(50), default="QUEUED", index=True, nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0 - 100
    total_pages: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="documents")
    questions: Mapped[List["Question"]] = relationship("Question", back_populates="document", cascade="all, delete-orphan", order_by="Question.question_number")
    answer_keys: Mapped[List["AnswerKey"]] = relationship("AnswerKey", back_populates="document", cascade="all, delete-orphan")
