export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";
export const API_V1 = `${API_BASE_URL}/api/v1`;
export const DEMO_CONTROLS_ENABLED =
  import.meta.env.VITE_DEMO_CONTROLS === "true";