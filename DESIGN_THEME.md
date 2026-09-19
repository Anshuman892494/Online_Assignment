# DESIGN & THEME SPECIFICATION
## Minimalist Modern Engineering Workbench (Red & Orange Standard)

> **DESIGN PHILOSOPHY & OBJECTIVE:**  
> The workbench embodies a clean, high-density, professional developer and data-engineering console. It utilizes a **harmonious Red & Orange palette** (Warm Flame Orange `#ea580c` primary + Crimson Red `#dc2626` accents + Warm Stone neutral canvas `#fafaf9`).  
>
> All decorative "AI-generated" tropes (neon glows, hyper-saturated purple gradients, floating blurred glassmorphism, oversized 9999px pills) are strictly excluded. The interface relies on **simple 1px crisp borders**, **subtle 4px–6px radii**, and uncluttered human-engineered structure.

---

## 🗑️ 1. Inventory of Removed Redundant Elements (De-Cluttering Audit)

To ensure maximum focus, screen space, and zero confusion, all unnecessary and non-functional elements have been removed:

| Removed Element | Location Prior | Reason for Removal | Resolution / Replacement |
| :--- | :--- | :--- | :--- |
| **"Select Document" Button** | Top Toolbar | Redundant. The "Ingestion Gateway" in the sidebar already provides a dedicated, direct dropzone/file selector. | Removed from toolbar. Users click the drag-and-drop gateway directly. |
| **"Ingest & Process" Button** | Top Toolbar | Duplicate action. The sidebar already features "Submit to Ingestion Queue". | Removed from toolbar. Kept single prominent submission button in the gateway. |
| **Entire Secondary Toolbar Row** | Beneath Header | Took up unnecessary vertical space with redundant buttons. | Unified into a single streamlined top navigation bar with remaining core actions. |
| **"About" Button** | Top-Right Header | Was an unstyled JavaScript `alert()` stub with static text; non-functional in production. | Removed completely. |
| **"v1.0 (Round 2)" Badge** | Header Title | Pure metadata clutter taking up visual attention. | Removed to keep title crisp and professional. |
| **Bottom Statusbar (`sys-statusbar`)** | Page Footer | Hardcoded static text ("System Ready", "PostgreSQL / SQLite", "Broker Ready") consuming 32px vertical room. | Removed completely. Gives extra vertical viewport to the questions docket. |
| **Mock Footer Status Cell** | Bottom Footer | Replaced by a clean live user chip in the top header (`evaluator@pragatibharati.org` with green active dot). | Moved to top-right header chip. |
| **Dead CSS Selectors** | `retro-system.css` | Leftover styles (`.sys-menubar`, `.sys-bevel-outset`, `.sys-bevel-inset`, unused tables). | Completely purged from stylesheet. |

---

## 🎨 2. Red & Orange Color Palette & Design Tokens

```css
:root {
    /* Canvas & Surfaces */
    --wb-canvas: #fafaf9;           /* Warm Stone 50 light canvas */
    --wb-surface: #ffffff;          /* Pure white card and container surface */
    --wb-surface-hover: #fff7ed;    /* Warm Orange 50 subtle highlight */
    
    /* Crisp 1px Borders & Dividers */
    --wb-border: #e7e5e4;           /* Warm Stone 200 clean 1px border */
    --wb-border-dark: #d6d3d1;      /* Stone 300 active/focus boundary */
    --wb-border-warm: #fed7aa;      /* Orange 200 warm border accent */
    
    /* Typography */
    --wb-text-primary: #1c1917;     /* Stone 900 — Maximum readability */
    --wb-text-secondary: #57534e;   /* Stone 600 — Metadata, options, and descriptions */
    --wb-text-muted: #78716c;       /* Stone 500 — Timestamps, badges, and captions */
    
    /* Primary Brand & Actions (Vivid Orange & Crimson Red) */
    --wb-primary: #ea580c;          /* Flame Orange 600 (Primary interactive) */
    --wb-primary-hover: #c2410c;    /* Deep Orange 700 (Hover state) */
    --wb-accent: #dc2626;           /* Crimson Red 600 (Warning & Action accent) */
    --wb-accent-hover: #b91c1c;     /* Deep Red 700 (Hover state) */
    
    /* Semantic Status Indicators */
    --wb-badge-review-bg: #fef2f2;  /* Light rose/red background */
    --wb-badge-review-text: #dc2626;/* Crimson red text */
    --wb-badge-review-border: #fecaca;/* Rose border */
    
    --wb-badge-ok-bg: #f0fdf4;      /* Light green background */
    --wb-badge-ok-text: #16a34a;    /* Emerald green text */
    --wb-badge-ok-border: #bbf7d0;  /* Green border */

    --wb-badge-orange-bg: #fff7ed;  /* Soft orange background */
    --wb-badge-orange-text: #c2410c;/* Burnt orange text */
    --wb-badge-orange-border: #fed7aa;/* Light orange border */

    /* Typography Stacks */
    --font-ui: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --font-mono: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
}
```

