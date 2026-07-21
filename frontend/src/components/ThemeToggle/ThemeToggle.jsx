import { useTheme } from "../../hooks/useTheme";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <button
      onClick={toggleTheme}
      type="button"
      className="btn btn-sm d-inline-flex align-items-center justify-content-center p-2"
      style={{
        width: "40px",
        height: "40px",
        borderRadius: "var(--radius-md)",
        background: "var(--color-surface)",
        border: "1px solid var(--color-border-soft)",
        color: "var(--color-text)",
        cursor: "pointer",
        transition: "all 0.2s ease"
      }}
      title={`Cambiar a modo ${isDark ? "claro" : "oscuro"}`}
    >
      <i 
        className={`bi ${isDark ? "bi-moon-stars-fill" : "bi-sun-fill"}`} 
        style={{ fontSize: "1rem", color: "var(--color-text-muted)" }} 
      />
    </button>
  );
}