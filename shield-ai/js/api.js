/**
 * Shield AI — Centralized REST API Client Wrapper
 * DecodeLabs Project 4: Full-Stack Frontend & Backend Integration
 *
 * Implements robust asynchronous Fetch API communication, HTTP response validation,
 * status-code discrimination (200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500, 502),
 * AbortController timeout handling, in-flight search cancellation, and structured error propagation.
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
   * @returns {Promise<any>} Parsed response data or null for 204
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const timeout = options.timeout ?? this.defaultTimeout;

    // Manage request timeout with AbortController if no external signal provided
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
      headers,
      body,
      signal
    };

    try {
      const response = await fetch(url, config);

      // Handle 204 No Content safely without attempting to parse JSON
      if (response.status === 204) {
        return null;
      }

      // Safe JSON parsing: verify Content-Type before calling .json()
      const contentType = response.headers.get("content-type") || "";
      const isJson = contentType.includes("application/json");
      const data = isJson ? await response.json() : await response.text();

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
            // FastAPI validation error format (422 / 400)
            if (Array.isArray(data.detail)) {
              errorMessage = data.detail.map(d => `${d.loc ? d.loc.join('.') + ': ' : ''}${d.msg}`).join("; ");
            } else {
              errorMessage = String(data.detail);
            }
            errorCode = "VALIDATION_ERROR";
          }
        }

        // Fallback descriptive status messages if none extracted
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
        throw httpError;
      }

      return data;
    } catch (err) {
      if (err.isHttpError) {
        throw err;
      }

      // Check if timeout triggered
      if (err.name === "AbortError") {
        const timeoutError = new Error(`Request timed out after ${timeout}ms. Please verify backend responsiveness.`);
        timeoutError.isTimeout = true;
        timeoutError.code = "REQUEST_TIMEOUT";
        throw timeoutError;
      }

      // Check network / connection error
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
     1. Health & System Status
     ------------------------------------------------------------------------ */
  getHealth() {
    return this.request("/health");
  }

  /* ------------------------------------------------------------------------
     2. Overview Dashboard
     ------------------------------------------------------------------------ */
  getDashboard() {
    return this.request("/dashboard");
  }

  /* ------------------------------------------------------------------------
     3. Prompt Scanner
     ------------------------------------------------------------------------ */
  scanPrompt(prompt) {
    return this.request("/scans", {
      method: "POST",
      body: { prompt }
    });
  }

  /* ------------------------------------------------------------------------
     4. Agent Monitor
     ------------------------------------------------------------------------ */
  getAgents(activeOnly = false) {
    const q = activeOnly ? "?active_only=true" : "";
    return this.request(`/agents${q}`);
  }

  getAgent(agentId) {
    return this.request(`/agents/${encodeURIComponent(agentId)}`);
  }

  getAgentActivity(agentId) {
    return this.request(`/agents/${encodeURIComponent(agentId)}/activity`);
  }

  /* ------------------------------------------------------------------------
     5. Tool Permissions & Catalog
     ------------------------------------------------------------------------ */
  getTools() {
    return this.request("/tools");
  }

  getTool(toolId) {
    return this.request(`/tools/${encodeURIComponent(toolId)}`);
  }

  updateTool(toolId, permissionStatus) {
    return this.request(`/tools/${encodeURIComponent(toolId)}`, {
      method: "PUT",
      body: { permission_status: permissionStatus }
    });
  }

  resetTools() {
    return this.request("/tools/reset", {
      method: "POST"
    });
  }

  /* ------------------------------------------------------------------------
     6. Approval Center
     ------------------------------------------------------------------------ */
  getApprovals(status = null) {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    return this.request(`/approvals${query}`);
  }

  getApproval(approvalId) {
    return this.request(`/approvals/${encodeURIComponent(approvalId)}`);
  }

  decideApproval(approvalId, decision) {
    return this.request(`/approvals/${encodeURIComponent(approvalId)}/decision`, {
      method: "POST",
      body: { decision }
    });
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
    return this.request(`/events${qs ? `?${qs}` : ""}`, { signal });
  }

  getEvent(eventId) {
    return this.request(`/events/${encodeURIComponent(eventId)}`);
  }

  /* ------------------------------------------------------------------------
     8. Attack Simulator
     ------------------------------------------------------------------------ */
  runSimulation(scenarioIndex) {
    return this.request("/simulations", {
      method: "POST",
      body: { scenario_index: scenarioIndex }
    });
  }

  /* ------------------------------------------------------------------------
     9. Settings & Demonstration State
     ------------------------------------------------------------------------ */
  getSettings() {
    return this.request("/settings");
  }

  updateSettings(settings) {
    return this.request("/settings", {
      method: "PUT",
      body: settings
    });
  }

  resetDemo() {
    return this.request("/demo/reset", {
      method: "POST"
    });
  }
}

// Global Singleton Export
const API = new ApiClient();
window.API = API;
