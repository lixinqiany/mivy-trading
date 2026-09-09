export const I18N_NAMESPACES = {
  common: 'common',
  navigation: 'navigation',
  securityPool: 'securityPool',
  watchlists: 'watchlists',
  dataCrawling: 'dataCrawling',
  taskCenter: 'taskCenter',
} as const;

export const BUSINESS_NAMESPACES = [
  I18N_NAMESPACES.securityPool,
  I18N_NAMESPACES.watchlists,
  I18N_NAMESPACES.dataCrawling,
  I18N_NAMESPACES.taskCenter,
] as const;

export const ALL_NAMESPACES = Object.values(I18N_NAMESPACES);
