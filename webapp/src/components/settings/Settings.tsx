import { useNavigate } from 'react-router-dom';
import {
  User, FolderOpen, CreditCard, Wallet, Tag, RefreshCw,
  Globe, Calendar, Hash, Moon, Bell, ChevronRight,
} from 'lucide-react';
import { useTelegram } from '../../hooks/useTelegram';

type SectionItem = {
  icon: React.ReactNode;
  label: string;
  value?: string;
  path: string | null;
};

type Section = {
  title: string;
  items: SectionItem[];
};

export function Settings() {
  const navigate = useNavigate();
  const { user } = useTelegram();

  const sections: Section[] = [
    {
      title: 'Рахунок',
      items: [
        {
          icon: <User size={18} />,
          label: user?.first_name ?? 'Профіль',
          value: user?.username ? `@${user.username}` : undefined,
          path: null,
        },
      ],
    },
    {
      title: 'Функції',
      items: [
        { icon: <Wallet size={18} />,   label: 'Управління бюджетом',       path: '/settings/budget' },
        { icon: <FolderOpen size={18} />, label: 'Управління категоріями',   path: '/settings/categories' },
        { icon: <CreditCard size={18} />, label: 'Управління рахунками',     path: '/settings/accounts' },
        { icon: <RefreshCw size={18} />,  label: 'Управління регулярними',   path: '/settings/recurring' },
        { icon: <Tag size={18} />,        label: 'Управління тегами',        path: '/settings/tags' },
      ],
    },
    {
      title: 'Налаштування',
      items: [
        { icon: <Globe size={18} />,    label: 'Валюта',                     value: 'Гривня (₴)', path: null },
        { icon: <Calendar size={18} />, label: 'Формат дати',                value: 'ДД/ММ/РРРР', path: null },
        { icon: <Hash size={18} />,     label: 'Формат чисел',               value: '1 234,56',   path: null },
        { icon: <Moon size={18} />,     label: 'Тема',                       value: 'Темна',      path: null },
        { icon: <Bell size={18} />,     label: 'Сповіщення',                                      path: null },
      ],
    },
  ];

  return (
    <div className="px-4 pb-10 space-y-6">
      {sections.map((section) => (
        <div key={section.title}>
          <p className="text-text-secondary text-xs font-medium mb-2 px-1">{section.title}</p>
          <div className="bg-bg-secondary rounded-3xl overflow-hidden">
            {section.items.map((item, idx) => (
              <button
                key={item.label}
                type="button"
                onClick={() => item.path && navigate(item.path)}
                disabled={!item.path}
                className={`w-full flex items-center gap-3.5 px-4 py-4 text-left transition-colors ${
                  item.path ? 'active:bg-bg-elevated' : 'cursor-default'
                } ${idx < section.items.length - 1 ? 'border-b border-bg-tertiary' : ''}`}
              >
                <span className="text-text-secondary flex-shrink-0">{item.icon}</span>
                <span className="flex-1 text-text-primary text-sm">{item.label}</span>
                {item.value && (
                  <span className="text-text-secondary text-sm">{item.value}</span>
                )}
                {item.path && (
                  <ChevronRight size={16} className="text-bg-tertiary flex-shrink-0" />
                )}
              </button>
            ))}
          </div>
        </div>
      ))}

      <p className="text-center text-text-secondary text-xs pt-2">ExpenseBot v1.0</p>
    </div>
  );
}
