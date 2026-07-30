import {
  useEffect,
  useMemo,
  useState,
} from "react";
import { useNavigate } from "react-router-dom";

import ConnectionBanner from "../../components/ConnectionBanner/ConnectionBanner";
import Header from "../../components/Header/Header";
import HistoryTable from "../../components/HistoryTable/HistoryTable";
import LiveChart from "../../components/LiveChart/LiveChart";
import SensorReadout from "../../components/SensorReadout/SensorReadout";
import SensorSelector from "../../components/SensorSelector/SensorSelector";
import SensorStatsCards from "../../components/SensorStatsCards/SensorStatsCards";
import StatsCards from "../../components/StatsCards/StatsCards";

import { useLiveReadings } from "../../hooks/useLiveReadings";
import { usePolledData } from "../../hooks/usePolledData";
import { useSensors } from "../../hooks/useSensors";
import { useSensorStats } from "../../hooks/useSensorStats";

import styles from "./DashboardPage.module.css";

export default function DashboardPage() {
  const navigate = useNavigate();

  const [
    selectedSensorId,
    setSelectedSensorId,
  ] = useState("");

  const {
    sensors,
    loading: sensorsLoading,
    error: sensorsError,
  } = useSensors();

  const {
    pointsBySensor,
    latestBySensor,
    connectionStatus,
  } = useLiveReadings();

  const {
    stats,
    anomalies,
    error: polledDataError,
  } = usePolledData();

  const {
    stats: selectedSensorStats,
    loading: selectedSensorStatsLoading,
    error: selectedSensorStatsError,
  } = useSensorStats(selectedSensorId);

  useEffect(() => {
    if (
      selectedSensorId ||
      sensors.length === 0
    ) {
      return;
    }

    const firstActiveSensor =
      sensors.find(
        (sensor) => sensor.is_active
      ) ?? sensors[0];

    setSelectedSensorId(firstActiveSensor.id);
  }, [sensors, selectedSensorId]);

  const selectedSensor = useMemo(
    () =>
      sensors.find(
        (sensor) =>
          sensor.id === selectedSensorId
      ) ?? null,
    [sensors, selectedSensorId]
  );

  const selectedPoints =
    pointsBySensor[selectedSensorId] ?? [];

  const selectedLatest =
    latestBySensor[selectedSensorId] ??
    selectedSensor?.latest_reading ??
    null;

  const recentAnomalies = useMemo(
    () => anomalies.slice(0, 5),
    [anomalies]
  );

  const pageError =
    sensorsError ||
    polledDataError ||
    selectedSensorStatsError;

  return (
    <div className={styles.page}>
      <Header
        isAnomaly={Boolean(
          selectedLatest?.is_anomaly
        )}
        hasSignal={Boolean(selectedLatest)}
        connectionStatus={connectionStatus}
      />

      {connectionStatus === "closed" && (
        <ConnectionBanner>
          Sin conexión al backend en tiempo
          real. Reintentando automáticamente…
        </ConnectionBanner>
      )}

      {pageError && (
        <ConnectionBanner>
          No se pudieron cargar todos los datos:{" "}
          {pageError}
        </ConnectionBanner>
      )}

      <section className={styles.summaryBlock}>
        <div className={styles.blockHeader}>
          <h2 className={styles.blockTitle}>
            Resumen general
          </h2>
        </div>

        <StatsCards stats={stats} />
      </section>

      <section className={styles.sensorBlock}>
        <div className={styles.sensorBlockHeader}>
          <div>
            <p className={styles.blockEyebrow}>
              Monitoreo individual
            </p>

            <h2 className={styles.blockTitle}>
              Sensor seleccionado
            </h2>

            <p className={styles.blockDescription}>
              Seleccioná un sensor para consultar
              sus lecturas y comportamiento en
              tiempo real.
            </p>
          </div>

          {!sensorsLoading &&
            sensors.length > 0 && (
              <div className={styles.selectorContainer}>
                <SensorSelector
                  sensors={sensors}
                  selectedSensorId={selectedSensorId}
                  onChange={setSelectedSensorId}
                />
              </div>
            )}
        </div>

        <div className={styles.sensorDivider} />

        <div className={styles.sensorIdentity}>
          <div>
            <span className={styles.sensorIdentityLabel}>
              Visualizando
            </span>

            <strong className={styles.sensorIdentityName}>
              {selectedSensor?.name ??
                selectedSensorId ??
                "Sin sensor seleccionado"}
            </strong>
          </div>

          {selectedSensorId && (
            <span className={styles.sensorIdentityId}>
              {selectedSensorId}
            </span>
          )}
        </div>

        <div className={styles.monitorGrid}>
          <LiveChart
            points={selectedPoints}
            sensorId={selectedSensorId}
          />

          <div className={styles.sideColumn}>
            <SensorReadout
              latest={selectedLatest}
              sensor={selectedSensor}
            />

            <SensorStatsCards
              stats={selectedSensorStats}
              loading={selectedSensorStatsLoading}
            />
          </div>
        </div>
      </section>

      <section className={styles.anomaliesSection}>
        <div className={styles.sectionHeader}>
          <div>
            <h2 className={styles.blockTitle}>
              Anomalías recientes
            </h2>

            <p className={styles.blockDescription}>
              Últimas anomalías detectadas.
            </p>
          </div>

          <button
            type="button"
            className={styles.historyButton}
            onClick={() => navigate("/history")}
          >
            Ver historial completo
            <i className="bi bi-arrow-right" />
          </button>
        </div>

        <HistoryTable
          readings={recentAnomalies}
          title=""
          emptyMessage="Todavía no se registraron anomalías. Buena señal."
          showStatus
        />
      </section>
    </div>
  );
}