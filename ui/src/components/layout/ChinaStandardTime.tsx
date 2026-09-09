import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { I18N_NAMESPACES } from '../../i18n/namespaces';

interface ChinaStandardTimeProps {
  compact?: boolean;
  className?: string;
}

export function ChinaStandardTime({
  compact = false,
  className,
}: ChinaStandardTimeProps) {
  const { t, i18n } = useTranslation(I18N_NAMESPACES.common);
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const intervalId = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(intervalId);
  }, []);

  const formatter = useMemo(
    () =>
      new Intl.DateTimeFormat(i18n.resolvedLanguage, {
        timeZone: 'Asia/Shanghai',
        ...(compact
          ? {}
          : {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
            }),
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hourCycle: 'h23',
      }),
    [compact, i18n.resolvedLanguage],
  );
  const formattedTime = formatter.format(now);

  return (
    <time className={className} dateTime={now.toISOString()}>
      {compact ? formattedTime : t('time.full', { time: formattedTime })}
    </time>
  );
}
