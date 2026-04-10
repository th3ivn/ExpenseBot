import { useState, useEffect } from 'react';
import { api } from '../../api/client';
import type { Category } from '../../types';

export function CategoryManager() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [name, setName] = useState('');
  const [emoji, setEmoji] = useState('');
  const [color, setColor] = useState('#00D4AA');
  const [group, setGroup] = useState('');
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    api.categories
      .list()
      .then(setCategories)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleAdd = async () => {
    if (!name || !emoji) return;
    setSaving(true);
    try {
      await api.categories.create({ name, emoji, color, group_name: group || undefined });
      setName(''); setEmoji(''); setGroup(''); setShowAdd(false);
      load();
    } catch (e) { /* ignore */ }
    finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    await api.categories.delete(id).catch(() => {});
    setCategories((prev) => prev.filter((c) => c.id !== id));
  };

  if (loading) return <div className="h-32 animate-pulse bg-bg-secondary rounded-xl m-4" />;

  return (
    <div className="px-4 pb-8">
      <div className="space-y-1 mb-4">
        {categories.map((c) => (
          <div key={c.id} className="flex items-center gap-3 px-3 py-3 bg-bg-secondary rounded-xl">
            <span className="text-2xl">{c.emoji}</span>
            <div className="flex-1">
              <p className="text-text-primary text-sm font-medium">{c.name}</p>
              {c.group_name && <p className="text-text-secondary text-xs">{c.group_name}</p>}
            </div>
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: c.color }} />
            <button
              onClick={() => handleDelete(c.id)}
              className="text-accent-red text-sm ml-2"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      {showAdd ? (
        <div className="bg-bg-secondary rounded-xl p-4 space-y-3">
          <div className="grid grid-cols-2 gap-2">
            <input
              placeholder="Emoji"
              value={emoji}
              onChange={(e) => setEmoji(e.target.value)}
              className="bg-bg-tertiary text-text-primary rounded-lg px-3 py-2 text-sm outline-none"
            />
            <input
              placeholder="Назва"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="bg-bg-tertiary text-text-primary rounded-lg px-3 py-2 text-sm outline-none"
            />
          </div>
          <input
            placeholder="Група (необов'язково)"
            value={group}
            onChange={(e) => setGroup(e.target.value)}
            className="w-full bg-bg-tertiary text-text-primary rounded-lg px-3 py-2 text-sm outline-none"
          />
          <div className="flex items-center gap-2">
            <label className="text-text-secondary text-xs">Колір:</label>
            <input type="color" value={color} onChange={(e) => setColor(e.target.value)} className="w-8 h-8 rounded cursor-pointer" />
          </div>
          <div className="flex gap-2">
            <button onClick={() => setShowAdd(false)} className="flex-1 py-2 rounded-lg bg-bg-tertiary text-text-secondary text-sm">Скасувати</button>
            <button onClick={handleAdd} disabled={saving} className="flex-1 py-2 rounded-lg bg-accent-cyan text-bg-primary font-medium text-sm disabled:opacity-50">
              {saving ? '...' : 'Додати'}
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setShowAdd(true)}
          className="w-full py-3 rounded-xl border border-dashed border-bg-tertiary text-text-secondary text-sm"
        >
          + Додати категорію
        </button>
      )}
    </div>
  );
}
