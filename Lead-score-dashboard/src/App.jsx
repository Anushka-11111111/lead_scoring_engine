import { useCallback, useEffect, useRef, useState } from "react";
import { api, apiErrorMessage } from "./api";
import { EMPTY_ANALYTICS } from "./constants";
import ConnectionBanner from "./components/ConnectionBanner";

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
} from "recharts";

import {
  Activity,
  Flame,
  Snowflake,
  BrainCircuit,
} from "lucide-react";

import AllLeadsView from "./components/AllLeadsView";
import LeadDetailModal from "./components/LeadDetailModal";
import SyncToolbar from "./components/SyncToolbar";

export default function App() {
  const [analytics, setAnalytics] = useState(EMPTY_ANALYTICS);
  const [apiError, setApiError] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);
  const fetchInFlight = useRef(false);
  const [allLeads, setAllLeads] = useState([]);
  const [view, setView] = useState("dashboard");
  const [selectedLeadId, setSelectedLeadId] = useState(null);
  const [leadDetail, setLeadDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState(null);
  const [fetchQuantity, setFetchQuantity] = useState(50);
  const [lookupId, setLookupId] = useState("");
  const [lookupLoading, setLookupLoading] = useState(false);

  const fetchAnalytics = useCallback(async () => {
    if (fetchInFlight.current) return;
    fetchInFlight.current = true;
    try {
      const res = await api.get("/analytics");
      setAnalytics(res.data);
      setApiError(null);
    } catch (err) {
      console.error(err);
      setApiError(apiErrorMessage(err));
      setAnalytics((prev) => ({
        ...EMPTY_ANALYTICS,
        status: prev?.status ?? EMPTY_ANALYTICS.status,
      }));
    } finally {
      fetchInFlight.current = false;
      setAnalyticsLoading(false);
    }
  }, []);

  const fetchAllLeads = async () => {
    try {
      const res = await api.get("/leads");
      setAllLeads(res.data.leads || []);
      setApiError(null);
    } catch (err) {
      console.error(err);
      setApiError(apiErrorMessage(err));
      setAllLeads([]);
    }
  };

  const openLeadDetail = useCallback(async (leadId) => {
    setSelectedLeadId(leadId);
    setLeadDetail(null);
    setDetailError(null);
    setDetailLoading(true);

    try {
      const res = await api.get(`/leads/${leadId}`);
      setLeadDetail(res.data);
    } catch (err) {
      setDetailError(
        err.response?.data?.detail || err.message || "Failed to load lead"
      );
    } finally {
      setDetailLoading(false);
    }
  }, []);

  const closeLeadDetail = () => {
    setSelectedLeadId(null);
    setLeadDetail(null);
    setDetailError(null);
  };

  const goToAllLeads = () => {
    setView("all-leads");
    fetchAllLeads();
  };

  const startScraping = async (quantityOverride) => {
    const quantity = Math.min(
      1000,
      Math.max(1, quantityOverride ?? fetchQuantity ?? 50)
    );
    setFetchQuantity(quantity);
    try {
      await api.post("/start-sync", { quantity });
      setApiError(null);
      fetchAnalytics();
      if (view === "all-leads") {
        fetchAllLeads();
      }
    } catch (err) {
      console.error(err);
      setApiError(apiErrorMessage(err));
    }
  };

  const scoreLeadById = async () => {
    const id = lookupId.trim();
    if (!id) return;

    setLookupLoading(true);
    setDetailError(null);

    try {
      await api.post(`/score/${encodeURIComponent(id)}`);
      await fetchAnalytics();
      if (view === "all-leads") {
        await fetchAllLeads();
      }
      await openLeadDetail(id);
    } catch (err) {
      setSelectedLeadId(id);
      setLeadDetail(null);
      setDetailError(
        err.response?.data?.detail || err.message || "Failed to score lead"
      );
    } finally {
      setLookupLoading(false);
    }
  };

  const syncRunning = analytics?.status?.running ?? false;

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(() => {
      fetchAnalytics();
      if (view === "all-leads") {
        fetchAllLeads();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [view, fetchAnalytics]);

  const pieData = [
    { name: "Hot", value: analytics.hot_leads },
    { name: "Warm", value: analytics.warm_leads },
    { name: "Cold", value: analytics.cold_leads },
  ];

  const scoreDistribution =
    analytics.score_distribution?.length > 0
      ? analytics.score_distribution
      : [
          { bracket: "0-19", companies: 0, leads: 0 },
          { bracket: "20-39", companies: 0, leads: 0 },
          { bracket: "40-59", companies: 0, leads: 0 },
          { bracket: "60-79", companies: 0, leads: 0 },
          { bracket: "80-100", companies: 0, leads: 0 },
        ];

  return (
    <div className="min-h-screen bg-white flex text-slate-900">
      <aside className="w-[260px] bg-[#dbeafe] border-r border-blue-200 p-6 hidden md:flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-3 mb-12">
            <div className="bg-blue-600 p-3 rounded-2xl">
              <BrainCircuit className="text-white" />
            </div>
            <div>
              <h1 className="font-bold text-2xl text-blue-700">TOGILE CRM</h1>
              <p className="text-slate-500 text-sm">AI Lead Intelligence</p>
            </div>
          </div>

          <div className="space-y-3">
            <SidebarBtn
              active={view === "dashboard"}
              onClick={() => setView("dashboard")}
            >
              Dashboard
            </SidebarBtn>
            <SidebarBtn active={view === "all-leads"} onClick={goToAllLeads}>
              All Leads
            </SidebarBtn>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-sm">
          <p className="font-semibold text-lg">Backend Status</p>
          <p className="text-slate-500 mt-2">
            {apiError
              ? "API offline"
              : analytics.status?.running
                ? "Sync Running..."
                : "Idle"}
          </p>
        </div>
      </aside>

      <main className="flex-1 p-6 min-w-0">
        <ConnectionBanner
          message={apiError}
          onRetry={() => {
            fetchAnalytics();
            if (view === "all-leads") fetchAllLeads();
          }}
        />

        {analyticsLoading && !apiError && (
          <p className="mb-4 text-sm text-slate-500">Refreshing analytics…</p>
        )}

        {view === "dashboard" ? (
          <>
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
              <div>
                <h1 className="text-5xl font-bold text-slate-900">
                  AI Lead Scoring Dashboard
                </h1>
                <p className="text-slate-500 mt-3 text-lg">
                  Live CRM leads scored by the backend ML engine
                </p>
              </div>

              <SyncToolbar
                fetchQuantity={fetchQuantity}
                onQuantityChange={setFetchQuantity}
                onStartSync={startScraping}
                syncDisabled={syncRunning}
                onShowAllLeads={goToAllLeads}
                lookupId={lookupId}
                onLookupIdChange={setLookupId}
                onLookupSubmit={scoreLeadById}
                lookupLoading={lookupLoading}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
              <AnalyticsCard
                title="Total Leads"
                value={analytics.total_leads}
                icon={<Activity />}
                color="blue"
              />
              <AnalyticsCard
                title="Hot Leads"
                value={analytics.hot_leads}
                icon={<Flame />}
                color="yellow"
              />
              <AnalyticsCard
                title="Cold Leads"
                value={analytics.cold_leads}
                icon={<Snowflake />}
                color="blue"
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="bg-[#dbeafe] rounded-3xl p-6 shadow-sm">
                <h2 className="text-2xl font-bold mb-6">Lead Distribution</h2>
                <div className="w-full min-w-0" style={{ height: 320 }}>
                  <ResponsiveContainer width="100%" height={320}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        dataKey="value"
                        outerRadius={120}
                        innerRadius={70}
                        label
                      >
                        <Cell fill="#2563eb" />
                        <Cell fill="#facc15" />
                        <Cell fill="#93c5fd" />
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-[#dbeafe] rounded-3xl p-6 shadow-sm">
                <h2 className="text-2xl font-bold mb-1">Score distribution</h2>
                <p className="text-slate-500 text-sm mb-5">
                  Companies per score range (all synced leads)
                </p>
                <div className="w-full min-w-0" style={{ height: 320 }}>
                  <ResponsiveContainer width="100%" height={320}>
                    <BarChart
                      layout="vertical"
                      data={scoreDistribution}
                      margin={{ left: 8, right: 24, top: 8, bottom: 8 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                      <XAxis
                        type="number"
                        allowDecimals={false}
                        label={{
                          value: "Number of companies",
                          position: "insideBottom",
                          offset: -4,
                          style: { fill: "#64748b", fontSize: 12 },
                        }}
                      />
                      <YAxis
                        type="category"
                        dataKey="bracket"
                        width={72}
                        tick={{ fontSize: 13, fontWeight: 600 }}
                        label={{
                          value: "Score range",
                          angle: -90,
                          position: "insideLeft",
                          style: { fill: "#64748b", fontSize: 12 },
                        }}
                      />
                      <Tooltip
                        formatter={(value, name) => [
                          value,
                          name === "companies" ? "Companies" : "Leads",
                        ]}
                        labelFormatter={(label) => `Score ${label}`}
                      />
                      <Bar
                        dataKey="companies"
                        fill="#2563eb"
                        radius={[0, 10, 10, 0]}
                        name="companies"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <LeadsTable
              title="Top Leads"
              leads={analytics.top_leads}
              onRowClick={openLeadDetail}
              footer={
                analytics.total_leads > analytics.top_leads.length && (
                  <button
                    onClick={goToAllLeads}
                    className="mt-4 text-blue-700 font-semibold hover:underline"
                  >
                    View all {analytics.total_leads} leads →
                  </button>
                )
              }
            />
          </>
        ) : (
          <>
            <SyncToolbar
              fetchQuantity={fetchQuantity}
              onQuantityChange={setFetchQuantity}
              onStartSync={startScraping}
              syncDisabled={syncRunning}
              onShowAllLeads={goToAllLeads}
              lookupId={lookupId}
              onLookupIdChange={setLookupId}
              onLookupSubmit={scoreLeadById}
              lookupLoading={lookupLoading}
            />
            <AllLeadsView
              leads={allLeads}
              onBack={() => setView("dashboard")}
              onSelectLead={openLeadDetail}
            />
          </>
        )}
      </main>

      {selectedLeadId && (
        <LeadDetailModal
          lead={leadDetail}
          loading={detailLoading}
          error={detailError}
          onClose={closeLeadDetail}
        />
      )}
    </div>
  );
}

function SidebarBtn({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      className={`w-full py-3 rounded-2xl font-semibold transition-all ${
        active
          ? "bg-blue-600 text-white shadow-md"
          : "bg-white text-slate-800 shadow-sm hover:bg-blue-50"
      }`}
    >
      {children}
    </button>
  );
}

function LeadsTable({ title, leads, onRowClick, footer }) {
  return (
    <div className="bg-[#dbeafe] rounded-3xl p-6 shadow-sm mb-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold">{title}</h2>
        <div className="bg-white px-5 py-2 rounded-2xl shadow-sm">
          <span className="font-semibold">Click a row for details</span>
        </div>
      </div>

      <div className="overflow-auto">
        <table className="w-full border-separate border-spacing-y-3">
          <thead>
            <tr className="text-left text-slate-600">
              <th>Lead ID</th>
              <th>Name</th>
              <th>Company</th>
              <th>Score</th>
              <th>Status</th>
              <th>ML Probability</th>
            </tr>
          </thead>
          <tbody>
            {leads.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-10 text-slate-500 bg-white rounded-2xl">
                  No leads scored yet. Run CRM Sync to load leads.
                </td>
              </tr>
            ) : (
              leads.map((lead) => (
                <tr
                  key={lead.lead_id}
                  onClick={() => onRowClick(lead.lead_id)}
                  className="bg-white shadow-sm cursor-pointer hover:ring-2 hover:ring-blue-400 transition-all"
                >
                  <td className="p-4 rounded-l-2xl">{lead.lead_id}</td>
                  <td>{lead.name}</td>
                  <td>{lead.company}</td>
                  <td>
                    <div
                      className={`w-fit px-4 py-2 rounded-xl font-bold ${
                        lead.score >= 80
                          ? "bg-red-100 text-red-600"
                          : lead.score >= 50
                            ? "bg-yellow-100 text-yellow-700"
                            : "bg-blue-100 text-blue-700"
                      }`}
                    >
                      {lead.score}
                    </div>
                  </td>
                  <td>{lead.label}</td>
                  <td className="rounded-r-2xl p-4">{lead.ml_probability}%</td>
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

function AnalyticsCard({ title, value, icon, color }) {
  return (
    <div className="bg-[#dbeafe] rounded-3xl p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-500">{title}</p>
          <h2 className="text-4xl font-bold mt-2">{value}</h2>
        </div>
        <div
          className={`w-16 h-16 rounded-2xl flex items-center justify-center ${
            color === "blue"
              ? "bg-blue-600 text-white"
              : "bg-yellow-400 text-slate-900"
          }`}
        >
          {icon}
        </div>
      </div>
    </div>
  );
}
