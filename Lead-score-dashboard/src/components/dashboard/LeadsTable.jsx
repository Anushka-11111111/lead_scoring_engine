import { ChevronRight } from "lucide-react";

function scoreBadgeClass(score) {
  if (score >= 80) return "bg-red-100 text-red-600 ring-1 ring-red-200";
  if (score >= 50) return "bg-yellow-100 text-yellow-800 ring-1 ring-yellow-200";
  return "bg-blue-100 text-blue-700 ring-1 ring-blue-200";
}

export default function LeadsTable({ title, leads, onRowClick, footer }) {
  return (
    <div className="bg-[#dbeafe] rounded-3xl p-6 shadow-sm border border-blue-200/50 mb-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <h2 className="text-2xl md:text-3xl font-bold text-slate-900">{title}</h2>
        <div className="bg-white/90 px-4 py-2 rounded-2xl shadow-sm border border-blue-100 text-sm font-semibold text-slate-600">
          Click a row for full details
        </div>
      </div>

      <div className="overflow-auto rounded-2xl">
        <table className="w-full border-separate border-spacing-y-2 min-w-[640px]">
          <thead>
            <tr className="text-left text-slate-600 text-sm">
              <th className="pb-2 pl-2 font-semibold">Lead ID</th>
              <th className="pb-2 font-semibold">Name</th>
              <th className="pb-2 font-semibold">Company</th>
              <th className="pb-2 font-semibold">Rule Score</th>
              <th className="pb-2 font-semibold">Status</th>
              <th className="pb-2 font-semibold">ML Score</th>
              <th className="pb-2 w-8" />
            </tr>
          </thead>
          <tbody>
            {leads.length === 0 ? (
              <tr>
                <td
                  colSpan={7}
                  className="text-center py-14 text-slate-500 bg-white rounded-2xl shadow-sm"
                >
                  No leads scored yet. Run CRM Sync to load leads.
                </td>
              </tr>
            ) : (
              leads.map((lead, index) => (
                <tr
                  key={lead.lead_id}
                  onClick={() => onRowClick(lead.lead_id)}
                  className="group bg-white shadow-sm cursor-pointer hover:shadow-md hover:ring-2 hover:ring-blue-400/60 transition-all duration-200"
                >
                  <td className="p-4 rounded-l-2xl font-mono text-sm text-slate-600">
                    <span className="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-blue-50 text-blue-700 text-xs font-bold mr-2">
                      {index + 1}
                    </span>
                    {lead.lead_id}
                  </td>
                  <td className="font-medium text-slate-900">{lead.name}</td>
                  <td className="text-slate-600">{lead.company}</td>
                  <td>
                    <span
                      className={`inline-block px-3 py-1.5 rounded-xl font-bold text-sm ${scoreBadgeClass(lead.score)}`}
                    >
                      {lead.score}
                    </span>
                  </td>
                  <td>
                    <span className="text-sm font-medium text-slate-700">
                      {lead.label}
                    </span>
                  </td>
                  <td>
                    {lead.ml_active && lead.ml_score != null ? (
                      <span className="inline-flex items-center gap-1 font-bold text-blue-700 bg-blue-50 px-3 py-1 rounded-xl text-sm">
                        {lead.ml_score}
                      </span>
                    ) : (
                      <span className="text-slate-400">—</span>
                    )}
                  </td>
                  <td className="rounded-r-2xl pr-3">
                    <ChevronRight
                      size={18}
                      className="text-slate-300 group-hover:text-blue-600 transition-colors"
                    />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {footer}
    </div>
  );
}
