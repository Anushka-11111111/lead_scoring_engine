import { useEffect, useState } from "react";
import { RefreshCcw, Search, List, Loader2 } from "lucide-react";

const MIN_LEADS = 1;
const MAX_LEADS = 1000;

function clampQuantity(value) {
  return Math.min(MAX_LEADS, Math.max(MIN_LEADS, value));
}

export default function SyncToolbar({
  fetchQuantity,
  onQuantityChange,
  onStartSync,
  syncDisabled,
  onShowAllLeads,
  lookupId,
  onLookupIdChange,
  onLookupSubmit,
  lookupLoading,
}) {
  const [quantityInput, setQuantityInput] = useState(String(fetchQuantity));

  useEffect(() => {
    setQuantityInput(String(fetchQuantity));
  }, [fetchQuantity]);

  const commitQuantity = () => {
    const n = parseInt(quantityInput, 10);
    const clamped = clampQuantity(Number.isNaN(n) ? MIN_LEADS : n);
    setQuantityInput(String(clamped));
    onQuantityChange(clamped);
    return clamped;
  };

  return (
    <div className="flex flex-col gap-4 mt-5 lg:mt-0">
      <div className="flex flex-wrap items-center gap-3">
        <label className="flex items-center gap-2 bg-white border border-blue-200 rounded-2xl px-4 py-3 shadow-sm">
          <span className="text-sm font-semibold text-slate-600 whitespace-nowrap">
            Leads to fetch
          </span>
          <input
            type="number"
            min={MIN_LEADS}
            max={MAX_LEADS}
            value={quantityInput}
            onChange={(e) => setQuantityInput(e.target.value)}
            onBlur={commitQuantity}
            onKeyDown={(e) => e.key === "Enter" && commitQuantity()}
            disabled={syncDisabled}
            className="w-24 bg-transparent font-bold text-blue-700 outline-none text-center [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
        </label>

        <button
          onClick={() => onStartSync(commitQuantity())}
          disabled={syncDisabled}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed text-white px-7 py-3 rounded-2xl font-semibold flex items-center gap-3 shadow-lg transition-all"
        >
          {syncDisabled ? (
            <Loader2 size={20} className="animate-spin" />
          ) : (
            <RefreshCcw size={20} />
          )}
          {syncDisabled ? "Syncing..." : "Start CRM Sync"}
        </button>

        <button
          onClick={onShowAllLeads}
          className="bg-white border-2 border-blue-600 text-blue-700 hover:bg-blue-50 px-6 py-3 rounded-2xl font-semibold flex items-center gap-2"
        >
          <List size={20} />
          Show All Leads
        </button>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          onLookupSubmit();
        }}
        className="flex items-center gap-2 bg-white border border-blue-200 rounded-2xl px-3 py-2 shadow-sm w-full max-w-md"
        title="Score a single lead by ID"
      >
        <button
          type="submit"
          disabled={lookupLoading || !lookupId.trim()}
          className="p-2 rounded-xl bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
          aria-label="Score lead by ID"
        >
          {lookupLoading ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <Search size={18} />
          )}
        </button>
        <input
          type="text"
          value={lookupId}
          onChange={(e) => onLookupIdChange(e.target.value)}
          placeholder="Enter lead ID (e.g. 518029)"
          className="flex-1 min-w-0 py-2 px-1 bg-transparent text-slate-900 outline-none placeholder:text-slate-400"
        />
      </form>
    </div>
  );
}
