# Shield AI — Project 4: Complete Frontend and Backend Integration
**DecodeLabs Full Stack Development Internship — Batch 2026**

> **Tagline**: Secure Every Prompt. Control Every Action. Trust Every Agent.

---

## 1. Project Overview

**Project 4** brings together the frontend, backend, and relational database into a unified, industrial-grade full-stack application. It fulfills all requirements from the 19-page DecodeLabs Project 4 curriculum: Input-Process-Output flows, asynchronous Fetch API patterns, complete REST HTTP verb coverage, robust error discrimination, preflight CORS, guaranteed resource cleanup, and regression testing.

---

## 2. Key Objectives & Architectural Highlights

1. **Complete REST HTTP Method Support**:
   - `GET`: Retrieve dashboard metrics, agent profiles, tool permissions, logs, settings, and health status.
   - `POST`: Create prompt scans, execute attack simulations, and register approval decisions.
   - `PUT`: Full replacement of tool permissions (`PUT /api/tools/{id}`) and application settings (`PUT /api/settings`).
   - `PATCH`: Partial updates for settings (`PATCH /api/settings`), tool permissions (`PATCH /api/tools/{id}`), agents (`PATCH /api/agents/{id}`), and approvals (`PATCH /api/approvals/{id}`).
   - `DELETE`: Permanent event purge returning **`HTTP 204 No Content`** with a clean empty body (`DELETE /api/events/{id}/purge`).

2. **Centralized REST API Client (`js/api.js`)**:
   - **`AbortController` Multiplexing**: Seamlessly combines external cancellation signals (debounced search input) with internal request timeouts (15s default).
   - **Accurate Error Discrimination**: Intentional user cancellations throw `AbortError` (`isCancelled = true`, `code = "REQUEST_CANCELLED"`) without ever misclassifying as timeouts. Actual timeouts report `TimeoutError` (`isTimeout = true`, `code = "REQUEST_TIMEOUT"`).
   - **Guaranteed `try...finally` Cleanup**: Timeout timers and external abort event listeners are freed in `finally` blocks across all paths, including circular JSON serialization failures, network drops, timeouts, cancellations, and successes.
   - **Predictable JSON Body Parsing**: Server responses declaring `application/json` or `+json` with invalid syntax explicitly throw a structured `MALFORMED_JSON` error with HTTP status preserved. Genuinely empty bodies and `HTTP 204` cleanly return `null`.

3. **Defensive UI State Management (`js/app.js`)**:
   - Guaranteed button re-enabling in `finally` blocks across all user actions (`scan()`, `runSim()`, `updateToolPermission()`, `decideApprovalAction()`, `applySettings()`).
   - Strict XSS protection via contextual HTML escaping (`esc()`).
   - Parallel initial data hydration via `Promise.allSettled()`.

4. **Cross-Origin Resource Sharing (CORS)**:
   - Configured FastAPI `CORSMiddleware` supporting `GET, POST, PUT, PATCH, DELETE, OPTIONS` and handling browser preflight requests across standard frontend development ports.

---

## 3. Verified Automated Test Suite (77 Tests, 100% Passing)

### A. Backend Pytest Suite (60 Tests)
```powershell
python -m pytest backend/tests -v
```
- Full-Stack Integration & 5 REST Verbs: `test_fullstack_integration.py` — **6 PASSED**
- Alembic Database Migrations: `test_migrations.py` — **4 PASSED**
- Model Constraints & Foreign Keys: `test_models_and_schema.py` — **5 PASSED**
- Complete Relational CRUD: `test_crud_operations.py` — **5 PASSED**
- Relational Cascades & Junctions: `test_relationships.py` — **3 PASSED**
- SQL Injection Parameterization: `test_sql_injection.py` — **2 PASSED**
- Scanner, Approvals, Simulator, Permissions & Events — **35 PASSED**
*Total Backend*: **60 passed in ~5.4s.**

### B. Frontend API Client Regression Suite (17 Tests)
```powershell
node --test tests/test_api_client.js
```
- `AbortController` cancellation before dispatch & during execution — **PASSED**
- Internal timeout enforcement with and without external signals — **PASSED**
- Guaranteed timer & listener cleanup on circular JSON serialization failure — **PASSED**
- Observable spy verification of resource cleanup on success, network failure, and cancellation — **PASSED**
- Explicit `MALFORMED_JSON` syntax error handling with HTTP status preservation — **PASSED**
- HTTP 204 No Content and empty body handling — **PASSED**
*Total Frontend*: **17 passed in ~400ms.**

### C. Browser-Based Automated End-to-End Verification (Chrome CDP)
```powershell
node scripts/browser_verify.js
```
- Real Headless Google Chrome (`Chrome/156`) tested via Chrome DevTools Protocol.
- All 8 interactive modules exercised.
- **0 Console Errors**, **0 Unhandled Promise Rejections**, **0 stuck loaders**.

---

## 4. Final Submission Deliverable Archive

- **Archive File**: `shield-ai-final.zip` (available in this directory and workspace root).
- **Format**: 100% POSIX forward slashes (`/`) for universal compatibility across Windows, Linux, and macOS.
- **Verification Script**: `python scripts/package_and_validate.py` verifies CRC32 integrity, absence of backslashes, and automated test execution against the extracted sandbox.

---

## 5. How to Run Project 4

```powershell
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Run database migrations
alembic upgrade head

# 3. Start server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

# 4. Open in browser
# Navigate to http://127.0.0.1:8000
```

