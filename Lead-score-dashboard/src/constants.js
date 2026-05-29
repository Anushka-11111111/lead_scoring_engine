export const EMPTY_ANALYTICS = {
  total_leads: 0,
  hot_leads: 0,
  warm_leads: 0,
  cold_leads: 0,
  average_score: 0,
  top_leads: [],
  score_distribution: [
    { bracket: "0-19", companies: 0, leads: 0 },
    { bracket: "20-39", companies: 0, leads: 0 },
    { bracket: "40-59", companies: 0, leads: 0 },
    { bracket: "60-79", companies: 0, leads: 0 },
    { bracket: "80-100", companies: 0, leads: 0 },
  ],
  status: {
    running: false,
    processed: 0,
    total: 0,
    current_lead: null,
    completed: false,
  },
};
