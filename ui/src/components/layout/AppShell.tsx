import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { findNavigationItem } from '../../config/navigation';
import { useCompactLayout } from '../../hooks/useCompactLayout';
import { useDocumentTitle } from '../../hooks/useDocumentTitle';
import { useSystemTheme } from '../../providers/system-theme/systemThemeContext';
import { AppHeader } from './AppHeader';
import { AppSidebar } from './AppSidebar';
import styles from './AppShell.module.css';

export function AppShell() {
  const location = useLocation();
  const compactLayout = useCompactLayout();
  const colorScheme = useSystemTheme();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const currentNavigationItem = findNavigationItem(location.pathname);
  const effectiveSidebarCollapsed = compactLayout ? false : sidebarCollapsed;

  useDocumentTitle(currentNavigationItem.headerTitle);

  return (
    <div
      className={styles.shell}
      data-color-scheme={colorScheme}
      data-layout={compactLayout ? 'compact' : 'desktop'}
      data-sidebar={effectiveSidebarCollapsed ? 'collapsed' : 'expanded'}
    >
      <AppSidebar
        collapsed={effectiveSidebarCollapsed}
        compact={compactLayout}
        onCollapsedChange={setSidebarCollapsed}
      />
      <section className={styles.workspace}>
        <AppHeader
          title={currentNavigationItem.headerTitle}
          compact={compactLayout}
        />
        <main className={styles.content} aria-labelledby="page-title">
          <Outlet />
        </main>
      </section>
    </div>
  );
}
