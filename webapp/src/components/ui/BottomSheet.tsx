import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';

interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  fullHeight?: boolean;
}

export function BottomSheet({ isOpen, onClose, title, children, fullHeight }: BottomSheetProps) {
  const sheetRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: TouchEvent) => {
      if (sheetRef.current && !sheetRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    document.addEventListener('touchstart', handler);
    return () => document.removeEventListener('touchstart', handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end">
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      <div
        ref={sheetRef}
        className={`relative w-full bg-bg-secondary rounded-t-2xl overflow-hidden flex flex-col ${
          fullHeight ? 'h-[92vh]' : 'max-h-[92vh]'
        }`}
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-bg-tertiary">
          {title && <h2 className="text-text-primary font-semibold text-base">{title}</h2>}
          <button
            onClick={onClose}
            className="ml-auto w-7 h-7 rounded-full bg-bg-tertiary flex items-center justify-center text-text-secondary text-sm"
          >
            ✕
          </button>
        </div>
        <div className="overflow-y-auto flex-1">{children}</div>
      </div>
    </div>
  );
}
