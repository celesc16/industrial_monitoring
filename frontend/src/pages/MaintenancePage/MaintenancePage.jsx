import { useEffect, useMemo, useState } from "react";

import { getMaintenanceSchedule } from "../../api/client";
import ConnectionBanner from "../../components/ConnectionBanner/ConnectionBanner";
import { useSensors } from "../../hooks/useSensors";

import styles from "./MaintenancePage.module.css";

const DEFAULT_CONFIG = {
  preventiveCost: 1000,
  failureCost: 20000,
  minWindowDays: 0.5,
  maxWindowDays: 365,
};

const FIELD_LABELS = {
  preventiveCost: "Costo preventivo",
  failureCost: "Costo por falla",
  minWindowDays: "Día mínimo (ventana)",
  maxWindowDays: "Día máximo (ventana)",
};

function formatMoney(value) {
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatDays(value) {
  return `${Number(value).toFixed(1)} días`;
}

export default function MaintenancePage() {
  const {
    sensors,
    loading: sensorsLoading,
    error: sensorsError,
  } = useSensors();

  const [sensorId, setSensorId] = useState("");
  const [form, setForm] = useState(DEFAULT_CONFIG);
  const [result, setResult] = useState(null);
  const [computing, setComputing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (sensorId || sensors.length === 0) {
      return;
    }

    const firstSensor =
      sensors.find((sensor) => sensor.is_active) ??
      sensors[0];

    setSensorId(firstSensor?.id ?? "");
  }, [sensors, sensorId]);

  const setField = (field) => (event) =>
    setForm((current) => ({
      ...current,
      [field]: Number(event.target.value),
    }));

  const validationMessage = useMemo(() => {
    if (form.failureCost < form.preventiveCost) {
      return "El costo por falla debe ser mayor o igual al costo preventivo.";
    }

    if (form.minWindowDays >= form.maxWindowDays) {
      return "El día mínimo debe ser menor que el día máximo.";
    }

    return null;
  }, [form]);

  async function handleCompute(event) {
    event.preventDefault();

    setComputing(true);
    setError(null);

    try {
      const data = await getMaintenanceSchedule(sensorId, {
        preventive_cost: form.preventiveCost,
        failure_cost: form.failureCost,
        min_window_days: form.minWindowDays,
        max_window_days: form.maxWindowDays,
      });

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setComputing(false);
    }
  }

  const windowProgress = result
    ? Math.min(
        100,
        Math.max(
          0,
          ((result.recommended_window_days -
            result.minimum_window_days) /
            Math.max(
              result.maximum_window_days -
                result.minimum_window_days,
              0.001
            )) *
            100
        )
      )
    : 0;

  const savingsRatio = result
    ? result.expected_cost_per_day /
      Math.max(result.run_to_failure_cost_per_day, 0.001)
    : 0;

  const pageError = error || sensorsError;

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>
            Investigación operativa
          </p>

          <h1 className={styles.title}>
            Planificador de mantenimiento
          </h1>

          <p className={styles.description}>
            Ventana óptima para detener cada máquina,
            minimizando el costo esperado entre mantenimiento
            planificado y fallas imprevistas.
          </p>
        </div>
      </header>

      {pageError && (
        <ConnectionBanner>
          <span>
            No se pudo calcular el plan de
            mantenimiento: {pageError}
          </span>
        </ConnectionBanner>
      )}

      <div className={styles.grid}>
        <section className={styles.configPanel}>
          <h2 className={styles.panelTitle}>
            Parámetros del modelo
          </h2>

          <form
            className={styles.form}
            onSubmit={handleCompute}
          >
            <label className={styles.field}>
              <span className={styles.fieldLabel}>
                Sensor
              </span>

              <select
                className={styles.fieldControl}
                value={sensorId}
                onChange={(event) =>
                  setSensorId(event.target.value)
                }
                disabled={sensorsLoading}
                aria-label="Sensor"
              >
                {sensors.map((sensor) => (
                  <option key={sensor.id} value={sensor.id}>
                    {sensor.id} — {sensor.name}
                  </option>
                ))}
              </select>
            </label>

            <div className={styles.fieldGrid}>
              {Object.entries(FIELD_LABELS).map(
                ([field, label]) => (
                  <label
                    key={field}
                    className={styles.field}
                  >
                    <span className={styles.fieldLabel}>
                      {label}
                    </span>

                    <input
                      type="number"
                      className={styles.fieldControl}
                      value={form[field]}
                      min={field.includes("Window")
                        ? 0.01
                        : 1}
                      step="any"
                      onChange={setField(field)}
                      aria-label={label}
                    />
                  </label>
                )
              )}
            </div>

            {validationMessage && (
              <p className={styles.validation} role="alert">
                {validationMessage}
              </p>
            )}

            <button
              type="submit"
              className={styles.calculateButton}
              disabled={
                computing ||
                !sensorId ||
                validationMessage !== null
              }
            >
              <i
                className={
                  computing
                    ? "bi bi-hourglass-split"
                    : "bi bi-calculator"
                }
              />

              {computing
                ? "Calculando..."
                : "Calcular ventana óptima"}
            </button>
          </form>
        </section>

        <section
          className={styles.resultPanel}
          aria-live="polite"
        >
          {!result ? (
            <div className={styles.emptyState}>
              <i className="bi bi-tools" />

              <p>
                Definí los costos y calculá la ventana
                óptima de mantenimiento.
              </p>
            </div>
          ) : (
            <>
              <div className={styles.resultHeader}>
                <div>
                  <span className={styles.resultEyebrow}>
                    Recomendación
                  </span>

                  <p className={styles.resultTitle}>
                    <strong>{result.recommended_window_days.toFixed(1)}</strong>{" "}
                    días
                  </p>

                  <p className={styles.resultSubtitle}>
                    Detener preventivamente en esta ventana
                    minimiza el costo esperado diario.
                  </p>
                </div>

                {result.parameters_estimated ? (
                  <span className={styles.estimatedBadge}>
                    <i className="bi bi-graph-up-arrow" />
                    Parámetros estimados
                  </span>
                ) : (
                  <span className={styles.defaultBadge}>
                    <i className="bi bi-slash-circle" />
                    Parámetros por defecto
                  </span>
                )}
              </div>

              <div className={styles.timelineBlock}>
                <span className={styles.timelineLabel}>
                  Ventana permitida
                </span>

                <div
                  className={styles.timeline}
                  role="img"
                  aria-label={`Ventana óptima al ${windowProgress.toFixed(0)}% del rango`}
                >
                  <div
                    className={styles.timelineMarker}
                    style={{ left: `${windowProgress}%` }}
                  />
                </div>

                <div className={styles.timelineScale}>
                  <span>{formatDays(result.minimum_window_days)}</span>
                  <span className={styles.timelineOptimum}>
                    óptimo {result.recommended_window_days.toFixed(1)} d
                  </span>
                  <span>{formatDays(result.maximum_window_days)}</span>
                </div>
              </div>

              <div className={styles.costTiles}>
                <div className={styles.costTile}>
                  <span className={styles.costTileLabel}>
                    Mantenimiento planificado
                  </span>
                  <strong className={styles.costTileValue}>
                    {formatMoney(
                      result.expected_planned_cost_per_day
                    )}
                  </strong>
                  <span className={styles.costTileHint}>
                    por día
                  </span>
                </div>

                <div className={styles.costTile}>
                  <span className={styles.costTileLabel}>
                    Fallas imprevistas
                  </span>
                  <strong className={styles.costTileValueDanger}>
                    {formatMoney(
                      result.expected_unplanned_cost_per_day
                    )}
                  </strong>
                  <span className={styles.costTileHint}>
                    por día ({(
                      result.failure_probability_at_window * 100
                    ).toFixed(1)}
                    % de fallar en la ventana)
                  </span>
                </div>

                <div className={styles.costTileImportant}>
                  <span className={styles.costTileLabel}>
                    Costo esperado total
                  </span>
                  <strong className={styles.costTileValue}>
                    {formatMoney(result.expected_cost_per_day)}
                  </strong>
                  <span className={styles.costTileHint}>
                    por día
                  </span>
                </div>
              </div>

              <div className={styles.savingsBlock}>
                <div className={styles.savingsHeader}>
                  <span>
                    Comparado con
                    correr hasta fallar
                  </span>

                  <strong>
                    {formatMoney(
                      result.run_to_failure_cost_per_day
                    )}{" "}
                    / día
                  </strong>
                </div>

                <div className={styles.savingsBar}>
                  <div
                    className={styles.savingsBarFraction}
                    style={{
                      width: `${Math.min(
                        savingsRatio * 100,
                        100
                      )}%`,
                    }}
                  />
                </div>

                <p className={styles.savingsCaption}>
                  Ahorro estimado:{" "}
                  <strong>
                    {formatMoney(result.avoided_cost_per_day)}
                  </strong>{" "}
                  por día si se programa el
                  mantenimiento en la ventana óptima.
                </p>
              </div>

              <div className={styles.weibullMeta}>
                <span>
                  Shape β:{" "}
                  <strong>{result.weibull_shape}</strong>
                </span>
                <span>
                  Scale η:{" "}
                  <strong>
                    {result.weibull_scale_days} días
                  </strong>
                </span>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}