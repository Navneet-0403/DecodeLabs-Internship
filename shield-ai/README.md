# Shield AI — AI Agent Security Shield (DecodeLabs Project 1)

Frontend-only responsive implementation of an AI agent security gateway dashboard and policy interceptor. Built with semantic HTML5, modern CSS3 (Grid, Flexbox, Container Queries), and vanilla JavaScript. No external frameworks, backend, or LLM required.

---

## Quick Start

Run the local development server from this folder:

```powershell
python -m http.server 8000
```

Then visit **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## Project Structure

```
shield-ai/
├── index.html           # Semantic HTML5 shell and all 8 view sections
├── css/
│   ├── style.css        # Mobile-first base styles, design tokens, and components
│   └── responsive.css   # Fluid breakpoints (480px, 768px tablet, 1024px desktop, 1440px wide)
├── js/
│   └── app.js           # Client-side state, rules engine, mobile drawer, and view router
├── screenshots/         # Audit screenshots across mobile, tablet, and desktop viewports
└── README.md            # Project documentation and audit report
```

---

## DecodeLabs Design Specifications & Aesthetics

Built in strict compliance with the **DecodeLabs Full Stack Project 1 Industrial Training Kit**:

- **2025 Warm & Grounded Color Palette**:
  - `Mocha Mousse` (`#A47864`) — Stability & primary active states
  - `Ethereal Blue` (`#A0D4E0`) — Trust, highlights, and accessible focus rings
  - `Moonlit Grey` (`#F2F0EA`) — Refined neutral background
  - Semantic accents: `--ok: #1E7B4B`, `--warn: #9A6200`, `--bad: #B3261E`, `--acc: #2D6A80`
- **Typography Constraints** (Max 2 font families, 3 weights):
  - **Headings**: `Montserrat` (600, 800)
  - **Body**: `Open Sans` (400, 600)
- **Fluid Sizing**:
  - Typography scales continuously with `clamp()` (e.g. `clamp(1.35rem, 2.5vw + 0.9rem, 2.2rem)`)
  - Macro layouts built with **CSS Grid**; micro components built with **Flexbox**
  - KPI metric cards utilize CSS Container Queries (`@container (min-width: 220px)`)

---

## Responsive Design Strategy

Mobile-first architecture structured around the DecodeLabs baseline breakpoints:

| Category | Viewport Range | Layout Behavior |
| :--- | :--- | :--- |
| **Mobile** | $320\text{px} - 479\text{px}$ | Single-column stacked cards; 2-row adaptive header; sliding navigation drawer with frosted backdrop; contained touch-scrolling tables. |
| **Phablet / Landscape** | $480\text{px} - 767\text{px}$ | 2-column KPI cards; flexible action button wrapping; responsive drawer. |
| **Tablet** | $768\text{px} - 1023\text{px}$ | 2-column macro grid; 2-column charts & workflow; compact header layout. |
| **Desktop** | $1024\text{px} - 1439\text{px}$ | 2-column app shell (`260px` sticky sidebar + `1fr` content); 4-column KPI row; 3-column workflow; hamburger menu hidden. |
| **Large Desktop** | $1440\text{px}+$ | Centered max-width container (`1440px`), expanded whitespace, 4-column cards. |

---

## Core Views & Capabilities

1. **Security Command Center (`#v-overview`)**: KPI metrics, risk distribution bar chart, SVG activity timeline, recent events table, 9-stage gateway workflow, and protection modules.
2. **Prompt Scanner (`#v-scanner`)**: Inspects natural-language prompts for prompt injection, instruction overrides, jailbreaks, and PII leakage with heuristic scoring (0–100).
3. **Agent Monitor (`#v-agents`)**: Inspects 4 autonomous agents, profiles, activity counts, and step-by-step telemetry flows.
4. **Tool Permissions (`#v-perms`)**: Granular policy toggles and interactive permission matrix (Allowed, Approval Required, Restricted, Blocked).
5. **Approval Center (`#v-appr`)**: Human-in-the-loop review queue for high-risk agent operations with Approve / Reject controls.
6. **Threat Logs (`#v-logs`)**: Filterable, searchable audit table with real-time severity, category, and decision filters.
7. **Attack Simulator (`#v-sim`)**: Interactive simulation of multi-stage attacks and security policy decisions.
8. **Settings & Policy Preferences (`#v-set`)**: Sensitivity thresholds, automatic blocking, PII masking, and notification toggles.

---

## Step 6: Responsive Audit & Testing Verification

The entire interface has been inspected and verified using headless Chrome and device emulation across all 9 target viewports:

- **$320 \times 568$ (Mobile SE)**: Zero horizontal overflow (`scrollWidth = 320px`). Stacked action buttons and cards.
- **$375 \times 812$ (Standard Mobile)**: Zero horizontal overflow. Functional drawer with backdrop blur.
- **$390 \times 844$ (Modern Mobile)**: Smooth responsive wrapping; touch targets $\ge 44\text{px}$.
- **$428 \times 926$ (Large Mobile)**: Zero clipping; clean 2-row header.
- **$768 \times 1024$ (Portrait Tablet)**: 2-column KPI cards and flow stages.
- **$1024 \times 768$ (Desktop)**: 4-column KPI row; persistent sticky sidebar.
- **$1280 \times 800$ (Laptop)**: Balanced 3-column workflow layout; smooth scrolling.
- **$1440 \times 900$ (Wide Desktop)**: Content constrained cleanly to $1440\text{px}$ max width.
- **$1920 \times 1080$ (Full HD)**: Proportional typography and consistent spacing.

### Accessibility & Performance
- **WCAG 2.1 AA Focus**: Highly visible `:focus-visible` outline using Ethereal Blue (`#A0D4E0`).
- **Keyboard Navigation**: Drawer closes via <kbd>Escape</kbd> and restores focus to `#menu`; table wrappers have `tabindex="0" role="region"` for keyboard scrollability.
- **Touch Targets**: Minimum $44 \times 44\text{px}$ hit areas for buttons, switches, and navigation links.
- **Layout Stability (CLS)**: Responsive SVGs with fixed aspect-ratio `viewBox` attributes eliminate layout shifts during rendering.

---

## Prototype Notes & Scope

All prompt scanning, permissions, approval decisions, and agent telemetry are client-side prototypes intended for frontend demonstration according to the DecodeLabs specification. No external operations or remote network requests are executed.
