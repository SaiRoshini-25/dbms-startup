const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api";

export function clearStoredAuth() {
  window.sessionStorage.removeItem("accessToken");
  window.sessionStorage.removeItem("currentUser");
  window.localStorage.removeItem("accessToken");
  window.localStorage.removeItem("currentUser");
}

export function getStoredAuthToken() {
  return window.sessionStorage.getItem("accessToken") || window.localStorage.getItem("accessToken");
}

export class APIError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "APIError";
    this.status = status;
  }
}

export async function apiRequest(path, options = {}) {
  const token = getStoredAuthToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401) {
      clearStoredAuth();
      window.dispatchEvent(new CustomEvent("auth:unauthorized"));
    }
    throw new APIError(data.message || "Request failed", response.status);
  }
  return data;
}

export async function downloadRequest(path, filename) {
  const token = getStoredAuthToken();
  const response = await fetch(`${API_BASE}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  });
  if (!response.ok) {
    if (response.status === 401) {
      clearStoredAuth();
      window.dispatchEvent(new CustomEvent("auth:unauthorized"));
    }
    throw new Error("Download failed");
  }
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
