import { createContext, useContext } from 'react';
import type { ColorScheme } from '../../hooks/useSystemColorScheme';

export const SystemThemeContext = createContext<ColorScheme | null>(null);

export function useSystemTheme() {
  const colorScheme = useContext(SystemThemeContext);

  if (!colorScheme) {
    throw new Error('useSystemTheme must be used inside SystemThemeProvider.');
  }

  return colorScheme;
}
