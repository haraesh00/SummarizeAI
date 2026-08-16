import type { SummarizeRequest, SummarizeResponse } from "../types/api";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function summarizeArticle(
  request: SummarizeRequest,
): Promise<SummarizeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let detail = "Request failed.";
    try {
      const body = (await response.json()) as { detail?: string | unknown[] };
      if (typeof body.detail === "string") {
        detail = body.detail;
      } else if (Array.isArray(body.detail)) {
        detail = "Invalid request.";
      }
    } catch {
      // use default message
    }
    throw new ApiError(detail, response.status);
  }

  return response.json() as Promise<SummarizeResponse>;
}

export function buildDownloadContent(
  response: SummarizeResponse,
  format: "markdown" | "txt",
): string {
  const lines: string[] = [];
  const title = response.source.title || "Article Summary";

  if (format === "markdown") {
    lines.push(`# ${title}`, "");
    if (response.source.url) {
      lines.push(`Source: ${response.source.url}`, "");
    }
    lines.push(`Word count: ${response.source.word_count}`, "");

    for (const result of response.results) {
      lines.push("", `## ${result.provider.toUpperCase()} (${result.model})`, "");
      if (result.status === "success" && result.summary) {
        lines.push(result.summary);
      } else {
        lines.push(`Error: ${result.error ?? "Unknown error"}`);
      }
    }
  } else {
    lines.push(title, "=".repeat(title.length), "");
    if (response.source.url) lines.push(`Source: ${response.source.url}`);
    lines.push(`Word count: ${response.source.word_count}`, "");

    for (const result of response.results) {
      lines.push("", `${result.provider.toUpperCase()} (${result.model})`, "-".repeat(40));
      if (result.status === "success" && result.summary) {
        lines.push(result.summary);
      } else {
        lines.push(`Error: ${result.error ?? "Unknown error"}`);
      }
    }
  }

  return lines.join("\n");
}

export function downloadText(content: string, filename: string) {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
