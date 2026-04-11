import { useState, useEffect, useCallback } from 'react';
import type { TelegramWebApp } from '../utils/telegram';
import { getTelegramWebApp } from '../utils/telegram';

let initialized = false;

export function useTelegram() {
  const [tg, setTg] = useState<TelegramWebApp | null>(() => getTelegramWebApp());

  useEffect(() => {
    const instance = getTelegramWebApp();
    if (instance && !initialized) {
      initialized = true;
      instance.ready();
      instance.expand();
    }
    setTg(instance);
  }, []);

  const user = tg?.initDataUnsafe?.user ?? null;
  const colorScheme = tg?.colorScheme ?? 'dark';

  const hapticFeedback = useCallback(
    (style: 'light' | 'medium' | 'heavy' = 'light') => {
      tg?.HapticFeedback?.impactOccurred(style);
    },
    [tg],
  );

  const showBackButton = useCallback(
    (onBack: () => void) => {
      tg?.BackButton?.show();
      tg?.BackButton?.onClick(onBack);
    },
    [tg],
  );

  const hideBackButton = useCallback(() => {
    tg?.BackButton?.hide();
  }, [tg]);

  const close = useCallback(() => {
    tg?.close();
  }, [tg]);

  return { tg, user, colorScheme, hapticFeedback, showBackButton, hideBackButton, close };
}
