import styles from "./SensorsSummary.module.css";

export default function SensorsSummary({ sensors }) {
  const summary = {
    total: sensors.length,
    online: sensors.filter(
      (sensor) => sensor.connection_status === "online"
    ).length,
    offline: sensors.filter(
      (sensor) => sensor.connection_status === "offline"
    ).length,
    inactive: sensors.filter(
      (sensor) => sensor.connection_status === "inactive"
    ).length,
    anomalies: sensors.filter(
      (sensor) => sensor.latest_reading?.is_anomaly
    ).length,
  };

  const items = [
    {
      label: "Total",
      value: summary.total,
      icon: "bi-cpu",
    },
    {
      label: "En línea",
      value: summary.online,
      icon: "bi-wifi",
      type: "success",
    },
    {
      label: "Fuera de línea",
      value: summary.offline,
      icon: "bi-wifi-off",
      type: "warning",
    },
    {
      label: "Inactivos",
      value: summary.inactive,
      icon: "bi-pause-circle",
    },
    {
      label: "Con anomalías",
      value: summary.anomalies,
      icon: "bi-exclamation-triangle",
      type: "danger",
    },
  ];

  return (
    <section className={styles.grid} aria-label="Resumen de sensores">
      {items.map((item) => (
        <article key={item.label} className={styles.card}>
          <div
            className={`${styles.icon} ${
              item.type ? styles[item.type] : ""
            }`}
          >
            <i className={`bi ${item.icon}`} />
          </div>

          <div>
            <span className={styles.label}>{item.label}</span>
            <strong className={styles.value}>{item.value}</strong>
          </div>
        </article>
      ))}
    </section>
  );
}