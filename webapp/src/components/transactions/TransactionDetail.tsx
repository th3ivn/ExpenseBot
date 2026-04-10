import { BottomSheet } from '../ui/BottomSheet';
import { formatCurrency, formatDateTime } from '../../utils/format';
import type { Transaction } from '../../types';

interface TransactionDetailProps {
  transaction: Transaction | null;
  onClose: () => void;
  onDelete: (id: number) => void;
}

const TYPE_COLORS = {
  expense: 'text-accent-red',
  income: 'text-accent-green',
  transfer: 'text-accent-blue',
};
const TYPE_LABELS = { expense: 'Витрата', income: 'Дохід', transfer: 'Переказ' };

export function TransactionDetail({ transaction, onClose, onDelete }: TransactionDetailProps) {
  if (!transaction) return null;

  const handleDelete = () => {
    onDelete(transaction.id);
    onClose();
  };

  return (
    <BottomSheet isOpen={!!transaction} onClose={onClose} title="Деталі транзакції">
      <div className="px-4 py-4 flex flex-col gap-4">
        <div className="flex flex-col items-center gap-2 py-4">
          <div className="w-16 h-16 rounded-full bg-bg-tertiary flex items-center justify-center text-4xl">
            {transaction.category?.emoji ?? '💸'}
          </div>
          <span className={`text-2xl font-bold ${TYPE_COLORS[transaction.type]}`}>
            {formatCurrency(transaction.amount)}
          </span>
          <span className="text-text-secondary text-sm">{TYPE_LABELS[transaction.type]}</span>
        </div>

        <div className="bg-bg-tertiary rounded-xl divide-y divide-bg-secondary">
          <Row label="Категорія" value={transaction.category?.name ?? '—'} />
          <Row label="Дата" value={formatDateTime(transaction.date)} />
          {transaction.description && <Row label="Опис" value={transaction.description} />}
          {transaction.merchant && <Row label="Продавець" value={transaction.merchant} />}
          {transaction.account && <Row label="Рахунок" value={`${transaction.account.emoji} ${transaction.account.name}`} />}
          {transaction.to_account && <Row label="На рахунок" value={`${transaction.to_account.emoji} ${transaction.to_account.name}`} />}
          {transaction.tags.length > 0 && (
            <Row
              label="Теги"
              value={
                <div className="flex flex-wrap gap-1 justify-end">
                  {transaction.tags.map((tag) => (
                    <span
                      key={tag.id}
                      className="px-2 py-0.5 rounded-full text-xs text-white"
                      style={{ backgroundColor: tag.color }}
                    >
                      {tag.name}
                    </span>
                  ))}
                </div>
              }
            />
          )}
        </div>

        <button
          onClick={handleDelete}
          className="w-full py-3 rounded-xl bg-accent-red/10 text-accent-red font-medium text-sm active:bg-accent-red/20 transition-colors"
        >
          Видалити транзакцію
        </button>
      </div>
    </BottomSheet>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between items-center px-4 py-3">
      <span className="text-text-secondary text-sm">{label}</span>
      {typeof value === 'string' ? (
        <span className="text-text-primary text-sm font-medium">{value}</span>
      ) : (
        value
      )}
    </div>
  );
}
