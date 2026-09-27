import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { DEMO_CREDENTIALS } from "../../auth/auth";
import { useAuth } from "../../auth/AuthContext";

import styles from "./LoginPage.module.css";

export default function LoginPage() {
  const navigate = useNavigate();
  const { session, loginAs } = useAuth();

  const [pendingRole, setPendingRole] = useState(null);
  const [error, setError] = useState(null);

  if (session) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleLogin(role) {
    setPendingRole(role);
    setError(null);

    try {
      await loginAs(role);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(
        err.message || "No se pudo iniciar sesión."
      );
    } finally {
      setPendingRole(null);
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <header className={styles.header}>
          <span className={styles.brandIcon}>
            <i className="bi bi-activity" aria-hidden="true" />
          </span>

          <p className={styles.eyebrow}>
            Industrial Monitor
          </p>

          <h1 className={styles.title}>Acceso al panel</h1>

          <p className={styles.subtitle}>
            Elegí un perfil de demostración para
            explorar la plataforma.
          </p>
        </header>

        <div className={styles.buttons}>
          {Object.entries(DEMO_CREDENTIALS).map(
            ([role, credentials]) => (
              <button
                key={role}
                type="button"
                className={`${styles.loginButton} ${
                  role === "ADMIN"
                    ? styles.adminButton
                    : ""
                }`}
                onClick={() => handleLogin(role)}
                disabled={pendingRole !== null}
              >
                <i
                  className={`bi ${
                    pendingRole === role
                      ? "bi-arrow-repeat"
                      : role === "ADMIN"
                        ? "bi-person-gear"
                        : "bi-person"
                  }`}
                  aria-hidden="true"
                />

                <span>
                  <strong>
                    Ingresar como {credentials.label} (Demo)
                  </strong>

                  <small>
                    {role === "ADMIN"
                      ? "Control total de la planta"
                      : "Acceso de solo lectura"}
                  </small>
                </span>
              </button>
            )
          )}
        </div>

        {error && (
          <p className={styles.error} role="alert">
            {error}
          </p>
        )}

        <p className={styles.hint}>
          Cuentas demo precargadas: no hace falta
          registrarse.
        </p>
      </div>
    </div>
  );
}