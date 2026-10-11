import { useSyncExternalStore, useCallback } from 'react';

export type Theme = 'light' | 'dark';

/**
 * Module-level theme store so every consumer (Topbar, Landing, charts…)
 * stays in sync. The initial class is applied pre-paint by the inline
 * script in index.html, so there is no flash of the wrong theme.
 */
const listeners = new Set<() => void>();

function readTheme(): Theme {
  if (typeof document === 'undefined') return 'light';
  return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
}

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  root.classList.remove('light', 'dark');
  root.classList.add(theme);
  try {
    localStorage.setItem('theme', theme);
  } catch {
    /* storage unavailable */
  }
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute('content', theme === 'dark' ? '#0A0F1E' : '#F6F7FB');
  listeners.forEach((l) => l());
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function useTheme() {
  const theme = useSyncExternalStore(subscribe, readTheme, () => 'light' as Theme);

  const setTheme = useCallback((t: Theme) => applyTheme(t), []);
  const toggleTheme = useCallback(() => applyTheme(readTheme() === 'dark' ? 'light' : 'dark'), []);

  return { theme, setTheme, toggleTheme };
}
