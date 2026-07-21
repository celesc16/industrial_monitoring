import { NavLink } from "react-router";

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
];

export default function AppNavigation() {
  return (
    <header className={styles.navigation}>
      <div className={styles.inner}>
        <NavLink to="/dashboard" className={styles.brand}>
          <span className={styles.brandIcon}>
            <i className="bi bi-activity" />
          </span>

          <span>
            <strong>Industrial Monitor</strong>
            <small>Control en tiempo real</small>
          </span>
        </NavLink>

        <nav className={styles.links} aria-label="Navegación principal">
          {NAVIGATION.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `${styles.link} ${
                  isActive ? styles.linkActive : ""
                }`
              }
            >
              <i className={`bi ${item.icon}`} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className={styles.actions}>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}