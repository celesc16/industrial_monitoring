import { API_V1 } from "../config";

async function request(path) {
  const response = await fetch(`${API_V1}${path}`);
  if (!response.ok) {
    throw new Error(`Error ${response.status} consultando ${path}`);
  }
  return response.json();
}

export function getStats() {
  return request("/stats");
}

export function getReadings({ limit = 100, onlyAnomalies = false } = {}) {
  const params = new URLSearchParams({ limit, only_anomalies: onlyAnomalies });
  return request(`/readings?${params.toString()}`);
}
