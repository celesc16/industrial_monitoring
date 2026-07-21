import { useEffect, useRef, useState } from "react";
import { WS_URL } from "../config";

const RECONNECT_DELAY_MS = 3000;
const MAX_POINTS = 60;

export function useLiveReadings() {
  const [points, setPoints] = useState([]);
  const [latest, setLatest] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const socketRef = useRef(null);
  const reconnectTimer = useRef(null);

  useEffect(() => {
    let cancelled = false;

    function connect() {
      if (cancelled) return;

      setConnectionStatus("connecting");
      const socket = new WebSocket(WS_URL);
      socketRef.current = socket;

      socket.onopen = () => setConnectionStatus("open");

      socket.onmessage = (event) => {
        try {
          const reading = JSON.parse(event.data);
          setLatest(reading);
          setPoints((prev) => {
            const next = [...prev, reading];
            return next.length > MAX_POINTS ? next.slice(next.length - MAX_POINTS) : next;
          });
        } catch {
          // mensaje no-JSON, se ignora
        }
      };

      socket.onclose = () => {
        setConnectionStatus("closed");
        if (!cancelled) {
          reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY_MS);
        }
      };

      socket.onerror = () => socket.close();
    }

    connect();

    return () => {
      cancelled = true;
      clearTimeout(reconnectTimer.current);
      socketRef.current?.close();
    };
  }, []);

  return { points, latest, connectionStatus };
}
