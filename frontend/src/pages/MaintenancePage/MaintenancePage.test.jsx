// @vitest-environment jsdom
import {
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { API_V1 } from "../../config";
import MaintenancePage from "./MaintenancePage";

const SENSORS = [
  {
    id: "SENSOR-001",
    name: "Motor principal",
    is_active: true,
  },
  {
    id: "SENSOR-002",
    name: "Bomba hidráulica",
    is_active: true,
  },
];

const SCHEDULE = {
  sensor_id: "SENSOR-001",
  recommended_window_days: 5.76,
  minimum_window_days: 0.5,
  maximum_window_days: 365,
  expected_cost_per_day: 198.41,
  expected_unplanned_cost_per_day: 26.03,
  expected_planned_cost_per_day: 172.38,
  failure_probability_at_window: 0.0075,
  weibull_shape: 8,
  weibull_scale_days: 10.619,
  parameters_estimated: true,
  run_to_failure_cost_per_day: 2000,
  avoided_cost_per_day: 1801.59,
  config_used: {
    preventive_cost: 1000,
    failure_cost: 20000,
    min_window_days: 0.5,
    max_window_days: 365,
  },
};

function jsonResponse(status, body) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  };
}

function mockFetch() {
  return vi.fn().mockImplementation((url, options = {}) => {
    if (url === `${API_V1}/sensors`) {
      return Promise.resolve(jsonResponse(200, SENSORS));
    }

    if (
      options.method === "POST" &&
      url.includes("/api/v1/maintenance/sensors/")
    ) {
      return Promise.resolve(jsonResponse(200, SCHEDULE));
    }

    return Promise.resolve(
      jsonResponse(404, { detail: "not found" })
    );
  });
}

afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
});

describe("MaintenancePage", () => {
  it("computes the optimal window for the selected sensor", async () => {
    const fetchMock = mockFetch();
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <MaintenancePage />
      </MemoryRouter>
    );

    const calculateButton = await screen.findByRole(
      "button",
      { name: /Calcular ventana óptima/ }
    );

    await waitFor(() =>
      expect(calculateButton).not.toBeDisabled()
    );

    await user.click(calculateButton);

    expect(
      await screen.findByText("Parámetros estimados")
    ).toBeInTheDocument();

    await waitFor(() => {
      const postCall = fetchMock.mock.calls.find(
        ([, options]) => options?.method === "POST"
      );

      expect(postCall).toBeDefined();
      expect(postCall[0]).toContain(
        "/api/v1/maintenance/sensors/SENSOR-001/schedule"
      );
      expect(JSON.parse(postCall[1].body)).toEqual({
        preventive_cost: 1000,
        failure_cost: 20000,
        min_window_days: 0.5,
        max_window_days: 365,
      });
    });
  });

  it("shows the recommended window expressed in days", async () => {
    vi.stubGlobal("fetch", mockFetch());
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <MaintenancePage />
      </MemoryRouter>
    );

    const calculateButton = await screen.findByRole(
      "button",
      { name: /Calcular ventana óptima/ }
    );

    await waitFor(() =>
      expect(calculateButton).not.toBeDisabled()
    );

    await user.click(calculateButton);

    const matches =
      await screen.findAllByText(/5\.8/);

    expect(matches.length).toBeGreaterThan(0);
  });

  it("blocks the calculation when the config is inconsistent", async () => {
    vi.stubGlobal("fetch", mockFetch());
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <MaintenancePage />
      </MemoryRouter>
    );

    const calculateButton = await screen.findByRole(
      "button",
      { name: /Calcular ventana óptima/ }
    );

    await waitFor(() =>
      expect(calculateButton).not.toBeDisabled()
    );

    const failureCostInput = screen.getByLabelText(
      "Costo por falla"
    );

    await user.clear(failureCostInput);
    await user.type(failureCostInput, "1");

    expect(
      await screen.findByText(
        "El costo por falla debe ser mayor o igual al costo preventivo."
      )
    ).toBeInTheDocument();
    expect(calculateButton).toBeDisabled();
  });

  it("pre-selects the first active sensor", async () => {
    vi.stubGlobal("fetch", mockFetch());

    render(
      <MemoryRouter>
        <MaintenancePage />
      </MemoryRouter>
    );

    const select = await screen.findByLabelText("Sensor");

    await waitFor(() =>
      expect(select).not.toBeDisabled()
    );

    expect(select).toHaveValue("SENSOR-001");
  });
});