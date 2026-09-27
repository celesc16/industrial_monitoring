import { afterEach, describe, expect, it, vi } from "vitest";

import { clearSession, saveSession } from "../auth/auth";
import {
  getMaintenanceSchedule,
  getSensors,
  updateSensorStatus,
} from "./client";
import { ForbiddenError } from "./errors";

function jsonResponse(status, body) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  };
}

afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
});

describe("api client requests", () => {
  it("attaches the Bearer token when a session exists", async () => {
    saveSession({
      token: "tok",
      role: "VIEWER",
      email: "operario@demo.com",
    });

    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse(200, []));

    vi.stubGlobal("fetch", fetchMock);

    await getSensors();

    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toContain("/api/v1/sensors");
    expect(options.headers.get("Authorization")).toBe(
      "Bearer tok"
    );
  });

  it("does not attach Authorization without a session", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse(200, []));

    vi.stubGlobal("fetch", fetchMock);

    await getSensors();

    const [, options] = fetchMock.mock.calls[0];
    expect(options.headers.get("Authorization")).toBeNull();
  });

  it("throws ForbiddenError with the server detail on 403", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse(403, {
        detail:
          "Acceso denegado: Se requieren permisos de Administrador",
      })
    );

    vi.stubGlobal("fetch", fetchMock);

    const error = await updateSensorStatus(
      "SENSOR-001",
      false
    ).catch((err) => err);

    expect(error).toBeInstanceOf(ForbiddenError);
    expect(error.name).toBe("ForbiddenError");
    expect(error.message).toBe(
      "Acceso denegado: Se requieren permisos de Administrador"
    );
  });

  it("throws a plain Error for other failures", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse(500, { detail: "Error interno" })
    );

    vi.stubGlobal("fetch", fetchMock);

    await expect(getSensors()).rejects.toBeInstanceOf(Error);
    await expect(getSensors()).rejects.not.toBeInstanceOf(
      ForbiddenError
    );
  });

  it("sends the status payload as JSON", async () => {
    saveSession({
      token: "tok",
      role: "ADMIN",
      email: "admin@demo.com",
    });

    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse(200, {
        id: "SENSOR-001",
        is_active: false,
      })
    );

    vi.stubGlobal("fetch", fetchMock);

    await updateSensorStatus("SENSOR-001", false);

    const [, options] = fetchMock.mock.calls[0];
    expect(options.method).toBe("PATCH");
    expect(JSON.parse(options.body)).toEqual({
      is_active: false,
    });
  });
});

describe("getMaintenanceSchedule", () => {
  it("POSTs the cost config and returns the schedule", async () => {
    const schedule = {
      sensor_id: "SENSOR-001",
      recommended_window_days: 5.76,
      config_used: {
        preventive_cost: 1000,
        failure_cost: 20000,
      },
    };

    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse(200, schedule)
    );

    vi.stubGlobal("fetch", fetchMock);

    const data = await getMaintenanceSchedule("SENSOR-001", {
      preventive_cost: 1000,
      failure_cost: 20000,
    });

    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toContain(
      "/api/v1/maintenance/sensors/SENSOR-001/schedule"
    );
    expect(options.method).toBe("POST");
    expect(JSON.parse(options.body)).toEqual({
      preventive_cost: 1000,
      failure_cost: 20000,
    });
    expect(data.recommended_window_days).toBe(5.76);
  });
});