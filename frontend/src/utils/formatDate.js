const ARGENTINA_TIME_ZONE =
  "America/Argentina/Mendoza";

const DATE_TIME_FORMATTER = new Intl.DateTimeFormat(
  "es-AR",
  {
    timeZone: ARGENTINA_TIME_ZONE,
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }
);

const DATE_FORMATTER = new Intl.DateTimeFormat(
  "es-AR",
  {
    timeZone: ARGENTINA_TIME_ZONE,
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }
);

const TIME_FORMATTER = new Intl.DateTimeFormat(
  "es-AR",
  {
    timeZone: ARGENTINA_TIME_ZONE,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }
);

function normalizeBackendDate(value) {
  let normalizedValue = String(value).trim();

  const hasTimeZone =
    normalizedValue.endsWith("Z") ||
    /[+-]\d{2}:\d{2}$/.test(normalizedValue);

  /*
   * El backend usa datetime.utcnow(), pero devuelve la fecha
   * sin indicar que está en UTC. se agrega "Z" para que el
   * navegador la interprete correctamente.
   */
  if (!hasTimeZone) {
    normalizedValue = `${normalizedValue}Z`;
  }
  normalizedValue = normalizedValue.replace(
    /(\.\d{3})\d+(?=Z|[+-]\d{2}:\d{2}$)/,
    "$1"
  );

  return normalizedValue;
}

function parseBackendDate(value) {
  if (!value) {
    return null;
  }

  const date = new Date(
    normalizeBackendDate(value)
  );

  if (Number.isNaN(date.getTime())) {
    return null;
  }

  return date;
}

export function formatDateTime(value) {
  const date = parseBackendDate(value);

  if (!date) {
    return "Sin registros";
  }

  return DATE_TIME_FORMATTER.format(date);
}

export function formatDate(value) {
  const date = parseBackendDate(value);

  if (!date) {
    return "—";
  }

  return DATE_FORMATTER.format(date);
}

export function formatTime(value) {
  const date = parseBackendDate(value);

  if (!date) {
    return "—";
  }

  return TIME_FORMATTER.format(date);
}