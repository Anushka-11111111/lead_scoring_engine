import { useEffect, useState } from "react";
import { KeyRound, Link2, Save, ShieldCheck } from "lucide-react";
import { api, apiErrorMessage } from "../api";

const EMPTY_FORM = {
  base_url: "",
  api_key: "",
  secret_key: "",
  origin: "",
};

export default function CrmConfigForm({ onConfigured }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadConfig() {
      setLoading(true);
      try {
        const res = await api.get("/config/crm");
        if (cancelled) return;
        setStatus(res.data);
        if (res.data.configured) {
          setForm((prev) => ({
            ...prev,
            base_url: res.data.base_url || "",
            origin: res.data.origin || "",
          }));
        }
        setError(null);
      } catch (err) {
        if (!cancelled) {
          setError(apiErrorMessage(err));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadConfig();
    return () => {
      cancelled = true;
    };
  }, []);

  const updateField = (field) => (event) => {
    setForm((prev) => ({ ...prev, [field]: event.target.value }));
    setMessage(null);
    setError(null);
  };

  const handleTest = async () => {
    setTesting(true);
    setMessage(null);
    setError(null);

    try {
      await api.post("/config/crm/test", form);
      setMessage("Connection successful. You can save these credentials.");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async (event) => {
    event.preventDefault();
    setSaving(true);
    setMessage(null);
    setError(null);

    try {
      const res = await api.post("/config/crm", form);
      setStatus(res.data);
      setMessage("CRM credentials saved. The backend will use them for all sync and scoring.");
      setForm((prev) => ({
        ...prev,
        api_key: "",
        secret_key: "",
      }));
      onConfigured?.(res.data);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto rounded-3xl bg-[#dbeafe] p-8 shadow-sm">
        <p className="text-slate-600">Loading CRM settings…</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900">CRM Connection</h1>
        <p className="text-slate-500 mt-3 text-lg">
          Enter your Togile CRM credentials. These are stored on the backend and
          used for sync, scoring, and lead lookups.
        </p>
      </div>

      {status?.configured && (
        <div className="mb-6 rounded-2xl border border-green-200 bg-green-50 px-5 py-4 text-green-900">
          <p className="font-semibold">Currently connected</p>
          <p className="text-sm mt-1">
            Base URL: {status.base_url} · Origin: {status.origin}
          </p>
          <p className="text-sm mt-1 text-green-800">
            API key: {status.api_key_hint} · Secret key: {status.secret_key_hint}
          </p>
        </div>
      )}

      {error && (
        <div className="mb-6 rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-red-900 text-sm">
          {error}
        </div>
      )}

      {message && (
        <div className="mb-6 rounded-2xl border border-green-200 bg-green-50 px-5 py-4 text-green-900 text-sm">
          {message}
        </div>
      )}

      <form
        onSubmit={handleSave}
        className="rounded-3xl bg-[#dbeafe] p-8 shadow-sm space-y-6"
      >
        <Field
          label="Base URL"
          icon={<Link2 size={18} />}
          value={form.base_url}
          onChange={updateField("base_url")}
          placeholder="https://test-server.togile.com"
          type="url"
          required
        />
        <Field
          label="Origin"
          icon={<Link2 size={18} />}
          value={form.origin}
          onChange={updateField("origin")}
          placeholder="https://test-next.togile.com"
          type="url"
          required
        />
        <Field
          label="API Key"
          icon={<KeyRound size={18} />}
          value={form.api_key}
          onChange={updateField("api_key")}
          placeholder={status?.configured ? "Leave blank to keep current key" : "Your CRM API key"}
          required={!status?.configured}
        />
        <Field
          label="Secret Key"
          icon={<ShieldCheck size={18} />}
          value={form.secret_key}
          onChange={updateField("secret_key")}
          placeholder={status?.configured ? "Leave blank to keep current secret" : "Your CRM secret key"}
          required={!status?.configured}
        />

        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <button
            type="button"
            onClick={handleTest}
            disabled={
              testing ||
              saving ||
              !form.base_url ||
              !form.origin ||
              (!status?.configured && (!form.api_key || !form.secret_key))
            }
            className="rounded-2xl bg-white px-6 py-3 font-semibold text-slate-800 shadow-sm hover:bg-blue-50 disabled:opacity-50"
          >
            {testing ? "Testing…" : "Test connection"}
          </button>
          <button
            type="submit"
            disabled={saving || testing}
            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-blue-600 px-6 py-3 font-semibold text-white shadow-md hover:bg-blue-700 disabled:opacity-50"
          >
            <Save size={18} />
            {saving ? "Saving…" : "Save credentials"}
          </button>
        </div>
      </form>
    </div>
  );
}

function Field({ label, icon, value, onChange, placeholder, type = "text", required = false }) {
  return (
    <label className="block">
      <span className="mb-2 flex items-center gap-2 font-semibold text-slate-800">
        {icon}
        {label}
      </span>
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className="w-full rounded-2xl border border-blue-200 bg-white px-4 py-3 text-slate-900 shadow-sm outline-none focus:ring-2 focus:ring-blue-500"
      />
    </label>
  );
}
