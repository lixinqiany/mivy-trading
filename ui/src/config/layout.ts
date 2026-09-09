export const LAYOUT_BREAKPOINTS = {
  compactNavigation: 690,
} as const;

export const COMPACT_NAVIGATION_QUERY = `(max-width: ${LAYOUT_BREAKPOINTS.compactNavigation}px)`;
