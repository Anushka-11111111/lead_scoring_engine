export default function StatCard({
  title,
  value,
  subtitle,
  icon,
  accent = "blue",
  trend,
}) {
  const accents = {
    blue: {
      icon: "bg-gradient-to-br from-blue-600 to-blue-700 text-white shadow-blue-600/30",
      ring: "ring-blue-100",
    },
    yellow: {
      icon: "bg-gradient-to-br from-yellow-400 to-amber-400 text-slate-900 shadow-amber-400/30",
      ring: "ring-amber-100",
    },
    sky: {
      icon: "bg-gradient-to-br from-sky-400 to-blue-400 text-white shadow-sky-400/30",
      ring: "ring-sky-100",
    },
    slate: {
      icon: "bg-gradient-to-br from-slate-600 to-slate-700 text-white",
      ring: "ring-slate-100",
    },
  };

  const style = accents[accent] || accents.blue;

  return (
    <div
      className={`dashboard-card rounded-3xl p-6 ring-1 ${style.ring} hover:shadow-lg hover:shadow-blue-500/10 transition-shadow duration-300`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-slate-500 text-sm font-semibold uppercase tracking-wide">
            {title}
          </p>
          <h2 className="text-4xl font-bold mt-2 text-slate-900 tabular-nums">
            {value}
          </h2>
          {subtitle && (
            <p className="text-slate-500 text-sm mt-1">{subtitle}</p>
          )}
          {trend != null && (
            <p className="text-blue-700 text-sm font-semibold mt-2">{trend}</p>
          )}
        </div>
        <div
          className={`w-14 h-14 shrink-0 rounded-2xl flex items-center justify-center shadow-lg ${style.icon}`}
        >
          {icon}
        </div>
      </div>
    </div>
  );
}
