# DecodeLabs Full Stack Internship

Repository for projects completed during the **DecodeLabs Full Stack Development Industrial Training Internship** (Batch 2026).

---

## Projects Directory

### [Project 1 & 2: Shield AI — AI Agent Security Shield](./shield-ai)
- **Tagline**: *Secure Every Prompt. Control Every Action. Trust Every Agent.*
- **Role**: Full-Stack AI Agent Security Gateway, Policy Interceptor & Command Center
- **Tech Stack**:
  - **Frontend**: Semantic HTML5, Modern CSS3 (Mobile-First, Grid, Flexbox, Container Queries), Vanilla JavaScript
  - **Backend**: Python 3.14, FastAPI, RESTful API (JSON), Pydantic v2
  - **Database**: SQLite (persistent storage for events, permissions, approvals, and settings)
  - **Design Tokens**: Mocha Mousse (`#A47864`), Ethereal Blue (`#A0D4E0`), Moonlit Grey (`#F2F0EA`), Montserrat & Open Sans
- **Key Modules & Capabilities**:
  1. **Security Command Center**: Aggregated live metrics, risk distribution bar chart, SVG activity timeline, recent events table.
  2. **Prompt Scanner**: Heuristic pattern matching & sensitive data masking (PII, API keys, tokens) via `POST /api/scans`.
  3. **Agent Monitor**: Simulated autonomous agent telemetry and real-time policy evaluation via `GET /api/agents/{id}/activity`.
  4. **Tool Permissions Matrix**: Granular least-privilege policy configuration persisted via `PUT /api/tools/{id}`.
  5. **Approval Center**: Human-in-the-loop review queue preventing replay attacks via `POST /api/approvals/{id}/decision`.
  6. **Threat Logs**: Comprehensive audit logs with multi-parameter search, filtering, and pagination via `GET /api/events`.
  7. **Attack Simulator**: Multi-stage attack vectors applying the Gatekeeper rule (*the stricter policy wins*) via `POST /api/simulations`.
  8. **Settings & Gateway Preferences**: Sensitivity multipliers, auto-blocking, and data masking via `GET` / `PUT /api/settings`.
- **Quality & Verification**: 35 automated unit and end-to-end integration tests passing with 100% test database isolation.
