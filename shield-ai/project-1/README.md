# Shield AI — Project 1: Responsive Frontend Development
**DecodeLabs Full Stack Development Internship — Batch 2026**

> **Tagline**: Secure Every Prompt. Control Every Action. Trust Every Agent.

---

## 1. Project Overview

**Project 1** establishes the user interface foundation for **Shield AI**, an AI Agent Security Gateway and Command Center. The goal was to build a modern, high-performance, mobile-first responsive web interface using vanilla web technologies without heavyweight frameworks.

---

## 2. Key Objectives & Learning Outcomes

- **Semantic HTML5**: Clean, accessible document structure utilizing `<header>`, `<main>`, `<section>`, `<article>`, `<dialog>`, and `<aside>`.
- **Mobile-First CSS3 Layouts**: Designed from small viewports (320px) up to ultra-wide desktop monitors (1440px+).
- **CSS Grid & Flexbox**: Two-dimensional layouts for dashboard KPI cards and permission matrices; one-dimensional layouts for headers, drawers, and action bars.
- **Modern Design System**: Custom design tokens with CSS custom properties (`--mocha`, `--ethereal`, `--moonlit`, etc.).
- **Interactive Vanilla JavaScript**: Asynchronous tab switching, modal dialog inspection, progressive visual attack simulation, and input character counter.

---

## 3. Design Tokens & Visual Hierarchy

| Token Name | Hex Code | Role |
|---|---|---|
| **Mocha Mousse** | `#A47864` | Primary brand accent, KPI headers, active navigation pills |
| **Ethereal Blue** | `#A0D4E0` | Secondary accent, info badges, subtle borders, focus rings |
| **Moonlit Grey** | `#F2F0EA` | Canvas background, off-white surface cards |
| **Ink** | `#201E1F` | High-contrast body typography and headings |
| **Success Emerald** | `#2E7D32` | "Allowed" policy badges and safe scan outputs |
| **Warning Amber** | `#ED6C02` | "Approval Required" state badges and medium risk indicators |
| **Critical Crimson** | `#D32F2F` | "Blocked" actions, high-risk flags, and threat banners |

---

## 4. The Eight Interactive Modules

1. **Overview Dashboard**: High-level telemetry, live KPI cards, dynamic risk distribution bars, and responsive SVG activity chart.
2. **Prompt Scanner**: Security gatekeeper interface with character counter, sample test prompts, and heuristic threat breakdown.
3. **Agent Monitor**: AI agent registry with execution stages, proposed actions, and policy risk levels.
4. **Tool Permissions Matrix**: Natural tool toggles and granular status dropdowns (`Allowed`, `Approval Required`, `Restricted`, `Blocked`).
5. **Approval Center**: Human-in-the-loop governance queue with one-click "Approve" or "Reject" actions.
6. **Threat Logs**: Filterable security audit table supporting search by keyword, severity, category, and policy decision.
7. **Attack Simulator**: Multi-stage attack scenario player featuring progressive visual stage transitions.
8. **Application Settings**: Policy controls including risk sensitivity slider, critical blocking toggles, and PII masking switches.

---

## 5. Responsive Breakpoints

- **Mobile (320px – 767px)**: Single-column stacked cards, off-canvas slide-out hamburger navigation drawer.
- **Tablet (768px – 1023px)**: 2-column KPI grid, horizontally scrollable data tables.
- **Laptop & Desktop (1024px – 1440px+)**: Multi-column desktop grid, sticky navigation header, full widescreen layout.

---

## 6. How to Run Project 1

Since Project 1 is a pure frontend implementation:
1. Double click `index.html` to open directly in any web browser.
2. Alternatively, serve via Python's built-in HTTP server:
   ```powershell
   python -m http.server 8000
   ```
3. Open `http://localhost:8000` in Chrome, Firefox, Safari, or Edge.

