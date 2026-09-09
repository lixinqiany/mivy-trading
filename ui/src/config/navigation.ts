export type NavigationIcon = 'activity' | 'database-zap' | 'layers' | 'orbit';

export interface NavigationItem {
  id: string;
  path: string;
  label: string;
  headerTitle: string;
  icon: NavigationIcon;
}

export interface NavigationGroup {
  id: string;
  label: string;
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
    label: 'Asset layer',
    items: [
      {
        id: 'security-pool',
        path: APP_PATHS.securityPool,
        label: '证券池',
        headerTitle: '全局证券池',
        icon: 'orbit',
      },
      {
        id: 'watchlists',
        path: APP_PATHS.watchlists,
        label: '自选池',
        headerTitle: '自选池',
        icon: 'layers',
      },
    ],
  },
  {
    id: 'data-plane',
    label: 'Data plane',
    items: [
      {
        id: 'data-crawling',
        path: APP_PATHS.dataCrawling,
        label: '原始数据抓取',
        headerTitle: '原始数据抓取',
        icon: 'database-zap',
      },
      {
        id: 'task-center',
        path: APP_PATHS.taskCenter,
        label: '任务中心',
        headerTitle: '任务中心',
        icon: 'activity',
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
