import { Routes, Route, useNavigate } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';
import { Settings } from '../components/settings/Settings';
import { CategoryManager } from '../components/settings/CategoryManager';
import { AccountManager } from '../components/settings/AccountManager';
import { BudgetManager } from '../components/settings/BudgetManager';
import { TagManager } from '../components/settings/TagManager';
import { RecurringManager } from '../components/settings/RecurringManager';

const SUB_TITLES: Record<string, string> = {
  '/settings/categories': 'Категорії',
  '/settings/accounts':   'Рахунки',
  '/settings/budget':     'Бюджет',
  '/settings/tags':       'Теги',
  '/settings/recurring':  'Регулярні транзакції',
};

function SubPageHeader({ path }: { path: string }) {
  const navigate = useNavigate();
  return (
    <div
      className="flex items-center gap-3 px-4 pb-3 bg-bg-primary flex-shrink-0"
      style={{ paddingTop: 'max(12px, env(safe-area-inset-top))' }}
    >
      <button
        type="button"
        onClick={() => navigate('/settings')}
        className="w-9 h-9 rounded-full bg-bg-secondary flex items-center justify-center active:opacity-70 transition-opacity"
      >
        <ChevronLeft size={20} className="text-text-primary" />
      </button>
      <h2 className="text-text-primary text-lg font-bold">{SUB_TITLES[path] ?? ''}</h2>
    </div>
  );
}

export function SettingsPage() {
  return (
    <div className="flex flex-col bg-bg-primary" style={{ height: '100dvh' }}>
      <Routes>
        <Route
          index
          element={
            <>
              <div
                className="px-4 pb-3 flex-shrink-0"
                style={{ paddingTop: 'max(12px, env(safe-area-inset-top))' }}
              >
                <h1 className="text-text-primary text-xl font-bold text-center">Налаштування</h1>
              </div>
              <div className="flex-1 overflow-y-auto">
                <Settings />
              </div>
            </>
          }
        />
        <Route
          path="categories"
          element={
            <div className="flex flex-col h-full">
              <SubPageHeader path="/settings/categories" />
              <div className="flex-1 overflow-y-auto"><CategoryManager /></div>
            </div>
          }
        />
        <Route
          path="accounts"
          element={
            <div className="flex flex-col h-full">
              <SubPageHeader path="/settings/accounts" />
              <div className="flex-1 overflow-y-auto"><AccountManager /></div>
            </div>
          }
        />
        <Route
          path="budget"
          element={
            <div className="flex flex-col h-full">
              <SubPageHeader path="/settings/budget" />
              <div className="flex-1 overflow-y-auto"><BudgetManager /></div>
            </div>
          }
        />
        <Route
          path="tags"
          element={
            <div className="flex flex-col h-full">
              <SubPageHeader path="/settings/tags" />
              <div className="flex-1 overflow-y-auto"><TagManager /></div>
            </div>
          }
        />
        <Route
          path="recurring"
          element={
            <div className="flex flex-col h-full">
              <SubPageHeader path="/settings/recurring" />
              <div className="flex-1 overflow-y-auto"><RecurringManager /></div>
            </div>
          }
        />
      </Routes>
    </div>
  );
}
