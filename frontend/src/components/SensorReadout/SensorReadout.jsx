import styles from "./SensorReadout.module.css";

const READOUTS = [
  { key: "temperature", label: "Temperatura", unit: "°C" },
  { key: "vibration", label: "Vibración", unit: "mm/s" },
  { key: "pressure", label: "Presión", unit: "kPa" },
];

export default function SensorReadout({ latest }) {
  return (
    <div className="panel">
      <div className="panel__header">
        <h2 className="panel__title">Sensor {latest?.sensor_id ?? "—"}</h2>
        {latest && (
          <span className={`badge ${latest.is_anomaly ? "badge--danger" : "badge--success"}`}>
            score {latest.anomaly_score}
          </span>
        )}
      </div>

      <div className={styles.readouts}>
        {READOUTS.map((r) => (
          <div key={r.key} className={styles.readout}>
            <span className={styles.label}>{r.label}</span>
            <span className={styles.value}>
              {latest ? latest[r.key] : "--"}
              <span className={styles.unit}>{r.unit}</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
