import {
  useEffect,
  useState,
} from "react";

import { getStats } from "../api/client";

const POLL_INTERVAL_MS = 5000;

export function useSensorStats(sensorId) {
  const [stats, setStats] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState(null);

  useEffect(() => {
    if (!sensorId) {
      setStats(null);
      setLoading(false);
      setError(null);

      return undefined;
    }

    let cancelled = false;

    async function loadSensorStats({
      showLoading = false,
    } = {}) {
      if (showLoading) {
        setLoading(true);
      }

      try {
        const response = await getStats({
          sensorId,
        });

        if (cancelled) {
          return;
        }

        setStats(response);
        setError(null);
      } catch (err) {
        if (cancelled) {
          return;
        }

        setError(
          err.message ||
            "No se pudieron cargar las estadísticas del sensor."
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadSensorStats({
      showLoading: true,
    });

    const intervalId = window.setInterval(
      () => {
        if (
          document.visibilityState !==
          "visible"
        ) {
          return;
        }

        loadSensorStats();
      },
      POLL_INTERVAL_MS
    );

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, [sensorId]);

  return {
    stats,
    loading,
    error,
  };
}