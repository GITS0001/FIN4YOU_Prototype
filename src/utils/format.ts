/**
 * Format a number as currency with the correct symbol.
 * FIN4YOU supports multi-currency (ZAR, IDR, EUR, USD).
 */
export function formatCurrency(amount: number | string | undefined | null, currency: string = 'INR'): string {
  if (amount === undefined || amount === null || Number.isNaN(Number(amount))) {
    return '—';
  }
  
  const numAmount = Number(amount);

  const activeCurrency = (!currency || currency === 'USD') ? 'INR' : currency;

  const currencyMap: Record<string, { locale: string; currency: string }> = {
    INR: { locale: 'en-IN', currency: 'INR' },
    IDR: { locale: 'id-ID', currency: 'IDR' },
    EUR: { locale: 'de-DE', currency: 'EUR' },
    USD: { locale: 'en-IN', currency: 'INR' },
    ZAR: { locale: 'en-IN', currency: 'INR' }
  };

  const config = currencyMap[activeCurrency] || { locale: 'en-IN', currency: activeCurrency };

  try {
    return new Intl.NumberFormat(config.locale, {
      style: 'currency',
      currency: config.currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(numAmount);
  } catch {
    return `${config.currency} ${numAmount.toLocaleString('en-IN')}`;
  }
}

/**
 * Format a number as a compact currency (e.g., ₹1.2 L, ₹1.5 Cr, etc.)
 */
export function formatCurrencyCompact(amount: number, currency: string = 'INR'): string {
  const absAmount = Math.abs(amount);
  const sign = amount < 0 ? '-' : '';
  const sym = formatCurrencySymbol(currency);
  
  if (absAmount >= 1_00_00_000) {
    return `${sign}${sym}${(absAmount / 1_00_00_000).toFixed(2)} Cr`;
  }
  if (absAmount >= 1_00_000) {
    return `${sign}${sym}${(absAmount / 1_00_000).toFixed(2)} L`;
  }
  if (absAmount >= 1_000) {
    return `${sign}${sym}${(absAmount / 1_000).toFixed(1)}K`;
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
    USD: '₹',
    INR: '₹',
  };
  return symbols[currency] || '₹';
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

/**
 * Extract clean username of the authenticated login account.
 * Guarantees that ONLY the account username is shown (no email domain or raw email strings).
 */
export function getAccountUsername(
  user?: { email?: string; full_name?: string; username?: string } | null,
  profile?: { email?: string; full_name?: string } | null
): string {
  // 1. Direct explicit username
  if (user?.username && typeof user.username === 'string' && !user.username.includes('@') && user.username.trim()) {
    return user.username.trim();
  }

  // 2. Email from authenticated user object
  if (user?.email && typeof user.email === 'string' && user.email.includes('@')) {
    const prefix = user.email.split('@')[0].trim();
    if (prefix) return prefix;
  }

  // 3. Email from profile object
  if (profile?.email && typeof profile.email === 'string' && profile.email.includes('@')) {
    const prefix = profile.email.split('@')[0].trim();
    if (prefix) return prefix;
  }

  // 4. Stored user from localStorage
  try {
    const raw = localStorage.getItem('fin4you_user');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed?.username && !parsed.username.includes('@')) return parsed.username.trim();
      if (parsed?.email && parsed.email.includes('@')) {
        const prefix = parsed.email.split('@')[0].trim();
        if (prefix) return prefix;
      }
      if (parsed?.full_name && parsed.full_name.trim() && parsed.full_name !== 'Demo User') {
        return parsed.full_name.includes('@') ? parsed.full_name.split('@')[0].trim() : parsed.full_name.trim();
      }
    }
  } catch {
    // ignore
  }

  // 5. User or Profile full_name if present and clean
  const candidate = user?.full_name || profile?.full_name;
  if (candidate && typeof candidate === 'string' && candidate.trim() && candidate !== 'Demo User') {
    return candidate.includes('@') ? candidate.split('@')[0].trim() : candidate.trim();
  }

  return 'User';
}
