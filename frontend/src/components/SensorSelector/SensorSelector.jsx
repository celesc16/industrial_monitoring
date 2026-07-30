import styles from "./SensorSelector.module.css";

export default function SensorSelector({
  sensors,
  selectedSensorId,
  onChange,
}) {
  return (
    <label className={styles.container}>
      <span className={styles.label}>
        Sensor monitoreado
      </span>

      <select
        className={styles.select}
        value={selectedSensorId}
        onChange={(event) => onChange(event.target.value)}
      >
        {sensors.map((sensor) => (
          <option
            key={sensor.id}
            value={sensor.id}
          >
            {sensor.id} — {sensor.name}
          </option>
        ))}
      </select>
    </label>
  );
}