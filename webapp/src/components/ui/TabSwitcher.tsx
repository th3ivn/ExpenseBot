interface Tab {
  id: string;
  label: string;
}

interface TabSwitcherProps {
  tabs: Tab[];
  active: string;
  onChange: (id: string) => void;
  className?: string;
}

export function TabSwitcher({ tabs, active, onChange, className = '' }: TabSwitcherProps) {
  return (
    <div className={`flex bg-bg-tertiary rounded-xl p-1 ${className}`}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`flex-1 py-1.5 px-3 rounded-lg text-sm font-medium transition-all ${
            active === tab.id
              ? 'bg-bg-secondary text-text-primary shadow-sm'
              : 'text-text-secondary'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
