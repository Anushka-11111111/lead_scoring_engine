import {
  BrainCircuit,
  LayoutDashboard,
  List,
  Settings,
  Wifi,
  WifiOff,
  Loader2,
} from "lucide-react";

export default function AppSidebar({
  view,
  setView,
  goToAllLeads,
  apiError,
  crmConfigured,
  status,
}) {
  const syncRunning = status?.running;
  const processed = status?.processed ?? 0;
  const total = status?.total ?? 0;
  const progress = total > 0 ? Math.round((processed / total) * 100) : 0;

  let statusLabel = "Idle";
  let statusTone = "text-slate-500";
  if (apiError) {
    statusLabel = "API offline";
    statusTone = "text-red-600";
  } else if (crmConfigured === false) {
    statusLabel = "CRM not configured";
    statusTone = "text-amber-700";
  } else if (syncRunning) {
    statusLabel = "Sync running…";
    statusTone = "text-blue-700";
  }

  return (
    <aside className="w-[280px] shrink-0 bg-gradient-to-b from-[#dbeafe] via-[#dbeafe] to-[#bfdbfe] border-r border-blue-200/80 p-6 hidden md:flex flex-col justify-between shadow-[4px_0_24px_rgba(37,99,235,0.08)]">
      <div>
        <div className="flex items-center gap-3 mb-10">
          <div className="bg-gradient-to-br from-blue-600 to-blue-700 p-3 rounded-2xl shadow-lg shadow-blue-600/30">
            <BrainCircuit className="text-white" size={28} />
          </div>
          <div>
            <h1 className="font-bold text-2xl text-blue-800 tracking-tight">
              TOGILE CRM
            </h1>
            <p className="text-slate-600 text-sm font-medium">
              AI Lead Intelligence
            </p>
          </div>
        </div>

        <nav className="space-y-2">
          <SidebarBtn
            active={view === "dashboard"}
            onClick={() => setView("dashboard")}
            icon={<LayoutDashboard size={18} />}
          >
            Dashboard
          </SidebarBtn>
          <SidebarBtn
            active={view === "all-leads"}
            onClick={goToAllLeads}
            icon={<List size={18} />}
          >
            All Leads
          </SidebarBtn>
          <SidebarBtn
            active={view === "settings"}
            onClick={() => setView("settings")}
            icon={<Settings size={18} />}
          >
            CRM Settings
          </SidebarBtn>
        </nav>
      </div>

      <div className="space-y-4">
        {syncRunning && total > 0 && (
          <div className="dashboard-card rounded-2xl p-4">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="font-semibold text-blue-800">Sync progress</span>
              <span className="text-blue-600 font-bold">{progress}%</span>
            </div>
            <div className="h-2.5 bg-blue-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-xs text-slate-500 mt-2">
              {processed} / {total} leads
            </p>
          </div>
        )}

        <div className="dashboard-card rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-2">
            {apiError ? (
              <WifiOff size={18} className="text-red-500" />
            ) : syncRunning ? (
              <Loader2 size={18} className="text-blue-600 animate-spin" />
            ) : (
              <Wifi size={18} className="text-blue-600" />
            )}
            <p className="font-semibold text-lg text-slate-900">Backend</p>
          </div>
          <p className={`text-sm font-medium ${statusTone}`}>{statusLabel}</p>
        </div>
      </div>
    </aside>
  );
}

function SidebarBtn({ active, onClick, children, icon }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full py-3 px-4 rounded-2xl font-semibold transition-all flex items-center gap-3 ${
        active
          ? "bg-blue-600 text-white shadow-lg shadow-blue-600/25 scale-[1.02]"
          : "bg-white/90 text-slate-800 shadow-sm hover:bg-white hover:shadow-md border border-blue-100/80"
      }`}
    >
      {icon}
      {children}
    </button>
  );
}
