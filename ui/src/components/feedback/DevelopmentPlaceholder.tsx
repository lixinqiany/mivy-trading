import { useId, type HTMLAttributes, type ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { I18N_NAMESPACES } from '../../i18n/namespaces';
import { AppIcon } from '../icons/AppIcon';
import {
  DEVELOPMENT_PLACEHOLDER_SIZES,
  DEVELOPMENT_STATUSES,
  type DevelopmentPlaceholderSize,
  type DevelopmentStatus,
} from './DevelopmentPlaceholder.constants';
import styles from './DevelopmentPlaceholder.module.css';

const PLACEHOLDER_ICON_VIEW_BOX = '0 0 32 32';

export interface DevelopmentPlaceholderProps extends Omit<
  HTMLAttributes<HTMLElement>,
  'title'
> {
  title?: ReactNode;
  description?: ReactNode;
  status?: DevelopmentStatus;
  size?: DevelopmentPlaceholderSize;
}

export function DevelopmentPlaceholder({
  title,
  description,
  status = DEVELOPMENT_STATUSES.inProgress,
  size = DEVELOPMENT_PLACEHOLDER_SIZES.section,
  className,
  'aria-labelledby': ariaLabelledBy,
  'aria-describedby': ariaDescribedBy,
  ...sectionProps
}: DevelopmentPlaceholderProps) {
  const { t } = useTranslation(I18N_NAMESPACES.common);
  const generatedId = useId();
  const titleId = `${generatedId}-title`;
  const descriptionId = `${generatedId}-description`;
  const translationKey = `developmentPlaceholder.${status}` as const;
  const resolvedTitle = title ?? t(`${translationKey}.title`);
  const resolvedDescription = description ?? t(`${translationKey}.description`);
  const mergedClassName = `${styles.placeholder}${className ? ` ${className}` : ''}`;

  return (
    <section
      className={mergedClassName}
      data-size={size}
      data-status={status}
      aria-labelledby={ariaLabelledBy ?? titleId}
      aria-describedby={ariaDescribedBy ?? descriptionId}
      {...sectionProps}
    >
      <div className={styles.card}>
        <div className={styles.visual} aria-hidden="true">
          <span className={styles.orbit} />
          <span className={styles.iconFrame}>
            <AppIcon size={32} viewBox={PLACEHOLDER_ICON_VIEW_BOX}>
              <path d="M8 10.5V8h2.5M21.5 8H24v2.5M24 21.5V24h-2.5M10.5 24H8v-2.5" />
              <path d="M11.5 12.5h9M11.5 16h6M11.5 19.5h9" />
            </AppIcon>
          </span>
          <span className={styles.sparkPrimary} />
          <span className={styles.sparkSecondary} />
        </div>

        <span className={styles.status}>
          <span className={styles.statusDot} />
          {t(`${translationKey}.label`)}
        </span>
        <h2 className={styles.title} id={titleId}>
          {resolvedTitle}
        </h2>
        <p className={styles.description} id={descriptionId}>
          {resolvedDescription}
        </p>
      </div>
    </section>
  );
}
