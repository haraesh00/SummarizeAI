import type { Provider, ProviderResult } from "../types/api";
import { SummaryCard } from "./SummaryCard";

interface SummaryResultsProps {
  selectedProviders: Provider[];
  results: ProviderResult[] | null;
  loading: boolean;
  onDownload: (format: "markdown" | "txt") => void;
}

export function SummaryResults({
  selectedProviders,
  results,
  loading,
  onDownload,
}: SummaryResultsProps) {
  if (!loading && !results) return null;

  const resultMap = new Map(results?.map((r) => [r.provider, r]) ?? []);

  return (
    <section aria-labelledby="results-heading" className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="results-heading" className="text-xl font-semibold text-white">
          Results
        </h2>
        {results && !loading && (
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => onDownload("markdown")}
              className="rounded-lg bg-slate-800 px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400"
            >
              Download MD
            </button>
            <button
              type="button"
              onClick={() => onDownload("txt")}
              className="rounded-lg bg-slate-800 px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400"
            >
              Download TXT
            </button>
          </div>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {selectedProviders.map((provider) => {
          const result =
            resultMap.get(provider) ??
            ({
              provider,
              model: "—",
              status: "error",
              summary: null,
              error: "No result returned.",
            } satisfies ProviderResult);

          return (
            <SummaryCard
              key={provider}
              result={result}
              loading={loading}
            />
          );
        })}
      </div>
    </section>
  );
}
