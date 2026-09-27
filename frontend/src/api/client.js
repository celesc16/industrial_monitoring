import { API_V1 } from "../config";
import { ForbiddenError } from "./errors";
import { getStoredToken } from "../auth/auth";

function toBackendUtcDate(value) {
  if (!value) {
    return "";
  }

  /*
   * datetime-local renders a local time.
   * We convert it to UTC and drop the Z because the DB stores
   * UTC timestamps without timezone information.
   */
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return date.toISOString().replace("Z", "");
}

function mergeHeaders(options = {}) {
  const headers = new Headers(options.headers ?? {});

  const token = getStoredToken();

  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return headers;
}

async function buildRequestError(response, path) {
  const errorPayload = await response.json().catch(() => null);

  const detail =
    errorPayload?.detail ||
    (response.status === 403
      ? "Acceso denegado: Se requieren permisos de Administrador."
      : `Error ${response.status} consultando ${path}`);

  if (response.status === 403) {
    return new ForbiddenError(detail);
  }

  return new Error(detail);
}

async function request(path, options = {}) {
  const response = await fetch(`${API_V1}${path}`, {
    ...options,
    headers: mergeHeaders(options),
  });

  if (!response.ok) {
    throw await buildRequestError(response, path);
  }

  return response.json();
}

export function getStats({ sensorId = "" } = {}) {
  const params = new URLSearchParams();

  if (sensorId) {
    params.set("sensor_id", sensorId);
  }

  const query = params.toString();

  return request(`/stats${query ? `?${query}` : ""}`);
}

export function getReadings({
  page = 1,
  pageSize = 20,
  sensorId = "",
  isAnomaly = null,
  dateFrom = "",
  dateTo = "",
} = {}) {
  const params = new URLSearchParams();

  params.set("page", String(page));
  params.set("page_size", String(pageSize));

  if (sensorId) {
    params.set("sensor_id", sensorId);
  }

  if (isAnomaly !== null) {
    params.set("is_anomaly", String(isAnomaly));
  }

  if (dateFrom) {
    params.set("date_from", toBackendUtcDate(dateFrom));
  }

  if (dateTo) {
    params.set("date_to", toBackendUtcDate(dateTo));
  }

  return request(`/readings?${params.toString()}`);
}

export function getSensors(options = {}) {
  return request("/sensors", options);
}

export function getSensor(sensorId, options = {}) {
  return request(`/sensors/${encodeURIComponent(sensorId)}`, options);
}

export function getMaintenanceSchedule(sensorId, config = {}) {
  return request(
    `/maintenance/sensors/${encodeURIComponent(sensorId)}/schedule`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(config),
    }
  );
}

export function updateSensorStatus(sensorId, isActive) {
  return request(`/sensors/${encodeURIComponent(sensorId)}/status`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      is_active: isActive,
    }),
  });
}

export async function exportReadingsCsv({
  sensorId = "",
  isAnomaly = null,
  dateFrom = "",
  dateTo = "",
} = {}) {
  const params = new URLSearchParams();

  if (sensorId) {
    params.set("sensor_id", sensorId);
  }

  if (isAnomaly !== null) {
    params.set("is_anomaly", String(isAnomaly));
  }

  if (dateFrom) {
    params.set("date_from", toBackendUtcDate(dateFrom));
  }

  if (dateTo) {
    params.set("date_to", toBackendUtcDate(dateTo));
  }

  const query = params.toString();

  const response = await fetch(
    `${API_V1}/readings/export${query ? `?${query}` : ""}`,
    { headers: mergeHeaders() }
  );

  if (!response.ok) {
    if (response.status === 403) {
      throw new ForbiddenError(
        "Acceso denegado: Se requieren permisos de Administrador."
      );
    }

    const errorPayload = await response.json().catch(() => null);

    throw new Error(
      errorPayload?.detail || "No se pudo exportar el historial."
    );
  }

  return response.blob();
}