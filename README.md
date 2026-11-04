# DecodeLabs Full Stack Internship

Repository for projects completed during the **DecodeLabs Full Stack Development Industrial Training Internship** (Batch 2026).

---

## Projects Directory

### [Project 1, 2 & 3: Shield AI — AI Agent Security Shield](./shield-ai)
- **Tagline**: *Secure Every Prompt. Control Every Action. Trust Every Agent.*
- **Role**: Full-Stack AI Agent Security Gateway, Policy Interceptor & Relational Command Center
- **Tech Stack**:
  - **Frontend**: Semantic HTML5, Modern CSS3 (Mobile-First, Grid, Flexbox, Container Queries), Vanilla JavaScript
  - **Backend**: Python 3.14, FastAPI, RESTful API (JSON), Pydantic v2
  - **Database & ORM (Project 3)**: SQLAlchemy 2.0 ORM, SQLite with Foreign Key PRAGMA enforcement, Alembic database migrations
  - **Design Tokens**: Mocha Mousse (`#A47864`), Ethereal Blue (`#A0D4E0`), Moonlit Grey (`#F2F0EA`), Montserrat & Open Sans
- **Database Architecture (Four Pillars)**:
  1. **Blueprint**: 6 normalized relational models (Agents, Tools, AgentTools M:M junction, Security Events, Approval Requests, Application Settings).
  2. **Bridge**: SQLAlchemy 2.0 session factory with SQLite PRAGMA `foreign_keys=ON;` connection listener.
  3. **Action**: Complete CRUD mapping across all entities with standard HTTP status codes (`200`, `201`, `204`, `400`, `404`, `409`).
  4. **Shield**: Database constraints (NOT NULL, UNIQUE, CHECK), referential cascading, and 100% parameterization against SQL Injection.
- **Key Modules & Capabilities**:
  1. **Security Command Center**: Aggregated live metrics, risk distribution bar chart, SVG activity timeline, recent events table.
  2. **Prompt Scanner**: Heuristic pattern matching & sensitive data masking (PII, API keys, tokens) via `POST /api/scans`.
  3. **Agent Monitor & CRUD**: Full agent management and real-time policy evaluation via `/api/agents`.
  4. **Tool Catalog & Permissions Matrix**: Granular least-privilege policy configuration persisted via `/api/tool-catalog` and `/api/tools`.
  5. **Approval Center**: Human-in-the-loop review queue preventing replay attacks via `/api/approvals`.
  6. **Threat Logs**: Comprehensive audit logs with multi-parameter search, filtering, and pagination via `/api/events`.
  7. **Attack Simulator**: Multi-stage attack vectors applying the Gatekeeper rule (*the stricter policy wins*) via `POST /api/simulations`.
  8. **Settings & Gateway Preferences**: Sensitivity multipliers, auto-blocking, and data masking via `/api/settings`.
- **Quality & Verification**: 50 automated unit, relational constraint, and end-to-end integration tests passing with 100% test database isolation.
