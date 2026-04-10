export function formatCurrency(amount: number): string {
  const abs = Math.abs(amount);
  const formatted = abs.toLocaleString('uk-UA', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return `${formatted} ₴`;
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

export function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr);
  const datePart = date.toLocaleDateString('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
  const timePart = date.toLocaleTimeString('uk-UA', {
    hour: '2-digit',
    minute: '2-digit',
  });
  return `${datePart} ${timePart}`;
}

const MONTH_SHORT: Record<number, string> = {
  0: 'січ.',
  1: 'лют.',
  2: 'бер.',
  3: 'кві.',
  4: 'тра.',
  5: 'чер.',
  6: 'лип.',
  7: 'сер.',
  8: 'вер.',
  9: 'жов.',
  10: 'лис.',
  11: 'гру.',
};

export function formatPeriod(start: string, end: string): string {
  const s = new Date(start);
  const e = new Date(end);
  const sm = MONTH_SHORT[s.getMonth()];
  const em = MONTH_SHORT[e.getMonth()];
  const sd = s.getDate();
  const ed = e.getDate();
  if (s.getMonth() === e.getMonth() && s.getFullYear() === e.getFullYear()) {
    return `${sm} ${sd} – ${ed}`;
  }
  return `${sm} ${sd} – ${em} ${ed}`;
}

export function getSavingsLevel(rate: number): { label: string; color: string } {
  if (rate >= 30) return { label: 'Відмінно', color: '#34C759' };
  if (rate >= 20) return { label: 'Добре', color: '#00D4AA' };
  if (rate >= 10) return { label: 'Непогано', color: '#007AFF' };
  if (rate >= 0) return { label: 'Низька', color: '#FF9500' };
  return { label: 'Дефіцит', color: '#FF3B30' };
}
