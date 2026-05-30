import { useCallback, useEffect, useRef, useState } from "react";
import { api, apiErrorMessage } from "./api";
import { EMPTY_ANALYTICS } from "./constants";
import ConnectionBanner from "./components/ConnectionBanner";
import CrmConfigForm from "./components/CrmConfigForm";
import AppSidebar from "./components/layout/AppSidebar";
import DashboardView from "./components/dashboard/DashboardView";
import AllLeadsView from "./components/AllLeadsView";
import LeadDetailModal from "./components/LeadDetailModal";

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
  const [crmConfigured, setCrmConfigured] = useState(null);

  const fetchCrmConfig = useCallback(async () => {
    try {
      const res = await api.get("/config/crm");
      setCrmConfigured(Boolean(res.data.configured));
      return res.data;
    } catch (err) {
      console.error(err);
      setCrmConfigured(false);
      return null;
    }
  }, []);

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
        ml_status: prev?.ml_status ?? EMPTY_ANALYTICS.ml_status,
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
    fetchCrmConfig().then((config) => {
      if (config && !config.configured) {
        setView("settings");
      }
    });
    fetchAnalytics();
    const interval = setInterval(() => {
      fetchAnalytics();
      if (view === "all-leads") {
        fetchAllLeads();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [view, fetchAnalytics, fetchCrmConfig]);

  return (
    <div className="min-h-screen flex text-slate-900">
      <AppSidebar
        view={view}
        setView={setView}
        goToAllLeads={goToAllLeads}
        apiError={apiError}
        crmConfigured={crmConfigured}
        status={analytics.status}
      />

      <main className="flex-1 p-4 md:p-8 min-w-0 max-w-[1600px]">
        <nav className="md:hidden flex gap-2 mb-4 overflow-x-auto pb-1">
          {[
            ["dashboard", "Dashboard"],
            ["all-leads", "All Leads"],
            ["settings", "Settings"],
          ].map(([id, label]) => (
            <button
              key={id}
              type="button"
              onClick={() =>
                id === "all-leads" ? goToAllLeads() : setView(id)
              }
              className={`shrink-0 px-4 py-2 rounded-xl text-sm font-semibold ${
                view === id
                  ? "bg-blue-600 text-white"
                  : "bg-white border border-blue-200 text-blue-800"
              }`}
            >
              {label}
            </button>
          ))}
        </nav>

        <ConnectionBanner
          message={apiError}
          onRetry={() => {
            fetchAnalytics();
            if (view === "all-leads") fetchAllLeads();
          }}
        />

        {crmConfigured === false && view !== "settings" && (
          <div className="mb-6 rounded-2xl border border-blue-200 bg-blue-50/90 px-5 py-4 text-blue-900 shadow-sm">
            <p className="text-sm font-medium">
              CRM credentials are not set. Open CRM Settings to connect before
              syncing leads.
            </p>
            <button
              type="button"
              onClick={() => setView("settings")}
              className="mt-3 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 shadow-md"
            >
              Open CRM Settings
            </button>
          </div>
        )}

        {analytics.ml_status?.warning && view !== "settings" && (
          <div className="mb-6 rounded-2xl border border-amber-300 bg-amber-50/95 px-5 py-4 text-amber-900 shadow-sm">
            <p className="text-sm font-medium">{analytics.ml_status.warning}</p>
            <p className="text-xs mt-2 text-amber-800">
              Completed leads: {analytics.ml_status.completed_leads}
              {analytics.ml_status.model_version
                ? ` · Model: ${analytics.ml_status.model_version}`
                : ""}
              {analytics.ml_status.training_in_progress
                ? " · Training in progress…"
                : ""}
            </p>
          </div>
        )}

        {view === "settings" ? (
          <CrmConfigForm
            onConfigured={(config) => {
              setCrmConfigured(Boolean(config?.configured));
              setView("dashboard");
            }}
          />
        ) : view === "dashboard" ? (
          <DashboardView
            analytics={analytics}
            analyticsLoading={analyticsLoading}
            fetchQuantity={fetchQuantity}
            onQuantityChange={setFetchQuantity}
            onStartSync={startScraping}
            syncRunning={syncRunning}
            onShowAllLeads={goToAllLeads}
            lookupId={lookupId}
            onLookupIdChange={setLookupId}
            onLookupSubmit={scoreLeadById}
            lookupLoading={lookupLoading}
            onRowClick={openLeadDetail}
            onViewAllLeads={goToAllLeads}
          />
        ) : (
          <AllLeadsView
            leads={allLeads}
            onBack={() => setView("dashboard")}
            onSelectLead={openLeadDetail}
            syncToolbarProps={{
              fetchQuantity,
              onQuantityChange: setFetchQuantity,
              onStartSync: startScraping,
              syncDisabled: syncRunning,
              onShowAllLeads: goToAllLeads,
              lookupId,
              onLookupIdChange: setLookupId,
              onLookupSubmit: scoreLeadById,
              lookupLoading,
            }}
          />
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
