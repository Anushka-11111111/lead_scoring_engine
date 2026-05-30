import {
  Activity,
  Flame,
  Snowflake,
  BrainCircuit,
  Thermometer,
  Target,
} from "lucide-react";
import SyncToolbar from "../SyncToolbar";
import StatCard from "./StatCard";
import InsightsCharts from "./InsightsCharts";
import LeadsTable from "./LeadsTable";
import { hotRate } from "../../utils/chartHelpers";

export default function DashboardView({
  analytics,
  analyticsLoading,
  fetchQuantity,
  onQuantityChange,
  onStartSync,
  syncRunning,
  onShowAllLeads,
  lookupId,
  onLookupIdChange,
  onLookupSubmit,
  lookupLoading,
  onRowClick,
  onViewAllLeads,
}) {
  const hotPct = hotRate(analytics);

  return (
    <>
      <header className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#dbeafe] via-[#dbeafe] to-blue-100 border border-blue-200/60 p-8 mb-8 shadow-sm">
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-400/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4" />
        <div className="relative flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">
          <div>
            <p className="text-blue-700 font-semibold text-sm uppercase tracking-widest mb-2">
              Live intelligence
            </p>
            <h1 className="text-4xl md:text-5xl font-bold text-slate-900 tracking-tight">
              AI Lead Scoring Dashboard
            </h1>
            <p className="text-slate-600 mt-3 text-lg max-w-xl">
              CRM leads scored by rules and ML — refreshed every few seconds
            </p>
            {analyticsLoading && (
              <p className="text-sm text-blue-600 font-medium mt-2 animate-pulse">
                Refreshing analytics…
              </p>
            )}
          </div>
          <SyncToolbar
            fetchQuantity={fetchQuantity}
            onQuantityChange={onQuantityChange}
            onStartSync={onStartSync}
            syncDisabled={syncRunning}
            onShowAllLeads={onShowAllLeads}
            lookupId={lookupId}
            onLookupIdChange={onLookupIdChange}
            onLookupSubmit={onLookupSubmit}
            lookupLoading={lookupLoading}
          />
        </div>
      </header>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6 gap-4 mb-8">
        <StatCard
          title="Total Leads"
          value={analytics.total_leads}
          subtitle="Synced from CRM"
          icon={<Activity size={26} />}
          accent="blue"
        />
        <StatCard
          title="Hot Leads"
          value={analytics.hot_leads}
          subtitle="Score ≥ 80"
          icon={<Flame size={26} />}
          accent="yellow"
          trend={hotPct > 0 ? `${hotPct}% of pipeline` : null}
        />
        <StatCard
          title="Warm Leads"
          value={analytics.warm_leads}
          subtitle="Score 50–79"
          icon={<Thermometer size={26} />}
          accent="yellow"
        />
        <StatCard
          title="Cold Leads"
          value={analytics.cold_leads}
          subtitle="Score below 50"
          icon={<Snowflake size={26} />}
          accent="sky"
        />
        <StatCard
          title="Avg Rule Score"
          value={analytics.average_score ?? 0}
          subtitle="Mean across all leads"
          icon={<Target size={26} />}
          accent="blue"
        />
        <StatCard
          title="ML Progress"
          value={`${analytics.ml_status?.completed_leads ?? 0}`}
          subtitle={`of ${analytics.ml_status?.mature_threshold ?? 3000} for mature model`}
          icon={<BrainCircuit size={26} />}
          accent="slate"
        />
      </div>

      <InsightsCharts analytics={analytics} />

      <LeadsTable
        title="Top Leads"
        leads={analytics.top_leads}
        onRowClick={onRowClick}
        footer={
          analytics.total_leads > (analytics.top_leads?.length || 0) && (
            <button
              type="button"
              onClick={onViewAllLeads}
              className="mt-4 inline-flex items-center gap-2 text-blue-700 font-semibold hover:text-blue-800 hover:underline"
            >
              View all {analytics.total_leads} leads →
            </button>
          )
        }
      />
    </>
  );
}
