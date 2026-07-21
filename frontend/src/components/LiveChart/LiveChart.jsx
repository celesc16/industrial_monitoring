import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import styles from "./LiveChart.module.css";

const METRICS = [
  { key: "temperature", label: "Temperatura", unit: "°C", color: "var(--color-temp)" },
  { key: "vibration", label: "Vibración", unit: "mm/s", color: "var(--color-vibration)" },
  { key: "pressure", label: "Presión", unit: "kPa", color: "var(--color-pressure)" },
];

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;

  return (
    <div className={styles.tooltip}>
      <div className={styles.tooltipTime}>{label}</div>
      {payload.map((entry) => (
        <div key={entry.dataKey} className={styles.tooltipRow}>
          <span className={styles.tooltipSwatch} style={{ background: entry.color }} />
          <span>{entry.name}</span>
          <strong>{entry.value}</strong>
        </div>
      ))}
    </div>
  );
}

export default function LiveChart({ points }) {
  const data = points.map((p) => ({
    time: new Date(p.timestamp).toLocaleTimeString("es-AR", { hour12: false }),
    temperature: p.temperature,
    vibration: p.vibration,
    pressure: p.pressure,
    is_anomaly: p.is_anomaly,
  }));

  const anomalyBands = [];
  data.forEach((d, i) => {
    if (d.is_anomaly) anomalyBands.push({ x1: data[Math.max(i - 1, 0)].time, x2: d.time });
  });

  return (
    <div className={`panel ${styles.card}`}>
      <div className="panel__header">
        <h2 className="panel__title">Telemetría en vivo</h2>
        <div className={styles.legend}>
          {METRICS.map((m) => (
            <span key={m.key} className={styles.legendItem}>
              <span className={styles.legendSwatch} style={{ background: m.color }} />
              {m.label} ({m.unit})
            </span>
          ))}
        </div>
      </div>

      <div className={styles.canvas}>
        {data.length === 0 ? (
          <div className="empty-state">
            Sin señal todavía.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={data} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
              <CartesianGrid stroke="var(--color-border-soft)" strokeDasharray="3 6" />
              <XAxis
                dataKey="time"
                stroke="var(--color-text-faint)"
                tick={{ fontFamily: "var(--font-mono)", fontSize: 11 }}
                minTickGap={40}
              />
              <YAxis
                stroke="var(--color-text-faint)"
                tick={{ fontFamily: "var(--font-mono)", fontSize: 11 }}
                width={38}
              />
              <Tooltip content={<CustomTooltip />} />
              {anomalyBands.map((band, i) => (
                <ReferenceArea
                  key={i}
                  x1={band.x1}
                  x2={band.x2}
                  fill="var(--color-danger)"
                  fillOpacity={0.12}
                  ifOverflow="visible"
                />
              ))}
              {METRICS.map((m) => (
                <Line
                  key={m.key}
                  type="monotone"
                  dataKey={m.key}
                  name={m.label}
                  stroke={m.color}
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
