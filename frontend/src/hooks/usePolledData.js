import { useEffect, useState } from "react";

import {
  getReadings,
  getStats,
} from "../api/client";

const POLL_INTERVAL_MS = 5000;

export function usePolledData() {
  const [stats, setStats] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchAll() {
      try {
        const [statsData, anomaliesData] =
          await Promise.all([
            getStats(),
            getReadings({
              page: 1,
              pageSize: 5,
              isAnomaly: true,
            }),
          ]);

        if (cancelled) {
          return;
        }

        setStats(statsData);

        setAnomalies(
          Array.isArray(anomaliesData.items)
            ? anomaliesData.items
            : []
        );

        setError(null);
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message ||
              "No se pudieron cargar los datos del dashboard."
          );
        }
      }
    }

    fetchAll();

    const interval = setInterval(
      fetchAll,
      POLL_INTERVAL_MS
    );

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return {
    stats,
    anomalies,
    error,
  };
}