# DecodeLabs Full Stack Internship

Repository for projects completed during the **DecodeLabs Full Stack Development Industrial Training Internship** (Batch 2026).

---

## Projects Directory

### [Shield AI — AI Agent Security Shield](./shield-ai)
- **Tagline**: *Secure Every Prompt. Control Every Action. Trust Every Agent.*
- **Role**: Full-Stack AI Agent Security Gateway, Policy Interceptor & Relational Command Center

---

### Project Milestones Overview

#### 🎨 [Project 1: Responsive Frontend Development](./shield-ai)
- **Objective**: Develop a modern, responsive, mobile-first frontend command center for AI agent security.
- **Technologies**: Semantic HTML5, CSS3 Modern Grid & Flexbox, Container Queries, Mobile-First Breakpoints (320px to 1440px+), Vanilla JavaScript (ES6+).
- **Design Tokens**: Mocha Mousse (`#A47864`), Ethereal Blue (`#A0D4E0`), Moonlit Grey (`#F2F0EA`), Montserrat & Open Sans.
- **8 Interactive Modules**: Overview Dashboard, Prompt Scanner, Agent Monitor, Tool Permissions Matrix, Approval Center, Threat Logs, Attack Simulator, Settings.

#### ⚡ [Project 2: Backend API Development & Integration](./shield-ai)
- **Objective**: Develop a high-performance REST API gateway connecting the frontend modules to backend application logic.
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

#### 🔄 [Project 4: Complete Frontend and Backend Integration](./shield-ai)
- **Objective**: Establish a seamless, unified full-stack application connecting the frontend and backend with asynchronous Fetch API communication, defensive state management, and CORS support.
- **Integration Capabilities**:
  - **Centralized Fetch API Client (`js/api.js`)**: Robust async/await wrapper with configurable base URL, 15s `AbortController` timeout, and comprehensive HTTP status-code discrimination (200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500, 502).
  - **Asynchronous Flow & Hydration**: Concurrent initial data fetching via `Promise.allSettled()`, debounced search with query cancellation (`AbortController`), and reactive cross-module UI updates.
  - **Defensive UI States**: Loading indicators and disabled buttons during in-flight mutations, success feedback toasts, empty state placeholders, and inline retry banners.
  - **Safe DOM Rendering**: Strict HTML sanitization via `esc()` preventing DOM-based XSS vulnerabilities.
  - **CORS & Preflight Handling**: Configured FastAPI `CORSMiddleware` supporting cross-origin setups and preflight `OPTIONS` requests.
- **Quality & Verification**: **57 automated pytest tests** covering full-stack integration, migrations, model constraints, relationships, CRUD, and SQL injection defense.
