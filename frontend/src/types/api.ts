export type Provider = "openai" | "gemini" | "claude";

export type SummaryStyle = "brief" | "standard" | "detailed";

export type InputType = "url" | "text";

export interface SummarizeRequest {
  input_type: InputType;
  content: string;
  providers: Provider[];
  style: SummaryStyle;
}

export interface ProviderResult {
  provider: Provider;
  model: string;
  status: "success" | "error";
  summary: string | null;
  elapsed_ms?: number;
  error?: string;
}

export interface SourceInfo {
  title: string | null;
  url: string | null;
  word_count: number;
}

export interface SummarizeResponse {
  source: SourceInfo;
  results: ProviderResult[];
}

export const PROVIDER_LABELS: Record<Provider, string> = {
  openai: "ChatGPT",
  gemini: "Gemini",
  claude: "Claude",
};

export const STYLE_LABELS: Record<SummaryStyle, string> = {
  brief: "Brief",
  standard: "Standard",
  detailed: "Detailed",
};
