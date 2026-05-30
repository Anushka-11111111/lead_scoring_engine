import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
  RadialBarChart,
  RadialBar,
  ComposedChart,
} from "recharts";
import { TrendingUp, PieChartIcon, BarChart3, GitCompare } from "lucide-react";
import {
  buildPieData,
  buildScoreDistribution,
  buildRuleVsMlData,
  buildMlProgress,
  hotRate,
} from "../../utils/chartHelpers";

const PIE_COLORS = ["#2563eb", "#facc15", "#93c5fd"];

const tooltipStyle = {
  backgroundColor: "#fff",
  border: "1px solid #bfdbfe",
  borderRadius: "12px",
  boxShadow: "0 8px 24px rgba(37,99,235,0.12)",
};

function ChartShell({ title, subtitle, icon, children, className = "" }) {
  return (
    <div
      className={`bg-[#dbeafe] rounded-3xl p-6 shadow-sm border border-blue-200/50 ${className}`}
    >
      <div className="flex items-start gap-3 mb-5">
        <div className="p-2.5 rounded-xl bg-white/80 text-blue-700 shadow-sm">
          {icon}
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-900">{title}</h2>
          {subtitle && (
            <p className="text-slate-500 text-sm mt-0.5">{subtitle}</p>
          )}
        </div>
      </div>
      <div className="chart-panel p-4">{children}</div>
    </div>
  );
}

