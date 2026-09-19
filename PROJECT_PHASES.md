# PROJECT PHASES & MASTER ROADMAP

**Project:** Document Intelligence & Question Extraction Service  
**Organization:** Pragati Bharati (Round 2 — Full Stack Developer Assignment)  
**Remote Git Repository:** [https://github.com/Anshuman892494/Online_Assignment.git](https://github.com/Anshuman892494/Online_Assignment.git)  
**Status Tracking:** Updated after every phase and committed to Git.

---

## 🧭 Phase Overview & Status Tracker

| Phase | Description | Status | Git Commit Tag |
| :--- | :--- | :--- | :--- |
| **Phase 0** | Project Setup, Git Initialization, Master Roadmap & Design Theme System | 🟢 COMPLETED | `phase-0-setup` |
| **Phase 1** | Database Architecture, SQLAlchemy Models & Alembic Migrations | 🟢 COMPLETED | `phase-1-database` |
| **Phase 2** | Security, JWT Authentication & Secure Ingestion Gateway | ⚪ PENDING | `phase-2-auth-ingestion` |
| **Phase 3** | Asynchronous Task Queue, Worker Engine & Status Tracking | ⚪ PENDING | `phase-3-async-worker` |
| **Phase 4** | Document Processing, PyMuPDF Preprocessor & Gemini Multimodal Vision AI | ⚪ PENDING | `phase-4-ai-extraction` |
| **Phase 5** | Answer Key Linker, Heuristic Confidence Scorer & Human Review Queue | ⚪ PENDING | `phase-5-review-engine` |
| **Phase 6** | Complete REST API Surface, Validation & Structured Export | ⚪ PENDING | `phase-6-api-surface` |
| **Phase 7** | Old-Fashioned Retro System Web Dashboard (Strict Design Theme) | ⚪ PENDING | `phase-7-retro-dashboard` |
| **Phase 8** | Sample Documents, Automated Tests, Postman Collection & Architecture Docs | ⚪ PENDING | `phase-8-deliverables` |

---

## 📌 Detailed Phase Specifications

### 🔹 Phase 0: Project Setup, Git Initialization & Design System
- **Objective:** Establish clean repository foundation, environment configs, and theme documentation.
- **Tasks:**
  1. Initialize Git repository with `main` branch connected to `https://github.com/Anshuman892494/Online_Assignment.git`.
  2. Create comprehensive `.gitignore` for Python, Node, Virtualenv, Database, and OS files.
  3. Create `PROJECT_PHASES.md` (this file) with phase tracking and requirements mapping.
  4. Create `DESIGN_THEME.md` specifying the mandatory **Old-Fashioned / Classic Retro System UI** design rules.
  5. Create `requirements.txt` with all pinned dependencies.
  6. Create `.env.example` with environment variable templates.
  7. Commit and push Phase 0 to GitHub remote.

---

### 🔹 Phase 1: Database Architecture, SQLAlchemy Models & Alembic Migrations
- **Objective:** Build robust relational schema with JSONB support adhering to PostgreSQL constraint.
- **Tasks:**
  1. Setup database configuration (`app/core/database.py`) supporting PostgreSQL (asyncpg/psycopg) with automatic SQLite fallback for zero-dependency evaluator testing.
  2. Implement SQLAlchemy 2.0 ORM models:
     - `User`: ID, email, hashed password, role, timestamps.
     - `Document`: UUID, user_id, filename, file_type, file_size, storage_path, role (`QUESTION_PAPER`, `ANSWER_KEY`, `COMBINED`), status (`QUEUED`, `PROCESSING`, `COMPLETED`, `FAILED`), progress, page_count.
     - `DocumentRelationship`: Links separate question papers and answer keys (`ANSWER_KEY_FOR`, `SUPPLEMENT_TO`).
     - `Question`: UUID, document_id, question_number, question_text, question_type (`MCQ`, `TRUE_FALSE`, `NUMERICAL`, `SHORT_ANSWER`), options (JSONB), answer, answer_explanation, confidence_score, review_required, review_reasons, source_pages, metadata_json.
     - `AnswerKey`: UUID, document_id, raw_key_data, confidence, is_associated.
  3. Configure Alembic migration framework (`alembic/`) and generate initial migration script.
  4. Commit and push Phase 1 to GitHub remote.

---

### 🔹 Phase 2: Security, JWT Authentication & Secure Ingestion Gateway
- **Objective:** Implement tenant-isolated authentication and tamper-proof file ingestion.
- **Tasks:**
  1. Implement password hashing with bcrypt and JWT generation/validation (`app/core/security.py`).
  2. Build Auth API endpoints (`POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`).
  3. Implement file validator (`app/core/file_validator.py`):
     - Magic bytes MIME type validation (disallows malicious disguised files).
     - File size limit (25MB max).
     - Supported formats: PDF, JPEG, JPG, PNG.
     - UUID-based sanitized storage saving to `storage/uploads/`.
  4. Implement `POST /api/v1/documents/upload` endpoint returning `202 Accepted` with initial status.
  5. Commit and push Phase 2 to GitHub remote.

---

### 🔹 Phase 3: Asynchronous Task Queue, Worker Engine & Status Tracking
- **Objective:** Enable non-blocking asynchronous processing with real-time status reporting.
- **Tasks:**
  1. Build Task Queue manager supporting Redis (with automatic background task fallback for local zero-config evaluation).
  2. Implement worker state machine: `QUEUED` -> `PROCESSING` (0-100% progress) -> `COMPLETED` / `FAILED`.
  3. Build status tracking endpoint `GET /api/v1/documents/{id}/status`.
  4. Build error recovery and graceful failure logging.
  5. Commit and push Phase 3 to GitHub remote.

---

### 🔹 Phase 4: Document Processing, PyMuPDF Preprocessor & Gemini Multimodal Vision AI
- **Objective:** Convert complex PDFs and images into structured question items.
- **Tasks:**
  1. Build preprocessor (`app/core/preprocessor.py`) using `PyMuPDF` (`fitz`):
     - Extract embedded digital text layers.
     - Render high-resolution page images (300 DPI) for vision models.
     - Page count, orientation detection, and deskew support.
  2. Build Extraction Engine (`app/services/extraction_service.py`):
     - Gemini Multimodal Vision API integration (`gemini-2.5-flash` or `gemini-1.5-flash`).
     - Multi-page spanning question stitching (detects questions starting on page N and ending on page N+1).
     - Option parser for all numbering formats (`A.`, `(a)`, `1)`, `[A]`, `(i)`).
     - Math formulas (LaTeX) and table preservation.
     - Offline rule-based regex parser fallback for air-gapped environments.
  3. Commit and push Phase 4 to GitHub remote.

---

### 🔹 Phase 5: Answer Key Linker, Heuristic Confidence Scorer & Human Review Queue
- **Objective:** Associate answers and intelligently flag questionable extractions.
- **Tasks:**
  1. Build Answer Key Engine (`app/services/answer_key_service.py`):
     - Detect embedded answer keys (at beginning, end, or scattered).
     - Support linking separate Answer Key document via `POST /api/v1/documents/{id}/associate-answer-key`.
     - Associate questions to answers with verification; flag uncertain matches with `answer: null`.
  2. Build Confidence & Review Scorer (`app/services/confidence_service.py`):
     - Heuristic rules: Missing MCQ options, non-sequential numbering, page-split uncertainty, missing answers.
     - Confidence score calculation (0.0 to 1.0).
     - Flagging items with `review_required=True` and specific `review_reasons`.
  3. Build review items endpoint `GET /api/v1/documents/{id}/review-items`.
  4. Commit and push Phase 5 to GitHub remote.

---

### 🔹 Phase 6: Complete REST API Surface, Validation & Structured Export
- **Objective:** Expose complete API surface complying with Section 11 & Section 7 of the assignment.
- **Tasks:**
  1. Implement remaining endpoints:
     - `GET /api/v1/documents` (List with filters).
     - `GET /api/v1/documents/{id}` (Document detail).
     - `GET /api/v1/documents/{id}/questions` (Questions with pagination & confidence filters).
     - `GET /api/v1/documents/{id}/questions/{question_id}` (Single question details).
     - `GET /api/v1/documents/{id}/answer-key` (Answer key data).
     - `GET /api/v1/documents/{id}/export` (Standardized, system-independent JSON output).
  2. OpenAPI / Swagger configuration with comprehensive schemas and response examples.
  3. Commit and push Phase 6 to GitHub remote.

---

### 🔹 Phase 7: Old-Fashioned Retro System Web Dashboard (Strict Design Theme)
- **Objective:** Deliver an unforgettable, high-functioning web UI strictly adhering to `DESIGN_THEME.md`.
- **Tasks:**
  1. Implement classic retro workstation layout (Windows 95 / Classic System GUI aesthetic):
     - 3D beveled windows, navy blue titlebars, system buttons, segmented progress bar.
     - Monospace code panels, classic tabular grids, high-contrast review badges.
  2. Interactive features:
     - File drag-and-drop with Document Role selector (`Question Paper`, `Answer Key`, `Combined`).
     - Real-time asynchronous progress tracker.
     - Split-screen viewer: Document page preview on the left, Question cards on the right.
     - Filter tabs: `All Questions`, `Needs Review [!]`, `High Confidence`.
     - 1-Click System-Independent JSON Export.
  3. Commit and push Phase 7 to GitHub remote.

---

### 🔹 Phase 8: Sample Documents, Automated Tests, Postman Collection & Documentation
- **Objective:** Complete all deliverables for Round 2 evaluation.
- **Tasks:**
  1. Create sample documents:
     - `sample_digital_exam.pdf` (Multi-page digital test with cross-page question).
     - `sample_scanned_page.png` (Scanned exam page with table and noise).
     - `sample_separate_answer_key.pdf` (Separate answer key file).
     - `sample_extracted_output.json` (Golden output JSON).
  2. Build comprehensive Pytest test suite (`tests/`):
     - Auth tests, upload validation, extraction parsing, answer linking, review queue.
  3. Create `postman_collection.json` with pre-configured variables and workflow demonstrations.
  4. Write `ARCHITECTURE.md` (detailed architecture, trade-offs, scalability, diagrams).
  5. Write `README.md` (1-click quickstart, Docker commands, API guide).
  6. Final commit and push to GitHub remote.
