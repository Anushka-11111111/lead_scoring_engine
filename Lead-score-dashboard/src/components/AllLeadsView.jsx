import { ArrowLeft, Search } from "lucide-react";
import { useMemo, useState } from "react";

function scoreTone(score) {
  if (score >= 80) return "bg-red-100 text-red-600";
  if (score >= 50) return "bg-yellow-100 text-yellow-700";
  return "bg-blue-100 text-blue-700";
}

export default function AllLeadsView({ leads, onBack, onSelectLead }) {
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
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8 gap-4">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="flex items-center gap-2 bg-white border border-blue-200 text-blue-700 px-4 py-2 rounded-2xl font-semibold hover:bg-blue-50"
          >
            <ArrowLeft size={18} />
            Back to dashboard
          </button>
          <div>
            <h1 className="text-4xl font-bold text-slate-900">All scored leads</h1>
            <p className="text-slate-500 mt-1">
              {filtered.length} of {leads.length} leads · click a row for full details
            </p>
          </div>
        </div>

        <div className="relative max-w-md w-full">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            placeholder="Search by name, company, or ID..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-3 rounded-2xl border border-blue-200 bg-white text-slate-900 outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>
      </div>

      <div className="bg-[#dbeafe] rounded-3xl p-6 shadow-sm">
        {filtered.length === 0 ? (
          <p className="text-center text-slate-600 py-16">
            No leads yet. Run <strong>Start CRM Sync</strong> on the dashboard first.
          </p>
        ) : (
          <div className="overflow-auto">
            <table className="w-full border-separate border-spacing-y-2">
              <thead>
                <tr className="text-left text-slate-600 text-sm">
                  <th className="pb-2">Lead ID</th>
                  <th>Name</th>
                  <th>Company</th>
                  <th>Score</th>
                  <th>Status</th>
                  <th>ML %</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((lead) => (
                  <tr
                    key={lead.lead_id}
                    onClick={() => onSelectLead(lead.lead_id)}
                    className="bg-white shadow-sm cursor-pointer hover:ring-2 hover:ring-blue-400 transition-all"
                  >
                    <td className="p-4 rounded-l-2xl font-mono text-sm">{lead.lead_id}</td>
                    <td className="font-medium">{lead.name}</td>
                    <td>{lead.company}</td>
                    <td>
                      <span
                        className={`inline-block px-3 py-1 rounded-xl font-bold ${scoreTone(lead.score)}`}
                      >
                        {lead.score}
                      </span>
                    </td>
                    <td>{lead.label}</td>
                    <td className="rounded-r-2xl p-4">{lead.ml_probability}%</td>
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
