import asyncio
import logging
import time

from openai import AsyncOpenAI

from app.config import Settings
from app.providers.base import ProviderResult
from app.providers.prompts import build_prompts

logger = logging.getLogger(__name__)


class OpenAIProvider:
    name = "openai"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.model = settings.openai_model
        self._client: AsyncOpenAI | None = None

    def is_configured(self) -> bool:
        return bool(self._settings.openai_api_key.strip())

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)
        return self._client

    async def summarize(self, text: str, style: str) -> ProviderResult:
        if not self.is_configured():
            return ProviderResult(
                provider=self.name,
                model=self.model,
                summary=None,
                status="error",
                error="Provider is not configured",
            )

        system_prompt, user_prompt = build_prompts(text, style)
        start = time.perf_counter()

        try:
            client = self._get_client()
            response = await asyncio.wait_for(
                client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=user_prompt,
                ),
                timeout=self._settings.provider_timeout_seconds,
            )
            summary = response.output_text.strip()
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return ProviderResult(
                provider=self.name,
                model=self.model,
                summary=summary,
                status="success",
                elapsed_ms=elapsed_ms,
            )
        except asyncio.TimeoutError:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            logger.warning("OpenAI request timed out")
            return ProviderResult(
                provider=self.name,
                model=self.model,
                summary=None,
                status="error",
                error="OpenAI API request timed out.",
                elapsed_ms=elapsed_ms,
            )
        except Exception:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            logger.exception("OpenAI request failed")
            return ProviderResult(
                provider=self.name,
                model=self.model,
                summary=None,
                status="error",
                error="OpenAI API request failed.",
                elapsed_ms=elapsed_ms,
            )
