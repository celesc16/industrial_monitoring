import { useState } from "react";

import { ForbiddenError } from "../../api/errors";
import { useAuth } from "../../auth/AuthContext";
import ConfirmDialog from "../../components/ConfirmDialog/ConfirmDialog";
import ConnectionBanner from "../../components/ConnectionBanner/ConnectionBanner";
import SensorCard from "../../components/SensorCard/SensorCard";
import SensorsSummary from "../../components/SensorsSummary/SensorsSummary";
import { useToast } from "../../components/Toast/ToastContext";
import { useSensors } from "../../hooks/useSensors";

import styles from "./SensorsPage.module.css";

export default function SensorsPage() {
  const [selectedSensor, setSelectedSensor] = useState(null);

  const { session } = useAuth();
  const { showToast } = useToast();

  const {
    sensors,
    loading,
    refreshing,
    error,
    updatingSensorId,
    refresh,
    changeSensorStatus,
  } = useSensors();

  async function handleConfirmStatusChange() {
    if (!selectedSensor) {
      return;
    }

    try {
      await changeSensorStatus(
        selectedSensor.id,
        !selectedSensor.is_active
      );

      setSelectedSensor(null);
    } catch (err) {
      /*
       * A 403 means the role has no permission for this action.
       * We surface a visual toast without breaking the rest of
       * the page (the confirm dialog is simply closed).
       */
      if (err instanceof ForbiddenError) {
        showToast(
          err.message || "Acceso denegado: Se requieren permisos de Administrador",
          "error"
        );
      }

      setSelectedSensor(null);
    }
  }

  function handleCancelStatusChange() {
    if (updatingSensorId) {
      return;
    }

    setSelectedSensor(null);
  }

  return (
    <div className={styles.page}>
      <header className={styles.pageHeader}>
        <div>
          <span className={styles.eyebrow}>
            INFRAESTRUCTURA INDUSTRIAL
          </span>

          <h1 className={styles.title}>Sensores</h1>

          <p className={styles.description}>
            Estado operativo y últimas mediciones de los equipos
            monitoreados.
          </p>
        </div>

        <button
          type="button"
          className={styles.refreshButton}
          onClick={refresh}
          disabled={refreshing}
        >
          <i
            className={`bi bi-arrow-clockwise ${
              refreshing ? styles.rotating : ""
            }`}
          />

          {refreshing ? "Actualizando" : "Actualizar"}
        </button>
      </header>

      {error && (
        <ConnectionBanner>
          No se pudieron cargar los sensores: {error}
        </ConnectionBanner>
      )}

      {!loading && <SensorsSummary sensors={sensors} />}

      <section className={styles.content}>
        <div className={styles.sectionHeader}>
          <div>
            <h2>Equipos monitoreados</h2>

            <span>
              {sensors.length} sensor
              {sensors.length === 1 ? "" : "es"} registrado
              {sensors.length === 1 ? "" : "s"}
            </span>
          </div>
        </div>

        {loading ? (
          <div className={styles.loadingGrid}>
            {Array.from({ length: 5 }).map((_, index) => (
              <div
                key={index}
                className={styles.skeleton}
                aria-hidden="true"
              />
            ))}
          </div>
        ) : sensors.length === 0 ? (
          <div className={`panel ${styles.empty}`}>
            <i className="bi bi-cpu" />

            <h2>No hay sensores registrados</h2>

            <p>
              Registra sensores en el backend para comenzar a
              monitorear la planta.
            </p>
          </div>
        ) : (
          <div className={styles.sensorGrid}>
            {sensors.map((sensor) => (
              <SensorCard
                key={sensor.id}
                sensor={sensor}
                showDemoControls={session?.role === "ADMIN"}
                isUpdating={updatingSensorId === sensor.id}
                onRequestStatusChange={setSelectedSensor}
              />
            ))}
          </div>
        )}
      </section>

      <ConfirmDialog
        open={Boolean(selectedSensor)}
        title={
          selectedSensor?.is_active
            ? "Desactivar sensor"
            : "Activar sensor"
        }
        message={
          selectedSensor?.is_active
            ? `El sensor ${selectedSensor.name} quedará inactivo y sus lecturas MQTT serán rechazadas.`
            : `El sensor ${selectedSensor?.name} volverá a aceptar lecturas y aparecerá en línea cuando reciba una nueva medición.`
        }
        confirmLabel={
          selectedSensor?.is_active
            ? "Desactivar"
            : "Activar"
        }
        danger={Boolean(selectedSensor?.is_active)}
        loading={updatingSensorId === selectedSensor?.id}
        onConfirm={handleConfirmStatusChange}
        onCancel={handleCancelStatusChange}
      />
    </div>
  );
}