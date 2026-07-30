const FORMATTERS = new Map();

function getNumberFormatter(decimals) {
  if (!FORMATTERS.has(decimals)) {
    FORMATTERS.set(
      decimals,
      new Intl.NumberFormat("es-AR", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      })
    );
  }

  return FORMATTERS.get(decimals);
}

export function formatNumber(value, decimals = 2) {
  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return "—";
  }

  return getNumberFormatter(decimals).format(
    numericValue
  );
}