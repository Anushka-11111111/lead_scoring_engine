import { X, Flame, Snowflake, BrainCircuit } from "lucide-react";

function scoreTone(score) {
  if (score >= 80) return "hot";
  if (score >= 50) return "warm";
  return "cold";
}

const toneStyles = {
  hot: "bg-red-100 text-red-700 border-red-200",
  warm: "bg-yellow-100 text-yellow-800 border-yellow-200",
  cold: "bg-blue-100 text-blue-700 border-blue-200",
};

export default function LeadDetailModal({ lead, loading, error, onClose }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-100">
          <div>
            <p className="text-sm text-slate-500">Lead details & AI score</p>
            <h2 className="text-2xl font-bold text-slate-900">
              {loading ? "Loading..." : lead?.name || "Lead"}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl hover:bg-slate-100 text-slate-600"
            aria-label="Close"
          >
            <X size={22} />
          </button>
        </div>

        <div className="overflow-y-auto p-6 space-y-6">
          {loading && (
            <p className="text-center text-slate-500 py-12">Fetching lead from CRM...</p>
          )}

          {error && (
            <p className="text-center text-red-600 py-12">{error}</p>
          )}

          {!loading && !error && lead && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className={`rounded-2xl border p-5 ${toneStyles[scoreTone(lead.score)]}`}>
                  <p className="text-sm font-medium opacity-80">Rule score</p>
                  <p className="text-4xl font-bold mt-1">{lead.score}</p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm text-slate-500">Classification</p>
                  <p className="text-xl font-bold mt-1 text-slate-900">{lead.label}</p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm text-slate-500 flex items-center gap-1">
                    <BrainCircuit size={16} /> ML probability
                  </p>
                  <p className="text-4xl font-bold mt-1 text-blue-700">
                    {lead.ml_probability}%
                  </p>
                </div>
              </div>

              <div className="rounded-2xl bg-[#dbeafe] p-5">
                <h3 className="font-bold text-lg mb-2">Score breakdown</h3>
                <p className="text-slate-700 whitespace-pre-wrap">
                  {lead.breakdown || "No rule breakdown available."}
                </p>
              </div>

              <div>
                <h3 className="font-bold text-lg mb-3">CRM lead information</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {(lead.crm_details || []).map((row) => (
                    <div
                      key={row.label}
                      className="bg-slate-50 rounded-xl px-4 py-3 border border-slate-100"
                    >
                      <p className="text-xs text-slate-500 uppercase tracking-wide">
                        {row.label}
                      </p>
                      <p className="font-medium text-slate-900 mt-1 break-words">
                        {row.value}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2 text-sm text-slate-500">
                {lead.score >= 80 ? (
                  <Flame size={16} className="text-red-500" />
                ) : (
                  <Snowflake size={16} className="text-blue-500" />
                )}
                Lead ID: {lead.lead_id} · {lead.company}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
