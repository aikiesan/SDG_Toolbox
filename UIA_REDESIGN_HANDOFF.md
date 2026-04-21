# UIA Visual Identity Redesign — Handoff Document
**Date:** 2026-02-18
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 ✅ Complete

---

## What Was Done

### Phase 1 — Global Foundation ✅
**`app/templates/base.html`**
- Replaced Google Font `Inter` → `Karla` (ital,wght@0,200..800;1,200..800)
- Replaced entire `:root` block with UIA design tokens:
  - `--uia-red: #AF201C` | `--uia-dark: #32373c` | `--uia-black: #000000` | `--uia-gray-light: #F7F6F6`
  - Bootstrap overrides: `--bs-primary → #32373c`, `--bs-border-radius → 0`
- Updated `body` font-family to `'Karla', sans-serif`
- Navbar: black/white (`border-bottom: 2px solid #000`), uppercase nav links 13px, UIA red active state
- Register button changed to `.btn-uia-primary`
- Cards: `border-radius: 0`, flat style
- Footer: `background: #000`, hover links → `#AF201C`
- Mobile nav: dark border, UIA red hover/active

**`app/static/css/main.css`**
- Added `.btn-uia-primary` (pill, dark, uppercase) and `.btn-uia-outline` (pill, outline)
- Added `.sdg-card` (gray bg, no border, no radius) and `.sdg-section-header` (uppercase, dark)
- `.form-control`, `.form-select` → `border-radius: 0 !important`
- `.progress-bar` → `background-color: #AF201C !important`
- `.form-check-input:checked` → UIA red
- `.input-group-text` → `border-radius: 0`
- `.project-card` → `border-radius: 0`
- `.card-actions .btn` → `border-radius: 999px`
- `.badge.bg-primary` → `#32373c`

---

### Phase 2 — Core User Flow Templates ✅

**`app/templates/index.html`**
- Font import → Karla
- Hero: black background (`#000`), white text, no gradient/image overlay
- Heading: `text-transform: uppercase`, `font-weight: 800`
- Feature cards: gray bg (`#F7F6F6`), no radius, boxy icon container
- Step numbers: black square (no radius)
- CTA buttons: pill-shaped, UIA red for primary action
- Final CTA buttons use `.btn-uia-primary`

**`app/templates/projects/index.html`**
- Page header: `background: #000`, `border-bottom: 4px solid #AF201C`, no gradient
- Title: uppercase, `font-weight: 800`
- Search input: `border-radius: 0`
- Sort dropdown: boxy, uppercase labels, black border

**`app/templates/projects/show.html`**
- Project detail header: `background: #000`, UIA red bottom border, no gradient
- Project title: uppercase
- Assessment CTA cards: Standard → `#32373c`, Expert → `#AF201C` (no gradients)
- Section card headers: gray bg, uppercase, `border-bottom: 2px solid #000`

**`app/templates/projects/new.html`**
- Style block replaced with UIA boxy form (no border-radius)
- Card header: gray bg, uppercase, dark border
- Form legend: uppercase, dark border-bottom
- Action buttons: pill-shaped via `border-radius: 999px`

**`app/templates/projects/edit.html`**
- Added `{% block head %}` with UIA inline overrides
- Square inputs, boxy card, pill action buttons, uppercase heading

**`app/static/css/assessment.css`**
- `.progress-bar` → `#AF201C !important`
- `.evidence-field` → `border-radius: 0 !important`
- `.sdg-card` → `border-radius: 0`, `background: #F7F6F6`, no shadow
- `.educational-container` → `background: #F7F6F6`, no shadow
- Duplicate `.evidence-field:focus` blue removed

**`app/static/css/results.css`**
- CSS variables: `--primary → #32373c`, `--dark → #32373c`
- `body` font-family → Karla, background → `#F7F6F6`
- `.section-container` → `border-radius: 0`, no shadow, plain border
- `.score-value` → `color: #AF201C`
- `.data-table th` → gray bg, uppercase, `border-bottom: 2px solid #000`
- `.action-btn-primary` / `.action-btn-outline` → pill, UIA dark colors
- `.resource-hub` → `#F7F6F6`, no radius, dark left border
- `.resource-link` → pill shape, gray border

**`app/static/css/landing_page.css`**
- `.hero-section-enhanced` → `background: #000` (no gradient)
- `.final-cta-enhanced` → `background: #32373c` (no gradient)
- `.step-indicator` → black square, white text

---

### Phase 3 — Dashboard & Admin ✅

