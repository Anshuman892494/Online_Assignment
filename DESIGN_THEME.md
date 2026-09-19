# DESIGN & THEME SPECIFICATION
## Classic Retro System (Old-Fashioned Default Engineering UI)

> **MANDATORY DESIGN GOAL & ENFORCEMENT:**  
> All visual components, pages, dashboard widgets, and user-facing elements in this project MUST strictly implement this **Old-Fashioned / Classic Retro System UI** design language. Modern minimal/flat/borderless styles are explicitly prohibited.

---

## 🏛️ 1. Aesthetic Philosophy & Visual Identity

The design language embodies the **Classic 1990s Operating System & Engineering Workstation UI** (Windows 95/98 / Classic Motif / NeXTSTEP / Vintage Scientific Console):
- **Tactile 3D Bevels**: Every window, button, and card has defined light and dark borders to create physical depth (Outset for elevated surfaces, Inset for input areas and viewports).
- **Classic System Palette**: Iconic desktop silver `#C0C0C0`, navy blue active titlebars `#000080`, high-contrast black text `#000000`, and crisp system highlight borders.
- **Default System Typography**: Pixel-crisp system sans-serif (`MS Sans Serif`, `Tahoma`, `Geneva`) for menus and labels, and authentic fixed-width monospace (`Courier New`, `Lucida Console`) for structured questions, options, logs, and JSON.
- **Segmented Block Progress Bars**: Classic blue marching block segments instead of modern gradient spinners.
- **High-Density Information Architecture**: Efficient, structured, tabular layouts maximizing screen real estate without wasted empty whitespace.

---

## 🎨 2. Official Color Palette & Design Tokens

| Token Name | Hex Code | Usage |
| :--- | :--- | :--- |
| `--sys-desktop` | `#008080` | Classic Vintage Teal Desktop Wallpaper |
| `--sys-gray-base` | `#C0C0C0` | Default Component / Window / Dialog Background |
| `--sys-gray-light` | `#DFDFDF` | Panel highlight and light surface |
| `--sys-gray-dark` | `#808080` | Inner shadow for 3D bevels and border dividers |
| `--sys-black` | `#000000` | Deepest border shadow, primary text, input borders |
| `--sys-white` | `#FFFFFF` | Light source reflection for top/left 3D bevel borders, input backgrounds |
| `--sys-titlebar-active` | `#000080` | Active Window Titlebar (Classic Navy) |
| `--sys-titlebar-text` | `#FFFFFF` | Active Titlebar Text (Bold White) |
| `--sys-titlebar-inactive` | `#808080` | Inactive Window Titlebar (Muted Gray) |
| `--sys-highlight` | `#000080` | Selected list items / focused options (Navy) |
| `--sys-highlight-text` | `#FFFFFF` | Text on selected items |
| `--sys-badge-review` | `#800000` | "NEEDS REVIEW" high-contrast warning badge (Maroon) |
| `--sys-badge-success` | `#008000` | "CONFIDENT" high-confidence badge (Dark Green) |
| `--sys-badge-queued` | `#000080` | "QUEUED / PROCESSING" status badge (Navy) |

---

## 📐 3. The Classic 3D Bevel System (CSS Specifications)

### A. Outset Surface (Windows, Modals, Unpressed Buttons, Cards)
Elevates the element above the background:
```css
.sys-bevel-outset {
    background-color: #c0c0c0;
    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #000000;
    border-bottom: 2px solid #000000;
    box-shadow: inset -1px -1px #808080, inset 1px 1px #dfdfdf;
}
```

### B. Inset Surface (Text Inputs, Textareas, Viewports, Content Panes, Code Boxes)
Recesses the element into the background:
```css
.sys-bevel-inset {
    background-color: #ffffff;
    border-top: 2px solid #808080;
    border-left: 2px solid #808080;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;
    box-shadow: inset 1px 1px #000000, inset -1px -1px #dfdfdf;
}
```

### C. Pressed / Active Button State
Physically depresses the button with a 1px downward shift:
```css
.sys-button:active {
    border-top: 2px solid #000000;
    border-left: 2px solid #000000;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;
    box-shadow: inset 1px 1px #808080;
    padding-top: 5px;
    padding-left: 7px;
    padding-bottom: 3px;
    padding-right: 5px;
}
```

