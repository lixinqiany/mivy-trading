import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Outlet, useLocation } from 'react-router-dom';
import { findNavigationItem } from '../../config/navigation';
import { useCompactLayout } from '../../hooks/useCompactLayout';
import { useDocumentTitle } from '../../hooks/useDocumentTitle';
import { BUSINESS_NAMESPACES } from '../../i18n/namespaces';
import { useSystemTheme } from '../../providers/system-theme/systemThemeContext';
import { LanguageSwitcher } from '../i18n/LanguageSwitcher';
import { AppHeader } from './AppHeader';
import { AppSidebar } from './AppSidebar';
import styles from './AppShell.module.css';

export function AppShell() {
  const location = useLocation();
  const { t } = useTranslation(BUSINESS_NAMESPACES);
  const compactLayout = useCompactLayout();
  const colorScheme = useSystemTheme();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const currentNavigationItem = findNavigationItem(location.pathname);
  const headerTitle = t(currentNavigationItem.headerTitleKey);
  const effectiveSidebarCollapsed = compactLayout ? false : sidebarCollapsed;

  useDocumentTitle(headerTitle);

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
          title={headerTitle}
          compact={compactLayout}
          actions={<LanguageSwitcher />}
        />
        <main className={styles.content} aria-labelledby="page-title">
          <Outlet />
        </main>
      </section>
    </div>
  );
}
