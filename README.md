# DecodeLabs Full Stack Internship

Repository for projects completed during the **DecodeLabs Full Stack Development Industrial Training Internship** (Batch 2026).

---

## Projects Directory

### [Shield AI — AI Agent Security Shield](./shield-ai)
- **Tagline**: *Secure Every Prompt. Control Every Action. Trust Every Agent.*
- **Role**: Full-Stack AI Agent Security Gateway, Policy Interceptor & Relational Command Center

---

### Project Milestones Overview

Inside the [`shield-ai/`](./shield-ai) directory, all four internship milestones are organized into dedicated project modules, each containing its own standalone code and comprehensive `README.md`:

| Milestone | Project Title | Path & Codebase | Dedicated Documentation |
|---|---|---|---|
| **Project 1** | **Responsive Frontend Development** | [`shield-ai/project-1/`](./shield-ai/project-1) | [`project-1/README.md`](./shield-ai/project-1/README.md) |
| **Project 2** | **Backend API Development & Integration** | [`shield-ai/project-2/`](./shield-ai/project-2) | [`project-2/README.md`](./shield-ai/project-2/README.md) |
| **Project 3** | **Relational Database Integration & Persistence** | [`shield-ai/project-3/`](./shield-ai/project-3) | [`project-3/README.md`](./shield-ai/project-3/README.md) |
| **Project 4** | **Complete Frontend and Backend Integration** | [`shield-ai/project-4/`](./shield-ai/project-4) | [`project-4/README.md`](./shield-ai/project-4/README.md) |

> 📦 **Final Project 4 Deliverable Archive**:
> - Direct repository download: [`shield-ai/project-4/shield-ai-final.zip`](./shield-ai/project-4/shield-ai-final.zip)
> - Also available at root: [`shield-ai/shield-ai-final.zip`](./shield-ai/shield-ai-final.zip)

---

#### 🎨 [Project 1: Responsive Frontend Development](./shield-ai/project-1)
- **Objective**: Develop a modern, responsive, mobile-first frontend command center for AI agent security.
- **Technologies**: Semantic HTML5, CSS3 Modern Grid & Flexbox, Container Queries, Mobile-First Breakpoints (320px to 1440px+), Vanilla JavaScript (ES6+).
- **Design Tokens**: Mocha Mousse (`#A47864`), Ethereal Blue (`#A0D4E0`), Moonlit Grey (`#F2F0EA`), Montserrat & Open Sans.
- **8 Interactive Modules**: Overview Dashboard, Prompt Scanner, Agent Monitor, Tool Permissions Matrix, Approval Center, Threat Logs, Attack Simulator, Settings.
- **Dedicated Guide**: [`shield-ai/project-1/README.md`](./shield-ai/project-1/README.md)

#### ⚡ [Project 2: Backend API Development & Integration](./shield-ai/project-2)
- **Objective**: Develop a high-performance REST API gateway connecting the frontend modules to backend application logic.
- **Technologies**: Python 3.14, FastAPI, RESTful JSON APIs, Pydantic v2 schemas.
- **Architectural Principles**:
  - **The Gatekeeper Rule**: "Never Trust the Client" — syntactic and semantic server-side validation.
  - **Meaningful HTTP Status Codes**: `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `404 Not Found`, `409 Conflict`.
  - **Security Logic**: Heuristic injection pattern detection, PII/secret masking, policy hierarchy evaluation (*strictest policy wins*).
- **Dedicated Guide**: [`shield-ai/project-2/README.md`](./shield-ai/project-2/README.md)

#### 🗄️ [Project 3: Relational Database Integration & Persistence](./shield-ai/project-3)
- **Objective**: Enterprise relational persistence, ORM data modeling, migrations, and comprehensive CRUD operations.
- **Technologies**: SQLAlchemy 2.0 ORM, SQLite with `PRAGMA foreign_keys=ON;`, Alembic migrations.
- **The Four Architectural Pillars**:
  1. **Blueprint (Schema & Design)**: 6 normalized 3NF relational models (`agents`, `tools`, `agent_tools` M:M junction, `security_events`, `approval_requests`, `application_settings`).
  2. **Bridge (Integration & Connection)**: Centralized singleton SQLAlchemy engine with reusable session factory, avoiding per-request connection overhead.
  3. **Action (CRUD & RESTful Standards)**: Complete CRUD APIs across all entities (Agents, Tool Catalog, Agent-Tool Permissions, Security Audit Events, Approvals, and Settings).
  4. **Shield (Integrity & Security)**: Database-level foreign keys with cascading rules, domain `CHECK` constraints (e.g. risk score 0–100, sensitivity 0.1–5.0), `UNIQUE` natural keys, and ORM parameterized queries.
- **Dedicated Guide**: [`shield-ai/project-3/README.md`](./shield-ai/project-3/README.md)

#### 🔄 [Project 4: Complete Frontend and Backend Integration](./shield-ai/project-4)
- **Objective**: Establish a seamless, unified full-stack application connecting the frontend and backend with asynchronous Fetch API communication, defensive state management, and CORS support.
- **Integration Capabilities**:
  - **All 5 REST Methods**: `GET`, `POST`, `PUT`, `PATCH`, and `DELETE` (HTTP 204 No Content empty responses).
  - **Centralized Fetch API Client (`js/api.js`)**: Robust async/await wrapper with configurable base URL, `AbortController` multiplexing (intentional cancellation vs timeout), explicit `MALFORMED_JSON` parsing, and guaranteed `finally` cleanup.
  - **Asynchronous Flow & Hydration**: Concurrent initial data fetching via `Promise.allSettled()`, debounced search with query cancellation (`AbortController`), and reactive cross-module UI updates.
  - **Defensive UI States**: Loading indicators and disabled buttons guaranteed re-enabled in `finally`, success feedback toasts, empty state placeholders, and inline retry banners.
  - **CORS & Preflight Handling**: Configured FastAPI `CORSMiddleware` supporting cross-origin setups and preflight `OPTIONS` requests across standard frontend ports.
- **Quality & Verification**: **77 automated tests** (60 backend pytest tests + 17 frontend Node.js API client tests, 100% passing) and automated Chrome browser CDP end-to-end verification.
- **Dedicated Guide**: [`shield-ai/project-4/README.md`](./shield-ai/project-4/README.md)
