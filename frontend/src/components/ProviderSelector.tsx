import type { Provider } from "../types/api";
import { PROVIDER_LABELS } from "../types/api";

const ALL_PROVIDERS: Provider[] = ["openai", "gemini", "claude"];

interface ProviderSelectorProps {
  selected: Provider[];
  onChange: (providers: Provider[]) => void;
  disabled?: boolean;
}

export function ProviderSelector({
  selected,
  onChange,
  disabled = false,
}: ProviderSelectorProps) {
  const toggle = (provider: Provider) => {
    if (selected.includes(provider)) {
      onChange(selected.filter((p) => p !== provider));
    } else {
      onChange([...selected, provider]);
    }
  };

  return (
    <fieldset className="space-y-2" disabled={disabled}>
      <legend className="text-sm font-medium text-slate-300">Providers</legend>
      <div className="flex flex-wrap gap-2">
        {ALL_PROVIDERS.map((provider) => {
          const isSelected = selected.includes(provider);
          return (
            <button
              key={provider}
              type="button"
              aria-pressed={isSelected}
              onClick={() => toggle(provider)}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 ${
                isSelected
                  ? "bg-emerald-600 text-white"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              } disabled:opacity-50`}
            >
              {isSelected ? "✓ " : ""}
              {PROVIDER_LABELS[provider]}
            </button>
          );
        })}
      </div>
    </fieldset>
  );
}
