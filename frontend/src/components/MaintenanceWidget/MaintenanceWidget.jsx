import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getMaintenanceSchedule } from "../../api/client";
import { useSensors } from "../../hooks/useSensors";

import styles from "./MaintenanceWidget.module.css";

const MAX_ROWS = 3;

function urgencyFor(windowDays) {
  if (windowDays < 30) {
    return "critical";
  }

  if (windowDays < 90) {
    return "warning";
  }

  return "healthy";
}

function formatDays(value) {
  return `${Number(value).toFixed(1)} d`;
}

function formatMoney(value) {
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

export default function MaintenanceWidget() {
  const navigate = useNavigate();

  const { sensors, loading: sensorsLoading } = useSensors();

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [revision, setRevision] = useState(0);

  const sensorKeys = useMemo(
    () =>
      sensors
        .map((sensor) => sensor.id)
        .sort()
        .join("|"),
    [sensors]
  );

  const namesById = useMemo(
    () =>
      new Map(
        sensors.map((sensor) => [sensor.id, sensor.name])
      ),
    [sensors]
  );

  useEffect(() => {
    if (sensorKeys === "") {
      setLoading(sensorsLoading);
      return;
    }

    let cancelled = false;

    setLoading(true);

    const ids = sensorKeys.split("|");

    Promise.all(
      ids.map((id) =>
        getMaintenanceSchedule(id).catch(() => null)
      )
    )
      .then((schedules) => {
        if (cancelled) {
          return;
        }

        const nonEmpty = schedules
          .map((schedule, index) => ({
            schedule,
            id: ids[index],
            name: namesById.get(ids[index]) ?? ids[index],
          }))
          .filter((entry) => entry.schedule !== null);

        setRows(nonEmpty);
        setError(null);
      })
      .catch(() => {
        if (!cancelled) {
          setError("No se pudo calcular el plan de mantenimiento.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [sensorKeys, namesById, revision, sensorsLoading]);

  const sortable = rows
    .slice()
    .sort(
      (a, b) =>
        a.schedule.recommended_window_days -
        b.schedule.recommended_window_days
    )
    .slice(0, MAX_ROWS);

  return (
    <section className={styles.widget}>
      <div className={styles.header}>
        <div>
          <p className={styles.eyebrow}>
            Planificación preventiva
          </p>

          <h2 className={styles.title}>
            Siguiente mantenimiento crítico
          </h2>
        </div>

        <div className={styles.actions}>
          <button
            type="button"
            className={styles.retryButton}
            onClick={() => setRevision((value) => value + 1)}
            disabled={loading}
            title="Recalcular"
          >
            <i
              className={`bi bi-arrow-repeat ${
                loading ? styles.spinning : ""
              }`}
            />
          </button>

          <button
            type="button"
            className={styles.planButton}
            onClick={() => navigate("/maintenance")}
          >
            Ver plan completo
            <i className="bi bi-arrow-right" />
          </button>
        </div>
      </div>

      {error && (
        <p className={styles.error} role="alert">
          {error}
        </p>
      )}

      {loading && sortable.length === 0 ? (
        <div className={styles.skeletonRow} aria-hidden="true">
          {[0, 1, 2].map((index) => (
            <span key={index} />
          ))}
        </div>
      ) : sortable.length === 0 ? (
        <p className={styles.empty}>
          Sin datos para estimar el próximo mantenimiento.
        </p>
      ) : (
        <ul className={styles.list}>
          {sortable.map(({ id, name, schedule }) => {
            const urgency = urgencyFor(
              schedule.recommended_window_days
            );

            const progress = Math.min(
              100,
              Math.max(
                0,
                ((schedule.recommended_window_days -
                  schedule.minimum_window_days) /
                  Math.max(
                    schedule.maximum_window_days -
                      schedule.minimum_window_days,
                    0.001
                  )) *
                  100
              )
            );

            return (
              <li
                key={id}
                className={styles.row}
              >
                <span
                  className={`${styles.urgencyDot} ${styles[urgency]}`}
                  aria-hidden="true"
                />

                <div className={styles.rowIdentity}>
                  <strong>{name}</strong>
                  <span>{id}</span>
                </div>

                <div className={styles.rowMetric}>
                  <span className={styles.rowMetricValue}>
                    {formatDays(
                      schedule.recommended_window_days
                    )}
                  </span>
                  <span className={styles.rowMetricLabel}>
                    costo {formatMoney(
                      schedule.expected_cost_per_day
                    )}
                    /día
                  </span>
                </div>

                <div
                  className={`${styles.rowBar} ${styles[urgency]}`}
                >
                  <span style={{ width: `${progress}%` }} />
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}