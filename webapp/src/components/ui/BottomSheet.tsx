import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import { X } from 'lucide-react';

interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  fullHeight?: boolean;
  /** Pass true when the child renders its own header/close controls */
  noHeader?: boolean;
}

export function BottomSheet({ isOpen, onClose, title, children, fullHeight, noHeader }: BottomSheetProps) {
  const sheetRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: TouchEvent) => {
      if (sheetRef.current && !sheetRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    document.addEventListener('touchstart', handler, { passive: true });
    return () => document.removeEventListener('touchstart', handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div
        ref={sheetRef}
        className={`relative w-full bg-bg-secondary rounded-t-3xl flex flex-col ${
          fullHeight ? 'h-[92vh]' : 'max-h-[92vh]'
        }`}
        style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
      >
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-1 flex-shrink-0">
          <div className="w-10 h-1 rounded-full bg-bg-tertiary" />
        </div>

        {/* Header — omitted when child provides its own */}
        {!noHeader && (
          <div className="flex items-center justify-between px-4 py-2 flex-shrink-0">
            {title ? (
              <h2 className="text-text-primary font-semibold text-base flex-1 text-center pr-8">{title}</h2>
            ) : (
              <div className="flex-1" />
            )}
            <button
              type="button"
              onClick={onClose}
              className="w-8 h-8 rounded-full bg-bg-tertiary flex items-center justify-center active:opacity-70 transition-opacity absolute right-4"
            >
              <X size={16} className="text-text-primary" />
            </button>
          </div>
        )}

        <div className="overflow-y-auto flex-1">{children}</div>
      </div>
    </div>
  );
}
