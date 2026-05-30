import axios from "axios";

/** Uses Vite proxy (/api -> backend) in dev; override with VITE_API_URL if needed. */
export const API_BASE = import.meta.env.VITE_API_URL || "/api";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

export function apiErrorMessage(err) {
  if (err.code === "ECONNABORTED") {
    return "Request timed out. Is the backend running on port 8000?";
  }
  if (err.response?.data?.detail) {
    const d = err.response.data.detail;
    return typeof d === "string" ? d : JSON.stringify(d);
  }
  if (err.message === "Network Error") {
    return (
      "Cannot reach the API. Run the backend with: uvicorn app:app --reload --port 8000. " +
      "Run the UI with: cd Lead-score-dashboard && npm run dev (open http://localhost:5173, not port 8000)."
    );
  }
  return err.message || "Request failed";
}
