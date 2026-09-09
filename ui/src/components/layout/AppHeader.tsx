import type { ReactNode } from 'react';
import styles from './AppHeader.module.css';

interface AppHeaderProps {
  title: string;
  compact?: boolean;
  actions?: ReactNode;
}

export function AppHeader({ title, compact = false, actions }: AppHeaderProps) {
  return (
    <header
      className={styles.header}
      data-layout={compact ? 'compact' : 'desktop'}
    >
      <div className={styles.titleGroup}>
        <span className={styles.marker} aria-hidden="true">
          <span className={styles.dot} />
        </span>
        <h1 className={styles.title} id="page-title">
          {title}
        </h1>
      </div>
      {actions ? <div className={styles.actions}>{actions}</div> : null}
    </header>
  );
}
