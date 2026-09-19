# DESIGN & THEME SPECIFICATION
## Minimalist Modern Engineering Workbench (Human-Engineered Standard)

> **DESIGN PHILOSOPHY & OBJECTIVE:**  
> The design language embodies a clean, high-density, professional developer and data-engineering workbench (inspired by GitHub, Linear, and modern telemetry consoles). It intentionally avoids flashy "AI-generated" design tropes (such as exaggerated neon glows, hyper-saturated purple/pink gradients, or heavy frosted glass blur). Instead, it prioritizes clarity, disciplined typography, simple 1px borders, subtle 4px/6px radii, and instant visual hierarchy.

---

## 🏛️ 1. Core Aesthetic Principles (Human-Crafted vs. AI-Generated)

| Aspect | ❌ Generic "AI-Generated" Tropes | ✅ Pragati Bharati Engineering Workbench |
| :--- | :--- | :--- |
| **Borders & Outlines** | Fuzzy glowing borders, floating neon outlines | **Crisp, solid 1px borders** (`#e2e8f0` / `#cbd5e1`) |
| **Corners & Geometry** | Oversized pills (`border-radius: 9999px`) or novelty shapes | **Subtle, uniform 4px–6px radii** |
| **Color Schemes** | Hyper-saturated purple/magenta gradients, dark cyan glow | **Slate neutral palette** (`#f8fafc` canvas, `#0f172a` primary text, `#2563eb` action blue) |
| **Elevation & Depth** | Heavy multidirectional drop shadows (`blur: 30px`) | **Minimal 1px–2px subtle border shadows** (`rgba(0,0,0,0.05)`) |
| **Typography** | Generic browser serif or playful rounded fonts | **Modern system UI font** for controls + **Crisp Monospace** for code, questions, options, and JSON |
| **Component Density**| Giant, spaced-out elements wasting screen space | **High-information density** optimized for reviewers and evaluators |

---

## 🎨 2. Official Color Palette & Design Tokens

```css
:root {
    /* Canvas & Surfaces */
    --wb-canvas: #f8fafc;           /* Light slate application background */
    --wb-surface: #ffffff;          /* Pure white card and container surface */
    --wb-surface-hover: #f1f5f9;    /* Subtle hover highlight */
    
    /* Borders & Dividers */
    --wb-border: #e2e8f0;           /* Standard clean 1px border */
    --wb-border-dark: #cbd5e1;      /* Focused input and divider boundary */
    
    /* Typography */
    --wb-text-primary: #0f172a;     /* Slate 900 — Maximum readability for text & questions */
    --wb-text-secondary: #475569;   /* Slate 600 — Metadata, options, and descriptions */
    --wb-text-muted: #64748b;       /* Slate 500 — Timestamps, badges, and captions */
    
    /* Primary Brand & Actions */
    --wb-primary: #2563eb;          /* Focused interactive blue (Blue 600) */
    --wb-primary-hover: #1d4ed8;    /* Interactive hover blue (Blue 700) */
    
    /* Semantic Status Indicators */
    --wb-badge-review-bg: #fef2f2;  /* Light crimson for "Review Required" */
    --wb-badge-review-text: #dc2626;/* Crimson text */
    --wb-badge-review-border: #fecaca;/* Crimson border */
    
    --wb-badge-ok-bg: #f0fdf4;      /* Light emerald for "Confident" */
    --wb-badge-ok-text: #16a34a;    /* Emerald text */
    --wb-badge-ok-border: #bbf7d0;  /* Emerald border */

    /* Typography Stacks */
    --font-ui: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --font-mono: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
}
```

---

## 📐 3. Component Architecture & UI Elements

### A. Application Top Bar & Navigation
- **Height**: 52px fixed header.
- **Styling**: Pure white surface, crisp 1px solid bottom border (`border-bottom: 1px solid var(--wb-border)`).
- **Elements**:
  - Service branding: `Pragati Bharati` with green operational status dot.
  - Interactive Action Toolbar: "Upload Document", "Link Answer Key", "Export Standard JSON", and "Refresh Archive".
  - Quick Links: Direct navigation to interactive Swagger API docs (`/docs`) and ReDoc (`/redoc`).

