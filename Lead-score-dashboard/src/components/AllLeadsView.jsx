import { ArrowLeft, Search } from "lucide-react";
import { useMemo, useState } from "react";
import SyncToolbar from "./SyncToolbar";

function scoreTone(score) {
  if (score >= 80) return "bg-red-100 text-red-600 ring-1 ring-red-200";
  if (score >= 50) return "bg-yellow-100 text-yellow-800 ring-1 ring-yellow-200";
  return "bg-blue-100 text-blue-700 ring-1 ring-blue-200";
}

export default function AllLeadsView({
  leads,
  onBack,
  onSelectLead,
  syncToolbarProps,
}) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return leads;
    return leads.filter(
      (lead) =>
        String(lead.lead_id).toLowerCase().includes(q) ||
        (lead.name || "").toLowerCase().includes(q) ||
        (lead.company || "").toLowerCase().includes(q)
    );
  }, [leads, query]);

  return (
    <div>
      <header className="rounded-3xl bg-gradient-to-r from-[#dbeafe] to-blue-100 border border-blue-200/60 p-6 mb-8 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={onBack}
              className="flex items-center gap-2 bg-white border border-blue-200 text-blue-700 px-4 py-2.5 rounded-2xl font-semibold hover:bg-blue-50 shadow-sm"
            >
              <ArrowLeft size={18} />
              Dashboard
            </button>
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-slate-900">
                All scored leads
              </h1>
              <p className="text-slate-600 mt-1 text-sm">
                {filtered.length} of {leads.length} leads · click a row for details
              </p>
            </div>
          </div>
          {syncToolbarProps && (
            <SyncToolbar {...syncToolbarProps} />
          )}
        </div>
      </header>

      <div className="mb-6 relative max-w-lg">
        <Search
          className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
          size={18}
        />
        <input
          type="text"
          placeholder="Search by name, company, or ID..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full pl-11 pr-4 py-3 rounded-2xl border border-blue-200 bg-white text-slate-900 outline-none focus:ring-2 focus:ring-blue-400 shadow-sm"
        />
      </div>

      <div className="bg-[#dbeafe] rounded-3xl p-6 shadow-sm border border-blue-200/50">
        {filtered.length === 0 ? (
          <p className="text-center text-slate-600 py-16">
            No leads yet. Run <strong>Start CRM Sync</strong> on the dashboard first.
          </p>
        ) : (
          <div className="overflow-auto rounded-2xl">
            <table className="w-full border-separate border-spacing-y-2 min-w-[640px]">
              <thead>
                <tr className="text-left text-slate-600 text-sm">
                  <th className="pb-2 pl-2">Lead ID</th>
                  <th>Name</th>
                  <th>Company</th>
                  <th>Rule Score</th>
                  <th>Status</th>
                  <th>ML Score</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((lead) => (
                  <tr
                    key={lead.lead_id}
                    onClick={() => onSelectLead(lead.lead_id)}
                    className="bg-white shadow-sm cursor-pointer hover:shadow-md hover:ring-2 hover:ring-blue-400/60 transition-all"
                  >
                    <td className="p-4 rounded-l-2xl font-mono text-sm text-slate-600">
                      {lead.lead_id}
                    </td>
                    <td className="font-medium text-slate-900">{lead.name}</td>
                    <td className="text-slate-600">{lead.company}</td>
                    <td>
                      <span
                        className={`inline-block px-3 py-1 rounded-xl font-bold text-sm ${scoreTone(lead.score)}`}
                      >
                        {lead.score}
                      </span>
                    </td>
                    <td className="text-sm">{lead.label}</td>
                    <td className="rounded-r-2xl p-4">
                      {lead.ml_active && lead.ml_score != null ? (
                        <span className="font-bold text-blue-700 bg-blue-50 px-2 py-1 rounded-lg">
                          {lead.ml_score}
                        </span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
