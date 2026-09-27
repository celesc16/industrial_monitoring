// @vitest-environment jsdom
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AuthProvider } from "../../auth/AuthContext";
import { ToastProvider } from "../../components/Toast/ToastContext";
import { API_BASE_URL } from "../../config";
import LoginPage from "./LoginPage";

function renderLoginPage() {
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <ToastProvider>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/dashboard"
              element={<div>Dashboard reached</div>}
            />
          </Routes>
        </AuthProvider>
      </ToastProvider>
    </MemoryRouter>
  );
}

function mockLoginSuccess(role = "ADMIN") {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      access_token: "token-abc",
      role,
      email: `${role.toLowerCase()}@demo.com`,
    }),
  });

  vi.stubGlobal("fetch", fetchMock);

  return fetchMock;
}

afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
});

describe("LoginPage", () => {
  it("renders the two demo login buttons", () => {
    renderLoginPage();

    expect(
      screen.getByRole("button", {
        name: /Ingresar como Administrador/,
      })
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: /Ingresar como Operario/,
      })
    ).toBeInTheDocument();
  });

  it("logs in as admin and redirects to the dashboard", async () => {
    const fetchMock = mockLoginSuccess("ADMIN");
    const user = userEvent.setup();

    renderLoginPage();

    await user.click(
      screen.getByRole("button", {
        name: /Ingresar como Administrador/,
      })
    );

    expect(
      await screen.findByText("Dashboard reached")
    ).toBeInTheDocument();

    expect(fetchMock).toHaveBeenCalledWith(
      `${API_BASE_URL}/api/login`,
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          email: "admin@demo.com",
          password: "1234",
        }),
      })
    );
  });

  it("logs in as viewer with the viewer credentials", async () => {
    const fetchMock = mockLoginSuccess("VIEWER");
    const user = userEvent.setup();

    renderLoginPage();

    await user.click(
      screen.getByRole("button", {
        name: /Ingresar como Operario/,
      })
    );

    await screen.findByText("Dashboard reached");

    expect(fetchMock).toHaveBeenCalledWith(
      `${API_BASE_URL}/api/login`,
      expect.objectContaining({
        body: JSON.stringify({
          email: "operario@demo.com",
          password: "1234",
        }),
      })
    );
  });

  it("shows an error message when login fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({
          detail: "Credenciales inválidas.",
        }),
      })
    );

    const user = userEvent.setup();

    renderLoginPage();

    await user.click(
      screen.getByRole("button", {
        name: /Ingresar como Administrador/,
      })
    );

    expect(
      await screen.findByText("Credenciales inválidas.")
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Dashboard reached")
    ).not.toBeInTheDocument();
  });

  it("stores the session in localStorage after login", async () => {
    mockLoginSuccess("ADMIN");
    const user = userEvent.setup();

    renderLoginPage();

    await user.click(
      screen.getByRole("button", {
        name: /Ingresar como Administrador/,
      })
    );

    await screen.findByText("Dashboard reached");

    const stored = JSON.parse(
      localStorage.getItem("industrial_monitor_session")
    );

    expect(stored).toEqual({
      token: "token-abc",
      role: "ADMIN",
      email: "admin@demo.com",
    });
  });
});