export default function InsightsCharts({ analytics }) {
  const pieData = buildPieData(analytics);
  const scoreDistribution = buildScoreDistribution(analytics);
  const ruleVsMl = buildRuleVsMlData(analytics.top_leads || []);
  const mlProgress = buildMlProgress(analytics.ml_status);
  const total = analytics.total_leads || 0;
  const hotPct = hotRate(analytics);

  const funnelData = [
    { stage: "Cold", count: analytics.cold_leads || 0, fill: "#93c5fd" },
    { stage: "Warm", count: analytics.warm_leads || 0, fill: "#facc15" },
    { stage: "Hot", count: analytics.hot_leads || 0, fill: "#2563eb" },
  ];

  const radialData = [
    {
      name: "ML training",
      value: mlProgress.pct,
      fill: "#2563eb",
    },
  ];

  const pieTotal = pieData.reduce((s, d) => s + d.value, 0);

  return (
    <div className="space-y-6 mb-8">
      {/* Row 1: distribution + funnel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartShell
          title="Lead temperature mix"
          subtitle="Share of hot, warm, and cold leads"
          icon={<PieChartIcon size={20} />}
        >
          <div className="relative" style={{ height: 300 }}>
            {pieTotal === 0 ? (
              <p className="text-center text-slate-500 py-24">
                Sync leads to see distribution
              </p>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={105}
                      innerRadius={62}
                      paddingAngle={3}
                      label={({ name, percent }) =>
                        `${name} ${(percent * 100).toFixed(0)}%`
                      }
                      labelLine={false}
                    >
                      {pieData.map((entry, i) => (
                        <Cell
                          key={entry.name}
                          fill={entry.fill || PIE_COLORS[i % PIE_COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={tooltipStyle} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="text-center mt-1">
                    <p className="text-3xl font-bold text-blue-700">{total}</p>
                    <p className="text-xs text-slate-500 font-medium">Total</p>
                  </div>
                </div>
              </>
            )}
          </div>
        </ChartShell>

        <ChartShell
          title="Pipeline funnel"
          subtitle="Lead count by temperature stage"
          icon={<BarChart3 size={20} />}
        >
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={funnelData} margin={{ top: 12, right: 12, left: 0, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="stage" tick={{ fontWeight: 600 }} />
                <YAxis allowDecimals={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="count" radius={[10, 10, 0, 0]}>
                  {funnelData.map((entry) => (
                    <Cell key={entry.stage} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartShell>
      </div>

      {/* Row 2: score brackets + ML progress */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ChartShell
          className="lg:col-span-2"
          title="Score distribution"
          subtitle="Leads and unique companies per score bracket"
          icon={<BarChart3 size={20} />}
        >
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height={280}>
              <ComposedChart
                layout="vertical"
                data={scoreDistribution}
                margin={{ left: 4, right: 24, top: 8, bottom: 8 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                <XAxis type="number" allowDecimals={false} />
                <YAxis
                  type="category"
                  dataKey="bracket"
                  width={64}
                  tick={{ fontSize: 12, fontWeight: 600 }}
                />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend />
                <Bar
                  dataKey="leads"
                  fill="#93c5fd"
                  radius={[0, 8, 8, 0]}
                  name="Leads"
                />
                <Bar
                  dataKey="companies"
                  fill="#2563eb"
                  radius={[0, 8, 8, 0]}
                  name="Companies"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </ChartShell>

        <ChartShell
          title="ML training progress"
          subtitle={`${mlProgress.completed} / ${mlProgress.target} completed leads`}
          icon={<TrendingUp size={20} />}
        >
          <div style={{ height: 280 }} className="flex flex-col items-center justify-center">
            <ResponsiveContainer width="100%" height={220}>
              <RadialBarChart
                cx="50%"
                cy="50%"
                innerRadius="58%"
                outerRadius="95%"
                data={radialData}
                startAngle={90}
                endAngle={-270}
              >
                <RadialBar
                  background={{ fill: "#dbeafe" }}
                  dataKey="value"
                  cornerRadius={12}
                />
                <Tooltip contentStyle={tooltipStyle} />
              </RadialBarChart>
            </ResponsiveContainer>
            <p className="text-3xl font-bold text-blue-700 -mt-4">
              {mlProgress.pct}%
            </p>
            <p className="text-xs text-slate-500 text-center px-4 mt-1">
              Training starts at {mlProgress.trainAt} leads · mature at{" "}
              {mlProgress.target}
            </p>
            {analytics.ml_status?.model_loaded && (
              <span className="mt-3 text-xs font-semibold text-green-700 bg-green-50 px-3 py-1 rounded-full border border-green-200">
                Model active
                {analytics.ml_status.model_version
                  ? ` · ${analytics.ml_status.model_version}`
                  : ""}
              </span>
            )}
          </div>
        </ChartShell>
      </div>

      {/* Row 3: rule vs ML + hot rate insight */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartShell
          title="Rule vs ML (top leads)"
          subtitle="Compare rule engine score with independent ML score"
          icon={<GitCompare size={20} />}
        >
          <div style={{ height: 280 }}>
            {ruleVsMl.length === 0 ? (
              <p className="text-center text-slate-500 py-20">
                ML scores appear after training (100+ completed leads)
              </p>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={ruleVsMl} margin={{ top: 8, right: 8, left: 0, bottom: 24 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={50} />
                  <YAxis domain={[0, 100]} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Legend />
                  <Bar dataKey="rule" fill="#2563eb" name="Rule score" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="ml" fill="#93c5fd" name="ML score" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </ChartShell>

        <ChartShell
          title="Score health snapshot"
          subtitle="Key ratios from your synced pipeline"
          icon={<TrendingUp size={20} />}
        >
          <div className="space-y-5 py-2">
            <InsightBar
              label="Hot lead rate"
              value={hotPct}
              max={100}
              color="bg-blue-600"
              detail={`${analytics.hot_leads || 0} of ${total} leads`}
            />
            <InsightBar
              label="Average rule score"
              value={analytics.average_score || 0}
              max={100}
              color="bg-blue-500"
              detail="Across all synced leads"
            />
            <InsightBar
              label="Warm pipeline share"
              value={
                total
                  ? Math.round(((analytics.warm_leads || 0) / total) * 100)
                  : 0
              }
              max={100}
              color="bg-yellow-400"
              detail={`${analytics.warm_leads || 0} warm leads`}
            />
            <InsightBar
              label="ML coverage (top 10)"
              value={
                (analytics.top_leads || []).length
                  ? Math.round(
                      ((analytics.top_leads || []).filter((l) => l.ml_active)
                        .length /
                        (analytics.top_leads || []).length) *
                        100
                    )
                  : 0
              }
              max={100}
              color="bg-sky-400"
              detail="Leads with active ML score in top list"
            />
          </div>
        </ChartShell>
      </div>
    </div>
  );
}

function InsightBar({ label, value, max, color, detail }) {
  const width = Math.min(100, Math.max(0, (value / max) * 100));
  return (
    <div>
      <div className="flex justify-between text-sm mb-1.5">
        <span className="font-semibold text-slate-700">{label}</span>
        <span className="font-bold text-blue-700 tabular-nums">{value}%</span>
      </div>
      <div className="h-3 bg-blue-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${width}%` }}
        />
      </div>
      {detail && <p className="text-xs text-slate-500 mt-1">{detail}</p>}
    </div>
  );
}
