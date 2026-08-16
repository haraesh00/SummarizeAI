import type { InputType } from "../types/api";

interface ArticleInputProps {
  inputType: InputType;
  content: string;
  onInputTypeChange: (type: InputType) => void;
  onContentChange: (content: string) => void;
  disabled?: boolean;
}

export function ArticleInput({
  inputType,
  content,
  onInputTypeChange,
  onContentChange,
  disabled = false,
}: ArticleInputProps) {
  return (
    <section aria-labelledby="article-input-heading" className="space-y-3">
      <h2 id="article-input-heading" className="sr-only">
        Article input
      </h2>

      <div className="flex gap-2" role="tablist" aria-label="Input type">
        {(["url", "text"] as InputType[]).map((type) => (
          <button
            key={type}
            type="button"
            role="tab"
            aria-selected={inputType === type}
            disabled={disabled}
            onClick={() => onInputTypeChange(type)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 ${
              inputType === type
                ? "bg-indigo-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            } disabled:opacity-50`}
          >
            {type === "url" ? "URL" : "Text"}
          </button>
        ))}
      </div>

      {inputType === "url" ? (
        <input
          id="article-url"
          type="url"
          value={content}
          onChange={(e) => onContentChange(e.target.value)}
          disabled={disabled}
          placeholder="https://example.com/article"
          className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 disabled:opacity-50"
        />
      ) : (
        <textarea
          id="article-text"
          value={content}
          onChange={(e) => onContentChange(e.target.value)}
          disabled={disabled}
          rows={8}
          placeholder="Paste your article text here..."
          className="w-full resize-y rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 disabled:opacity-50"
        />
      )}
    </section>
  );
}
