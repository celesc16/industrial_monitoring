import { API_V1 } from "../config";

async function request(path, options = {}) {
  const response = await fetch(`${API_V1}${path}`, options);

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null);

    throw new Error(
      errorPayload?.detail ||
        `Error ${response.status} consultando ${path}`
    );
  }

  return response.json();
}

export function getStats({
  sensorId = "",
} = {}) {
  const params = new URLSearchParams();

  if (sensorId) {
    params.set("sensor_id", sensorId);
  }

  const query = params.toString();

  return request(
    `/stats${query ? `?${query}` : ""}`
  );
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
    params.set("date_from", dateFrom);
  }

  if (dateTo) {
    params.set("date_to", dateTo);
  }

  return request(`/readings?${params.toString()}`);
}

export function getSensors(options = {}) {
  return request("/sensors", options);
}

export function getSensor(sensorId, options = {}) {
  return request(
    `/sensors/${encodeURIComponent(sensorId)}`,
    options
  );
}

export function updateSensorStatus(sensorId, isActive) {
  return request(
    `/sensors/${encodeURIComponent(sensorId)}/status`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        is_active: isActive,
      }),
    }
  );
}