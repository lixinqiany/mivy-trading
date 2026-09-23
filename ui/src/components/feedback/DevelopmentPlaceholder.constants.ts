export const DEVELOPMENT_PLACEHOLDER_SIZES = {
  page: 'page',
  section: 'section',
} as const;

export type DevelopmentPlaceholderSize =
  (typeof DEVELOPMENT_PLACEHOLDER_SIZES)[keyof typeof DEVELOPMENT_PLACEHOLDER_SIZES];

export const DEVELOPMENT_STATUSES = {
  planned: 'planned',
  inProgress: 'inProgress',
} as const;

export type DevelopmentStatus =
  (typeof DEVELOPMENT_STATUSES)[keyof typeof DEVELOPMENT_STATUSES];
