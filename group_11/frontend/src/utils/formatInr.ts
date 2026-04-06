/** Format rupee amounts; API may send JSON `null` for missing numbers. */
export function formatInr(value: number | null | undefined): string {
  if (value == null || (typeof value === 'number' && Number.isNaN(value))) {
    return '—'
  }
  return `₹${Number(value).toLocaleString('en-IN')}`
}

/** Safe numeric value for comparisons / percentages when API sends `null`. */
export function numOr(value: number | null | undefined, fallback = 0): number {
  if (value == null || (typeof value === 'number' && Number.isNaN(value))) {
    return fallback
  }
  return Number(value)
}
