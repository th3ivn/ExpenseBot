import { useNavigate } from 'react-router-dom';
import { useTelegram } from '../../hooks/useTelegram';

export function Settings() {
  const navigate = useNavigate();
  const { user } = useTelegram();

  const sections = [
    {
      title: 'Управління',
      items: [
        { emoji: '📂', label: 'Категорії', path: '/settings/categories' },
        { emoji: '💳', label: 'Рахунки', path: '/settings/accounts' },
        { emoji: '🎯', label: 'Бюджет', path: '/settings/budget' },
        { emoji: '🏷️', label: 'Теги', path: '/settings/tags' },
        { emoji: '🔄', label: 'Регулярні транзакції', path: '/settings/recurring' },
      ],
    },
    {
      title: 'Загальні',
      items: [
        { emoji: '💱', label: 'Валюта: ₴ UAH', path: null },
        { emoji: '📅', label: 'Формат дати', path: null },
      ],
    },
  ];

  return (
    <div className="px-4 pb-8 space-y-6">
      {/* Profile */}
      {user && (
        <div className="flex items-center gap-4 bg-bg-secondary rounded-2xl p-4">
          <div className="w-14 h-14 rounded-full bg-accent-cyan flex items-center justify-center text-2xl font-bold text-bg-primary">
            {user.first_name.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="text-text-primary font-semibold text-base">{user.first_name}</p>
            {user.username && (
              <p className="text-text-secondary text-sm">@{user.username}</p>
            )}
            <p className="text-text-secondary text-xs mt-0.5">ID: {user.id}</p>
          </div>
        </div>
      )}

      {sections.map((section) => (
        <div key={section.title}>
          <p className="text-text-secondary text-xs font-medium uppercase tracking-wide mb-2 px-1">
            {section.title}
          </p>
          <div className="bg-bg-secondary rounded-2xl overflow-hidden divide-y divide-bg-tertiary">
            {section.items.map((item) => (
              <button
                key={item.label}
                onClick={() => item.path && navigate(item.path)}
                disabled={!item.path}
                className="w-full flex items-center gap-3 px-4 py-3.5 text-left active:bg-bg-tertiary transition-colors disabled:opacity-50"
              >
                <span className="text-xl">{item.emoji}</span>
                <span className="flex-1 text-text-primary text-sm">{item.label}</span>
                {item.path && <span className="text-text-secondary text-sm">›</span>}
              </button>
            ))}
          </div>
        </div>
      ))}

      <p className="text-center text-text-secondary text-xs">ExpenseBot v1.0</p>
    </div>
  );
}
