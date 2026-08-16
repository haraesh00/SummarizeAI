import type { ProviderResult } from "../types/api";
import { PROVIDER_LABELS } from "../types/api";

interface SummaryCardProps {
  result: ProviderResult;
  loading?: boolean;
}

export function SummaryCard({ result, loading = false }: SummaryCardProps) {
  const label = PROVIDER_LABELS[result.provider];

  const copySummary = async () => {
    if (!result.summary) return;
    await navigator.clipboard.writeText(result.summary);
  };

  if (loading) {
    return (
      <article
        aria-busy="true"
        aria-label={`${label} loading`}
        className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5"
      >
        <div className="mb-3 h-5 w-24 animate-pulse rounded bg-slate-700" />
        <div className="space-y-2">
          <div className="h-4 w-full animate-pulse rounded bg-slate-800" />
          <div className="h-4 w-5/6 animate-pulse rounded bg-slate-800" />
          <div className="h-4 w-4/6 animate-pulse rounded bg-slate-800" />
        </div>
      </article>
    );
  }

  return (
    <article
      aria-label={`${label} summary`}
      className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg shadow-black/20"
    >
      <header className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-lg font-semibold text-white">{label}</h3>
        <div className="flex flex-wrap gap-3 text-xs text-slate-400">
          <span>Model: {result.model}</span>
          {result.elapsed_ms != null && <span>Time: {result.elapsed_ms} ms</span>}
        </div>
      </header>

      {result.status === "success" && result.summary ? (
        <>
          <div className="max-h-80 overflow-y-auto whitespace-pre-wrap text-sm leading-relaxed text-slate-200">
            {result.summary}
          </div>
          <button
            type="button"
            onClick={copySummary}
            className="mt-4 rounded-lg bg-slate-800 px-3 py-1.5 text-sm text-slate-200 transition hover:bg-slate-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400"
          >
            Copy
          </button>
        </>
      ) : (
        <p className="text-sm text-red-400" role="alert">
          {result.error ?? "An error occurred."}
        </p>
      )}
    </article>
  );
}
