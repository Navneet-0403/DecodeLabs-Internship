/**
 * Shield AI — Frontend API Client Regression Test Suite
 * DecodeLabs Project 4: Full-Stack Frontend & Backend Integration
 *
 * Verifies:
 * 1. AbortController multiplexing (external cancellation vs internal timeout)
 * 2. Guaranteed resource cleanup (timers & event listeners)
 * 3. Robust JSON response parsing (valid, malformed, empty, 204, plain text)
 * 4. Error classification & HTTP status preservation
 */

const test = require("node:test");
const assert = require("node:assert/strict");
const { ApiClient } = require("../js/api.js");

// Helper to build mock Fetch responses
function createMockResponse({
  status = 200,
  statusText = "OK",
  headers = {},
  body = ""
} = {}) {
  const headerMap = new Map();
  for (const [k, v] of Object.entries(headers)) {
    headerMap.set(k.toLowerCase(), v);
  }

  return {
    status,
    statusText,
    ok: status >= 200 && status < 300,
    headers: {
      get: (name) => headerMap.get(String(name).toLowerCase()) || null
    },
    text: async () => body
  };
}

test("AbortController: External request cancellation before dispatch", async () => {
  const client = new ApiClient("http://test.local", 5000);
  const controller = new AbortController();
  controller.abort("User navigated away");

  await assert.rejects(
    async () => {
      await client.request("/test", { signal: controller.signal });
    },
    (err) => {
      assert.equal(err.name, "AbortError");
      assert.equal(err.isCancelled, true);
      assert.equal(err.isTimeout, false);
      assert.equal(err.code, "REQUEST_CANCELLED");
      return true;
    }
  );
});

