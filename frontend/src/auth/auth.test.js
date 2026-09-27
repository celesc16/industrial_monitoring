import { afterEach, describe, expect, it, vi } from "vitest";

import { API_BASE_URL } from "../config";
import {
  DEMO_CREDENTIALS,
  clearSession,
  getStoredToken,
  loadSession,
  login,
  saveSession,
} from "./auth";

afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
});

describe("DEMO_CREDENTIALS", () => {
  it("exposes the admin and viewer demo accounts", () => {
    expect(DEMO_CREDENTIALS.ADMIN).toMatchObject({
      email: "admin@demo.com",
      password: "1234",
      label: "Administrador",
    });

    expect(DEMO_CREDENTIALS.VIEWER).toMatchObject({
      email: "operario@demo.com",
      password: "1234",
      label: "Operario",
    });
  });
});

describe("login", () => {
  it("POSTs the credentials to /api/login and returns a session", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        access_token: "token-abc",
        role: "ADMIN",
        email: "admin@demo.com",
      }),
    });

    vi.stubGlobal("fetch", fetchMock);

    const session = await login(DEMO_CREDENTIALS.ADMIN);

    expect(fetchMock).toHaveBeenCalledWith(
      `${API_BASE_URL}/api/login`,
      expect.objectContaining({
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: "admin@demo.com",
          password: "1234",
        }),
      })
    );

    expect(session).toEqual({
      token: "token-abc",
      role: "ADMIN",
      email: "admin@demo.com",
    });
  });

  it("throws the server detail on failure", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ detail: "Credenciales inválidas." }),
    });

    vi.stubGlobal("fetch", fetchMock);

    await expect(login(DEMO_CREDENTIALS.VIEWER)).rejects.toThrow(
      "Credenciales inválidas."
    );
  });

  it("falls back to a status message when the payload is not JSON", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => {
        throw new Error("not json");
      },
    });

    vi.stubGlobal("fetch", fetchMock);

    await expect(login(DEMO_CREDENTIALS.VIEWER)).rejects.toThrow(
      "Login failed (500)"
    );
  });
});

describe("session storage", () => {
  it("saves, loads and clears a session", () => {
    const session = {
      token: "tok",
      role: "VIEWER",
      email: "operario@demo.com",
    };

    expect(loadSession()).toBeNull();

    saveSession(session);
    expect(loadSession()).toEqual(session);
    expect(getStoredToken()).toBe("tok");

    clearSession();
    expect(loadSession()).toBeNull();
    expect(getStoredToken()).toBeNull();
  });

  it("returns null when the stored value is corrupt", () => {
    localStorage.setItem(
      "industrial_monitor_session",
      "{not valid json"
    );

    expect(loadSession()).toBeNull();
  });
});