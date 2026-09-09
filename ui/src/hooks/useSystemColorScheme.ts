import { useMediaQuery } from './useMediaQuery';

export type ColorScheme = 'dark' | 'light';

const DARK_COLOR_SCHEME_QUERY = '(prefers-color-scheme: dark)';

export function useSystemColorScheme(): ColorScheme {
  return useMediaQuery(DARK_COLOR_SCHEME_QUERY) ? 'dark' : 'light';
}
