export const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0
});

export const compactNumber = new Intl.NumberFormat("en-IN", {
  notation: "compact",
  maximumFractionDigits: 1
});

export function money(value) {
  return currency.format(Number(value || 0));
}

export function number(value) {
  return compactNumber.format(Number(value || 0));
}

export function percent(value) {
  return `${Number(value || 0).toFixed(1)}%`;
}
