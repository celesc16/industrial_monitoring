import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import { getReadings } from "../api/client";

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
  const [error, setError] = useState(null);

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

  // Carga inicial al entrar a la página.
  useEffect(() => {
    loadReadings({
      page: INITIAL_PAGINATION.page,
      pageSize: INITIAL_PAGINATION.page_size,
      currentFilters: INITIAL_FILTERS,
      showInitialLoading: true,
    });
  }, [loadReadings]);

  // Actualización automática solo en la primera página.
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

  return {
    readings,
    pagination,
    filters,
    loading,
    refreshing,
    error,
    applyFilters,
    clearFilters,
    changePage,
    changePageSize,
    refresh,
  };
}