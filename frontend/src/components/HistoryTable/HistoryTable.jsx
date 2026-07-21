import styles from "./HistoryTable.module.css";

export default function HistoryTable({ anomalies }) {
  return (
    <div className="panel">
      <div className="panel__header">
        <h2 className="panel__title">Histórico de anomalías</h2>
        <span className="panel__subtitle">últimas {anomalies.length} detectadas</span>
      </div>

      {anomalies.length === 0 ? (
        <div className="empty-state">Todavía no se registraron anomalías. Buena señal.</div>
      ) : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Hora</th>
                <th>Sensor</th>
                <th>Temp.</th>
                <th>Vibración</th>
                <th>Presión</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {anomalies.map((row) => (
                <tr key={row.id}>
                  <td className="mono">
                    {new Date(row.timestamp).toLocaleTimeString("es-AR", { hour12: false })}
                  </td>
                  <td>{row.sensor_id}</td>
                  <td className="mono">{row.temperature}°C</td>
                  <td className="mono">{row.vibration}</td>
                  <td className="mono">{row.pressure}</td>
                  <td className={`mono ${styles.score}`}>{row.anomaly_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
