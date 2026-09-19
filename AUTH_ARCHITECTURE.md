# AUTHENTICATION & MULTI-TENANCY ARCHITECTURE
## Pragati Bharati Document Intelligence & Question Extraction Service

> **ARCHITECTURAL OVERVIEW:**  
> To satisfy **Section 1 (Core Requirements)** and **Section 9 (Security & File Handling)** of the Pragati Bharati Engineering Assignment, the system implements a production-ready, multi-tenant authentication and authorization infrastructure.  
> 
> The system offers a **Dual-Mode Experience**:
> 1. **Option A (Evaluator Auto-Session)**: Seamless, zero-friction evaluation. Upon workbench load, a lead evaluator session is automatically synchronized in the background, issuing a real, cryptographically signed Bearer JWT token. Evaluators can immediately test document upload, OCR, and question extraction without being blocked by login forms.
> 2. **Option B (Interactive Multi-Tenant UI Modal)**: Fully interactive "Sign In" and "Create Account" modal in the frontend workbench. Enables multi-user isolation testing where different users can register, sign in, and only access their own uploaded documents and question dockets.

---

## 🏛️ 1. Dual-Mode Authentication Design

```
                     ┌────────────────────────────────────────────────────────┐
                     │              PRAGATI BHARATI WORKBENCH UI               │
                     └──────────┬─────────────────────────────────┬───────────┘
                                │                                 │
                   [Option A: Auto-Session]             [Option B: Interactive Modal]
                                │                                 │
         Background Handshake on Page Load             "Account" Button Click in Header
                                │                                 │
            POST /api/v1/auth/login/json                 Tabs: [Sign In] | [Create Account]
                                │                                 │
                                └──────────────┬──────────────────┘
                                               ▼
                             ┌───────────────────────────────────┐
                             │       FastAPI Security Layer      │
                             │  - JWT Bearer Token Generator     │
                             │  - Direct Bcrypt Password Hashing │
                             │  - Row-Level Tenant Verification  │
                             └─────────────────┬─────────────────┘
                                               ▼
                             ┌───────────────────────────────────┐
                             │    PostgreSQL / SQLite Database   │
                             │  - User Model (uuid, email, role) │
                             │  - Document.user_id Foreign Key   │
                             └───────────────────────────────────┘
```

### Option A: Frictionless Evaluator Session (Default)
- **Problem**: Evaluators grading 24-hour engineering assignments have strict time constraints. Forcing an evaluator through a mandatory signup/login wall introduces friction.
- **Implementation**:
  - `seed_demo.py` synchronizes the default evaluator account (`evaluator@pragatibharati.org`, `EvaluatorSecure2026!`).
  - On workbench load, `authenticateDefaultUser()` in `workbench.js` automatically obtains a real Bearer JWT token.
  - The token is stored in memory and attached to every HTTP request (`Authorization: Bearer <token>`).
  - The evaluator status chip in the top-right header reflects the live authenticated session.

### Option B: Interactive Multi-Tenant Auth Modal (UI Switcher)
- **Problem**: Demonstrating true multi-tenancy (Section 9: *"Users should only be able to access documents and extracted data they are authorized to access"*).
- **Implementation**:
  - The top navigation bar features an **"Account"** button and interactive user badge.
  - Clicking opens the **User Authentication Modal** styled with simple 1px borders and subtle corners.
  - **Sign In Tab**: Allows logging in with any registered user email and password. Includes a 1-click **"⚡ Load Default Demo Evaluator Credentials"** button.
  - **Create Account Tab**: Allows creating a new user with Full Name, Email, and Password (min. 6 characters). Upon registration, the user is automatically logged in, the active document docket is cleared, and only documents belonging to the new user are loaded.

---

## 🔒 2. Security & Cryptographic Implementation

| Security Dimension | Technical Implementation | Purpose / Section Compliance |
| :--- | :--- | :--- |
| **Password Hashing** | Direct `bcrypt.hashpw` with automated per-user salt generation | Secures credentials against rainbow-table attacks; handles UTF-8 byte boundary safely. |
| **Token Format** | HMAC-SHA256 signed JSON Web Tokens (JWT) | Stateless, tamper-proof user claims with expiration (`ACCESS_TOKEN_EXPIRE_MINUTES = 1440`). |
| **OAuth2 Compatibility** | Form-data endpoint `POST /api/v1/auth/login` | Native integration with FastAPI Swagger UI (`/docs`) "Authorize" button. |
| **Programmatic API** | JSON endpoint `POST /api/v1/auth/login/json` | Frictionless programmatic login for frontend SPAs, Postman scripts, and SDKs. |
| **Multi-Tenancy** | Foreign key `Document.user_id` bound to `User.id` | Strict database filtering: queries enforce `where(Document.user_id == current_user.id)`. |
| **Unauthorized Protection** | `Depends(get_current_user)` on all document routes | Rejects unauthenticated or cross-tenant requests with `401 Unauthorized` or `403 Forbidden`. |

---

## 📡 3. API Surface Reference

### 1. `POST /api/v1/auth/register`
- **Description**: Registers a new user account.
- **Request Body**:
  ```json
  {
    "email": "educator@university.edu",
    "password": "SecurePassword123!",
    "full_name": "Prof. Richard Feynman"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": "e6b7c2a1-...",
    "email": "educator@university.edu",
    "full_name": "Prof. Richard Feynman",
    "role": "user",
    "is_active": true,
    "created_at": "2026-09-19T20:15:00Z"
  }
  ```

### 2. `POST /api/v1/auth/login/json`
- **Description**: Authenticates user credentials and returns a Bearer access token.
- **Request Body**:
  ```json
  {
    "email": "evaluator@pragatibharati.org",
    "password": "EvaluatorSecure2026!"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer",
    "user": {
      "id": "c1f8a...",
      "email": "evaluator@pragatibharati.org",
      "full_name": "Lead Evaluator",
      "role": "admin"
    }
  }
  ```

### 3. `GET /api/v1/auth/me`
- **Description**: Retrieves current authenticated profile.
- **Headers**: `Authorization: Bearer <token>`
- **Response (200 OK)**: User profile details.

---

## 🎨 4. Theme & UI Geometry Conformance

The Auth Modal strictly follows [`DESIGN_THEME.md`](file:///c:/Users/anshu/OneDrive/Desktop/Assignment/DESIGN_THEME.md):
- **Borders**: Crisp `1px solid var(--wb-border)` (`#e7e5e4`).
- **Corners**: `border-radius: 6px` on modal container, `4px` on input fields and buttons.
- **Palette**: Warm Stone canvas, Vibrant Orange primary action buttons (`#ea580c`), and Crimson Red alerts (`#dc2626`).
- **No AI Tropes**: Avoids floating glassmorphic blurs or hyper-saturated gradients.
