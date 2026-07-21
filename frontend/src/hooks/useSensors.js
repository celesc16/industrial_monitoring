import { useCallback, useEffect, useRef, useState } from "react";

import { getSensors, updateSensorStatus as updateSensorStatusRequest } from "../api/client";

const POLL_INTERVAL_MS = 5000;

export function useSensors() {
  const [sensors, setSensors] = useState([]);
  const [updatingSensorId, setUpdatingSensorId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const mountedRef = useRef(false);
  const requestInProgressRef = useRef(false);

  const loadSensors = useCallback(async ({ initial = false } = {}) => {
    if (requestInProgressRef.current) {
      return;
    }

    requestInProgressRef.current = true;

    if (initial) {
      setLoading(true);
    } else {
      setRefreshing(true);
    }

    try {
      const data = await getSensors();

      if (!mountedRef.current) {
        return;
      }

      setSensors(data);
      setError(null);
    } catch (err) {
      if (mountedRef.current) {
        setError(err.message);
      }
    } finally {
      requestInProgressRef.current = false;

      if (mountedRef.current) {
        setLoading(false);
        setRefreshing(false);
      }
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;

    loadSensors({ initial: true });

    const interval = window.setInterval(() => {
      loadSensors();
    }, POLL_INTERVAL_MS);

    return () => {
      mountedRef.current = false;
      window.clearInterval(interval);
    };
  }, [loadSensors]);

  const changeSensorStatus = useCallback(
    async (sensorId, isActive) => {
        setUpdatingSensorId(sensorId);

        try {
        const updatedSensor = await updateSensorStatusRequest(
            sensorId,
            isActive
        );

        if (mountedRef.current) {
            setSensors((currentSensors) =>
            currentSensors.map((sensor) =>
                sensor.id === updatedSensor.id
                ? updatedSensor
                : sensor
            )
            );

            setError(null);
        }

        return updatedSensor;
        } catch (err) {
        if (mountedRef.current) {
            setError(err.message);
        }

        throw err;
        } finally {
        if (mountedRef.current) {
            setUpdatingSensorId(null);
        }
        }
    },
    []
    );

  return {
    sensors,
    loading,
    refreshing,
    error,
    updatingSensorId,
    refresh: () => loadSensors(),
    changeSensorStatus,
  };
}