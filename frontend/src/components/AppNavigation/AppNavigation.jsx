import { NavLink } from "react-router-dom";

import { useAuth } from "../../auth/AuthContext";
import ThemeToggle from "../ThemeToggle/ThemeToggle";

import styles from "./AppNavigation.module.css";

const NAVIGATION = [
  {
    to: "/dashboard",
    label: "Dashboard",
    icon: "bi-grid-1x2",
  },
  {
    to: "/sensors",
    label: "Sensores",
    icon: "bi-cpu",
  },
  {
    to: "/history",
    label: "Historial",
    icon: "bi-clock-history",
  },
];

const ROLE_LABELS = {
  ADMIN: "Administrador",
  VIEWER: "Operario",
};

export default function AppNavigation() {
  const { session, logout } = useAuth();

  const roleLabel =
    ROLE_LABELS[session?.role] ?? session?.role ?? "";

  return (
    <header className={styles.navigation}>
      <div className={styles.inner}>
        <NavLink
          to="/dashboard"
          className={styles.brand}
        >
          <span className={styles.brandIcon}>
            <i className="bi bi-activity" />
          </span>

          <span>
            <strong>Industrial Monitor</strong>
            <small>Control en tiempo real</small>
          </span>
        </NavLink>

        <nav
          className={styles.links}
          aria-label="Navegación principal"
        >
          {NAVIGATION.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `${styles.link} ${
                  isActive
                    ? styles.linkActive
                    : ""
                }`
              }
            >
              <i className={`bi ${item.icon}`} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className={styles.actions}>
          {roleLabel && (
            <span className={styles.roleBadge}>
              <i
                className={`bi ${
                  session?.role === "ADMIN"
                    ? "bi-person-gear"
                    : "bi-person"
                }`}
                aria-hidden="true"
              />
              {roleLabel}
            </span>
          )}

          <ThemeToggle />

          <button
            type="button"
            className={styles.logout}
            onClick={logout}
            title="Cerrar sesión"
          >
            <i className="bi bi-box-arrow-right" />
          </button>
        </div>
      </div>
    </header>
  );
}