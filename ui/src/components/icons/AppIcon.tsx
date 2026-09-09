import type { ReactNode, SVGProps } from 'react';
import type { NavigationIcon } from '../../config/navigation';

export type AppIconName = NavigationIcon | 'chevron-left';

interface AppIconProps extends Omit<
  SVGProps<SVGSVGElement>,
  'children' | 'name'
> {
  name: AppIconName;
}

const iconPaths: Record<AppIconName, ReactNode> = {
  activity: <path d="M3 12h4l2.4-7 5.2 14 2.4-7h4" />,
  'chevron-left': <path d="m15 18-6-6 6-6" />,
  'database-zap': (
    <>
      <ellipse cx="12" cy="5" rx="8" ry="3" />
      <path d="M4 5v6c0 1.7 3.6 3 8 3h1" />
      <path d="M4 11v6c0 1.7 3.6 3 8 3" />
      <path d="m19 12-3 4h3l-2 4" />
    </>
  ),
  layers: (
    <>
      <path d="m12 2 9 5-9 5-9-5 9-5Z" />
      <path d="m3 12 9 5 9-5" />
      <path d="m3 17 9 5 9-5" />
    </>
  ),
  orbit: (
    <>
      <circle cx="12" cy="12" r="3" />
      <circle cx="19" cy="5" r="2" />
      <circle cx="5" cy="19" r="2" />
      <path d="M10.4 21.9A10 10 0 0 0 20.3 6" />
      <path d="M13.6 2.1A10 10 0 0 0 3.7 18" />
    </>
  ),
};

export function AppIcon({ name, ...props }: AppIconProps) {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      {iconPaths[name]}
    </svg>
  );
}
