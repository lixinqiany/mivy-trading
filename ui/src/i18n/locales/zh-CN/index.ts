import type { LocaleShape } from '../localeShape';
import type { en } from '../en';
import { common } from './common';
import { dataCrawling } from './dataCrawling';
import { navigation } from './navigation';
import { securityPool } from './securityPool';
import { taskCenter } from './taskCenter';
import { watchlists } from './watchlists';

export const zhCN = {
  common,
  navigation,
  securityPool,
  watchlists,
  dataCrawling,
  taskCenter,
} as const satisfies LocaleShape<typeof en>;
