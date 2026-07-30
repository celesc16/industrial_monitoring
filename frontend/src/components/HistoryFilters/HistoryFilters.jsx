import { useEffect, useState } from "react";

import styles from "./HistoryFilters.module.css";

const EMPTY_FILTERS = {
  sensorId: "",
  status: "all",
  dateFrom: "",
  dateTo: "",
};

export default function HistoryFilters({
  sensors,
  filters,
  loading = false,
  onApply,
  onClear,
}) {
  const [draftFilters, setDraftFilters] = useState(
    filters ?? EMPTY_FILTERS
  );

  useEffect(() => {
    setDraftFilters(filters ?? EMPTY_FILTERS);
  }, [filters]);

  function handleChange(event) {
    const { name, value } = event.target;

    setDraftFilters((current) => ({
      ...current,
      [name]: value,
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    onApply(draftFilters);
  }

  function handleClear() {
    setDraftFilters(EMPTY_FILTERS);
    onClear();
  }

  return (
    <form
      className={styles.filters}
      onSubmit={handleSubmit}
    >
      <div className={styles.field}>
        <label htmlFor="history-sensor">
          Sensor
        </label>

        <select
          id="history-sensor"
          name="sensorId"
          value={draftFilters.sensorId}
          onChange={handleChange}
          disabled={loading}
        >
          <option value="">
            Todos los sensores
          </option>

          {sensors.map((sensor) => (
            <option
              key={sensor.id}
              value={sensor.id}
            >
              {sensor.id} — {sensor.name}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.field}>
        <label htmlFor="history-status">
          Clasificación
        </label>

        <select
          id="history-status"
          name="status"
          value={draftFilters.status}
          onChange={handleChange}
          disabled={loading}
        >
          <option value="all">
            Todas
          </option>

          <option value="normal">
            Normales
          </option>

          <option value="anomaly">
            Anomalías
          </option>
        </select>
      </div>

      <div className={styles.field}>
        <label htmlFor="history-date-from">
          Desde
        </label>

        <input
          id="history-date-from"
          type="datetime-local"
          name="dateFrom"
          value={draftFilters.dateFrom}
          onChange={handleChange}
          disabled={loading}
        />
      </div>

      <div className={styles.field}>
        <label htmlFor="history-date-to">
          Hasta
        </label>

        <input
          id="history-date-to"
          type="datetime-local"
          name="dateTo"
          value={draftFilters.dateTo}
          onChange={handleChange}
          disabled={loading}
        />
      </div>

      <div className={styles.actions}>
        <button
          type="button"
          className={styles.clearButton}
          onClick={handleClear}
          disabled={loading}
        >
          Limpiar
        </button>

        <button
          type="submit"
          className={styles.applyButton}
          disabled={loading}
        >
          <i className="bi bi-funnel" />

          {loading
            ? "Aplicando..."
            : "Aplicar filtros"}
        </button>
      </div>
    </form>
  );
}