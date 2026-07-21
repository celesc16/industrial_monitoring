import { formatDateTime } from "../../utils/formatDate";

import styles from "./SensorCard.module.css";

const STATUS_CONFIG = {
  online: {
    label: "En línea",
    icon: "bi-wifi",
    className: "online",
  },
  offline: {
    label: "Fuera de línea",
    icon: "bi-wifi-off",
    className: "offline",
  },
  inactive: {
    label: "Inactivo",
    icon: "bi-pause-circle",
    className: "inactive",
  },
};

const METRICS = [
  {
    key: "temperature",
    label: "Temperatura",
    unit: "°C",
    icon: "bi-thermometer-half",
  },
  {
    key: "vibration",
    label: "Vibración",
    unit: "mm/s",
    icon: "bi-activity",
  },
  {
    key: "pressure",
    label: "Presión",
    unit: "kPa",
    icon: "bi-speedometer2",
  },
];

function formatMetric(value) {
  if (value === null || value === undefined) {
    return "—";
  }

  const numericValue = Number(value);

  if (Number.isNaN(numericValue)) {
    return "—";
  }

  return numericValue.toFixed(2);
}

export default function SensorCard({ sensor, showDemoControls, isUpdating, onRequestStatusChange, }) {
  const status =
    STATUS_CONFIG[sensor.connection_status] ||
    STATUS_CONFIG.offline;

  const latest = sensor.latest_reading;
  const hasAnomaly = Boolean(latest?.is_anomaly);

  return (
    <article
      className={`${styles.card} ${
        hasAnomaly ? styles.cardAnomaly : ""
      }`}
    >
      <header className={styles.header}>
        <div className={styles.identity}>
          <span className={styles.sensorId}>{sensor.id}</span>

          <h2 className={styles.name}>{sensor.name}</h2>

          <span className={styles.location}>
            <i className="bi bi-geo-alt" />
            {sensor.location}
          </span>
        </div>

        <div
          className={`${styles.status} ${
            styles[status.className]
          }`}
        >
          <i className={`bi ${status.icon}`} />
          {status.label}
        </div>
      </header>

      {hasAnomaly && (
        <div className={styles.alert}>
          <div>
            <i className="bi bi-exclamation-triangle-fill" />
            Anomalía detectada
          </div>

          <span className="mono">
            score {latest.anomaly_score}
          </span>
        </div>
      )}

      <div className={styles.metrics}>
        {METRICS.map((metric) => (
          <div key={metric.key} className={styles.metric}>
            <div className={styles.metricHeader}>
              <i className={`bi ${metric.icon}`} />
              <span>{metric.label}</span>
            </div>

            <div className={styles.metricValue}>
              <span>{formatMetric(latest?.[metric.key])}</span>
              <small>{metric.unit}</small>
            </div>
          </div>
        ))}
      </div>

      <footer className={styles.footer}>
        <div>
          <span className={styles.footerLabel}>
            Última comunicación
          </span>

          <span className={styles.footerValue}>
            {formatDateTime(sensor.last_seen_at)}
          </span>
        </div>

        {latest && (
          <div className={styles.prediction}>
            <span
              className={`${styles.predictionDot} ${
                hasAnomaly
                  ? styles.predictionDanger
                  : styles.predictionNormal
              }`}
            />

            {hasAnomaly ? "Evento anómalo" : "Operación normal"}
          </div>
        )}

        {showDemoControls && (
            <button
                type="button"
                className={`${styles.statusButton} ${
                sensor.is_active
                    ? styles.deactivateButton
                    : styles.activateButton
                }`}
                onClick={() => onRequestStatusChange(sensor)}
                disabled={isUpdating}
            >
                <i
                className={`bi ${
                    sensor.is_active
                    ? "bi-pause-circle"
                    : "bi-play-circle"
                }`}
                />

                {isUpdating
                ? "Procesando..."
                : sensor.is_active
                    ? "Desactivar"
                    : "Activar"}
            </button>
            )}
      </footer>
    </article>
  );
}