---

## 🏛️ 3. Aesthetic Rules & Principles

1. **Simple 1px Borders**:
   - All panels, cards, tabs, and inputs use clean `1px solid var(--wb-border)`.
   - Focused inputs and active cards use warm border highlight (`#fed7aa` / `#ea580c`).
2. **Subtle Corners (4px to 6px)**:
   - Buttons, badges, and inputs: `border-radius: 4px`.
   - Panel cards and modals: `border-radius: 6px`.
   - Never use circular pills (`border-radius: 9999px`) or heavy 3D bevels.
3. **Red & Orange Visual Hierarchy**:
   - Top window accent line: `linear-gradient(90deg, #ea580c 0%, #dc2626 100%)`.
   - Primary action buttons: Warm vibrant orange (`#ea580c`) with crisp white typography.
   - Question counter badges & active tabs: Warm orange highlight (`#ffedd5` background, `#c2410c` text).
   - "Needs Review [!]" flags: Clear crimson red (`#dc2626`) for immediate identification.
   - Correct answer key: Emerald green badge (`#16a34a`) for instantaneous visual validation.

---

## 📐 4. Streamlined Component Layout

### A. Top Navigation Bar (52px Unified Header)
- **Left**: Service branding with document intelligence icon.
- **Right**:
  - `Link Answer Key` button (opens separate key merger dialog).
  - `Refresh` button (re-fetches active document questions).
  - `Export JSON` primary orange button (opens Section 7 standard export inspector).
  - `API Docs` quick-link (`/docs`).
  - Active user session indicator chip with green connection dot.

### B. Ingestion & Archive Drawer (Left Panel — 360px)
- **Ingestion Gateway**:
  - Drag-and-drop file upload target with orange hover tint.
  - Document Role dropdown selector (`QUESTION_PAPER`, `ANSWER_KEY`, `COMBINED`).
  - Primary button: "Submit to Ingestion Queue".
- **Processing Status**:
  - Sleek linear progress bar with orange gradient fill (`linear-gradient(90deg, #ea580c, #f97316)`).
  - Dynamic status badge (`IDLE`, `QUEUED`, `PREPROCESSING`, `DUAL_ENGINE_EXTRACTION`, `LINKING`, `COMPLETED`).
- **Document Archive**:
  - Scrollable list of processed documents.
  - Active document has clean orange left accent border (`border-left: 3px solid #ea580c`) and warm tint.

### C. Review Docket & Workspace (Right Panel — Flex 1)
- **Filter Tabs**:
  - `All Questions`, `Needs Review [!]`, and `High Confidence`.
  - Active tab indicated by clean 2px solid orange underline (`#ea580c`).
- **Question Cards**:
  - Monospace prompt with high contrast.
  - Options list with radio selection and green "✓ Key Match" indicator.
  - In-place "✓ Approve Question" orange button to resolve review flags instantly.

### D. Export Modal & Code Inspector
- High-contrast dark code inspector (`#1c1917` warm dark slate background, `#fb923c` warm amber syntax).
- 1-Click **"Copy JSON"** and **"Download .json"** buttons.

---

## ⚡ 5. Performance & Code Optimization

1. **Lightweight Native Implementation**:
   - Zero framework overhead, zero redundant dependencies. 100% native ES6+ and Vanilla CSS custom properties.
2. **Debounced & Safe Polling**:
   - 1,500ms status polling interval during active extraction, automatically cleared upon completion.
3. **WCAG AA Accessibility**:
   - Text contrast ratio of 16.8:1 (Stone 900 on Stone 50) exceeds accessibility standards.
