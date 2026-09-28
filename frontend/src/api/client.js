/**
 * HTTP client for `/api/v1/` (DEC-015 envelope).
 *
 * DEC-010: the access token lives only in memory (held by the auth store).
 * The refresh token is an httpOnly cookie scoped to `/api/v1/auth/` and is
 * never read by JavaScript. Every auth request must send credentials so
 * the browser attaches that cookie.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

function getAccessToken() {
  return window.__gymportalAccessToken || null;
}

export function setAccessToken(token) {
  // Module-level would be lost across HMR; a single window slot is still
  // in-memory only (never localStorage/sessionStorage).
  window.__gymportalAccessToken = token || null;
}

export function clearAccessToken() {
  window.__gymportalAccessToken = null;
}

async function parseBody(response) {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export class ApiError extends Error {
  constructor({ status, code, message, fieldErrors }) {
    super(message || "Request failed");
    this.status = status;
    this.code = code;
    this.fieldErrors = fieldErrors || {};
  }
}

let refreshInFlight = null;

async function refreshAccessToken() {
  if (refreshInFlight) return refreshInFlight;
  refreshInFlight = (async () => {
    const response = await fetch(`${API_BASE}/auth/refresh/`, {
      method: "POST",
      credentials: "include",
      headers: { Accept: "application/json" },
    });
    const body = await parseBody(response);
    if (!response.ok) {
      clearAccessToken();
      throw new ApiError({
        status: response.status,
        code: body?.error?.code || "AUTHENTICATION_REQUIRED",
        message: body?.error?.message || "Session expired.",
      });
    }
    const access = body?.data?.access;
    setAccessToken(access);
    return access;
  })().finally(() => {
    refreshInFlight = null;
  });
  return refreshInFlight;
}

export async function apiRequest(
  path,
  { method = "GET", body, auth = true, _retried = false, parseAs = "json" } = {},
) {
  const headers = {
    Accept: parseAs === "text" ? "text/csv, text/plain, */*" : "application/json",
  };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = getAccessToken();
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    credentials: "include",
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (response.status === 401 && auth && !_retried && !path.startsWith("/auth/refresh/")) {
    try {
      await refreshAccessToken();
      return apiRequest(path, { method, body, auth, _retried: true, parseAs });
    } catch {
      // fall through to parse the original 401
    }
  }

  if (!response.ok) {
    const payload = await parseBody(response);
    throw new ApiError({
      status: response.status,
      code: payload?.error?.code || "REQUEST_FAILED",
      message: payload?.error?.message || "Request failed.",
      fieldErrors: payload?.error?.field_errors,
    });
  }
  if (parseAs === "text") {
    return response.text();
  }
  const payload = await parseBody(response);
  return payload?.data ?? payload;
}

export const authApi = {
  login(email, password) {
    return apiRequest("/auth/login/", { method: "POST", body: { email, password }, auth: false });
  },
  refresh() {
    return refreshAccessToken();
  },
  logout() {
    return apiRequest("/auth/logout/", { method: "POST" });
  },
  me() {
    return apiRequest("/auth/me/");
  },
};
