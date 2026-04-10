import { Routes, Route, useNavigate } from 'react-router-dom';
import { Settings } from '../components/settings/Settings';
import { CategoryManager } from '../components/settings/CategoryManager';
import { AccountManager } from '../components/settings/AccountManager';
import { BudgetManager } from '../components/settings/BudgetManager';
import { TagManager } from '../components/settings/TagManager';
import { RecurringManager } from '../components/settings/RecurringManager';

const SUB_TITLES: Record<string, string> = {
  '/settings/categories': 'Категорії',
  '/settings/accounts': 'Рахунки',
  '/settings/budget': 'Бюджет',
  '/settings/tags': 'Теги',
  '/settings/recurring': 'Регулярні транзакції',
};

export function SettingsPage() {
  const navigate = useNavigate();

  const SubHeader = ({ path }: { path: string }) => (
    <div className="flex items-center gap-3 px-4 pt-4 pb-2">
      <button
        onClick={() => navigate('/settings')}
        className="w-8 h-8 rounded-full bg-bg-secondary flex items-center justify-center text-text-secondary"
      >
        ‹
      </button>
      <h2 className="text-text-primary font-semibold">{SUB_TITLES[path] ?? ''}</h2>
    </div>
  );

  return (
    <div className="h-full overflow-y-auto">
      <Routes>
        <Route index element={
          <>
            <div className="px-4 pt-4 pb-2">
              <h1 className="text-text-primary text-xl font-bold">Налаштування</h1>
            </div>
            <Settings />
          </>
        } />
        <Route path="categories" element={
          <>
            <SubHeader path="/settings/categories" />
            <CategoryManager />
          </>
        } />
        <Route path="accounts" element={
          <>
            <SubHeader path="/settings/accounts" />
            <AccountManager />
          </>
        } />
        <Route path="budget" element={
          <>
            <SubHeader path="/settings/budget" />
            <BudgetManager />
          </>
        } />
        <Route path="tags" element={
          <>
            <SubHeader path="/settings/tags" />
            <TagManager />
          </>
        } />
        <Route path="recurring" element={
          <>
            <SubHeader path="/settings/recurring" />
            <RecurringManager />
          </>
        } />
      </Routes>
    </div>
  );
}
