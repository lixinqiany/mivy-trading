import type { ParseKeys } from 'i18next';
import activityIcon from '../assets/icons/activity.svg';
import databaseZapIcon from '../assets/icons/database-zap.svg';
import layersIcon from '../assets/icons/layers.svg';
import orbitIcon from '../assets/icons/orbit.svg';

type NavigationTranslationKey = ParseKeys<['navigation']>;
type BusinessTranslationKey = ParseKeys<
  ['securityPool', 'watchlists', 'dataCrawling', 'taskCenter']
>;

export interface NavigationItem {
  id: string;
  path: string;
  labelKey: NavigationTranslationKey;
  headerTitleKey: BusinessTranslationKey;
  icon: string;
}

export interface NavigationGroup {
  id: string;
  labelKey: NavigationTranslationKey;
  items: readonly NavigationItem[];
}

export const APP_PATHS = {
  securityPool: '/security-pool',
  watchlists: '/watchlists',
  dataCrawling: '/data-crawling',
  taskCenter: '/task-center',
} as const;

export const NAVIGATION_GROUPS: readonly NavigationGroup[] = [
  {
    id: 'asset-layer',
    labelKey: 'navigation:groups.assetLayer',
    items: [
      {
        id: 'security-pool',
        path: APP_PATHS.securityPool,
        labelKey: 'navigation:items.securityPool',
        headerTitleKey: 'securityPool:headerTitle',
        icon: orbitIcon,
      },
      {
        id: 'watchlists',
        path: APP_PATHS.watchlists,
        labelKey: 'navigation:items.watchlists',
        headerTitleKey: 'watchlists:headerTitle',
        icon: layersIcon,
      },
    ],
  },
  {
    id: 'data-plane',
    labelKey: 'navigation:groups.dataPlane',
    items: [
      {
        id: 'data-crawling',
        path: APP_PATHS.dataCrawling,
        labelKey: 'navigation:items.dataCrawling',
        headerTitleKey: 'dataCrawling:headerTitle',
        icon: databaseZapIcon,
      },
      {
        id: 'task-center',
        path: APP_PATHS.taskCenter,
        labelKey: 'navigation:items.taskCenter',
        headerTitleKey: 'taskCenter:headerTitle',
        icon: activityIcon,
      },
    ],
  },
] as const;

export const DEFAULT_NAVIGATION_ITEM = NAVIGATION_GROUPS[0].items[0];

export function findNavigationItem(pathname: string): NavigationItem {
  return (
    NAVIGATION_GROUPS.flatMap((group) => group.items).find(
      (item) => pathname === item.path || pathname.startsWith(`${item.path}/`),
    ) ?? DEFAULT_NAVIGATION_ITEM
  );
}
