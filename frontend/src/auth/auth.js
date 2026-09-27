import { API_BASE_URL } from "../config";

// Demo accounts created automatically by the backend. Recruiters can
// explore the platform with one click, no sign-up required.
export const DEMO_CREDENTIALS = Object.freeze({
  ADMIN: Object.freeze({
    email: "admin@demo.com",
    password: "1234",
    label: "Administrador",
  }),
  VIEWER: Object.freeze({
    email: "operario@demo.com",
    password: "1234",
    label: "Operario",
  }),
});

const SESSION_STORAGE_KEY = "industrial_monitor_session";

export async function login({ email, password }) {
  const response = await fetch(`${API_BASE_URL}/api/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail =
      payload?.detail || `Login failed (${response.status})`;

    throw new Error(detail);
  }

  const data = await response.json();

  return {
    token: data.access_token,
    role: data.role,
    email: data.email,
  };
}

export function saveSession(session) {
  localStorage.setItem(
    SESSION_STORAGE_KEY,
    JSON.stringify(session)
  );
}

export function loadSession() {
  try {
    return JSON.parse(
      localStorage.getItem(SESSION_STORAGE_KEY) ?? "null"
    );
  } catch {
    return null;
  }
}

export function clearSession() {
  localStorage.removeItem(SESSION_STORAGE_KEY);
}

export function getStoredToken() {
  return loadSession()?.token ?? null;
}