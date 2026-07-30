import { useEffect, useMemo, useRef, useState } from "react";

import { WS_URL } from "../config";

const RECONNECT_DELAY_MS = 3000;
const MAX_POINTS_PER_SENSOR = 60;

export function useLiveReadings() {
  const [pointsBySensor, setPointsBySensor] = useState({});
  const [latestBySensor, setLatestBySensor] = useState({});
  const [connectionStatus, setConnectionStatus] =
    useState("connecting");

  const socketRef = useRef(null);
  const reconnectTimerRef = useRef(null);

  useEffect(() => {
    let cancelled = false;

    function connect() {
      if (cancelled) return;

      setConnectionStatus("connecting");

      const socket = new WebSocket(WS_URL);
      socketRef.current = socket;

      socket.onopen = () => {
        setConnectionStatus("open");
      };

      socket.onmessage = (event) => {
        try {
          const reading = JSON.parse(event.data);
          const sensorId = reading.sensor_id;

          if (!sensorId) return;

          setLatestBySensor((current) => ({
            ...current,
            [sensorId]: reading,
          }));

          setPointsBySensor((current) => {
            const sensorPoints = current[sensorId] ?? [];
            const nextPoints = [...sensorPoints, reading];

            return {
              ...current,
              [sensorId]:
                nextPoints.length > MAX_POINTS_PER_SENSOR
                  ? nextPoints.slice(-MAX_POINTS_PER_SENSOR)
                  : nextPoints,
            };
          });
        } catch {
          // Los mensajes que no sean JSON se ignoran.
        }
      };

      socket.onclose = () => {
        setConnectionStatus("closed");

        if (!cancelled) {
          reconnectTimerRef.current = setTimeout(
            connect,
            RECONNECT_DELAY_MS
          );
        }
      };

      socket.onerror = () => {
        socket.close();
      };
    }

    connect();

    return () => {
      cancelled = true;

      clearTimeout(reconnectTimerRef.current);
      socketRef.current?.close();
    };
  }, []);

  const connectedSensorIds = useMemo(
    () => Object.keys(latestBySensor),
    [latestBySensor]
  );

  return {
    pointsBySensor,
    latestBySensor,
    connectedSensorIds,
    connectionStatus,
  };
}