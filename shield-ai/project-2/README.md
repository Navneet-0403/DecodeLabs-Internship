# Shield AI — Project 2: Backend API Development & Integration
**DecodeLabs Full Stack Development Internship — Batch 2026**

> **Tagline**: Secure Every Prompt. Control Every Action. Trust Every Agent.

---

## 1. Project Overview

**Project 2** connects the Shield AI frontend to a high-performance Python REST API gateway built with **FastAPI**. It introduces server-side security logic, data validation via Pydantic v2 schemas, and standard HTTP error handling according to the DecodeLabs curriculum.

---

## 2. Key Objectives & Learning Outcomes

- **The Gatekeeper Rule**: *"Never Trust the Client"* — all prompt evaluations, policy decisions, and tool permissions are enforced on the server.
- **RESTful API Principles**: Proper use of HTTP verbs (`GET`, `POST`, `PUT`, `DELETE`), URL hierarchies, and standard JSON status contracts.
- **Pydantic Validation**: Strict schema validation for incoming payloads and outbound serialization models.
- **Heuristic Security Engine**: Pattern-based detection for prompt injections, system prompt leak attempts, credential harvesting, and regex PII masking (emails, phone numbers, API keys).
- **Policy Engine**: Interception hierarchy where tool policies and risk sensitivity multipliers govern the final decision (*strictest rule wins*).

---

## 3. Implemented REST Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check reporting database availability |
| `GET` | `/api/dashboard` | Aggregated security metrics, risk distribution, and timeline buckets |
| `POST` | `/api/scans` | Heuristic evaluation of prompt text with PII detection and masking |
| `GET` | `/api/agents` | Catalog of monitored AI agents |
| `GET` | `/api/agents/{id}/activity` | Telemetry pipeline and policy evaluation for a specific agent |
| `GET` | `/api/tools` | Complete catalog of registered agent tools |
| `PUT` | `/api/tools/{id}` | Updates tool permission status (`Allowed`, `Approval Required`, `Restricted`, `Blocked`) |
| `POST` | `/api/tools/reset` | Restores default demonstration permissions |
| `GET` | `/api/approvals` | Human-in-the-loop review queue |
| `POST` | `/api/approvals/{id}/decision` | Resolves approval request (`Approved` or `Rejected`) |
| `GET` | `/api/events` | Query security audit events with search, risk, and category filters |
| `GET` | `/api/events/{id}` | Single security event detail inspection |
| `POST` | `/api/simulations` | Executes multi-stage attack scenarios against policy engine |
| `GET` | `/api/settings` | Retrieves global security sensitivity settings |
| `PUT` | `/api/settings` | Updates application sensitivity settings |
| `POST` | `/api/demo/reset` | Resets demonstration events and approvals to initial seed state |

---

## 4. Standard Gatekeeper Error Handling

All client and server errors conform to the standard Gatekeeper error format:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Prompt text cannot be empty or exceed 1000 characters.",
    "details": {}
  }
}
```

- **HTTP 400 Bad Request**: Input syntax errors, empty prompt strings, or invalid parameters.
- **HTTP 404 Not Found**: Resource not found (`AGENT_NOT_FOUND`, `TOOL_NOT_FOUND`, `EVENT_NOT_FOUND`).
- **HTTP 409 Conflict**: Attempting to resolve an already-decided approval request.
- **HTTP 422 Unprocessable Entity**: Pydantic schema validation failures.
- **HTTP 500 Internal Server Error**: Sanitized internal error; stack traces are never leaked to clients.

---

## 5. How to Run Project 2

### Prerequisites:
- Python 3.10+ (tested on Python 3.14.3)

### Installation & Execution:
```powershell
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Start FastAPI Server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Accessing the APIs:
- Application UI: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc Documentation: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
