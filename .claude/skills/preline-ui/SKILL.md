---
name: preline-ui
description: Use for ANY template, page, partial, or frontend change in this repo. Enforces Preline UI (Tailwind + preline.js) via a Jinja macro kit. Triggers on HTML, Jinja, CSS, modal, table, form, navbar, sidebar, dashboard, chart, toast.
---

# Preline UI rules (non-negotiable)

Preline = Tailwind class patterns + `preline.js` driven by `data-hs-*` attributes.
Never invent component markup. Official markup lives in `docs/preline/` and is wrapped by macros in `app/templates/macros/`.

## Workflow for every UI task
1. Check `app/templates/macros/` for an existing macro. Use it.
2. If none exists, fetch the component's official page from https://preline.co/docs/<component>.html,
   save the relevant markup to `docs/preline/<component>.html`, then add a macro in `macros/` that copies that markup verbatim and parameterises text, ids, and URLs.
3. Pages and partials call macros only. No hand-written components.
4. Run `python scripts/check_ui.py` and `make build-css` (or `cd frontend && npm run build`) before finishing. Fix every failure.

## Hard rules
- Raw `<button> <input> <select> <textarea> <table>` are allowed ONLY inside `templates/macros/`.
- Modals: Preline Overlay (`hs-overlay`, `data-hs-overlay="#id"`). Open from JS with `HSOverlay.open('#id')`. Never `display:none` toggling or custom modal JS.
- Dropdowns, select, collapse, tooltip, toast, tabs, datepicker, and combobox use the matching Preline plugin markup.
- Tailwind setup in `frontend/src/input.css` (Preline v5, Tailwind v4). Paths are relative to `frontend/src/` because `node_modules` lives in `frontend/`:
  ```css
  @import "tailwindcss";
  @import "preline/variants.css";
  @import "preline/theme.css";
  @source "../node_modules/preline/dist/*.js";
  ```
  Verify against https://preline.co/docs/frameworks-tailwind.html for the installed version.
- JS: `npm run build` copies `node_modules/preline/dist/preline.js` to `app/static/js/`. Load it once in `base.html`.
  After every HTMX swap:
  ```js
  document.body.addEventListener('htmx:afterSettle', () => window.HSStaticMethods.autoInit());
  ```
- No CDN links, no inline `<style>`, no `style=""`, no jQuery, no Bootstrap classes, no custom CSS unless Tailwind genuinely cannot do it (then put it in `input.css` under `@layer components`).
- Layout: Preline application layout with a sidebar (collapsible on mobile via `hs-overlay`) and a top header. Light theme, `bg-gray-50` body, white cards with `border border-gray-200 rounded-xl shadow-2xs`.
- Forms: Preline form-layout pattern, label above input, inline error text under the field (`text-red-600 text-sm`), repopulated values.
- Tables: Preline table-in-card pattern with header row, divided rows, pagination footer, and empty-state row.
- Status badges: one `badge()` macro, fixed colour map (available=teal, checked_out=blue, under_maintenance=yellow, retired=gray, expired=red).
- Icons: inline SVG from Lucide, via an `icon(name)` macro. No icon fonts.
- Charts: Preline's ApexCharts pattern (`buildChart` from `preline/dist/helper-apexcharts.mjs`), vendored under `app/static/js/vendor/`.

## Definition of done
`python scripts/check_ui.py` exits 0, `make build-css` succeeds, and every page renders with no console errors.
