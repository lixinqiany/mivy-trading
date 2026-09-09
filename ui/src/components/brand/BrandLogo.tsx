import { useTranslation } from 'react-i18next';
import darkWordmark from '../../assets/brand/mivy-wordmark-dark.svg';
import lightWordmark from '../../assets/brand/mivy-wordmark-light.svg';
import { I18N_NAMESPACES } from '../../i18n/namespaces';
import styles from './BrandLogo.module.css';

interface BrandLogoProps {
  collapsed?: boolean;
  compact?: boolean;
}

export function BrandLogo({
  collapsed = false,
  compact = false,
}: BrandLogoProps) {
  const { t } = useTranslation(I18N_NAMESPACES.common);

  return (
    <div
      className={styles.brand}
      data-collapsed={collapsed}
      data-compact={compact}
      aria-label={t('brand.accessibleName')}
    >
      <picture className={styles.picture}>
        <source srcSet={darkWordmark} media="(prefers-color-scheme: dark)" />
        <img
          className={styles.wordmark}
          src={lightWordmark}
          alt={t('brand.name')}
        />
      </picture>
      <span className={styles.subtitle}>{t('brand.subtitle')}</span>
    </div>
  );
}
