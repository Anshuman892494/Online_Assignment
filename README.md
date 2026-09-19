# Document Intelligence & Question Extraction Service
### Pragati Bharati — Full Stack Developer (Round 2 Engineering Assignment)

A scalable, production-oriented **Document Intelligence & Question Extraction Service** built with **FastAPI**, **PostgreSQL**, **Redis**, and **Google Gemini Multimodal Vision AI** (with an offline rule-based fallback engine). It converts unstructured examination documents (PDFs, scans, photos) into standardized, machine-readable structured questions.

Included is a **Minimalist Modern Engineering Workbench UI** conforming strictly to [`DESIGN_THEME.md`](./DESIGN_THEME.md) (Red & Orange theme, simple 1px borders, subtle 4px/6px corners, split-screen review desk, multi-tenant auth modal, and 1-click JSON export).

> 📖 **Looking for a complete step-by-step walkthrough?**  
> Check out the **[Complete Step-by-Step Usage & Run Guide (INSTRUCTIONS.md)](./INSTRUCTIONS.md)** for detailed installation, UI walkthrough, and evaluation instructions.

---

## 🚀 Key Features

1. **Robust Multi-Format Ingestion**: Supports digital multi-page PDFs, scanned low-quality PDFs, and mobile camera images (PNG, JPG, JPEG) up to 25MB with magic-byte file spoofing validation.
2. **Asynchronous Non-Blocking Processing**: Decoupled task queue architecture (Redis with automatic in-process fallback) that never blocks HTTP upload clients (`202 Accepted`).
3. **Multi-Page Spanning Question Stitching**: Seamlessly correlates question stems starting on Page $N$ with options continuing onto Page $N+1$ without fracturing items.
4. **Answer Key Association**:
   - Automatically detects embedded answer key sections.
   - Supports linking decoupled, separate Answer Key documents (`POST /api/v1/documents/{id}/associate-answer-key`).
   - Strictly flags uncertain answers with `answer: null` instead of hallucinating incorrect values.
5. **Confidence Scoring & Human Review Queue**:
   - Heuristically detects incomplete MCQ options, low OCR confidence, page-split uncertainties, and missing answers.
   - Dedicated Review Queue endpoint (`GET /api/v1/documents/{id}/review-items`).
6. **Standardized System-Independent Output**: Conforms to Assignment Section 7 schema, ready for downstream assessment engines.
7. **Complete Deliverables**: Docker Compose, Alembic Migrations, Pytest Suite (100% pass), Postman Collection, and Architecture Docs.
8. **Dual-Mode Authentication**: Seamless evaluator auto-session + interactive multi-tenant modal ([`AUTH_ARCHITECTURE.md`](./AUTH_ARCHITECTURE.md)).

---

## 🛠️ Technology Stack

- **API Layer**: FastAPI (Python 3.12/3.14), Pydantic v2, Pydantic-Settings
- **Primary Database**: PostgreSQL 16 + SQLAlchemy 2.0 + Alembic migrations *(with automatic zero-config SQLite fallback for local testing without Postgres)*
- **Task Queue & Caching**: Redis 7 *(with automatic asyncio background worker fallback)*
- **Document Preprocessing**: PyMuPDF (`fitz`), Pillow (200 DPI high-res page rendering)
- **AI / Vision Engine**: Google Gemini Multimodal Vision 2.5-Flash + Local Rule-Based Regex Fallback
- **Authentication**: JWT (OAuth2 Bearer) + 12-round Bcrypt password hashing
- **Frontend UI**: Modern Minimalist Engineering Workbench (Red & Orange Theme, Vanilla HTML5 + CSS + JS)

---

## ⚡ Quickstart (Running Locally)

### Prerequisites:
- Python 3.10+ (Tested on Python 3.12, 3.13, 3.14)
- Git

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/Anshuman892494/Online_Assignment.git
cd Online_Assignment

python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Environment Configuration
Copy the template environment file:
```bash
cp .env.example .env
```
*(Optional: If you have a Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/), add `GEMINI_API_KEY="your-key"` in `.env`. If left blank, the system automatically uses the high-performance local rule-based extraction engine).*

### 3. Run Database Migrations
```bash
alembic upgrade head
```

### 4. Start the Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Classic Retro Workbench Dashboard**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive Swagger UI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc API Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🐳 Docker Deployment (1-Click Run)

To run the complete production stack (FastAPI, PostgreSQL 16, Redis 7):

```bash
docker compose up --build
```
The API and Workbench will be available at `http://localhost:8000`.

---

## 🧪 Running Automated Tests

A comprehensive `pytest` test suite verifies all layers:

```bash
pytest -v
```
All 8 test suites will execute and pass:
- `tests/test_auth_and_upload.py`: JWT Auth, magic byte spoofing defense, size limits.
- `tests/test_database.py`: SQLAlchemy models, relationships, and CRUD operations.
- `tests/test_async_worker.py`: Asynchronous queue state machine (`QUEUED` &rarr; `PROCESSING` &rarr; `COMPLETED`).
- `tests/test_extraction.py`: Multi-page question parsing, options extraction, and PyMuPDF rendering.
- `tests/test_answer_key_and_review.py`: Decoupled answer key association and review flagging.
- `tests/test_api_surface_and_export.py`: Question filtering, human review approval, and Section 7 JSON export.
- `tests/test_retro_dashboard.py`: Serving Retro HTML5 workbench and design theme CSS.

---

## 📬 Postman API Collection

A complete Postman collection is included in [`postman_collection.json`](./postman_collection.json).
1. Open Postman &rarr; **Import** &rarr; Select `postman_collection.json`.
2. Set the collection variable `baseUrl` to `http://localhost:8000`.
3. Execute the requests in sequence:
   - `1. Authentication` &rarr; Register &rarr; Login (Token is automatically captured).
   - `2. Document Ingestion` &rarr; Upload Question Paper PDF (`sample_data/sample_digital_exam.pdf`).
   - `Track Status` &rarr; Poll status until `COMPLETED`.
   - `3. Question Extraction` &rarr; Retrieve questions and export standardized JSON.

---

## 📁 Sample Documents Included

Located in the [`sample_data/`](./sample_data/) directory:
- `sample_digital_exam.pdf`: A 2-page examination PDF with MCQs and Question 3 spanning across pages 1 and 2.
- `sample_separate_answer_key.pdf`: A decoupled Answer Key PDF for demonstrating multi-document association.
- `sample_scanned_page.png`: A scanned examination page with data tables and questions.
- `expected_output.json`: The golden structured output conforming to Assignment Section 7.

---

## 📚 Deliverables Index

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Complete Source Code** | `app/` | Production-grade modular FastAPI implementation |
| **Database Migrations** | `alembic/` | Versioned schema migrations for PostgreSQL/SQLite |
| **Sample Inputs & Outputs** | `sample_data/` | Test documents and golden output JSON |
| **Setup Instructions** | `README.md` | Complete local and Docker setup guide |
| **Architecture Documentation** | `ARCHITECTURE.md` | Detailed design, trade-offs, and scalability |
| **Automated Tests** | `tests/` | Complete Pytest automated test suite |
| **Postman Collection** | `postman_collection.json` | Ready-to-run API workflows |
| **Design Specification** | `DESIGN_THEME.md` | Classic Retro System visual identity rules |
| **Project Roadmap** | `PROJECT_PHASES.md` | 8-Phase completed tracking and git tags |
