import styles from "./ConfirmDialog.module.css";

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "Confirmar",
  cancelLabel = "Cancelar",
  loading = false,
  danger = false,
  onConfirm,
  onCancel,
}) {
  if (!open) {
    return null;
  }

  return (
    <div
      className={styles.overlay}
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !loading) {
          onCancel();
        }
      }}
    >
      <section
        className={styles.dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
      >
        <div className={styles.icon}>
          <i
            className={`bi ${
              danger
                ? "bi-exclamation-triangle"
                : "bi-arrow-repeat"
            }`}
          />
        </div>

        <h2 id="confirm-dialog-title">{title}</h2>
        <p>{message}</p>

        <div className={styles.actions}>
          <button
            type="button"
            className={styles.cancelButton}
            onClick={onCancel}
            disabled={loading}
          >
            {cancelLabel}
          </button>

          <button
            type="button"
            className={`${styles.confirmButton} ${
              danger ? styles.dangerButton : ""
            }`}
            onClick={onConfirm}
            disabled={loading}
          >
            {loading && (
              <i className="bi bi-arrow-clockwise" />
            )}

            {loading ? "Procesando..." : confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}