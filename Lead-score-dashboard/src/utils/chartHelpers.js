/** Derive chart-ready datasets from analytics API payload */

export function buildPieData(analytics) {
  return [
    { name: "Hot", value: analytics.hot_leads || 0, fill: "#2563eb" },
    { name: "Warm", value: analytics.warm_leads || 0, fill: "#facc15" },
    { name: "Cold", value: analytics.cold_leads || 0, fill: "#93c5fd" },
  ];
}

export function buildScoreDistribution(analytics) {
  if (analytics.score_distribution?.length > 0) {
    return analytics.score_distribution;
  }
  return [
    { bracket: "0-19", companies: 0, leads: 0 },
    { bracket: "20-39", companies: 0, leads: 0 },
    { bracket: "40-59", companies: 0, leads: 0 },
    { bracket: "60-79", companies: 0, leads: 0 },
    { bracket: "80-100", companies: 0, leads: 0 },
  ];
}

export function buildRuleVsMlData(leads = []) {
  return leads
    .filter((l) => l.ml_active && l.ml_score != null)
    .slice(0, 8)
    .map((l) => ({
      name: (l.name || l.lead_id || "").slice(0, 12),
      rule: l.score ?? 0,
      ml: l.ml_score ?? 0,
    }));
}

export function buildMlProgress(mlStatus) {
  const completed = mlStatus?.completed_leads ?? 0;
  const target = mlStatus?.mature_threshold ?? 3000;
  const trainAt = mlStatus?.training_threshold ?? 100;
  const pct = Math.min(100, Math.round((completed / target) * 100));
  return { completed, target, trainAt, pct };
}

export function hotRate(analytics) {
  const total = analytics.total_leads || 0;
  if (!total) return 0;
  return Math.round(((analytics.hot_leads || 0) / total) * 100);
}
