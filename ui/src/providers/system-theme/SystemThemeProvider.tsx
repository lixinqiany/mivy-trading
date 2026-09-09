import { useEffect } from 'react';
import type { PropsWithChildren } from 'react';
import { useSystemColorScheme } from '../../hooks/useSystemColorScheme';
import { SystemThemeContext } from './systemThemeContext';

export function SystemThemeProvider({ children }: PropsWithChildren) {
  const colorScheme = useSystemColorScheme();

  useEffect(() => {
    document.documentElement.dataset.colorScheme = colorScheme;
    document.documentElement.style.colorScheme = colorScheme;
  }, [colorScheme]);

  return (
    <SystemThemeContext.Provider value={colorScheme}>
      {children}
    </SystemThemeContext.Provider>
  );
}
