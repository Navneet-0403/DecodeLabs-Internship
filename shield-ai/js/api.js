/**
 * Shield AI — REST API Client Wrapper
 * Handles all HTTP communication between the vanilla JS frontend and the FastAPI backend.
 */

const API = {
  baseUrl: "/api",

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const defaultHeaders = {
      "Accept": "application/json",
    };

    if (options.body && typeof options.body === "object") {
      defaultHeaders["Content-Type"] = "application/json";
      options.body = JSON.stringify(options.body);
    }

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      if (response.status === 204) {
        return null;
      }

      const contentType = response.headers.get("content-type");
      const isJson = contentType && contentType.includes("application/json");
      const data = isJson ? await response.json() : await response.text();

      if (!response.ok) {
        const errorMsg = data && data.error && data.error.message
          ? data.error.message
          : `HTTP error ${response.status}: ${response.statusText}`;
        const error = new Error(errorMsg);
        error.status = response.status;
        error.data = data;
        throw error;
      }

      return data;
    } catch (err) {
      if (err.name === "TypeError" && err.message.includes("fetch")) {
        console.error("Backend connection failure:", err);
        throw new Error("Unable to connect to Shield AI backend server. Please verify it is running on http://127.0.0.1:8000.");
      }
      throw err;
    }
  },

  // Health
  getHealth() {
    return this.request("/health");
  },

  // Dashboard
  getDashboard() {
    return this.request("/dashboard");
  },

  // Prompt Scanner
  scanPrompt(prompt) {
    return this.request("/scans", {
      method: "POST",
      body: { prompt },
    });
  },

  // Agent Monitor
  getAgents() {
    return this.request("/agents");
  },

  getAgentActivity(agentId) {
    return this.request(`/agents/${encodeURIComponent(agentId)}/activity`);
  },

  // Tool Permissions
  getTools() {
    return this.request("/tools");
  },

  getTool(toolId) {
    return this.request(`/tools/${encodeURIComponent(toolId)}`);
  },

  updateTool(toolId, permissionStatus) {
    return this.request(`/tools/${encodeURIComponent(toolId)}`, {
      method: "PUT",
      body: { permission_status: permissionStatus },
    });
  },

  resetTools() {
    return this.request("/tools/reset", {
      method: "POST",
    });
  },

  // Approval Center
  getApprovals(status = null) {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    return this.request(`/approvals${query}`);
  },

  decideApproval(approvalId, decision) {
    return this.request(`/approvals/${encodeURIComponent(approvalId)}/decision`, {
      method: "POST",
      body: { decision },
    });
  },

  // Threat Logs
  getEvents(params = {}) {
    const queryParams = new URLSearchParams();
    if (params.q) queryParams.set("q", params.q);
    if (params.risk) queryParams.set("risk", params.risk);
    if (params.category) queryParams.set("category", params.category);
    if (params.decision) queryParams.set("decision", params.decision);
    if (params.limit !== undefined) queryParams.set("limit", params.limit);
    if (params.offset !== undefined) queryParams.set("offset", params.offset);

    const qs = queryParams.toString();
    return this.request(`/events${qs ? `?${qs}` : ""}`);
  },

  getEvent(eventId) {
    return this.request(`/events/${encodeURIComponent(eventId)}`);
  },

  // Attack Simulator
  runSimulation(scenarioIndex) {
    return this.request("/simulations", {
      method: "POST",
      body: { scenario_index: scenarioIndex },
    });
  },

  // Settings
  getSettings() {
    return this.request("/settings");
  },

  updateSettings(settings) {
    return this.request("/settings", {
      method: "PUT",
      body: settings,
    });
  },

  resetDemo() {
    return this.request("/demo/reset", {
      method: "POST",
    });
  },
};

window.API = API;

