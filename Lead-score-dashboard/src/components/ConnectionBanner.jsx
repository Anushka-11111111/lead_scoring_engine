export default function ConnectionBanner({ message, onRetry }) {
  if (!message) return null;

  return (
    <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 rounded-2xl border border-amber-300 bg-amber-50 px-5 py-4 text-amber-900">
      <p className="text-sm font-medium">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="shrink-0 rounded-xl bg-amber-600 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-700"
        >
          Retry connection
        </button>
      )}
    </div>
  );
}
