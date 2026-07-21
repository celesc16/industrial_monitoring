import { useEffect, useState } from "react";
import { getReadings, getStats } from "../api/client";

const POLL_INTERVAL_MS = 5000;

export function usePolledData() {
  const [stats, setStats] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchAll() {
      try {
        const [statsData, anomaliesData] = await Promise.all([
          getStats(),
          getReadings({ limit: 25, onlyAnomalies: true }),
        ]);
        if (!cancelled) {
          setStats(statsData);
          setAnomalies(anomaliesData.reverse()); // más reciente primero en la tabla
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    }

    fetchAll();
    const interval = setInterval(fetchAll, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return { stats, anomalies, error };
}
