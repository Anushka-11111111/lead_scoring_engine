import { useEffect, useState } from "react";
import axios from "axios";

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
  RefreshCcw,
} from "lucide-react";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [analytics, setAnalytics] = useState(null);

  const fetchAnalytics = async () => {
    try {
      const res = await axios.get(`${API}/analytics`);
      setAnalytics(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const startScraping = async () => {
    try {
      await axios.post(`${API}/start-sync`);
      fetchAnalytics();
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 3000);
    return () => clearInterval(interval);
  }, []);

  if (!analytics) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white text-3xl font-bold text-blue-600">
        Loading Dashboard...
      </div>
    );
  }

  const pieData = [
    { name: "Hot", value: analytics.hot_leads },
    { name: "Warm", value: analytics.warm_leads },
    { name: "Cold", value: analytics.cold_leads },
  ];

  const scoreData = analytics.top_leads.map((lead) => ({
    id: lead.name,
    score: lead.score,
  }));

  return (
    <div className="min-h-screen bg-white flex text-slate-900">
      {/* SIDEBAR */}
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
            <button className="w-full bg-blue-600 text-white py-3 rounded-2xl font-semibold">
              Dashboard
            </button>

            <button className="w-full bg-white py-3 rounded-2xl font-semibold shadow-sm">
              Leads
            </button>

            <button className="w-full bg-white py-3 rounded-2xl font-semibold shadow-sm">
              AI Insights
            </button>

            <button className="w-full bg-white py-3 rounded-2xl font-semibold shadow-sm">
              Reports
            </button>

            <button className="w-full bg-white py-3 rounded-2xl font-semibold shadow-sm">
              Settings
            </button>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-sm">
          <p className="font-semibold text-lg">Backend Status</p>
          <p className="text-slate-500 mt-2">
            {analytics.status.running ? "Sync Running..." : "Idle"}
          </p>
        </div>
      </aside>

      {/* MAIN */}
      <main className="flex-1 p-6">
        {/* HEADER */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
          <div>
            <h1 className="text-5xl font-bold text-slate-900">
              AI Lead Scoring Dashboard
            </h1>
            <p className="text-slate-500 mt-3 text-lg">
              Live scraped leads scored by backend ML engine
            </p>
          </div>

          <button
            onClick={startScraping}
            className="mt-5 lg:mt-0 bg-blue-600 hover:bg-blue-700 text-white px-7 py-4 rounded-2xl font-semibold flex items-center gap-3 shadow-lg transition-all"
          >
            <RefreshCcw size={20} />
            Start CRM Sync
          </button>
        </div>

        {/* TOP CARDS */}
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

        {/* CHARTS */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-[#dbeafe] rounded-3xl p-6 shadow-sm">
            <h2 className="text-2xl font-bold mb-6">Lead Distribution</h2>

            <div className="h-80">
              <ResponsiveContainer>
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
            <h2 className="text-2xl font-bold mb-5">Lead Score Trends</h2>

            <div className="h-80">
              <ResponsiveContainer>
                <BarChart data={scoreData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="id" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="score" fill="#2563eb" radius={[10, 10, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* TOP LEADS TABLE */}
        <div className="bg-[#dbeafe] rounded-3xl p-6 shadow-sm mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-3xl font-bold">Top Leads</h2>

            <div className="bg-white px-5 py-2 rounded-2xl shadow-sm">
              <span className="font-semibold">Live Backend Data</span>
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
                {analytics.top_leads.map((lead) => (
                  <tr key={lead.lead_id} className="bg-white shadow-sm">
                    <td className="p-4 rounded-l-2xl">{lead.lead_id}</td>
                    <td>{lead.name}</td>
                    <td>{lead.company}</td>

                    <td>
                      <div
                        className={`w-fit px-4 py-2 rounded-xl font-bold ${
                          lead.score >= 80
                            ? "bg-red-100 text-red-600"
                            : lead.score >= 60
                              ? "bg-yellow-100 text-yellow-700"
                              : "bg-blue-100 text-blue-700"
                        }`}
                      >
                        {lead.score}
                      </div>
                    </td>

                    <td>{lead.label}</td>

                    <td className="rounded-r-2xl">{lead.ml_probability}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}

/* ======================= */
/* ANALYTICS CARD */
/* ======================= */

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
