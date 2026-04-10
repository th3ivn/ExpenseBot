import { useState, useEffect } from 'react';
import { api } from '../../api/client';
import type { Tag } from '../../types';

const PRESET_COLORS = ['#FF3B30', '#FF9500', '#34C759', '#007AFF', '#00D4AA', '#AF52DE', '#FF2D55', '#5AC8FA'];

export function TagManager() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [name, setName] = useState('');
  const [color, setColor] = useState(PRESET_COLORS[0]);
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    api.tags
      .list()
      .then(setTags)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleAdd = async () => {
    if (!name) return;
    setSaving(true);
    try {
      await api.tags.create({ name, color });
      setName(''); setShowAdd(false);
      load();
    } catch (e) { /* ignore */ }
    finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    await api.tags.delete(id).catch(() => {});
    setTags((prev) => prev.filter((t) => t.id !== id));
  };

  if (loading) return <div className="h-32 animate-pulse bg-bg-secondary rounded-xl m-4" />;

  return (
    <div className="px-4 pb-8">
      <div className="flex flex-wrap gap-2 mb-4">
        {tags.map((tag) => (
          <div key={tag.id} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm text-white" style={{ backgroundColor: tag.color }}>
            <span>{tag.name}</span>
            <button onClick={() => handleDelete(tag.id)} className="opacity-70 hover:opacity-100 ml-0.5">✕</button>
          </div>
        ))}
      </div>

      {showAdd ? (
        <div className="bg-bg-secondary rounded-xl p-4 space-y-3">
          <input
            placeholder="Назва тегу"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full bg-bg-tertiary text-text-primary rounded-lg px-3 py-2 text-sm outline-none"
          />
          <div>
            <label className="text-text-secondary text-xs mb-2 block">Колір</label>
            <div className="flex gap-2">
              {PRESET_COLORS.map((c) => (
                <button
                  key={c}
                  onClick={() => setColor(c)}
                  className="w-7 h-7 rounded-full border-2 transition-all"
                  style={{ backgroundColor: c, borderColor: color === c ? '#fff' : 'transparent' }}
                />
              ))}
            </div>
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
          + Додати тег
        </button>
      )}
    </div>
  );
}
