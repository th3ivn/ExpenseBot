import { X, Edit2, Calendar, AlignLeft, Tag, CreditCard, Trash2 } from 'lucide-react';
import { BottomSheet } from '../ui/BottomSheet';
import { formatCurrency, formatDateTime } from '../../utils/format';
import type { Transaction } from '../../types';

interface TransactionDetailProps {
  transaction: Transaction | null;
  onClose: () => void;
  onDelete: (id: number) => void;
  onEdit?: (t: Transaction) => void;
}

const TYPE_COLORS = {
  expense: 'text-accent-red',
  income: 'text-accent-green',
  transfer: 'text-accent-blue',
};
const TYPE_LABELS = { expense: 'Витрата', income: 'Дохід', transfer: 'Переказ' };
const TYPE_SIGNS = { expense: '−', income: '+', transfer: '' };

export function TransactionDetail({ transaction, onClose, onDelete, onEdit }: TransactionDetailProps) {
  if (!transaction) return null;

  const handleDelete = () => {
    onDelete(transaction.id);
    onClose();
  };

  return (
    <BottomSheet isOpen={!!transaction} onClose={onClose} noHeader>
      {/* Custom header with X + Edit */}
      <div className="flex items-center px-4 pb-2">
        <button
          type="button"
          onClick={onClose}
          className="w-8 h-8 rounded-full bg-bg-tertiary flex items-center justify-center active:opacity-70 transition-opacity"
        >
          <X size={16} className="text-text-primary" />
        </button>
        <h2 className="flex-1 text-text-primary font-semibold text-base text-center">
          Деталі транзакції
        </h2>
        {onEdit ? (
          <button
            type="button"
            onClick={() => onEdit(transaction)}
            className="h-8 px-3 rounded-full bg-bg-tertiary flex items-center gap-1.5 active:opacity-70 transition-opacity"
          >
            <Edit2 size={13} className="text-text-secondary" />
            <span className="text-text-secondary text-xs font-medium">Редагувати</span>
          </button>
        ) : (
          <div className="w-8" />
        )}
      </div>

      <div className="px-4 pb-6 flex flex-col gap-4">
        {/* Hero */}
        <div className="flex flex-col items-center gap-2 py-3">
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center text-4xl"
            style={{
              backgroundColor: transaction.category?.color
                ? `${transaction.category.color}33`
                : '#252B3B',
            }}
          >
            {transaction.category?.emoji ?? '💸'}
          </div>
          <span className={`text-3xl font-bold ${TYPE_COLORS[transaction.type]}`}>
            {TYPE_SIGNS[transaction.type]}{formatCurrency(transaction.amount)}
          </span>
          <div className="flex flex-col items-center gap-0.5">
            <span className="text-text-primary font-semibold text-base">
              {transaction.category?.name ?? TYPE_LABELS[transaction.type]}
            </span>
            <span className="text-text-secondary text-sm">{TYPE_LABELS[transaction.type]}</span>
          </div>
        </div>

        {/* Detail rows */}
        <div className="bg-bg-tertiary rounded-2xl overflow-hidden">
          <DetailRow icon={<Calendar size={16} />} label="Дата" value={formatDateTime(transaction.date)} />
          {transaction.description && (
            <DetailRow icon={<AlignLeft size={16} />} label="Опис" value={transaction.description} />
          )}
          {transaction.merchant && (
            <DetailRow icon={<CreditCard size={16} />} label="Продавець" value={transaction.merchant} />
          )}
          {transaction.tags.length > 0 && (
            <DetailRow
              icon={<Tag size={16} />}
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
          {transaction.account && (
            <DetailRow
              icon={<CreditCard size={16} />}
              label="Рахунок"
              value={`${transaction.account.emoji} ${transaction.account.name}`}
            />
          )}
          {transaction.to_account && (
            <DetailRow
              icon={<CreditCard size={16} />}
              label="На рахунок"
              value={`${transaction.to_account.emoji} ${transaction.to_account.name}`}
            />
          )}
        </div>

        {/* Delete */}
        <button
          type="button"
          onClick={handleDelete}
          className="w-full py-3.5 rounded-2xl bg-accent-red/10 flex items-center justify-center gap-2 active:bg-accent-red/20 transition-colors"
        >
          <Trash2 size={16} className="text-accent-red" />
          <span className="text-accent-red font-medium text-sm">Видалити транзакцію</span>
        </button>
      </div>
    </BottomSheet>
  );
}

function DetailRow({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="flex justify-between items-center px-4 py-3.5 border-b border-bg-elevated last:border-0">
      <div className="flex items-center gap-2.5">
        <span className="text-text-secondary">{icon}</span>
        <span className="text-text-secondary text-sm">{label}</span>
      </div>
      {typeof value === 'string' ? (
        <span className="text-text-primary text-sm font-medium">{value}</span>
      ) : (
        value
      )}
    </div>
  );
}
