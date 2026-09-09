import { useTranslation } from 'react-i18next';
import { NavLink } from 'react-router-dom';
import chevronLeftIcon from '../../assets/icons/chevron-left.svg';
import { NAVIGATION_GROUPS } from '../../config/navigation';
import { I18N_NAMESPACES } from '../../i18n/namespaces';
import { BrandLogo } from '../brand/BrandLogo';
import { AppIcon } from '../icons/AppIcon';
import { ChinaStandardTime } from './ChinaStandardTime';
import styles from './AppSidebar.module.css';

interface AppSidebarProps {
  collapsed: boolean;
  compact: boolean;
  onCollapsedChange: (collapsed: boolean) => void;
}

export function AppSidebar({
  collapsed,
  compact,
  onCollapsedChange,
}: AppSidebarProps) {
  const { t } = useTranslation([
    I18N_NAMESPACES.navigation,
    I18N_NAMESPACES.common,
  ]);
  const iconOnly = collapsed || compact;

  return (
    <aside
      className={styles.sidebar}
      data-collapsed={collapsed}
      data-layout={compact ? 'compact' : 'desktop'}
      aria-label={t('navigation:mainLabel')}
    >
      <BrandLogo collapsed={collapsed} compact={compact} />

      {!compact ? (
        <button
          className={styles.toggle}
          type="button"
          aria-label={
            collapsed
              ? t('navigation:toggle.expand')
              : t('navigation:toggle.collapse')
          }
          aria-expanded={!collapsed}
          onClick={() => onCollapsedChange(!collapsed)}
        >
          <AppIcon className={styles.toggleIcon} src={chevronLeftIcon} />
        </button>
      ) : null}

      <div className={styles.navigation}>
        {NAVIGATION_GROUPS.map((group) => (
          <section
            className={styles.group}
            key={group.id}
            aria-label={t(group.labelKey)}
          >
            <div className={styles.sectionLabel} aria-hidden="true">
              {t(group.labelKey)}
            </div>
            <nav className={styles.nav}>
              {group.items.map((item) => (
                <NavLink
                  className={({ isActive }) =>
                    `${styles.navItem}${isActive ? ` ${styles.active}` : ''}`
                  }
                  key={item.id}
                  to={item.path}
                  title={iconOnly ? t(item.labelKey) : undefined}
                  aria-label={t(item.labelKey)}
                >
                  <AppIcon className={styles.navIcon} src={item.icon} />
                  <span className={styles.navLabel}>{t(item.labelKey)}</span>
                </NavLink>
              ))}
            </nav>
          </section>
        ))}
      </div>

      <footer className={styles.footer}>
        <div className={styles.status}>
          <span className={styles.statusDot} aria-hidden="true" />
          <span>{t('common:status.dataPlaneOnline')}</span>
        </div>
        <ChinaStandardTime className={styles.clock} />
        <div
          className={styles.compactClock}
          aria-label={t('common:time.chinaStandardTime')}
        >
          <strong>{t('common:time.region')}</strong>
          <ChinaStandardTime compact />
        </div>
      </footer>
    </aside>
  );
}
