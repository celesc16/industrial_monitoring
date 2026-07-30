import { formatNumber } from "../../utils/formatNumber";
import styles from "./SensorStatsCards.module.css";

const METRICS = [
  {
    key: "total_anomalies",
    label: "Anomalías totales",
    description: "Acumuladas por este sensor",
    icon: "bi-exclamation-triangle",
  },
  {
    key: "anomalies_last_24h",
    label: "Anomalías en 24 h",
    description: "Detectadas en las últimas 24 horas",
    icon: "bi-clock-history",
  },
];

export default function SensorStatsCards({
  stats,
  loading = false,
}) {
  return (
    <div className={styles.grid}>
      {METRICS.map((item) => (
        <article
          key={item.key}
          className={styles.card}
        >
          <div className={styles.icon}>
            <i className={`bi ${item.icon}`} />
          </div>

          <div className={styles.content}>
            <span className={styles.label}>
              {item.label}
            </span>

            <strong className={styles.value}>
              {loading && !stats
                ? "—"
                : formatNumber(
                    stats?.[item.key] ?? 0,
                    0
                  )}
            </strong>

            <span className={styles.description}>
              {item.description}
            </span>
          </div>
        </article>
      ))}
    </div>
  );
}