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

import { Activity, Flame, Snowflake, Timer } from "lucide-react";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [analytics, setAnalytics] = useState(null);

  const fetchAnalytics = async () => {
    try {
      const res = await axios.get(`${API}/analytics`);
      console.log(res)

      setAnalytics(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const startScraping = async () => {
    try {
     const data =  await axios.post("http://127.0.0.1:8000/start-sync");
     console.log(data)
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
    return <div className="p-10 text-white">Loading...</div>;
  }

  const pieData = [
    {
      name: "Hot",
      value: analytics.hot_leads,
    },
    {
      name: "Warm",
      value: analytics.warm_leads,
    },
    {
      name: "Cold",
      value: analytics.cold_leads,
    },
  ];

  const scoreData = analytics.top_leads.map((lead) => ({
    id: lead.lead_id,
    score: lead.score,
  }));

  return (
    <div className="min-h-screen bg-violet-950 text-white p-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold">AI Lead Scoring Dashboard</h1>

          <p className="text-slate-400 mt-2">CRM Lead Intelligence System</p>
        </div>

        <button
          onClick={startScraping}
          className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-xl font-semibold"
        >
          Start CRM Sync
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-5 mb-8">
        <Card
          title="Total Leads"
          value={analytics.total_leads}
          icon={<Activity />}
        />

        <Card title="Hot Leads" value={analytics.hot_leads} icon={<Flame />} />

        <Card
          title="Cold Leads"
          value={analytics.cold_leads}
          icon={<Snowflake />}
        />

        <Card
          title="Average Score"
          value={analytics.average_score}
          icon={<Timer />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-slate-900 p-5 rounded-2xl">
          <h2 className="text-2xl font-bold mb-4">Lead Distribution</h2>

          <div className="h-80">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={pieData} dataKey="value" outerRadius={120} label>
                  <Cell fill="#ef4444" />
                  <Cell fill="#facc15" />
                  <Cell fill="#3b82f6" />
                </Pie>

                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900 p-5 rounded-2xl">
          <h2 className="text-2xl font-bold mb-4">Top Lead Scores</h2>

          <div className="h-80">
            <ResponsiveContainer>
              <BarChart data={scoreData}>
                <CartesianGrid strokeDasharray="3 3" />

                <XAxis dataKey="id" />

                <YAxis />

                <Tooltip />

                <Bar dataKey="score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="bg-slate-900 p-5 rounded-2xl">
        <h2 className="text-2xl font-bold mb-5">Top Leads</h2>

        <div className="overflow-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left border-b border-slate-700">
                <th className="pb-3">Lead ID</th>
                <th>Name</th>
                <th>Company</th>
                <th>Score</th>
                <th>Label</th>
                <th>ML Probability</th>
              </tr>
            </thead>

            <tbody>
              {analytics.top_leads.map((lead) => (
                <tr key={lead.lead_id} className="border-b border-slate-800">
                  <td className="py-4">{lead.lead_id}</td>

                  <td>{lead.name}</td>

                  <td>{lead.company}</td>

                  <td>{lead.score}</td>

                  <td>{lead.label}</td>

                  <td>{lead.ml_probability}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-8 bg-slate-900 p-5 rounded-2xl">
        <h2 className="text-2xl font-bold mb-4">Pipeline Status</h2>

        <div className="space-y-3">
          <p>Running: {analytics.status.running ? "YES" : "NO"}</p>

          <p>Processed: {analytics.status.processed}</p>

          <p>Total: {analytics.status.total}</p>

          <p>Current Lead: {analytics.status.current_lead}</p>

          <p>Completed: {analytics.status.completed ? "YES" : "NO"}</p>
        </div>
      </div>
    </div>
  );
}

function Card({ title, value, icon }) {
  return (
    <div className="bg-slate-900 rounded-2xl p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-400">{title}</p>

          <h2 className="text-3xl font-bold mt-2">{value}</h2>
        </div>

        <div className="text-blue-400">{icon}</div>
      </div>
    </div>
  );
}
