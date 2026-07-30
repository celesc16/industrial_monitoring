import ConnectionBanner from "../../components/ConnectionBanner/ConnectionBanner";
import HistoryFilters from "../../components/HistoryFilters/HistoryFilters";
import HistoryPagination from "../../components/HistoryPagination/HistoryPagination";
import HistoryTable from "../../components/HistoryTable/HistoryTable";
import { useReadings } from "../../hooks/useReadings";
import { useSensors } from "../../hooks/useSensors";

import styles from "./HistoryPage.module.css";

export default function HistoryPage() {
  const {
    readings,
    pagination,
    filters,
    loading,
    refreshing,
    exporting,
    error,
    exportError,
    applyFilters,
    clearFilters,
    changePage,
    changePageSize,
    refresh,
    exportCsv,
  } = useReadings();

  const {
    sensors,
    loading: sensorsLoading,
    error: sensorsError,
  } = useSensors();

  const pageError =
    error ||
    sensorsError ||
    exportError;

  const filtersBusy =
    loading ||
    refreshing ||
    sensorsLoading;

  const actionsBusy =
    filtersBusy ||
    exporting;

  const hasResults =
    pagination.total_items > 0;

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>
            Análisis histórico
          </p>

          <h1 className={styles.title}>
            Historial de lecturas
          </h1>

          <p className={styles.description}>
            Consultá y filtrá las mediciones
            registradas por los sensores de la planta.
          </p>
        </div>

        <div className={styles.headerActions}>
          <button
            type="button"
            className={styles.exportButton}
            onClick={exportCsv}
            disabled={
              actionsBusy ||
              !hasResults
            }
          >
            <i
              className={
                exporting
                  ? "bi bi-hourglass-split"
                  : "bi bi-download"
              }
            />

            {exporting
              ? "Exportando..."
              : "Exportar CSV"}
          </button>

          <button
            type="button"
            className={styles.refreshButton}
            onClick={refresh}
            disabled={actionsBusy}
          >
            <i
              className={`bi bi-arrow-clockwise ${
                refreshing
                  ? styles.rotating
                  : ""
              }`}
            />

            {refreshing
              ? "Actualizando..."
              : "Actualizar"}
          </button>
        </div>
      </header>

      {pageError && (
        <ConnectionBanner>
          {exportError
            ? "No se pudo exportar el historial: "
            : "No se pudo cargar el historial: "}

          {pageError}
        </ConnectionBanner>
      )}

      <section className={styles.filtersSection}>
        <HistoryFilters
          sensors={sensors}
          filters={filters}
          loading={filtersBusy}
          onApply={applyFilters}
          onClear={clearFilters}
        />
      </section>

      <section className={styles.resultsSection}>
        <div className={styles.resultsHeader}>
          <div>
            <h2 className={styles.resultsTitle}>
              Resultados
            </h2>

            <p className={styles.resultsDescription}>
              Lecturas ordenadas desde la más
              reciente hasta la más antigua.
            </p>
          </div>

          {!loading && (
            <span className={styles.totalBadge}>
              {pagination.total_items} lecturas
            </span>
          )}
        </div>

        <HistoryTable
          readings={readings}
          loading={loading}
          title=""
          emptyMessage="No se encontraron lecturas con los filtros seleccionados."
          showStatus={true}
        />

        <HistoryPagination
          pagination={pagination}
          loading={refreshing}
          onPageChange={changePage}
          onPageSizeChange={changePageSize}
        />
      </section>
    </div>
  );
}