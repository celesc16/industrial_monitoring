import styles from "./Toast.module.css";

export default function ToastView({ toasts, onDismiss }) {
  if (toasts.length === 0) {
    return null;
  }

  return (
    <div
      className={styles.container}
      role="region"
      aria-label="Notificaciones"
    >
      {toasts.map((toast) => (
        <div
          key={toast.id}
          role="alert"
          className={`${styles.toast} ${
            toast.type === "error"
              ? styles.error
              : styles.info
          }`}
        >
          <i
            className={`bi ${
              toast.type === "error"
                ? "bi-shield-exclamation"
                : "bi-info-circle"
            }`}
            aria-hidden="true"
          />

          <span>{toast.message}</span>

          <button
            type="button"
            className={styles.close}
            onClick={() => onDismiss(toast.id)}
            aria-label="Cerrar notificación"
          >
            <i className="bi bi-x-lg" aria-hidden="true" />
          </button>
        </div>
      ))}
    </div>
  );
}