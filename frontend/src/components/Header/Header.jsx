import { useEffect, useState } from "react";
import StatusLed from "../StatusLed/StatusLed";
import styles from "./Header.module.css";

export default function Header({ isAnomaly, hasSignal, connectionStatus }) {
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const statusLabel = !hasSignal
    ? "ESPERANDO DATOS"
    : isAnomaly
      ? "¡ANOMALÍA DETECTADA!"
      : "OPERACIÓN NORMAL";

  return (
    <header className={styles.header}>
      <div>
        <span className={styles.eyebrow}>SISTEMA DE MONITOREO</span>
        <h1 className={styles.title}>Detección de Anomalías en Tiempo Real</h1>
      </div>

      <div className={styles.topBar}>
        <div className={styles.status}>
          <div
            className={`${styles.pill} ${
              isAnomaly && hasSignal
                ? styles.pillDanger
                : styles.pillSuccess
            }`}
          >
            <StatusLed
              isAnomaly={isAnomaly}
              hasSignal={hasSignal}
            />

            <span>{statusLabel}</span>
          </div>

          <div className={styles.meta}>
            <span
              className={`${styles.connectionDot} ${
                styles[`connection-${connectionStatus}`]
              }`}
            />

            <span className={styles.clock}>
              {now.toLocaleTimeString("es-AR", {
                hour12: false,
              })}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}