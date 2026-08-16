import asyncio
import logging
import re
import uuid

from app.config import Settings
from app.providers.base import AIProvider, ProviderResult
from app.providers.claude_provider import ClaudeProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.openai_provider import OpenAIProvider
from app.schemas import (
    ProviderResultResponse,
    ProviderName,
    SourceInfo,
    SummarizeRequest,
    SummarizeResponse,
)
from app.services.article_extractor import (
    ArticleExtractionError,
    URLValidationError,
    fetch_and_extract,
)

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


class SummarizerService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._providers: dict[ProviderName, AIProvider] = {
            "openai": OpenAIProvider(settings),
            "gemini": GeminiProvider(settings),
            "claude": ClaudeProvider(settings),
        }

    def log_provider_availability(self) -> None:
        for name, provider in self._providers.items():
            status = "available" if provider.is_configured() else "not configured"
            logger.info("provider=%s status=%s model=%s", name, status, provider.model)

    async def summarize(self, request: SummarizeRequest) -> SummarizeResponse:
        request_id = uuid.uuid4().hex[:12]
        logger.info(
            "request_id=%s action=summarize providers=%s style=%s input_type=%s",
            request_id,
            request.providers,
            request.style,
            request.input_type,
        )

        if request.input_type == "url":
            if len(request.content) > self._settings.max_url_length:
                raise ValueError("URL exceeds maximum allowed length.")
            try:
                article = await fetch_and_extract(request.content, self._settings)
            except URLValidationError as exc:
                raise ValueError(str(exc)) from exc
            except ArticleExtractionError as exc:
                raise ValueError(str(exc)) from exc

            article_text = normalize_text(article.text)
            source = SourceInfo(
                title=article.title,
                url=article.url,
                word_count=len(article_text.split()),
            )
        else:
            if len(request.content) > self._settings.max_text_length:
                raise ValueError("Article text exceeds maximum allowed length.")
            article_text = normalize_text(request.content)
            if not article_text:
                raise ValueError("Content cannot be blank.")
            source = SourceInfo(
                title=None,
                url=None,
                word_count=len(article_text.split()),
            )

        selected = [self._providers[name] for name in request.providers]
        tasks = [provider.summarize(article_text, request.style) for provider in selected]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        results: list[ProviderResultResponse] = []
        for provider, raw in zip(selected, raw_results, strict=True):
            if isinstance(raw, Exception):
                logger.exception(
                    "request_id=%s provider=%s status=error",
                    request_id,
                    provider.name,
                )
                result = ProviderResult(
                    provider=provider.name,
                    model=provider.model,
                    summary=None,
                    status="error",
                    error=f"{provider.name.title()} API request failed.",
                )
            else:
                result = raw
                logger.info(
                    "request_id=%s provider=%s status=%s elapsed_ms=%s",
                    request_id,
                    result.provider,
                    result.status,
                    result.elapsed_ms,
                )

            results.append(
                ProviderResultResponse(
                    provider=result.provider,  # type: ignore[arg-type]
                    model=result.model,
                    status=result.status,  # type: ignore[arg-type]
                    summary=result.summary,
                    elapsed_ms=result.elapsed_ms,
                    error=result.error,
                )
            )

        return SummarizeResponse(source=source, results=results)
