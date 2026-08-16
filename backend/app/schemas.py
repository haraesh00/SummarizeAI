from typing import Literal

from pydantic import BaseModel, Field, field_validator


ProviderName = Literal["openai", "gemini", "claude"]
InputType = Literal["url", "text"]
SummaryStyle = Literal["brief", "standard", "detailed"]


class SummarizeRequest(BaseModel):
    input_type: InputType
    content: str = Field(min_length=1)
    providers: list[ProviderName] = Field(min_length=1)
    style: SummaryStyle

    @field_validator("providers")
    @classmethod
    def dedupe_providers(cls, providers: list[ProviderName]) -> list[ProviderName]:
        seen: set[str] = set()
        deduped: list[ProviderName] = []
        for provider in providers:
            if provider not in seen:
                seen.add(provider)
                deduped.append(provider)
        return deduped

    @field_validator("content")
    @classmethod
    def strip_content(cls, content: str) -> str:
        normalized = content.strip()
        if not normalized:
            raise ValueError("Content cannot be blank.")
        return normalized


class SourceInfo(BaseModel):
    title: str | None = None
    url: str | None = None
    word_count: int


class ProviderResultResponse(BaseModel):
    provider: ProviderName
    model: str
    status: Literal["success", "error"]
    summary: str | None = None
    elapsed_ms: int | None = None
    error: str | None = None


class SummarizeResponse(BaseModel):
    source: SourceInfo
    results: list[ProviderResultResponse]


class HealthResponse(BaseModel):
    status: str = "ok"
