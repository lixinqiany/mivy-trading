import { NavLink } from 'react-router-dom';
import { NAVIGATION_GROUPS } from '../../config/navigation';
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
  const iconOnly = collapsed || compact;

  return (
    <aside
      className={styles.sidebar}
      data-collapsed={collapsed}
      data-layout={compact ? 'compact' : 'desktop'}
      aria-label="主导航"
    >
      <BrandLogo collapsed={collapsed} compact={compact} />

      {!compact ? (
        <button
          className={styles.toggle}
          type="button"
          aria-label={collapsed ? '展开侧边栏' : '收起侧边栏'}
          aria-expanded={!collapsed}
          onClick={() => onCollapsedChange(!collapsed)}
        >
          <AppIcon className={styles.toggleIcon} name="chevron-left" />
        </button>
      ) : null}

      <div className={styles.navigation}>
        {NAVIGATION_GROUPS.map((group) => (
          <section
            className={styles.group}
            key={group.id}
            aria-label={group.label}
          >
            <div className={styles.sectionLabel} aria-hidden="true">
              {group.label}
            </div>
            <nav className={styles.nav}>
              {group.items.map((item) => (
                <NavLink
                  className={({ isActive }) =>
                    `${styles.navItem}${isActive ? ` ${styles.active}` : ''}`
                  }
                  key={item.id}
                  to={item.path}
                  title={iconOnly ? item.label : undefined}
                  aria-label={item.label}
                >
                  <AppIcon className={styles.navIcon} name={item.icon} />
                  <span className={styles.navLabel}>{item.label}</span>
                </NavLink>
              ))}
            </nav>
          </section>
        ))}
      </div>

      <footer className={styles.footer}>
        <div className={styles.status}>
          <span className={styles.statusDot} aria-hidden="true" />
          <span>Data Plane Online</span>
        </div>
        <ChinaStandardTime className={styles.clock} />
        <div className={styles.compactClock} aria-label="中国标准时间">
          <strong>CN</strong>
          <ChinaStandardTime compact />
        </div>
      </footer>
    </aside>
  );
}
