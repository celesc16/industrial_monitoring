import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  exportReadingsCsv,
  getReadings,
} from "../api/client";

const AUTO_REFRESH_INTERVAL_MS = 5000;

const INITIAL_PAGINATION = {
  page: 1,
  page_size: 20,
  total_items: 0,
  total_pages: 0,
};

const INITIAL_FILTERS = {
  sensorId: "",
  status: "all",
  dateFrom: "",
  dateTo: "",
};

function parseAnomalyFilter(status) {
  if (status === "anomaly") {
    return true;
  }

  if (status === "normal") {
    return false;
  }

  return null;
}

function createCsvFilename() {
  const now = new Date();

  const pad = (value) =>
    String(value).padStart(2, "0");

  const timestamp = [
    now.getFullYear(),
    pad(now.getMonth() + 1),
    pad(now.getDate()),
  ].join("");

  const time = [
    pad(now.getHours()),
    pad(now.getMinutes()),
    pad(now.getSeconds()),
  ].join("");

  return `lecturas_industriales_${timestamp}_${time}.csv`;
}

export function useReadings() {
  const [readings, setReadings] = useState([]);

  const [pagination, setPagination] = useState(
    INITIAL_PAGINATION
  );

  const [filters, setFilters] = useState(
    INITIAL_FILTERS
  );

  const [loading, setLoading] = useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [exporting, setExporting] =
    useState(false);

  const [error, setError] = useState(null);

  const [exportError, setExportError] =
    useState(null);

  const mountedRef = useRef(true);
  const requestIdRef = useRef(0);

  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
    };
  }, []);

  const loadReadings = useCallback(
    async ({
      page,
      pageSize,
      currentFilters,
      showInitialLoading = false,
      silent = false,
    }) => {
      const requestId = ++requestIdRef.current;

      if (showInitialLoading) {
        setLoading(true);
      } else if (!silent) {
        setRefreshing(true);
      }

      try {
        const response = await getReadings({
          page,
          pageSize,
          sensorId: currentFilters.sensorId,
          isAnomaly: parseAnomalyFilter(
            currentFilters.status
          ),
          dateFrom: currentFilters.dateFrom,
          dateTo: currentFilters.dateTo,
        });

        if (
          !mountedRef.current ||
          requestId !== requestIdRef.current
        ) {
          return;
        }

        setReadings(
          Array.isArray(response.items)
            ? response.items
            : []
        );

        setPagination(
          response.pagination ??
            INITIAL_PAGINATION
        );

        setError(null);
      } catch (err) {
        if (
          !mountedRef.current ||
          requestId !== requestIdRef.current
        ) {
          return;
        }

        setError(
          err.message ||
            "No se pudo cargar el historial de lecturas."
        );
      } finally {
        if (
          mountedRef.current &&
          requestId === requestIdRef.current
        ) {
          setLoading(false);

          if (!silent) {
            setRefreshing(false);
          }
        }
      }
    },
    []
  );

  useEffect(() => {
    loadReadings({
      page: INITIAL_PAGINATION.page,
      pageSize: INITIAL_PAGINATION.page_size,
      currentFilters: INITIAL_FILTERS,
      showInitialLoading: true,
    });
  }, [loadReadings]);

  useEffect(() => {
    if (
      loading ||
      refreshing ||
      pagination.page !== 1
    ) {
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      if (
        document.visibilityState !== "visible"
      ) {
        return;
      }

      loadReadings({
        page: 1,
        pageSize: pagination.page_size,
        currentFilters: filters,
        silent: true,
      });
    }, AUTO_REFRESH_INTERVAL_MS);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [
    filters,
    loading,
    refreshing,
    pagination.page,
    pagination.page_size,
    loadReadings,
  ]);

  const applyFilters = useCallback(
    async (newFilters) => {
      setFilters(newFilters);
      setExportError(null);

      await loadReadings({
        page: 1,
        pageSize: pagination.page_size,
        currentFilters: newFilters,
      });
    },
    [
      loadReadings,
      pagination.page_size,
    ]
  );

  const clearFilters = useCallback(async () => {
    setFilters(INITIAL_FILTERS);
    setExportError(null);

    await loadReadings({
      page: 1,
      pageSize: pagination.page_size,
      currentFilters: INITIAL_FILTERS,
    });
  }, [
    loadReadings,
    pagination.page_size,
  ]);

  const changePage = useCallback(
    async (newPage) => {
      if (
        newPage < 1 ||
        newPage > pagination.total_pages ||
        newPage === pagination.page
      ) {
        return;
      }

      await loadReadings({
        page: newPage,
        pageSize: pagination.page_size,
        currentFilters: filters,
      });
    },
    [
      filters,
      loadReadings,
      pagination.page,
      pagination.page_size,
      pagination.total_pages,
    ]
  );

  const changePageSize = useCallback(
    async (newPageSize) => {
      await loadReadings({
        page: 1,
        pageSize: newPageSize,
        currentFilters: filters,
      });
    },
    [
      filters,
      loadReadings,
    ]
  );

  const refresh = useCallback(async () => {
    await loadReadings({
      page: pagination.page,
      pageSize: pagination.page_size,
      currentFilters: filters,
    });
  }, [
    filters,
    loadReadings,
    pagination.page,
    pagination.page_size,
  ]);

  const exportCsv = useCallback(async () => {
    setExporting(true);
    setExportError(null);

    try {
      const csvBlob = await exportReadingsCsv({
        sensorId: filters.sensorId,
        isAnomaly: parseAnomalyFilter(
          filters.status
        ),
        dateFrom: filters.dateFrom,
        dateTo: filters.dateTo,
      });

      if (!mountedRef.current) {
        return;
      }

      const downloadUrl =
        window.URL.createObjectURL(csvBlob);

      const downloadLink =
        document.createElement("a");

      downloadLink.href = downloadUrl;
      downloadLink.download = createCsvFilename();

      document.body.appendChild(downloadLink);
      downloadLink.click();
      downloadLink.remove();

      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      if (!mountedRef.current) {
        return;
      }

      setExportError(
        err.message ||
          "No se pudo exportar el historial."
      );
    } finally {
      if (mountedRef.current) {
        setExporting(false);
      }
    }
  }, [filters]);

  return {
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
  };
}