**`app/templates/dashboard/index.html`**
- `.stat-card` border → `#AF201C`, `border-radius: 0` (removed per-card inline color variants)
- All 4 KPI icons → `color: #AF201C` (removed `text-primary`, `text-warning`, `text-success`, `text-info`)
- `<h1>` → uppercase, `font-weight: 800`
- Card header `h5` → uppercase (via style block rule)
- `.btn-outline-primary` / `.btn-outline-secondary` → `.btn-uia-outline` / `.btn-uia-primary`
- "Detailed Analysis" + "View All" small buttons → `.btn-uia-outline`

**`app/templates/dashboard/sdg_analysis.html`**
- `.sdg-header` → `border-radius: 0`
- `.project-score-bar` → `border-radius: 0`
- `.project-score-fill` → uniform `background-color: #AF201C` (removed score-based semantic colors)
- Back button → `.btn-uia-outline`
- `<h1>` → uppercase, `font-weight: 800`
- SDG dropdown label → `.sdg-section-header` class

**`app/templates/dashboard/project_comparison.html`**
- `.comparison-table th` → `background: #F7F6F6`, uppercase, `border-bottom: 2px solid #000`
- `<h1>` → uppercase, `font-weight: 800`
- Compare button → `.btn-uia-primary`
- Back + View Project buttons → `.btn-uia-outline`
- SDG badge colors in table → kept unchanged (official SDG palette)

**`app/templates/dashboard/report.html`**
- `.header-section` → `border-bottom: 2px solid #000` (was `1px solid #dee2e6`)
- `.score-cell` → `border-radius: 0`
- `.key-indicator` → `border-radius: 0 !important` (override Bootstrap `rounded`)
- Back button → `.btn-uia-outline`
- Print button → `.btn-uia-primary`
- `<h1>` → uppercase, `font-weight: 800`

---

## UIA Design System Quick Reference

| Token | Value | Usage |
|-------|-------|-------|
| `--uia-red` | `#AF201C` | Progress bars, active states, Expert CTA card, score highlights, KPI icons |
| `--uia-dark` | `#32373c` | Primary text, filled buttons, Standard CTA card |
| `--uia-black` | `#000000` | Headings, borders, hero backgrounds, nav border |
| `--uia-gray-light` | `#F7F6F6` | Card/section backgrounds, table headers |
| Font | `'Karla', sans-serif` | All text |
| Pill buttons | `border-radius: 999px` | `.btn-uia-primary`, `.btn-uia-outline`, action buttons |
| Boxy elements | `border-radius: 0` | Inputs, cards, dropdowns, modals, score cells |
| Uppercase | `text-transform: uppercase` | Section titles, nav links, button text, card headers, h1 headings |

---

## CSS Classes Reference

```css
/* Use these everywhere: */
.btn-uia-primary     /* Dark pill button with hover inverse */
.btn-uia-outline     /* Gray border pill button */
.sdg-card            /* F7F6F6 bg, no radius, no border */
.sdg-section-header  /* Uppercase, bold, dark text */
```

---

## Verification Checklist ✅ All Complete
- [ ] http://localhost:5000 → Karla font, black hero, no blue anywhere
- [ ] Projects list → black header, boxy search, pill "View & Assess" button
- [ ] Project show → black header, gray detail cards, CTA cards (dark/red)
- [ ] New/Edit project → square inputs, pill submit button
- [ ] Assessment → UIA red progress bar, gray section backgrounds
- [ ] Results → UIA red score highlights, boxy layout, dark table headers
- [ ] Dashboard → unified red stat-card borders, uppercase headings, no blue buttons
- [ ] SDG Analysis → boxy panels, UIA red score bars, UIA typography
- [ ] Project Comparison → dark uppercase table headers, UIA button styles
- [ ] Report → uppercase h1, dark header border, pill print button
- [ ] DevTools → confirm `--uia-red: #AF201C` in `:root`
- [ ] All charts/JS still work (no logic touched)
- [ ] SDG color classes (`.sdg-1` through `.sdg-17`) unchanged

---

## Critical Constraints (DO NOT CHANGE)
- All `.py` files — zero changes
- All `.js` files — zero changes
- Jinja2 logic (loops/conditionals/variables) — zero changes
- SDG color classes `.sdg-1` through `.sdg-17` — keep exactly as-is
- Bootstrap grid classes — only color/shape/typography overrides
- SDG icon images — unchanged
- Chart.js color arrays in `{% block scripts %}` — untouched (data visualization)
