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

export function getStats(options = {}) {
  return request("/stats", options);
}

export function getReadings(
  { limit = 100, onlyAnomalies = false } = {},
  options = {}
) {
  const params = new URLSearchParams({
    limit: String(limit),
    only_anomalies: String(onlyAnomalies),
  });

  return request(`/readings?${params.toString()}`, options);
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