import pytest
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.models import User, Document, Question, DocumentRelationship, AnswerKey

@pytest.mark.asyncio
async def test_database_initialization_and_crud():
    # Initialize schema
    await init_db()

    async with AsyncSessionLocal() as session:
        # Create test user
        user = User(
            email="pytest_evaluator@pragatibharati.org",
            hashed_password="hashed_evaluator_password_123",
            full_name="PyTest Evaluator",
            role="admin"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        assert user.id is not None
        assert user.email == "pytest_evaluator@pragatibharati.org"

        # Create test document
        doc = Document(
            user_id=user.id,
            filename="unit_test_paper.pdf",
            original_filename="Sample_Exam.pdf",
            file_type="application/pdf",
            file_size_bytes=2048,
            storage_path="./storage/uploads/unit_test_paper.pdf",
            role="QUESTION_PAPER",
            status="COMPLETED",
            progress=100,
            total_pages=2,
            metadata_json={"subject": "Physics"}
        )
        session.add(doc)
        await session.commit()
        await session.refresh(doc)

        assert doc.id is not None
        assert doc.status == "COMPLETED"

        # Create test question
        question = Question(
            document_id=doc.id,
            question_number="1",
            question_text="What is the unit of electric current?",
            question_type="multiple_choice",
            options=[
                {"label": "A", "text": "Volt"},
                {"label": "B", "text": "Ampere"},
                {"label": "C", "text": "Ohm"},
                {"label": "D", "text": "Joule"}
            ],
            answer="B",
            confidence_score=0.99,
            review_required=False,
            source_pages=[1]
        )
        session.add(question)
        await session.commit()
        await session.refresh(question)

        assert question.id is not None
        assert question.answer == "B"

        # Query and verify
        stmt = select(Question).where(Question.document_id == doc.id)
        result = await session.execute(stmt)
        questions = result.scalars().all()
        assert len(questions) == 1
        assert questions[0].question_number == "1"
