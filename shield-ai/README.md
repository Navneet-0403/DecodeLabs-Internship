# Shield AI — AI Agent Security Shield

**Secure Every Prompt. Control Every Action. Trust Every Agent.**

Full-Stack Implementation (DecodeLabs Projects 1 & 2): Responsive UI frontend paired with a high-performance **Python + FastAPI + SQLite** backend REST API gateway.

---

## 1. Quick Start Guide (Windows)

### Prerequisites
- Python 3.10+ (tested on Python 3.14.3)
- PowerShell or Command Prompt

### Step 1: Create and Activate Virtual Environment
```powershell
# Navigate to the project root directory
cd C:\Users\navne\Downloads\shield-ai

# Create virtual environment
python -m venv .venv

# Activate virtual environment (PowerShell)
.\.venv\Scripts\Activate.ps1
```

### Step 2: Install Backend Dependencies
```powershell
pip install -r backend/requirements.txt
```

### Step 3: Run the Application
```powershell
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### Step 4: Open in Your Browser
- **Integrated Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- **Interactive OpenAPI Documentation (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 2. Project Architecture & Structure

The application serves both the static frontend (HTML5/CSS3/Vanilla JS) and the REST API from the same FastAPI server instance, ensuring seamless same-origin communication and zero CORS complications.

```
shield-ai/
├── index.html                  # Semantic HTML5 shell and 8 modular views
├── css/
│   ├── style.css               # Mobile-first design system and design tokens
│   └── responsive.css          # Fluid layout breakpoints (320px to 1440px+)
├── js/
│   ├── api.js                  # Centralized REST API client (Fetch wrapper)
│   └── app.js                  # Frontend controllers and UI state management
├── data/
│   └── shield_ai.db            # Persistent SQLite database (auto-initialized)
├── backend/
│   ├── requirements.txt        # Backend dependencies
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI entrypoint, middleware, static mounting
│   │   ├── database.py         # SQLite schema initialization & connection pooling
│   │   ├── schemas.py          # Pydantic models for validation and serialization
│   │   ├── exceptions.py       # Standard Gatekeeper error handling and status codes
│   │   ├── routes/
│   │   │   ├── dashboard.py    # GET /api/dashboard
│   │   │   ├── scanner.py      # POST /api/scans
│   │   │   ├── agents.py       # GET /api/agents, GET /api/agents/{id}/activity
│   │   │   ├── permissions.py  # GET, PUT /api/tools, POST /api/tools/reset
│   │   │   ├── approvals.py    # GET, POST /api/approvals/{id}/decision
│   │   │   ├── events.py       # GET /api/events, GET /api/events/{id}
│   │   │   ├── simulator.py    # POST /api/simulations
│   │   │   └── settings.py     # GET, PUT /api/settings, POST /api/demo/reset
│   │   └── services/
│   │       ├── security_engine.py # Heuristic pattern & PII detection engine
│   │       ├── policy_engine.py   # Decision hierarchy & tool policy evaluator
│   │       ├── risk_engine.py     # Settings-aware composite risk calculation
│   │       └── audit_service.py   # Thread-safe event and approval logger
│   └── tests/
│       ├── test_health.py      # Health and root serving checks
│       ├── test_scanner.py     # Prompt detection and PII masking tests
│       ├── test_permissions.py  # Tool permission CRUD and validation tests
│       ├── test_approvals.py    # Approval workflow and conflict checks
│       ├── test_events.py       # Audit logs filtering, search, and pagination
│       ├── test_simulator.py    # Multi-stage attack simulation tests
│       ├── test_persistence.py  # SQLite persistence across restarts
│       └── test_integration.py  # End-to-end frontend-backend workflow tests
└── README.md
```

---

## 3. Database Schema (SQLite)

The backend creates and seeds `data/shield_ai.db` automatically on startup:

### 1. `security_events`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `event_id`: TEXT UNIQUE (e.g., `EV-1001`)
- `category`: TEXT (e.g., `Prompt injection attempt`, `Sensitive data exposure`)
- `source`: TEXT (e.g., `Prompt Scanner`, `Attack Simulator`, agent name)
- `risk_level`: TEXT (`Low`, `Medium`, `High`, `Critical`)
- `decision`: TEXT (`Allowed`, `Approval required`, `Blocked`)
- `explanation`: TEXT (matched indicators, rationale; **never stores raw prompts or secrets**)
- `created_at`: TEXT (ISO 8601 timestamp)
- `event_source`: TEXT (`seed` or `application`)

### 2. `tool_permissions`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `tool_id`: TEXT UNIQUE (e.g., `tool-1` through `tool-7`)
- `tool_name`: TEXT
- `description`: TEXT
- `assigned_agent`: TEXT
- `risk_level`: TEXT
- `permission_status`: TEXT (`Allowed`, `Approval Required`, `Restricted`, `Blocked`)
- `updated_at`: TEXT

### 3. `approval_requests`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `approval_id`: TEXT UNIQUE (e.g., `AP-201` through `AP-204`)
- `agent_name`: TEXT
- `operation`: TEXT
- `risk_level`: TEXT
- `reason`: TEXT
- `status`: TEXT (`Pending`, `Approved`, `Rejected`)
- `created_at`: TEXT
- `updated_at`: TEXT

### 4. `settings`
- `id`: INTEGER PRIMARY KEY (Row 1)
- `risk_sensitivity`: REAL (0.1 to 5.0, default 1.0)
- `automatic_critical_blocking`: INTEGER (0 or 1)
- `require_high_risk_approval`: INTEGER (0 or 1)
- `mask_sensitive_data`: INTEGER (0 or 1)
- `notifications_enabled`: INTEGER (0 or 1)
- `updated_at`: TEXT

---

## 4. API Endpoints Reference

All endpoints return JSON responses. Errors follow a unified standard format.

### Standard Error Format
```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Prompt exceeds the maximum allowed length of 1000 characters.",
    "details": {}
  }
}
```

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `GET` | `/api/health` | System health and database connection status | 200 |
| `GET` | `/api/dashboard` | Aggregated security metrics, risk distribution, timeline | 200 |
| `POST` | `/api/scans` | Analyze input prompt, detect injection & PII, log event | 200, 400 |
| `GET` | `/api/agents` | List 4 simulated autonomous agent profiles | 200 |
| `GET` | `/api/agents/{agent_id}/activity` | Fetch agent's real-time policy telemetry and workflow stages | 200, 404 |
| `GET` | `/api/tools` | Retrieve tool permission matrix | 200 |
| `GET` | `/api/tools/{tool_id}` | Retrieve single tool permission | 200, 404 |
| `PUT` | `/api/tools/{tool_id}` | Update tool permission status | 200, 400, 404 |
| `POST` | `/api/tools/reset` | Restore tool permissions to default baseline | 200 |
| `GET` | `/api/approvals` | List approval requests (optional `?status=Pending`) | 200 |
| `POST` | `/api/approvals/{approval_id}/decision` | Approve or Reject pending request | 200, 400, 404, 409 |
| `GET` | `/api/events` | Filter and paginate security audit events | 200 |
| `GET` | `/api/events/{event_id}` | Retrieve individual audit event | 200, 404 |
| `POST` | `/api/simulations` | Execute attack simulation vector and apply policy | 200, 400 |
| `GET` | `/api/settings` | Retrieve active policy thresholds | 200 |
| `PUT` | `/api/settings` | Persist updated security thresholds | 200, 400 |
| `POST` | `/api/demo/reset` | Reset demo events and approval requests to seed data | 200 |

---

## 5. Security & Architectural Principles

### Gatekeeper Rule: "Never Trust the Client"
- **Syntactic Validation**: Enforced via Pydantic schemas (prompt presence, 1000-character upper limit, valid enum values for decisions and permissions, numeric sensitivity bounds).
- **Semantic Validation**: Enforced in route handlers and services (verifying that agents and tools exist in the database, verifying that approval requests are in `Pending` state before resolution to prevent replay attacks, rejecting conflicting updates).

### Authentication vs. Authorization
- **Authentication (AuthN)**: Proves **who** an entity is (e.g., verifying user identity via JWT tokens, OAuth2, or certificates). In this prototype, authentication is documented as external to this stage since the application operates as an internal enterprise API gateway.
- **Authorization (AuthZ)**: Governs **what** an authenticated entity is permitted to execute. Shield AI enforces fine-grained authorization policies at the tool and policy level on the server. Even if a client claims an action is "Allowed", the backend independently verifies the permission matrix in SQLite and overrides any insecure frontend state.

### Privacy & Data Loss Prevention
- Raw prompt texts and unmasked API keys/tokens are **never written to the SQLite event log**. Only detected threat indicator classifications and masked previews (`sk-••••••cd`) are retained in audit records.

---

## 6. Automated Testing Verification

Run the test suite using pytest:

```powershell
python -m pytest backend/tests -v
```

### Verified Test Results (35 passed in 1.62s):
- **Health & Serving**: `test_health.py` (Health check, root HTML serving) — **PASSED**
- **Scanner**: `test_scanner.py` (Safe prompts, prompt injection, PII masking, empty prompts, oversized prompts) — **PASSED**
- **Tool Permissions**: `test_permissions.py` (List tools, single tool lookup, invalid status rejection, reset tools) — **PASSED**
- **Approval Center**: `test_approvals.py` (Pending filters, approve workflow, reject workflow, conflict resolution on already-resolved requests) — **PASSED**
- **Audit Logs**: `test_events.py` (Search query, severity filter, category filter, 404 on missing event) — **PASSED**
- **Attack Simulator**: `test_simulator.py` (Safe request, instruction override, external email approval generation, invalid scenarios) — **PASSED**
- **Persistence**: `test_persistence.py` (Settings updates, database persistence, dashboard metric calculations) — **PASSED**
- **Integration**: `test_integration.py` (Static file mounting, end-to-end prompt scan to dashboard updates, tool permission to live agent telemetry updates, simulation to approval queue workflow) — **PASSED**

---

## 7. Known Prototype Boundaries

1. **Autonomous Agents**: The four agent profiles are simulated models with telemetry workflows. They represent the intercepted actions of autonomous systems rather than live connected LLMs.
2. **Detection Heuristics**: The security engine uses pattern-matching regexes and sensitive data signatures representing first-stage firewall heuristics. In production, this would be backed by semantic embedding classification and vector-based anomaly detection.
3. **Local Scope**: Storage uses SQLite for simple, dependency-free local execution. In production, PostgreSQL with connection pooling would be utilized.
