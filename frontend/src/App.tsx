import { useState } from "react";
import { ArticleInput } from "./components/ArticleInput";
import { ProviderSelector } from "./components/ProviderSelector";
import { SummaryResults } from "./components/SummaryResults";
import {
  ApiError,
  buildDownloadContent,
  downloadText,
  summarizeArticle,
} from "./services/api";
import type {
  InputType,
  Provider,
  ProviderResult,
  SummarizeResponse,
  SummaryStyle,
} from "./types/api";
import { STYLE_LABELS } from "./types/api";

const DEFAULT_PROVIDERS: Provider[] = ["openai", "gemini", "claude"];

export default function App() {
  const [inputType, setInputType] = useState<InputType>("text");
  const [content, setContent] = useState("");
  const [providers, setProviders] = useState<Provider[]>(DEFAULT_PROVIDERS);
  const [style, setStyle] = useState<SummaryStyle>("standard");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<SummarizeResponse | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!content.trim() || providers.length === 0) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await summarizeArticle({
        input_type: inputType,
        content: content.trim(),
        providers,
        style,
      });
      setResponse(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setResponse(null);
    setError(null);
  };

  const handleDownload = (format: "markdown" | "txt") => {
    if (!response) return;
    const text = buildDownloadContent(response, format);
    downloadText(text, `summary.${format === "markdown" ? "md" : "txt"}`);
  };

  const loadingResults: ProviderResult[] = providers.map((provider) => ({
    provider,
    model: "…",
    status: "success",
    summary: null,
  }));

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 py-8">
          <h1 className="text-3xl font-bold tracking-tight text-white">
            AI Article Summarizer
          </h1>
          <p className="mt-2 text-slate-400">
            Summarize an article with ChatGPT, Gemini &amp; Claude
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-8 px-4 py-8">
        <form onSubmit={handleSubmit} className="space-y-6 rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
          <ArticleInput
            inputType={inputType}
            content={content}
            onInputTypeChange={setInputType}
            onContentChange={setContent}
            disabled={loading}
          />

          <ProviderSelector
            selected={providers}
            onChange={setProviders}
            disabled={loading}
          />

          <fieldset className="space-y-2" disabled={loading}>
            <legend className="text-sm font-medium text-slate-300">
              Summary Style
            </legend>
            <div className="flex flex-wrap gap-2">
              {(Object.keys(STYLE_LABELS) as SummaryStyle[]).map((value) => (
                <button
                  key={value}
                  type="button"
                  aria-pressed={style === value}
                  onClick={() => setStyle(value)}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 ${
                    style === value
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                  } disabled:opacity-50`}
                >
                  {STYLE_LABELS[value]}
                </button>
              ))}
            </div>
          </fieldset>

          {error && (
            <p className="rounded-lg border border-red-900/50 bg-red-950/40 px-4 py-3 text-sm text-red-300" role="alert">
              {error}
            </p>
          )}

          <div className="flex flex-wrap gap-3">
            <button
              type="submit"
              disabled={loading || !content.trim() || providers.length === 0}
              className="rounded-xl bg-indigo-600 px-6 py-3 text-sm font-semibold uppercase tracking-wide text-white transition hover:bg-indigo-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Summarizing…" : "Summarize Article"}
            </button>
            {(response || error) && (
              <button
                type="button"
                onClick={handleClear}
                disabled={loading}
                className="rounded-xl border border-slate-700 px-6 py-3 text-sm font-medium text-slate-300 transition hover:bg-slate-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 disabled:opacity-50"
              >
                Clear
              </button>
            )}
          </div>
        </form>

        <SummaryResults
          selectedProviders={providers}
          results={loading ? loadingResults : response?.results ?? null}
          loading={loading}
          onDownload={handleDownload}
        />
      </main>
    </div>
  );
}
