import { useTranslation } from 'react-i18next';
import languageSwitchIcon from '../../assets/icons/language-switch.svg';
import {
  APP_LANGUAGES,
  changeAppLanguage,
  resolveAppLanguage,
  type AppLanguage,
} from '../../i18n';
import { I18N_NAMESPACES } from '../../i18n/namespaces';
import { AppIcon } from '../icons/AppIcon';
import styles from './LanguageSwitcher.module.css';

export function LanguageSwitcher() {
  const { t, i18n } = useTranslation(I18N_NAMESPACES.common);
  const currentLanguage = resolveAppLanguage(i18n.resolvedLanguage);
  const isChinese = currentLanguage === APP_LANGUAGES.simplifiedChinese;
  const nextLanguage: AppLanguage = isChinese
    ? APP_LANGUAGES.english
    : APP_LANGUAGES.simplifiedChinese;
  const label = isChinese
    ? t('language.switchToEnglish')
    : t('language.switchToChinese');

  return (
    <button
      className={styles.button}
      type="button"
      aria-label={label}
      title={label}
      onClick={() => void changeAppLanguage(nextLanguage)}
    >
      <AppIcon src={languageSwitchIcon} size={18} />
    </button>
  );
}
