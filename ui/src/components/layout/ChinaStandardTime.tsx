import { useEffect, useMemo, useState } from 'react';

interface ChinaStandardTimeProps {
  compact?: boolean;
  className?: string;
}

const fullTimeFormatter = new Intl.DateTimeFormat('sv-SE', {
  timeZone: 'Asia/Shanghai',
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hourCycle: 'h23',
});

const compactTimeFormatter = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'Asia/Shanghai',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hourCycle: 'h23',
});

export function ChinaStandardTime({
  compact = false,
  className,
}: ChinaStandardTimeProps) {
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const intervalId = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(intervalId);
  }, []);

  const formattedTime = useMemo(
    () => (compact ? compactTimeFormatter : fullTimeFormatter).format(now),
    [compact, now],
  );

  return (
    <time className={className} dateTime={now.toISOString()}>
      {compact ? formattedTime : `CN · ${formattedTime}`}
    </time>
  );
}
