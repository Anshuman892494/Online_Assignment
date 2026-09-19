import pytest
import uuid
from pathlib import Path
import fitz  # PyMuPDF
from sqlalchemy import select
from app.core.database import init_db, AsyncSessionLocal
from app.models.document import Document
from app.models.question import Question
from app.models.answer_key import AnswerKey
from app.services.extraction_service import extraction_engine
from app.core.preprocessor import preprocessor

def create_sample_exam_pdf(file_path: Path):
    """Generates a realistic 2-page examination PDF with MCQs and answer key."""
    doc = fitz.open()

    # Page 1
    page1 = doc.new_page()
    page1_text = (
        "PRAGATI BHARATI ALL INDIA ENTRANCE EXAMINATION 2026\n"
        "SECTION A: COMPUTER SCIENCE\n\n"
        "1. What is the time complexity of searching an element in a balanced binary search tree?\n"
        "A. O(1)\n"
        "B. O(n)\n"
        "C. O(log n)\n"
        "D. O(n log n)\n\n"
        "2. Which protocol is primarily responsible for reliable, connection-oriented data transfer on the internet?\n"
        "A. UDP\n"
        "B. TCP\n"
        "C. IP\n"
        "D. ICMP\n\n"
        "3. Consider a graph with V vertices and E edges. Question continues on next page...\n"
    )
    page1.insert_text((50, 50), page1_text, fontsize=11)

    # Page 2
    page2 = doc.new_page()
    page2_text = (
        "SECTION A (CONTINUED)\n\n"
        "3. Which algorithm finds the shortest path in a weighted graph with non-negative weights?\n"
        "A. Bellman-Ford\n"
        "B. Dijkstra's Algorithm\n"
        "C. Floyd-Warshall\n"
        "D. Kruskal's Algorithm\n\n"
        "ANSWER KEY:\n"
        "1. C\n"
        "2. B\n"
        "3. B\n"
    )
    page2.insert_text((50, 50), page2_text, fontsize=11)

    doc.save(str(file_path))
    doc.close()

@pytest.mark.asyncio
async def test_preprocessor_and_question_extraction():
    await init_db()

    # 1. Create a test PDF
    temp_dir = Path("./storage/uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_dir / f"test_exam_{uuid.uuid4().hex[:8]}.pdf"
    create_sample_exam_pdf(pdf_path)

    doc_id = str(uuid.uuid4())

    # 2. Test Preprocessor
    prep_data = preprocessor.process(doc_id, str(pdf_path))
    assert prep_data.total_pages == 2
    assert prep_data.is_pdf is True
    assert len(prep_data.pages) == 2
    assert Path(prep_data.pages[0].image_path).exists()
    assert Path(prep_data.pages[1].image_path).exists()

    # 3. Create Document Record in DB
    async with AsyncSessionLocal() as session:
        db_doc = Document(
            id=doc_id,
            user_id=1,
            filename=pdf_path.name,
            original_filename="Sample_Exam.pdf",
            file_type="application/pdf",
            file_size_bytes=pdf_path.stat().st_size,
            storage_path=str(pdf_path),
            role="QUESTION_PAPER",
            status="PROCESSING",
            progress=10,
            total_pages=2,
            metadata_json={}
        )
        session.add(db_doc)
        await session.commit()

    # 4. Run Extraction Engine
    await extraction_engine.process_document(doc_id, str(pdf_path), "QUESTION_PAPER")

    # 5. Verify Database Records
    async with AsyncSessionLocal() as session:
        # Check Questions
        q_stmt = select(Question).where(Question.document_id == doc_id).order_by(Question.question_number)
        q_res = await session.execute(q_stmt)
        questions = q_res.scalars().all()

        assert len(questions) >= 3, f"Expected at least 3 questions, got {len(questions)}"

        q1 = next((q for q in questions if q.question_number == "1"), None)
        assert q1 is not None
        assert "binary search tree" in q1.question_text.lower()
        assert len(q1.options) == 4
        assert q1.answer == "C"  # Successfully linked from Answer Key section!

        q2 = next((q for q in questions if q.question_number == "2"), None)
        assert q2 is not None
        assert "TCP" in [opt["text"] for opt in q2.options]
        assert q2.answer == "B"

        # Check Answer Key Record
        ak_stmt = select(AnswerKey).where(AnswerKey.document_id == doc_id)
        ak_res = await session.execute(ak_stmt)
        ak = ak_res.scalars().first()
        assert ak is not None
        assert ak.raw_key_data.get("1") == "C"
        assert ak.raw_key_data.get("2") == "B"

    # Clean up test file
    if pdf_path.exists():
        pdf_path.unlink()
