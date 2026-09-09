import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { en } from './locales/en';
import { zhCN } from './locales/zh-CN';
import { ALL_NAMESPACES, I18N_NAMESPACES } from './namespaces';

export const APP_LANGUAGES = {
  english: 'en',
  simplifiedChinese: 'zh-CN',
} as const;

export type AppLanguage = (typeof APP_LANGUAGES)[keyof typeof APP_LANGUAGES];

const LANGUAGE_STORAGE_KEY = 'mivy.language';

function normalizeLanguage(language?: string | null): AppLanguage | null {
  if (!language) return null;

  const normalizedLanguage = language.toLowerCase();
  if (normalizedLanguage.startsWith('zh')) {
    return APP_LANGUAGES.simplifiedChinese;
  }
  if (normalizedLanguage.startsWith('en')) {
    return APP_LANGUAGES.english;
  }

  return null;
}

function readStoredLanguage() {
  try {
    return normalizeLanguage(window.localStorage.getItem(LANGUAGE_STORAGE_KEY));
  } catch {
    return null;
  }
}

function detectInitialLanguage(): AppLanguage {
  const storedLanguage = readStoredLanguage();
  if (storedLanguage) return storedLanguage;

  for (const browserLanguage of window.navigator.languages) {
    const supportedLanguage = normalizeLanguage(browserLanguage);
    if (supportedLanguage) return supportedLanguage;
  }

  return APP_LANGUAGES.simplifiedChinese;
}

function syncDocumentLanguage(language: string) {
  const normalizedLanguage =
    normalizeLanguage(language) ?? APP_LANGUAGES.simplifiedChinese;

  document.documentElement.lang = normalizedLanguage;

  try {
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, normalizedLanguage);
  } catch {
    // Language persistence is optional when storage is unavailable.
  }
}

i18n.on('languageChanged', syncDocumentLanguage);

void i18n.use(initReactI18next).init({
  resources: {
    [APP_LANGUAGES.english]: en,
    [APP_LANGUAGES.simplifiedChinese]: zhCN,
  },
  lng: detectInitialLanguage(),
  fallbackLng: APP_LANGUAGES.simplifiedChinese,
  supportedLngs: Object.values(APP_LANGUAGES),
  ns: ALL_NAMESPACES,
  defaultNS: I18N_NAMESPACES.common,
  interpolation: {
    escapeValue: false,
  },
  react: {
    useSuspense: false,
  },
});

export function resolveAppLanguage(language?: string): AppLanguage {
  return normalizeLanguage(language) ?? APP_LANGUAGES.simplifiedChinese;
}

export function changeAppLanguage(language: AppLanguage) {
  return i18n.changeLanguage(language);
}

export { i18n };
