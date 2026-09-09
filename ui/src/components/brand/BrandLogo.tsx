import darkWordmark from '../../assets/brand/mivy-wordmark-dark.svg';
import lightWordmark from '../../assets/brand/mivy-wordmark-light.svg';
import styles from './BrandLogo.module.css';

interface BrandLogoProps {
  collapsed?: boolean;
  compact?: boolean;
}

export function BrandLogo({
  collapsed = false,
  compact = false,
}: BrandLogoProps) {
  return (
    <div
      className={styles.brand}
      data-collapsed={collapsed}
      data-compact={compact}
      aria-label="MIVY — Quant Research Platform v0.1.0"
    >
      <picture className={styles.picture}>
        <source srcSet={darkWordmark} media="(prefers-color-scheme: dark)" />
        <img className={styles.wordmark} src={lightWordmark} alt="MIVY" />
      </picture>
      <span className={styles.subtitle}>Quant Research Platform v0.1.0</span>
    </div>
  );
}
