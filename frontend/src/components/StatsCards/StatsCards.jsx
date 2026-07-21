import styles from "./StatsCards.module.css";

export default function StatsCards({ stats }) {
  const items = [
    { label: "Lecturas totales", value: stats?.total_readings ?? "--" },
    { label: "Anomalías totales", value: stats?.total_anomalies ?? "--", danger: true },
    { label: "Anomalías (24h)", value: stats?.anomalies_last_24h ?? "--", danger: true },
  ];

  return (
    <div className={styles.grid}>
      {items.map((item) => (
        <div key={item.label} className={styles.card}>
          <span className={styles.label}>{item.label}</span>
          <span className={`${styles.value} ${item.danger && item.value > 0 ? styles.valueDanger : ""}`}>
            {item.value}
          </span>
        </div>
      ))}
    </div>
  );
}
