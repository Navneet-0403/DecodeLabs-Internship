# DecodeLabs Full Stack Internship

Repository for projects completed during the **DecodeLabs Full Stack Development Industrial Training Internship** (Batch 2026).

---

## Projects Directory

### [Shield AI — AI Agent Security Shield](./shield-ai)
- **Tagline**: *Secure Every Prompt. Control Every Action. Trust Every Agent.*
- **Role**: Full-Stack AI Agent Security Gateway, Policy Interceptor & Relational Command Center

---

### Project Phases Overview

#### 🎨 [Project 1: Responsive Frontend Development](./shield-ai)
- **Objective**: Develop a modern, responsive, mobile-first frontend command center for AI agent security.
- **Technologies**: Semantic HTML5, CSS3 Modern Grid & Flexbox, Container Queries, Mobile-First Breakpoints (320px to 1440px+), Vanilla JavaScript (ES6+).
- **Design Tokens**: Mocha Mousse (`#A47864`), Ethereal Blue (`#A0D4E0`), Moonlit Grey (`#F2F0EA`), Montserrat & Open Sans.
- **8 Interactive Modules**:
  1. Security Overview Dashboard (KPIs, SVG timeline, risk distribution)
  2. Prompt Scanner (live detection UI with classification badges)
  3. Agent Monitor (real-time telemetry and execution pipeline)
  4. Tool Permissions Matrix (interactive policy configuration)
  5. Approval Center (human-in-the-loop modal dialogs)
  6. Threat Logs (audit table with category filtering and search)
  7. Attack Simulator (multi-stage attack vector selector)
  8. Settings Panel (gateway preference sliders and switches)

#### ⚡ [Project 2: Backend API Development & Integration](./shield-ai)
- **Objective**: Develop a high-performance REST API gateway connecting the frontend modules to backend logic.
- **Technologies**: Python 3.14, FastAPI, RESTful JSON APIs, Pydantic v2 schemas.
- **Architectural Principles**:
  - **The Gatekeeper Rule**: "Never Trust the Client" — syntactic and semantic server-side validation.
  - **Meaningful HTTP Status Codes**: `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `404 Not Found`, `409 Conflict`.
  - **Security Logic**: Heuristic injection pattern detection, PII/secret masking, policy hierarchy evaluation (*strictest policy wins*).

#### 🗄️ [Project 3: Relational Database Integration & Persistence](./shield-ai)
- **Objective**: Enterprise relational persistence, ORM data modeling, migrations, and comprehensive CRUD operations.
- **Technologies**: SQLAlchemy 2.0 ORM, SQLite with `PRAGMA foreign_keys=ON;`, Alembic migrations.
- **The Four Architectural Pillars**:
  1. **Blueprint (Schema & Design)**: 6 normalized 3NF relational models (`agents`, `tools`, `agent_tools` M:M junction, `security_events`, `approval_requests`, `application_settings`).
  2. **Bridge (Integration & Connection)**: Centralized singleton SQLAlchemy engine with reusable session factory, avoiding per-request connection overhead.
  3. **Action (CRUD & RESTful Standards)**: Complete CRUD APIs across all entities (Agents, Tool Catalog, Agent-Tool Permissions, Security Audit Events, Approvals, and Settings).
  4. **Shield (Integrity & Security)**: Database-level foreign keys with cascading rules, domain `CHECK` constraints (e.g. risk score 0–100, sensitivity 0.1–5.0), `UNIQUE` natural keys, and ORM parameterized queries.
- **Database Migrations**: Fully reversible Alembic migrations (`backend/migrations/`) verified on fresh databases with zero Project 2 data loss.
- **Quality & Verification**: **54 automated pytest tests** covering models, relationships, CRUD, migrations, SQL injection defense, and end-to-end integration with 100% test database isolation.
