import styles from "./ConnectionBanner.module.css";

export default function ConnectionBanner({ children }) {
  return <div className={styles.banner}>{children}</div>;
}
