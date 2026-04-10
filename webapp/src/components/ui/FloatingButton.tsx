interface FloatingButtonProps {
  onClick: () => void;
  label?: string;
}

export function FloatingButton({ onClick, label = '+ Додати' }: FloatingButtonProps) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-24 right-4 z-40 bg-accent-cyan text-bg-primary font-semibold px-5 py-3 rounded-full shadow-lg active:scale-95 transition-transform text-sm"
    >
      {label}
    </button>
  );
}