### B. Ingestion & Documents Drawer (Left Panel — 360px)
- **Drag-and-Drop Ingestion Zone**:
  - 1px dashed border (`#cbd5e1`), subtle hover background transition (`#f8fafc`).
  - Strict client-side and server-side MIME type + magic bytes validation (`%PDF-`, `\x89PNG`, `\xff\xd8\xff`).
  - Document Role dropdown selector (`QUESTION_PAPER`, `ANSWER_KEY`, `COMBINED`).
- **Live Asynchronous Progress Tracker**:
  - Sleek 6px linear progress bar (`background: #2563eb; border-radius: 3px;`).
  - Dynamic stage label updating in real-time (`QUEUED` ➔ `PREPROCESSING` ➔ `DUAL_ENGINE_EXTRACTION` ➔ `LINKING` ➔ `READY`).
- **Document History Archive**:
  - Scrollable high-density card list with active item indicator (`border-left: 3px solid var(--wb-primary)`).
  - Clear metadata: Document Role chip, page count, question count, and creation timestamp.

### C. Review Docket & Workspace (Right Panel — Flex 1)
- **Status Filter Tabs**:
  - Minimal underline/flat tabs: `All Questions`, `Needs Review [!]`, and `High Confidence`.
  - Displays instant live counter chips for each state.
- **Question Cards**:
  - Crisp white surface, 1px solid border (`#e2e8f0`), 6px border radius.
  - Header: Question Number badge (`Q1`, `Q2`), Type chip (`MCQ`, `DESCRIPTIVE`), Page Index tag (`Page 1-2` for cross-page stitched questions), and Confidence score chip (`95% Confident` vs `62% Review Required`).
  - Question Prompt: Clear monospace block with high contrast.
  - Options Grid: Clean bordered rows; the correct answer key is prominently highlighted with a light green background (`#f0fdf4`) and green checkmark.
  - Review Actions: In-place "Approve Question" button enabling instant resolution of low-confidence questions.

### D. Answer Key Linker Modal
- Clean, centered dialog with a dark semi-transparent backdrop (`rgba(15, 23, 42, 0.5)`).
- Dropdown selector to choose the Question Paper and corresponding Answer Key document.
- One-click relationship binding via `POST /api/v1/documents/{id}/relationships`.

### E. Standard Section 7 JSON Export Modal
- Full JSON schema inspector with dark theme container (`#0f172a` slate background, `#38bdf8` light blue syntax).
- Includes one-click **"Copy to Clipboard"** button and **"Download .json"** button.

---

## ⚡ 4. Code & Performance Optimization

1. **Lightweight Native Implementation**:
   - Zero heavy frontend dependencies (no React runtime overhead, no bloated CSS framework).
   - Entire interface is powered by native ES6+ JavaScript and Vanilla CSS Custom Properties.
2. **Optimized Polling Lifecycle**:
   - Asynchronous status polling is debounced to 1,500ms intervals during active processing.
   - Interval is automatically cleared upon terminal states (`COMPLETED` or `FAILED`), eliminating redundant network traffic.
3. **Memory Management**:
   - Event listeners are cleanly scoped and reused.
   - Clean DOM fragment updates avoid layout thrashing and unnecessary repaints.
4. **Resilient Backend Fallbacks**:
   - Dynamic database proxy (`DynamicAsyncSessionLocal`) handles automatic fallback between PostgreSQL and SQLite.
   - Dual-Engine AI extraction pairs Gemini Vision 2.5-Flash with local PyMuPDF regex fallback for zero downtime.

---

## 🔒 5. Accessibility & Human Ergonomics
- **Contrast Ratios**: All text elements satisfy WCAG 2.1 AA compliance (Slate 900 on Slate 50 achieves an exceptional contrast ratio of 16.8:1).
- **Focused States**: Visible, clean 2px focus outlines (`outline: 2px solid var(--wb-primary)`) for keyboard accessibility.
- **Semantic HTML**: Fully semantic structural elements (`<header>`, `<main>`, `<aside>`, `<section>`, `<dialog>`).
