import type { CSSProperties, HTMLAttributes, ReactNode } from 'react';
import styles from './AppIcon.module.css';

type IconSize = number | string;

interface AppIconBaseProps extends Omit<
  HTMLAttributes<HTMLSpanElement>,
  'children' | 'color'
> {
  size?: IconSize;
  color?: CSSProperties['color'];
  label?: string;
}

interface FileIconProps {
  src: string;
  children?: never;
  viewBox?: never;
}

interface InlineIconProps {
  src?: never;
  children: ReactNode;
  viewBox?: string;
}

export type AppIconProps = AppIconBaseProps & (FileIconProps | InlineIconProps);

interface AppIconStyle extends CSSProperties {
  '--app-icon-size': string;
  '--app-icon-source'?: string;
}

const DEFAULT_ICON_SIZE = 16;
const DEFAULT_VIEW_BOX = '0 0 24 24';

function toCssSize(size: IconSize) {
  return typeof size === 'number' ? `${size}px` : size;
}

export function AppIcon({
  src,
  children,
  viewBox = DEFAULT_VIEW_BOX,
  size = DEFAULT_ICON_SIZE,
  color,
  label,
  className,
  style,
  ...spanProps
}: AppIconProps) {
  const iconStyle: AppIconStyle = {
    ...style,
    '--app-icon-size': toCssSize(size),
    color,
  };

  if (src) {
    iconStyle['--app-icon-source'] = `url("${src}")`;
  }

  const sourceClassName = src ? ` ${styles.fileSource}` : '';
  const mergedClassName = `${styles.icon}${sourceClassName}${className ? ` ${className}` : ''}`;

  return (
    <span
      className={mergedClassName}
      style={iconStyle}
      role={label ? 'img' : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
      {...spanProps}
    >
      {src ? null : (
        <svg
          className={styles.svg}
          viewBox={viewBox}
          fill="none"
          stroke="currentColor"
          strokeWidth="1.7"
          strokeLinecap="round"
          strokeLinejoin="round"
          focusable="false"
        >
          {children}
        </svg>
      )}
    </span>
  );
}