---

## 🔤 4. Typography & Font Rules

```css
/* UI Labels, Menus, Dialogs, Window Headers */
font-family: "MS Sans Serif", Tahoma, Geneva, "Segoe UI", sans-serif;
font-size: 11px;
line-height: 1.3;
-webkit-font-smoothing: antialiased;

/* Structured Data, Questions, OCR Raw Text, JSON, Code Viewers */
font-family: "Courier New", Courier, "Lucida Console", monospace;
font-size: 13px;
line-height: 1.4;
```

---

## 🎛️ 5. Component Style Guide (Strict Templates)

### 1. Window Frame (`.sys-window`)
- Classic window container with navy header and control icons.
```html
<div class="sys-window sys-bevel-outset">
    <div class="sys-titlebar">
        <div class="sys-titlebar-text">
            <span class="sys-icon">&#128196;</span> Document Intelligence Workbench v1.0
        </div>
        <div class="sys-titlebar-controls">
            <button class="sys-control-btn">&#9660;</button>
            <button class="sys-control-btn">&#9650;</button>
            <button class="sys-control-btn sys-close-btn">&#10006;</button>
        </div>
    </div>
    <div class="sys-menubar">
        <span><u>F</u>ile</span>
        <span><u>E</u>dit</span>
        <span><u>V</u>iew</span>
        <span><u>T</u>ools</span>
        <span><u>H</u>elp</span>
    </div>
    <div class="sys-window-body">
        <!-- Window content here -->
    </div>
    <div class="sys-statusbar sys-bevel-inset">
        <span>Ready</span>
        <span>Connected to PostgreSQL</span>
        <span>Queue: Idle</span>
    </div>
</div>
```

### 2. Segmented Progress Bar (`.sys-progress-bar`)
- Features authentic retro block chunks:
```html
<div class="sys-progress-container sys-bevel-inset">
    <div class="sys-progress-blocks">
        <div class="sys-progress-block"></div>
        <div class="sys-progress-block"></div>
        <div class="sys-progress-block"></div>
        <!-- Repeating chunks filling up according to progress -->
    </div>
</div>
```

### 3. Question Docket Card (`.sys-question-card`)
- Clean index-card styling with high-contrast review tags:
```html
<div class="sys-question-card sys-bevel-outset">
    <div class="sys-card-header">
        <span class="sys-q-badge">QUESTION 04</span>
        <span class="sys-page-ref">[Page 1 &rarr; 2]</span>
        <span class="sys-badge-flag-review">&#9888; REVIEW REQUIRED: MISSING_OPTION_D</span>
    </div>
    <div class="sys-card-body sys-bevel-inset">
        <p class="sys-q-text">Which of the following sorting algorithms has worst-case time complexity O(n log n)?</p>
        <div class="sys-options-list">
            <div class="sys-opt-item"><strong>[A]</strong> Quick Sort</div>
            <div class="sys-opt-item sys-opt-correct"><strong>[B]</strong> Merge Sort <em>(Identified Key: B)</em></div>
            <div class="sys-opt-item"><strong>[C]</strong> Bubble Sort</div>
        </div>
    </div>
    <div class="sys-card-footer">
        <span>Confidence: <strong>0.72</strong></span>
        <button class="sys-button">Inspect Raw OCR</button>
        <button class="sys-button">Approve Item</button>
    </div>
</div>
```

### 4. Tab Navigation (`.sys-tabs`)
- Windows 95 tabbed folder aesthetic with overlapping active tab.

---

## 🔒 6. Strict Enforcement Rules for All Developers & Agents
1. **No Flat Buttons**: Every button must have a 3D bevel and active depression state.
2. **No Border-Radius Pill Shapes**: All containers, inputs, buttons, and badges must have crisp 0px or 1px corners.
3. **No Blurred Shadows**: Box shadows must use hard color edges (1px / 2px bevels), no `blur-radius` gradients.
4. **Authentic System Cursors**: Use `cursor: default`, `cursor: pointer`, `cursor: text` where appropriate.
5. **No Ad-Hoc CSS**: All components must import and use the master `static/css/retro-system.css` style definitions.
