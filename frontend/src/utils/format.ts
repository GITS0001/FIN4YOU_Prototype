/**
 * Format a number as currency with the correct symbol.
 * FIN4YOU supports multi-currency (ZAR, IDR, EUR, USD).
 */
export function formatCurrency(amount: number | string | undefined | null, currency: string = 'USD'): string {
  if (amount === undefined || amount === null || Number.isNaN(Number(amount))) {
    return '—';
  }
  
  const numAmount = Number(amount);

  const currencyMap: Record<string, { locale: string; currency: string }> = {
    INR: { locale: 'en-IN', currency: 'INR' },
    IDR: { locale: 'id-ID', currency: 'IDR' },
    EUR: { locale: 'de-DE', currency: 'EUR' },
    USD: { locale: 'en-US', currency: 'USD' },
    ZAR: { locale: 'en-ZA', currency: 'ZAR' }
  };

  const config = currencyMap[currency] || { locale: 'en-US', currency: currency };

  try {
    return new Intl.NumberFormat(config.locale, {
      style: 'currency',
      currency: config.currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(numAmount);
  } catch {
    return `${config.currency} ${numAmount.toLocaleString('en-US')}`;
  }
}

/**
 * Format a number as a compact currency (e.g., ₹1.2L, R58K, etc.)
 */
export function formatCurrencyCompact(amount: number, currency: string = 'USD'): string {
  if (Math.abs(amount) >= 1_000_000) {
    return `${formatCurrencySymbol(currency)}${(amount / 1_000_000).toFixed(1)}M`;
  }
  if (Math.abs(amount) >= 1_000) {
    return `${formatCurrencySymbol(currency)}${(amount / 1_000).toFixed(1)}K`;
  }
  return formatCurrency(amount, currency);
}

/**
 * Get just the currency symbol for a given currency code
 */
export function formatCurrencySymbol(currency: string): string {
  // ZAR is treated as INR (₹) for this prototype
  const symbols: Record<string, string> = {
    ZAR: '₹',
    IDR: 'Rp',
    EUR: '€',
    USD: '$',
    INR: '₹',
  };
  return symbols[currency] || currency;
}

/**
 * Format a percentage (0.25 → "25%")
 */
export function formatPercent(value: number, decimals: number = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Get a human-readable label for a category key
 */
export function formatCategory(category: string): string {
  return category
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (l) => l.toUpperCase());
}

/**
 * Get a greeting based on the current time
 */
export function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

/**
 * Format a confidence string to display text
 */
export function formatConfidence(confidence: string): { label: string; variant: 'positive' | 'warning' | 'neutral' } {
  switch (confidence.toUpperCase()) {
    case 'HIGH':
      return { label: 'High confidence', variant: 'positive' };
    case 'MEDIUM':
      return { label: 'Medium confidence', variant: 'warning' };
    case 'LOW':
      return { label: 'Low confidence', variant: 'warning' };
    default:
      return { label: 'Unknown confidence', variant: 'neutral' };
  }
}

/**
 * Get a color class for a category (for charts)
 */
const CATEGORY_COLORS = [
  '#2563EB', '#16A34A', '#F59E0B', '#DC2626', '#7C3AED',
  '#DB2777', '#059669', '#D97706', '#0891B2', '#9333EA',
];

export function getCategoryColor(index: number): string {
  return CATEGORY_COLORS[index % CATEGORY_COLORS.length];
}

/**
 * Clamp a number between min and max
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/**
 * Format date string to readable format
 */
export function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateStr;
  }
}
