export const common = {
  brand: {
    accessibleName: 'MIVY — Quant Research Platform v0.1.0',
    name: 'MIVY',
    subtitle: 'Quant Research Platform v0.1.0',
  },
  document: {
    description:
      'MIVY Quant Research Platform — quantitative data research workspace.',
    pageTitle: '{{pageTitle}} · MIVY Quant Data Hub',
  },
  developmentPlaceholder: {
    inProgress: {
      label: 'In development',
      title: 'This feature is taking shape',
      description:
        'We are building and refining this part of the workspace. It will be available in a future update.',
    },
    planned: {
      label: 'Planned',
      title: 'This feature is on the roadmap',
      description:
        'This area has been reserved for a future capability and is not available yet.',
    },
  },
  language: {
    switchToChinese: 'Switch to Chinese',
    switchToEnglish: 'Switch to English',
  },
  status: {
    dataPlaneOnline: 'Data Plane Online',
  },
  time: {
    chinaStandardTime: 'China Standard Time',
    full: 'CN · {{time}}',
    region: 'CN',
  },
} as const;
