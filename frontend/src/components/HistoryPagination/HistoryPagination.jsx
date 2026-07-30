import { useMemo } from "react";

import styles from "./HistoryPagination.module.css";

const ELLIPSIS = "ellipsis";

function createRange(start, end) {
  const range = [];

  for (let page = start; page <= end; page += 1) {
    range.push(page);
  }

  return range;
}

function getPaginationItems(
  currentPage,
  totalPages
) {
  const siblingCount = 1;
  const boundaryCount = 1;

  /*
   * Cantidad máxima aproximada:
   * primera + puntos + anterior + actual +
   * siguiente + puntos + última.
   */
  const visibleItems =
    boundaryCount * 2 +
    siblingCount * 2 +
    3;

  if (totalPages <= visibleItems) {
    return createRange(1, totalPages);
  }

  const leftSibling = Math.max(
    currentPage - siblingCount,
    boundaryCount + 2
  );

  const rightSibling = Math.min(
    currentPage + siblingCount,
    totalPages - boundaryCount - 1
  );

  const showLeftEllipsis =
    leftSibling > boundaryCount + 2;

  const showRightEllipsis =
    rightSibling <
    totalPages - boundaryCount - 1;

  const firstPages = createRange(
    1,
    boundaryCount
  );

  const lastPages = createRange(
    totalPages - boundaryCount + 1,
    totalPages
  );

  /*
   * Estamos cerca del inicio:
   * 1 2 3 4 5 … última
   */
  if (
    !showLeftEllipsis &&
    showRightEllipsis
  ) {
    const leftItemCount =
      boundaryCount +
      siblingCount * 2 +
      2;

    return [
      ...createRange(1, leftItemCount),
      ELLIPSIS,
      ...lastPages,
    ];
  }

  /*
   * Estamos cerca del final:
   * primera … 80 81 82 83 84
   */
  if (
    showLeftEllipsis &&
    !showRightEllipsis
  ) {
    const rightItemCount =
      boundaryCount +
      siblingCount * 2 +
      2;

    return [
      ...firstPages,
      ELLIPSIS,
      ...createRange(
        totalPages - rightItemCount + 1,
        totalPages
      ),
    ];
  }

  /*
   * Estamos en una zona intermedia:
   * primera … anterior actual siguiente … última
   */
  return [
    ...firstPages,
    ELLIPSIS,
    ...createRange(
      leftSibling,
      rightSibling
    ),
    ELLIPSIS,
    ...lastPages,
  ];
}

export default function HistoryPagination({
  pagination,
  loading = false,
  onPageChange,
  onPageSizeChange,
}) {
  const {
    page,
    page_size: pageSize,
    total_items: totalItems,
    total_pages: totalPages,
  } = pagination;

  const paginationItems = useMemo(
    () =>
      getPaginationItems(
        page,
        totalPages
      ),
    [page, totalPages]
  );

  if (
    totalItems === 0 ||
    totalPages === 0
  ) {
    return null;
  }

  const firstItem =
    (page - 1) * pageSize + 1;

  const lastItem = Math.min(
    page * pageSize,
    totalItems
  );

  return (
    <div className={styles.pagination}>
      <div className={styles.summary}>
        Mostrando{" "}
        <strong>
          {firstItem}-{lastItem}
        </strong>{" "}
        de <strong>{totalItems}</strong>{" "}
        lecturas
      </div>

      <div className={styles.controls}>
        <label className={styles.pageSize}>
          <span>Por página</span>

          <select
            value={pageSize}
            onChange={(event) =>
              onPageSizeChange(
                Number(event.target.value)
              )
            }
            disabled={loading}
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </label>

        <nav
          className={styles.pages}
          aria-label="Paginación del historial"
        >
          <button
            type="button"
            className={styles.navigationButton}
            onClick={() =>
              onPageChange(page - 1)
            }
            disabled={loading || page <= 1}
            aria-label="Página anterior"
          >
            <i className="bi bi-chevron-left" />
          </button>

          {paginationItems.map(
            (item, index) => {
              if (item === ELLIPSIS) {
                return (
                  <span
                    key={`ellipsis-${index}`}
                    className={styles.ellipsis}
                    aria-hidden="true"
                  >
                    …
                  </span>
                );
              }

              const isActive =
                item === page;

              return (
                <button
                  key={item}
                  type="button"
                  className={`${styles.pageButton} ${
                    isActive
                      ? styles.activePage
                      : ""
                  }`}
                  onClick={() =>
                    onPageChange(item)
                  }
                  disabled={
                    loading || isActive
                  }
                  aria-label={`Ir a la página ${item}`}
                  aria-current={
                    isActive
                      ? "page"
                      : undefined
                  }
                >
                  {item}
                </button>
              );
            }
          )}

          <button
            type="button"
            className={styles.navigationButton}
            onClick={() =>
              onPageChange(page + 1)
            }
            disabled={
              loading ||
              page >= totalPages
            }
            aria-label="Página siguiente"
          >
            <i className="bi bi-chevron-right" />
          </button>
        </nav>
      </div>
    </div>
  );
}