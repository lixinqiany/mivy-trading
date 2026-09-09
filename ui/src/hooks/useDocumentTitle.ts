import { useEffect } from 'react';

export function useDocumentTitle(pageTitle: string) {
  useEffect(() => {
    document.title = `${pageTitle} · MIVY Quant Data Hub`;
  }, [pageTitle]);
}
