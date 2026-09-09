import { COMPACT_NAVIGATION_QUERY } from '../config/layout';
import { useMediaQuery } from './useMediaQuery';

export function useCompactLayout() {
  return useMediaQuery(COMPACT_NAVIGATION_QUERY);
}
