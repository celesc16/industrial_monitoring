import styles from "./StatusLed.module.css";

export default function StatusLed({ isAnomaly, hasSignal }) {
  const color = !hasSignal
    ? "var(--color-text-faint)"
    : isAnomaly
      ? "var(--color-danger)"
      : "var(--color-success)";
  const glow = !hasSignal ? "none" : isAnomaly ? "var(--color-danger-glow)" : "var(--color-success-glow)";

  return (
    <span
      className={`${styles.led} ${isAnomaly && hasSignal ? styles.ledPulse : ""}`}
      style={{ "--led-color": color, "--led-glow": glow }}
    />
  );
}
