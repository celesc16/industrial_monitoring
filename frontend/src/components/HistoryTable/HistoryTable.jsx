import {
  formatDate,
  formatTime,
} from "../../utils/formatDate";
import { formatNumber } from "../../utils/formatNumber";
import styles from "./HistoryTable.module.css";

export default function HistoryTable({
  readings = [],
  title = "Historial de lecturas",
  emptyMessage = "No se encontraron lecturas.",
  loading = false,
  showStatus = true,
}) {
  return (
    <div className="panel">
      {(title || readings.length > 0) && (
        <div className="panel__header">
          {title && (
            <h2 className="panel__title">
              {title}
            </h2>
          )}

          <span className="panel__subtitle">
            {readings.length} en esta página
          </span>
        </div>
      )}

      {loading ? (
        <div className="empty-state">
          Cargando historial…
        </div>
      ) : readings.length === 0 ? (
        <div className="empty-state">
          {emptyMessage}
        </div>
      ) : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Hora</th>
                <th>Sensor</th>
                <th>Temperatura</th>
                <th>Vibración</th>
                <th>Presión</th>

                {showStatus && (
                  <th>Estado</th>
                )}
              </tr>
            </thead>

            <tbody>
              {readings.map((row) => (
                <tr key={row.id}>
                  <td className="mono">
                    {formatDate(row.timestamp)}
                  </td>

                  <td className="mono">
                    {formatTime(row.timestamp)}
                  </td>

                  <td>{row.sensor_id}</td>

                  <td className="mono">
                    {formatNumber(
                      row.temperature
                    )}{" "}
                    °C
                  </td>

                  <td className="mono">
                    {formatNumber(
                      row.vibration
                    )}{" "}
                    mm/s
                  </td>

                  <td className="mono">
                    {formatNumber(
                      row.pressure
                    )}{" "}
                    kPa
                  </td>

                  {showStatus && (
                    <td>
                      <span
                        className={
                          row.is_anomaly
                            ? styles.anomalyBadge
                            : styles.normalBadge
                        }
                      >
                        {row.is_anomaly
                          ? "Anomalía"
                          : "Normal"}
                      </span>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}