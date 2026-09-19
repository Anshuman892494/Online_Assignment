# 📖 STEP-BY-STEP USAGE & RUN GUIDE
## Pragati Bharati Document Intelligence & Question Extraction Service
### Full Stack Developer — Round 2 Engineering Submission

> This comprehensive manual provides exact, step-by-step instructions on how to install, run, test, and demonstrate the entire system—both via the **Modern Web Workbench UI** and the **FastAPI REST API**.

---

## 📋 Table of Contents
1. [Prerequisites & System Requirements](#1-prerequisites--system-requirements)
2. [Quickstart: Setup & Launch in 2 Minutes](#2-quickstart-setup--launch-in-2-minutes)
3. [Step-by-Step Web Workbench Walkthrough](#3-step-by-step-web-workbench-walkthrough)
4. [Dual-Mode Authentication Walkthrough](#4-dual-mode-authentication-walkthrough)
5. [Demonstrating Required Evaluation Scenarios](#5-demonstrating-required-evaluation-scenarios)
6. [Running Automated Tests](#6-running-automated-tests)
7. [Postman Collection Usage](#7-postman-collection-usage)
8. [Docker Production Stack](#8-docker-production-stack)
9. [Architecture & Design References](#9-architecture--design-references)

---

## 1. Prerequisites & System Requirements

- **Operating System**: Windows, macOS, or Linux.
- **Python**: Version `3.10`, `3.11`, `3.12`, or `3.14`.
- **Zero-Dependency Fallback**: The service includes an automatic SQLite and in-process task queue fallback. You **do not need** to install PostgreSQL or Redis locally to test the entire application.

---

## 2. Quickstart: Setup & Launch in 2 Minutes

### Step 1: Open Terminal in Project Directory
```bash
cd /path/to/Online_Assignment
```

### Step 2: Create & Activate Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(On macOS / Linux: `python3 -m venv .venv && source .venv/bin/activate`)*

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the pre-configured `.env.example` file:
```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

> [!NOTE]
> The `.env` file comes pre-configured with default credentials and local SQLite fallback. If you have a Google Gemini API key, you can optionally set `GEMINI_API_KEY="your-key"`; otherwise, the **Dual-Engine local parser** will operate out of the box with zero external dependencies.

### Step 5: Start the Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Once started, open your web browser and navigate to:
- 🌐 **Modern Web Workbench**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 📑 **Swagger API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📚 **ReDoc Specification**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 3. Step-by-Step Web Workbench Walkthrough

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to access the **Document Intelligence Workbench**.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  📄 Document Intelligence & Question Extraction Workbench    [Link Answer Key] [Refresh] [Export JSON] │
├──────────────────────────────┬─────────────────────────────────────────────────────────────────────────┤
│  INGESTION GATEWAY           │  [All Questions (5)]  [Needs Review [!] (2)]  [High Confidence (3)]     │
│  [ Click or Drag & Drop ]    ├─────────────────────────────────────────────────────────────────────────┤
│  Role: [Question Paper ▼]    │  Q1 [Page 1] [MCQ]                                      [95% Confident] │
│  [Submit to Ingestion Queue] │  Which of the following is a key feature of Python?                     │
│                              │  (A) Static typing   (B) Dynamic typing [✓ Key Match]                   │
│  PROCESSING STATUS           │                                                                         │
│  Status: [COMPLETED] 100%    │  Q2 [Page 1-2] [MCQ]                                  [62% Review Req.] │
│  [████████████████████████]  │  [Cross-Page Stitched Question]                   [✓ Approve Question]  │
│                              │                                                                         │
│  DOCUMENT ARCHIVE            │  Q3 [Page 2] [DESCRIPTIVE]                              [88% Confident] │
│  • sample_digital_exam.pdf   │  Explain the differences between multiprocessing and multithreading...  │
└──────────────────────────────┴─────────────────────────────────────────────────────────────────────────┘
```

### Step 3.1: Ingesting a Document
1. In the left panel under **Ingestion Gateway**, click the drag-and-drop zone or drag a file into it.
2. Choose one of the sample test files from the `sample_data/` folder:
   - `sample_data/sample_digital_exam.pdf` (Multi-page digital test with cross-page question).
   - `sample_data/sample_scanned_page.png` (Scanned exam page with table and noise).
   - `sample_data/sample_separate_answer_key.pdf` (Separate answer key file).
3. Select the **Document Role**:
   - `Question Paper (Exam)` — for question papers.
   - `Answer Key Document` — for separate answer keys.
   - `Combined (Questions + Answers)` — for exams containing embedded answer keys.
4. Click the **"Submit to Ingestion Queue"** button.

### Step 3.2: Live Asynchronous Progress Monitoring
1. Watch the **Processing Status** card immediately update:
   - Status badge moves from `QUEUED` ➔ `PREPROCESSING` ➔ `DUAL_ENGINE_EXTRACTION` ➔ `LINKING` ➔ `COMPLETED`.
   - The sleek orange linear progress bar animates from `0%` to `100%`.
2. Once complete, the document appears in the **Document Archive** list below.

### Step 3.3: Reviewing Extracted Questions
1. Click on any document in the **Document Archive** on the left.
2. The right panel immediately loads the extracted question cards:
   - **Question Number**: `Q1`, `Q2`, etc.
   - **Source Pages**: Displays originating page(s), e.g., `Page 1-2` for questions spanning multiple pages.
   - **Question Type**: `[MCQ]`, `[DESCRIPTIVE]`, etc.
   - **Confidence Metric**: e.g., `95% Confident` (green) or `62% Review Required` (red).
   - **Options Grid**: Displays all choices `(A)`, `(B)`, `(C)`, `(D)` with the correct answer key highlighted with `✓ Key Match`.

### Step 3.4: Using Filter Tabs
Use the filter tabs at the top of the questions viewport:
- **`All Questions`**: View all extracted questions.
- **`Needs Review [!]`**: Filters down to questions requiring human review (low confidence, OCR uncertainty, or cross-page splits).
- **`High Confidence`**: Displays cleanly verified extractions.

### Step 3.5: In-Place Human Review & Approval
1. On any card displaying the `Review Required` red flag, click the **"✓ Approve Question"** button.
2. The question status is updated immediately in the database via `PATCH /api/v1/documents/{id}/questions/{q_id}`.

### Step 3.6: Linking a Separate Answer Key
1. Ingest `sample_data/sample_digital_exam.pdf` as a `Question Paper`.
2. Ingest `sample_data/sample_separate_answer_key.pdf` as an `Answer Key Document`.
3. In the top navigation bar, click **"Link Answer Key"**.
4. In the dialog modal, select the uploaded Answer Key document and click **"Associate Now"**.
5. The system binds the answer key, automatically maps answers to questions, and marks them with `✓ Key Match`.

### Step 3.7: Exporting Standard Section 7 JSON
1. Click the primary orange button **"Export JSON"** in the top navigation bar.
2. The **JSON Structured Export Modal** displays the clean, system-independent Section 7 schema in a dark code inspector.
3. Click **"Copy JSON"** to copy the payload to your clipboard, or **"Download .json"** to save it to disk.

---

## 4. Dual-Mode Authentication Walkthrough

The application provides a dual authentication workflow detailed in [`AUTH_ARCHITECTURE.md`](file:///c:/Users/anshu/OneDrive/Desktop/Assignment/AUTH_ARCHITECTURE.md):

### Option A: Frictionless Evaluator Mode (Active by Default)
- When opening the workbench, the evaluator session (`evaluator@pragatibharati.org`) is automatically initialized.
- A real **Bearer JWT Token** is generated and attached to all background API requests.
- The top-right header displays `evaluator@pragatibharati.org` with an active green status indicator.

### Option B: Interactive Multi-Tenant Switcher (Testing Isolation)
1. Click the **"Account"** button or the user badge in the top-right header.
2. The **User Authentication Modal** opens with two tabs:
   - **`Sign In`**:
     - Pre-filled with demo credentials or enter custom user credentials.
     - Click **"⚡ Load Default Demo Evaluator Credentials"** for instant reset.
   - **`Create Account`**:
     - Enter Full Name, Email, and Password (min. 6 characters).
     - Click **"Create Account & Sign In"**.
3. **Observe Multi-Tenant Isolation**:
   - When switching to a newly registered user, the **Document Archive** empties because documents are tenant-isolated via foreign key `Document.user_id`.
   - Switch back to `evaluator@pragatibharati.org` to restore the seeded test documents.

---

## 5. Demonstrating Required Evaluation Scenarios

The 10 specific evaluation requirements from **Section 12 of the assignment** can be verified as follows:

| Scenario | How to Verify |
| :--- | :--- |
| **1. Upload a PDF** | Upload `sample_data/sample_digital_exam.pdf` via Ingestion Gateway. |
| **2. Upload an Image** | Upload `sample_data/sample_scanned_page.png` via Ingestion Gateway. |
| **3. Process Scanned Document** | Upload `sample_scanned_page.png`; PyMuPDF preprocessor normalizes DPI and handles noise. |
| **4. Extract Multiple Questions** | View `sample_digital_exam.pdf` docket; extracts multiple MCQs and descriptive questions. |
| **5. Question Spanning Multiple Pages** | Inspect `Q2` in `sample_digital_exam.pdf`; stitched seamlessly across pages (`Page 1-2`). |
| **6. Extract Question Options** | Inspect question options grid; accurately separates options `(A)`, `(B)`, `(C)`, `(D)`. |
| **7. Detect & Associate Answer Key** | Use the **Link Answer Key** modal to associate `sample_separate_answer_key.pdf`. |
| **8. Low-Confidence / Uncertain Items** | View the **Needs Review [!]** tab; shows low-confidence items with specific flags. |
| **9. Retrieve Final Structured Data** | Click **Export JSON** to inspect the standardized Section 7 JSON output. |
| **10. Invalid / Unsupported Document** | Try uploading an invalid `.txt` file or spoofed file; rejected with `400 Bad Request` magic byte validation error. |

---

## 6. Running Automated Tests

Run the comprehensive Pytest test suite:
```bash
pytest -v
```

### Expected Output:
```text
tests/test_answer_key_and_review.py::test_answer_key_and_review_workflow PASSED      [ 12%]
tests/test_api_surface_and_export.py::test_questions_api_and_standard_export PASSED  [ 25%]
tests/test_async_worker.py::test_async_task_lifecycle_and_status_tracking PASSED      [ 37%]
tests/test_async_worker.py::test_worker_error_handling PASSED                         [ 50%]
tests/test_auth_and_upload.py::test_auth_and_upload_lifecycle PASSED                  [ 62%]
tests/test_database.py::test_database_initialization_and_crud PASSED                  [ 75%]
tests/test_extraction.py::test_preprocessor_and_question_extraction PASSED          [ 87%]
tests/test_retro_dashboard.py::test_retro_dashboard_serves_html_and_assets PASSED    [100%]

============================== 8 passed in ~5.5s ==============================
```

---

## 7. Postman Collection Usage

1. Open Postman.
2. Click **Import** and select `postman_collection.json` from the repository root.
3. The collection is pre-configured with the base URL `http://127.0.0.1:8000` and contains 10 sequential workflow requests:
   1. `Auth - Register Evaluator`
   2. `Auth - Login & Acquire JWT`
   3. `Auth - Get Current User Profile (/me)`
   4. `Upload - Digital Exam PDF`
   5. `Status - Poll Document Processing Status`
   6. `Questions - List Extracted Questions`
   7. `Review - Get Review Required Items`
   8. `Relationships - Associate Separate Answer Key`
   9. `Review - Approve Flagged Question (PATCH)`
   10. `Export - Get Standardized Section 7 JSON`

---

## 8. Docker Production Stack

To run the complete production stack (FastAPI + PostgreSQL + Redis + Worker):
```bash
docker-compose up --build -d
```
- **FastAPI Application**: `http://localhost:8000`
- **PostgreSQL Database**: `localhost:5432`
- **Redis Broker**: `localhost:6379`

To stop the containers:
```bash
docker-compose down
```

---

## 9. Architecture & Design References

- **[`ARCHITECTURE.md`](file:///c:/Users/anshu/OneDrive/Desktop/Assignment/ARCHITECTURE.md)**: Deep technical dive into architecture, dual-engine AI, storage design, trade-offs, and scalability considerations.
- **[`AUTH_ARCHITECTURE.md`](file:///c:/Users/anshu/OneDrive/Desktop/Assignment/AUTH_ARCHITECTURE.md)**: Documentation of the Dual-Mode Authentication (Option A Evaluator Auto-Session + Option B Interactive Modal).
- **[`DESIGN_THEME.md`](file:///c:/Users/anshu/OneDrive/Desktop/Assignment/DESIGN_THEME.md)**: Red & Orange minimalist design specification, 1px borders, subtle corners, and typography standard.
- **[`PROJECT_PHASES.md`](file:///c:/Users/anshu/OneDrive/Desktop/Assignment/PROJECT_PHASES.md)**: Phase-by-phase development log from Phase 0 to Phase 8.
