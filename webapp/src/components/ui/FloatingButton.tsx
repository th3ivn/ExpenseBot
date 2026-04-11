interface FloatingButtonProps {
  onClick: () => void;
  label?: string;
}

export function FloatingButton({ onClick, label = 'Додати' }: FloatingButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="fixed z-40 bg-bg-elevated text-text-primary font-semibold px-6 py-3.5 rounded-full shadow-xl active:scale-95 transition-transform flex items-center gap-2 border border-white/10"
      style={{
        bottom: 'max(24px, env(safe-area-inset-bottom))',
        right: '16px',
      }}
    >
      <span>{label}</span>
      <span className="text-accent-cyan font-bold text-lg leading-none">+</span>
    </button>
  );
}
