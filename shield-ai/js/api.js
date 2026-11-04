/**
 * Shield AI — Centralized REST API Client Wrapper
 * DecodeLabs Project 4: Full-Stack Frontend & Backend Integration
 *
 * Provides comprehensive support for all five REST HTTP methods (GET, POST, PUT, PATCH, DELETE),
 * request timeout enforcement via AbortController, empty response handling (HTTP 204 No Content),
 * robust error discrimination (Network, Timeout, 4xx Client, 5xx Server), and safe JSON serialization.
 */

class ApiClient {
  constructor(baseUrl = "/api", defaultTimeout = 15000) {
    this.baseUrl = baseUrl;
    this.defaultTimeout = defaultTimeout;
  }

  /**
   * Centralized HTTP request execution with defensive validation and error handling.
   * @param {string} endpoint - API relative path (e.g. "/dashboard")
   * @param {Object} options - Fetch options (method, headers, body, signal, timeout)
   * @returns {Promise<any>} Parsed response data or null for empty / 204 responses
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const method = (options.method || "GET").toUpperCase();
    const timeout = options.timeout ?? this.defaultTimeout;

    // Manage request timeout with AbortController if no external signal is supplied
    let controller = null;
    let signal = options.signal;
    let timer = null;

    if (!signal && timeout > 0) {
      controller = new AbortController();
      signal = controller.signal;
      timer = setTimeout(() => {
        controller.abort();
      }, timeout);
    }

    const headers = {
      "Accept": "application/json",
      ...(options.headers || {})
    };

    let body = options.body;
    if (body !== undefined && body !== null && typeof body === "object" && !(body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
      body = JSON.stringify(body);
    }

    const config = {
      ...options,
      method,
      headers,
      body,
      signal
    };

    try {
      const response = await fetch(url, config);

      // Handle HTTP 204 No Content or HTTP 205 Reset Content safely
      if (response.status === 204 || response.status === 205) {
        return null;
      }

      // Safe body reading: handles empty bodies without throwing unexpected JSON EOF errors
      const contentType = response.headers.get("content-type") || "";
      const isJson = contentType.includes("application/json");
      let data = null;

      const rawText = await response.text();
      if (rawText && rawText.trim()) {
        if (isJson) {
          try {
            data = JSON.parse(rawText);
          } catch (jsonErr) {
            data = rawText;
          }
        } else {
          data = rawText;
        }
      }

      // Inspect response.ok to discriminate HTTP status codes
      if (!response.ok) {
        let errorMessage = "";
        let errorCode = `HTTP_${response.status}`;
        let errorDetails = {};

        // Parse structured backend error response
        if (data && typeof data === "object") {
          if (data.error && data.error.message) {
            errorMessage = data.error.message;
            errorCode = data.error.code || errorCode;
            errorDetails = data.error.details || {};
          } else if (data.detail) {
            if (Array.isArray(data.detail)) {
              errorMessage = data.detail.map(d => `${d.loc ? d.loc.join('.') + ': ' : ''}${d.msg}`).join("; ");
            } else {
              errorMessage = String(data.detail);
            }
            errorCode = "VALIDATION_ERROR";
          }
        }

        // Fallback status code mapping if backend did not emit structured text
        if (!errorMessage) {
          switch (response.status) {
            case 400: errorMessage = "Bad Request: Invalid input parameters."; break;
            case 401: errorMessage = "Unauthorized: Authentication required."; break;
            case 403: errorMessage = "Forbidden: Permission denied."; break;
            case 404: errorMessage = "Not Found: The requested resource does not exist."; break;
            case 409: errorMessage = "Conflict: Operation cannot be completed due to conflicting state."; break;
            case 422: errorMessage = "Unprocessable Entity: Input validation failed."; break;
            case 429: errorMessage = "Too Many Requests: Rate limit exceeded."; break;
            case 500: errorMessage = "Internal Server Error: Unexpected backend failure."; break;
            case 502:
            case 503:
            case 504: errorMessage = "Service Unavailable: Backend gateway is unreachable."; break;
            default: errorMessage = `HTTP error ${response.status}: ${response.statusText || "Request failed"}`;
          }
        }

        const httpError = new Error(errorMessage);
        httpError.status = response.status;
        httpError.statusText = response.statusText;
        httpError.code = errorCode;
        httpError.details = errorDetails;
        httpError.data = data;
        httpError.isHttpError = true;
        httpError.isClientError = response.status >= 400 && response.status < 500;
        httpError.isServerError = response.status >= 500;
        throw httpError;
      }

      return data;
    } catch (err) {
      if (err.isHttpError) {
        throw err;
      }

      // Check request timeout
      if (err.name === "AbortError") {
        const timeoutError = new Error(`Request timed out after ${timeout}ms. Please verify backend responsiveness.`);
        timeoutError.isTimeout = true;
        timeoutError.code = "REQUEST_TIMEOUT";
        throw timeoutError;
      }

      // Check network connection failure
      if (err.name === "TypeError" || String(err.message).toLowerCase().includes("failed to fetch")) {
        const netError = new Error("Unable to connect to Shield AI backend server. Please verify it is running on http://127.0.0.1:8000.");
        netError.isNetworkError = true;
        netError.code = "NETWORK_UNAVAILABLE";
        throw netError;
      }

      throw err;
    } finally {
      if (timer) {
        clearTimeout(timer);
      }
    }
  }

  /* ------------------------------------------------------------------------
     Generic REST Methods (GET, POST, PUT, PATCH, DELETE)
     ------------------------------------------------------------------------ */
  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "GET" });
  }

  post(endpoint, body = null, options = {}) {
    return this.request(endpoint, { ...options, method: "POST", body });
  }

  put(endpoint, body = null, options = {}) {
    return this.request(endpoint, { ...options, method: "PUT", body });
  }

  patch(endpoint, body = null, options = {}) {
    return this.request(endpoint, { ...options, method: "PATCH", body });
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "DELETE" });
  }

  /* ------------------------------------------------------------------------
     1. Health & System Status
     ------------------------------------------------------------------------ */
  getHealth() {
    return this.get("/health");
  }

  /* ------------------------------------------------------------------------
     2. Overview Dashboard
     ------------------------------------------------------------------------ */
  getDashboard() {
    return this.get("/dashboard");
  }

  /* ------------------------------------------------------------------------
     3. Prompt Scanner
     ------------------------------------------------------------------------ */
  scanPrompt(prompt) {
    return this.post("/scans", { prompt });
  }

  /* ------------------------------------------------------------------------
     4. Agent Monitor & CRUD
     ------------------------------------------------------------------------ */
  getAgents(activeOnly = false) {
    const q = activeOnly ? "?active_only=true" : "";
    return this.get(`/agents${q}`);
  }

  getAgent(agentId) {
    return this.get(`/agents/${encodeURIComponent(agentId)}`);
  }

  createAgent(agentData) {
    return this.post("/agents", agentData);
  }

  updateAgent(agentId, agentData) {
    return this.put(`/agents/${encodeURIComponent(agentId)}`, agentData);
  }

  patchAgent(agentId, partialData) {
    return this.patch(`/agents/${encodeURIComponent(agentId)}`, partialData);
  }

  deleteAgent(agentId) {
    return this.delete(`/agents/${encodeURIComponent(agentId)}`);
  }

  getAgentActivity(agentId) {
    return this.get(`/agents/${encodeURIComponent(agentId)}/activity`);
  }

  /* ------------------------------------------------------------------------
     5. Tool Permissions & Catalog
     ------------------------------------------------------------------------ */
  getTools() {
    return this.get("/tools");
  }

  getTool(toolId) {
    return this.get(`/tools/${encodeURIComponent(toolId)}`);
  }

  updateTool(toolId, permissionStatus) {
    return this.put(`/tools/${encodeURIComponent(toolId)}`, { permission_status: permissionStatus });
  }

  patchTool(toolId, permissionStatus) {
    return this.patch(`/tools/${encodeURIComponent(toolId)}`, { permission_status: permissionStatus });
  }

  resetTools() {
    return this.post("/tools/reset");
  }

  /* ------------------------------------------------------------------------
     6. Approval Center
     ------------------------------------------------------------------------ */
  getApprovals(status = null) {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    return this.get(`/approvals${query}`);
  }

  getApproval(approvalId) {
    return this.get(`/approvals/${encodeURIComponent(approvalId)}`);
  }

  createApproval(approvalData) {
    return this.post("/approvals", approvalData);
  }

  updateApproval(approvalId, updateData) {
    return this.put(`/approvals/${encodeURIComponent(approvalId)}`, updateData);
  }

  patchApproval(approvalId, partialData) {
    return this.patch(`/approvals/${encodeURIComponent(approvalId)}`, partialData);
  }

  deleteApproval(approvalId) {
    return this.delete(`/approvals/${encodeURIComponent(approvalId)}`);
  }

  decideApproval(approvalId, decision) {
    return this.post(`/approvals/${encodeURIComponent(approvalId)}/decision`, { decision });
  }

  /* ------------------------------------------------------------------------
     7. Threat Logs & Security Events
     ------------------------------------------------------------------------ */
  getEvents(params = {}, signal = null) {
    const queryParams = new URLSearchParams();
    if (params.q) queryParams.set("q", params.q);
    if (params.risk) queryParams.set("risk", params.risk);
    if (params.category) queryParams.set("category", params.category);
    if (params.decision) queryParams.set("decision", params.decision);
    if (params.limit !== undefined) queryParams.set("limit", params.limit);
    if (params.offset !== undefined) queryParams.set("offset", params.offset);

    const qs = queryParams.toString();
    return this.get(`/events${qs ? `?${qs}` : ""}`, { signal });
  }

  getEvent(eventId) {
    return this.get(`/events/${encodeURIComponent(eventId)}`);
  }

  deleteEvent(eventId) {
    return this.delete(`/events/${encodeURIComponent(eventId)}`);
  }

  purgeEvent(eventId) {
    // Tests HTTP 204 No Content empty response handling
    return this.delete(`/events/${encodeURIComponent(eventId)}/purge`);
  }

  /* ------------------------------------------------------------------------
     8. Attack Simulator
     ------------------------------------------------------------------------ */
  runSimulation(scenarioIndex) {
    return this.post("/simulations", { scenario_index: scenarioIndex });
  }

  /* ------------------------------------------------------------------------
     9. Settings & Demonstration State
     ------------------------------------------------------------------------ */
  getSettings() {
    return this.get("/settings");
  }

  updateSettings(settings) {
    return this.put("/settings", settings);
  }

  patchSettings(partialSettings) {
    return this.patch("/settings", partialSettings);
  }

  resetDemo() {
    return this.post("/demo/reset");
  }
}

// Global Singleton Export
const API = new ApiClient();
window.API = API;
