import Header from "../../components/Header/Header";
import LiveChart from "../../components/LiveChart/LiveChart";
import SensorReadout from "../../components/SensorReadout/SensorReadout";
import StatsCards from "../../components/StatsCards/StatsCards";
import HistoryTable from "../../components/HistoryTable/HistoryTable";
import ConnectionBanner from "../../components/ConnectionBanner/ConnectionBanner";
import { useLiveReadings } from "../../hooks/useLiveReadings";
import { usePolledData } from "../../hooks/usePolledData";
import styles from "./DashboardPage.module.css";

export default function DashboardPage() {
  const { points, latest, connectionStatus } = useLiveReadings();
  const { stats, anomalies, error } = usePolledData();

  return (
    <div className={styles.page}>
      <Header
        isAnomaly={Boolean(latest?.is_anomaly)}
        hasSignal={Boolean(latest)}
        connectionStatus={connectionStatus}
      />

      {connectionStatus === "closed" && (
        <ConnectionBanner>
          Sin conexión al backend en tiempo real. Reintentando automáticamente…
        </ConnectionBanner>
      )}
      {error && <ConnectionBanner>No se pudo cargar el histórico: {error}</ConnectionBanner>}

      <div className={styles.grid}>
        <LiveChart points={points} />

        <div className={styles.side}>
          <SensorReadout latest={latest} />
          <StatsCards stats={stats} />
        </div>
      </div>

      <div className={styles.tableSection}>
        <HistoryTable anomalies={anomalies} />
      </div>
    </div>
  );
}