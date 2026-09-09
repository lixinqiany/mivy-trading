export const common = {
  brand: {
    accessibleName: 'MIVY — Quant Research Platform v0.1.0',
    name: 'MIVY',
    subtitle: 'Quant Research Platform v0.1.0',
  },
  document: {
    description: 'MIVY 量化研究平台——面向量化数据研究的工作空间。',
    pageTitle: '{{pageTitle}} · MIVY Quant Data Hub',
  },
  developmentPlaceholder: {
    inProgress: {
      label: '开发中',
      title: '功能正在建设中',
      description: '我们正在开发和完善这部分功能，它将在后续版本中与你见面。',
    },
    planned: {
      label: '待开发',
      title: '功能暂未开放',
      description: '这里已为后续功能预留位置，相关能力将在未来版本中提供。',
    },
  },
  language: {
    switchToChinese: '切换为中文',
    switchToEnglish: '切换为英文',
  },
  status: {
    dataPlaneOnline: 'Data Plane Online',
  },
  time: {
    chinaStandardTime: '中国标准时间',
    full: 'CN · {{time}}',
    region: 'CN',
  },
} as const;
