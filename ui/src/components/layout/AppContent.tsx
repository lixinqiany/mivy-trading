import type { PropsWithChildren } from 'react';
import styles from './AppContent.module.css';

export function AppContent({ children }: PropsWithChildren) {
  return (
    <main className={styles.content} aria-labelledby="page-title">
      {children}
    </main>
  );
}