test("AbortController: Internal request timeout triggers correctly", async () => {
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = (_url, { signal }) => {
      return new Promise((resolve, reject) => {
        signal.addEventListener("abort", () => {
          const abortErr = new Error("This operation was aborted");
          abortErr.name = "AbortError";
          reject(abortErr);
        });
      });
    };

    const client = new ApiClient("http://test.local", 40);

    await assert.rejects(
      async () => {
        await client.request("/slow-endpoint", { timeout: 40 });
      },
      (err) => {
        assert.equal(err.name, "TimeoutError");
        assert.equal(err.isTimeout, true);
        assert.equal(err.isCancelled, false);
        assert.equal(err.code, "REQUEST_TIMEOUT");
        assert.match(err.message, /timed out after 40ms/i);
        return true;
      }
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("AbortController: External cancellation before timeout occurs (No false timeout)", async () => {
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = (_url, { signal }) => {
      return new Promise((resolve, reject) => {
        signal.addEventListener("abort", () => {
          const abortErr = new Error("The operation was aborted.");
          abortErr.name = "AbortError";
          reject(abortErr);
        });
      });
    };

    const client = new ApiClient("http://test.local", 1000);
    const controller = new AbortController();

    // Abort intentionally after 30ms, well before the 1000ms timeout
    setTimeout(() => {
      controller.abort();
    }, 30);

    await assert.rejects(
      async () => {
        await client.request("/search", { signal: controller.signal, timeout: 1000 });
      },
      (err) => {
        assert.equal(err.name, "AbortError");
        assert.equal(err.isCancelled, true);
        assert.equal(err.isTimeout, false);
        assert.equal(err.code, "REQUEST_CANCELLED");
        return true;
      }
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("AbortController: Timeout while external signal is supplied", async () => {
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = (_url, { signal }) => {
      return new Promise((resolve, reject) => {
        signal.addEventListener("abort", () => {
          const abortErr = new Error("The operation was aborted.");
          abortErr.name = "AbortError";
          reject(abortErr);
        });
      });
    };

    const client = new ApiClient("http://test.local", 40);
    const controller = new AbortController(); // Not aborted by user

    await assert.rejects(
      async () => {
        await client.request("/search", { signal: controller.signal, timeout: 40 });
      },
      (err) => {
        assert.equal(err.name, "TimeoutError");
        assert.equal(err.isTimeout, true);
        assert.equal(err.isCancelled, false);
        assert.equal(err.code, "REQUEST_TIMEOUT");
        return true;
      }
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("AbortController: Cleanup event listeners and timers on success", async () => {
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = async () => {
      return createMockResponse({
        status: 200,
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ success: true })
      });
    };

    const client = new ApiClient("http://test.local", 2000);
    const controller = new AbortController();

    const result = await client.request("/test", { signal: controller.signal, timeout: 2000 });
    assert.deepEqual(result, { success: true });

    // Aborting controller after success must NOT trigger any delayed errors or unhandled rejections
    controller.abort();
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("AbortController: Cleanup event listeners and timers on network failure", async () => {
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = async () => {
      throw new TypeError("Failed to fetch");
    };

    const client = new ApiClient("http://test.local", 2000);
    const controller = new AbortController();

    await assert.rejects(
      async () => {
        await client.request("/fail", { signal: controller.signal, timeout: 2000 });
      },
      (err) => {
        assert.equal(err.isNetworkError, true);
        assert.equal(err.code, "NETWORK_UNAVAILABLE");
        return true;
      }
    );

    // Aborting controller after failure must NOT throw or leak
    controller.abort();
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("JSON Handling: Parse valid JSON response", async () => {
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = async () => {
      return createMockResponse({
        status: 200,
        headers: { "content-type": "application/json; charset=utf-8" },
        body: JSON.stringify({ status: "healthy", version: "3.0.0" })
      });
    };

    const client = new ApiClient("http://test.local", 5000);
    const res = await client.request("/health");
    assert.deepEqual(res, { status: "healthy", version: "3.0.0" });
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("JSON Handling: Detect malformed JSON when Content-Type is application/json", async () => {
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = async () => {
      return createMockResponse({
        status: 200,
        headers: { "content-type": "application/json" },
        body: "{ this is not valid json : 123"
      });
    };

    const client = new ApiClient("http://test.local", 5000);

    await assert.rejects(
      async () => {
        await client.request("/corrupt-json");
      },
      (err) => {
        assert.equal(err.name, "SyntaxError");
        assert.equal(err.isParseError, true);
        assert.equal(err.code, "MALFORMED_JSON");
        assert.equal(err.status, 200);
        assert.match(err.message, /malformed json response/i);
        assert.ok(err.bodyPreview.includes("this is not valid json"));
        return true;
      }
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("JSON Handling: Handle HTTP 204 No Content with empty return value", async () => {
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = async () => {
      return createMockResponse({
        status: 204,
        statusText: "No Content",
        headers: {},
        body: ""
      });
    };

    const client = new ApiClient("http://test.local", 5000);
    const res = await client.request("/events/1/purge", { method: "DELETE" });
    assert.equal(res, null);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("JSON Handling: Handle genuinely empty response body without false parse error", async () => {
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = async () => {
      return createMockResponse({
        status: 200,
        headers: { "content-type": "application/json" },
        body: "   \n\t  "
      });
    };

    const client = new ApiClient("http://test.local", 5000);
    const res = await client.request("/empty");
    assert.equal(res, null);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("JSON Handling: Support legitimate non-JSON plain text responses", async () => {
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = async () => {
      return createMockResponse({
        status: 200,
        headers: { "content-type": "text/plain" },
        body: "Shield AI Gatekeeper Active"
      });
    };

    const client = new ApiClient("http://test.local", 5000);
    const res = await client.request("/ping");
    assert.equal(res, "Shield AI Gatekeeper Active");
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("JSON Handling: Preserve HTTP status information on malformed JSON 500 error", async () => {
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = async () => {
      return createMockResponse({
        status: 500,
        statusText: "Internal Server Error",
        headers: { "content-type": "application/json" },
        body: "Internal server error traceback: <html>Error</html>"
      });
    };

    const client = new ApiClient("http://test.local", 5000);

    await assert.rejects(
      async () => {
        await client.request("/crash");
      },
      (err) => {
        assert.equal(err.status, 500);
        assert.equal(err.isServerError, true);
        assert.equal(err.isParseError, true);
        assert.equal(err.code, "MALFORMED_JSON");
        return true;
      }
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});

/* --------------------------------------------------------------------------
   Guaranteed Resource Cleanup & Serialization Failure Regression Tests
   -------------------------------------------------------------------------- */

test("Cleanup: Circular JSON serialization failure cleans up timers and listeners", async () => {
  const originalClearTimeout = globalThis.clearTimeout;
  const originalFetch = globalThis.fetch;
  let clearedTimerId = null;
  let removeListenerCalled = false;
  let fetchCalled = false;

  try {
    globalThis.clearTimeout = (id) => {
      clearedTimerId = id;
      return originalClearTimeout(id);
    };

    globalThis.fetch = async () => {
      fetchCalled = true;
      return createMockResponse({ status: 200, body: "{}" });
    };

    const client = new ApiClient("http://test.local", 10000);
    const controller = new AbortController();

    const origRemove = controller.signal.removeEventListener;
    controller.signal.removeEventListener = function(type, listener) {
      if (type === "abort") removeListenerCalled = true;
      return origRemove.apply(this, arguments);
    };

    // Construct circular reference
    const circularBody = {};
    circularBody.self = circularBody;

    await assert.rejects(
      async () => {
        await client.request("/circular", {
          method: "POST",
          body: circularBody,
          signal: controller.signal,
          timeout: 10000
        });
      },
      (err) => {
        assert.ok(err.isSerializationError || err instanceof TypeError);
        assert.equal(err.code, "SERIALIZATION_ERROR");
        return true;
      }
    );

    // Verify Observable Resource Cleanup:
    assert.equal(fetchCalled, false, "Fetch must not be dispatched when serialization fails");
    assert.ok(clearedTimerId !== null, "clearTimeout must be invoked on serialization failure");
    assert.equal(removeListenerCalled, true, "removeEventListener must be invoked on serialization failure");
  } finally {
    globalThis.clearTimeout = originalClearTimeout;
    globalThis.fetch = originalFetch;
  }
});

test("Cleanup: Observable spy verification on successful request", async () => {
  const originalClearTimeout = globalThis.clearTimeout;
  const originalFetch = globalThis.fetch;
  let clearedTimerId = null;
  let removeListenerCalled = false;

  try {
    globalThis.clearTimeout = (id) => {
      clearedTimerId = id;
      return originalClearTimeout(id);
    };

    globalThis.fetch = async () => {
      return createMockResponse({
        status: 200,
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ ok: true })
      });
    };

    const client = new ApiClient("http://test.local", 5000);
    const controller = new AbortController();

    const origRemove = controller.signal.removeEventListener;
    controller.signal.removeEventListener = function(type, listener) {
      if (type === "abort") removeListenerCalled = true;
      return origRemove.apply(this, arguments);
    };

    const res = await client.request("/spy-success", { signal: controller.signal, timeout: 5000 });
    assert.deepEqual(res, { ok: true });

    assert.ok(clearedTimerId !== null, "Timer must be cleared on success");
    assert.equal(removeListenerCalled, true, "Abort listener must be removed on success");
  } finally {
    globalThis.clearTimeout = originalClearTimeout;
    globalThis.fetch = originalFetch;
  }
});

test("Cleanup: Observable spy verification on network failure", async () => {
  const originalClearTimeout = globalThis.clearTimeout;
  const originalFetch = globalThis.fetch;
  let clearedTimerId = null;
  let removeListenerCalled = false;

  try {
    globalThis.clearTimeout = (id) => {
      clearedTimerId = id;
      return originalClearTimeout(id);
    };

    globalThis.fetch = async () => {
      throw new TypeError("Failed to fetch");
    };

    const client = new ApiClient("http://test.local", 5000);
    const controller = new AbortController();

    const origRemove = controller.signal.removeEventListener;
    controller.signal.removeEventListener = function(type, listener) {
      if (type === "abort") removeListenerCalled = true;
      return origRemove.apply(this, arguments);
    };

    await assert.rejects(
      async () => {
        await client.request("/spy-fail", { signal: controller.signal, timeout: 5000 });
      },
      (err) => {
        assert.equal(err.isNetworkError, true);
        return true;
      }
    );

    assert.ok(clearedTimerId !== null, "Timer must be cleared on network failure");
    assert.equal(removeListenerCalled, true, "Abort listener must be removed on network failure");
  } finally {
    globalThis.clearTimeout = originalClearTimeout;
    globalThis.fetch = originalFetch;
  }
});

test("Cleanup: Observable spy verification on intentional cancellation", async () => {
  const originalClearTimeout = globalThis.clearTimeout;
  const originalFetch = globalThis.fetch;
  let clearedTimerId = null;
  let removeListenerCalled = false;

  try {
    globalThis.clearTimeout = (id) => {
      clearedTimerId = id;
      return originalClearTimeout(id);
    };

    globalThis.fetch = (_url, { signal }) => {
      return new Promise((_resolve, reject) => {
        signal.addEventListener("abort", () => {
          const err = new Error("Aborted");
          err.name = "AbortError";
          reject(err);
        });
      });
    };

    const client = new ApiClient("http://test.local", 5000);
    const controller = new AbortController();

    const origRemove = controller.signal.removeEventListener;
    controller.signal.removeEventListener = function(type, listener) {
      if (type === "abort") removeListenerCalled = true;
      return origRemove.apply(this, arguments);
    };

    setTimeout(() => {
      controller.abort();
    }, 20);

    await assert.rejects(
      async () => {
        await client.request("/spy-cancel", { signal: controller.signal, timeout: 5000 });
      },
      (err) => {
        assert.equal(err.isCancelled, true);
        assert.equal(err.isTimeout, false);
        return true;
      }
    );

    assert.ok(clearedTimerId !== null, "Timer must be cleared on cancellation");
    assert.equal(removeListenerCalled, true, "Abort listener must be removed on cancellation");
  } finally {
    globalThis.clearTimeout = originalClearTimeout;
    globalThis.fetch = originalFetch;
  }
});

test("Cleanup: Observable spy verification on timeout expiration", async () => {
  const originalClearTimeout = globalThis.clearTimeout;
  const originalFetch = globalThis.fetch;
  let clearedTimerId = null;
  let removeListenerCalled = false;

  try {
    globalThis.clearTimeout = (id) => {
      clearedTimerId = id;
      return originalClearTimeout(id);
    };

    globalThis.fetch = (_url, { signal }) => {
      return new Promise((_resolve, reject) => {
        signal.addEventListener("abort", () => {
          const err = new Error("Aborted");
          err.name = "AbortError";
          reject(err);
        });
      });
    };

    const client = new ApiClient("http://test.local", 30);
    const controller = new AbortController();

    const origRemove = controller.signal.removeEventListener;
    controller.signal.removeEventListener = function(type, listener) {
      if (type === "abort") removeListenerCalled = true;
      return origRemove.apply(this, arguments);
    };

    await assert.rejects(
      async () => {
        await client.request("/spy-timeout", { signal: controller.signal, timeout: 30 });
      },
      (err) => {
        assert.equal(err.isTimeout, true);
        assert.equal(err.isCancelled, false);
        return true;
      }
    );

    assert.ok(clearedTimerId !== null, "Timer must be cleared in finally on timeout");
    assert.equal(removeListenerCalled, true, "Abort listener must be removed on timeout");
  } finally {
    globalThis.clearTimeout = originalClearTimeout;
    globalThis.fetch = originalFetch;
  }
});

