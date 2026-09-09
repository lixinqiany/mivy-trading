import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { I18N_NAMESPACES } from '../i18n/namespaces';

export function useDocumentTitle(pageTitle: string) {
  const { t } = useTranslation(I18N_NAMESPACES.common);
  const documentTitle = t('document.pageTitle', { pageTitle });
  const documentDescription = t('document.description');

  useEffect(() => {
    document.title = documentTitle;
    document
      .querySelector('meta[name="description"]')
      ?.setAttribute('content', documentDescription);
  }, [documentDescription, documentTitle]);
}
