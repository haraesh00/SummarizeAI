import asyncio
import logging
import time

from anthropic import AsyncAnthropic

from app.config import Settings
from app.providers.base import ProviderResult
from app.providers.prompts import build_prompts

logger = logging.getLogger(__name__)


class ClaudeProvider:
    name = "claude"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.model = settings.anthropic_model
        self._client: AsyncAnthropic | None = None

    def is_configured(self) -> bool:
        return bool(self._settings.anthropic_api_key.strip())

    def _get_client(self) -> AsyncAnthropic:
        if self._client is None:
            self._client = AsyncAnthropic(api_key=self._settings.anthropic_api_key)
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
                client.messages.create(
                    model=self.model,
                    max_tokens=1200,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                ),
                timeout=self._settings.provider_timeout_seconds,
            )
            summary = "".join(
                block.text
                for block in response.content
                if getattr(block, "type", None) == "text"
            ).strip()
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
            logger.warning("Claude request timed out")
            return ProviderResult(
                provider=self.name,
                model=self.model,
                summary=None,
                status="error",
                error="Claude API request timed out.",
                elapsed_ms=elapsed_ms,
            )
        except Exception:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            logger.exception("Claude request failed")
            return ProviderResult(
                provider=self.name,
                model=self.model,
                summary=None,
                status="error",
                error="Claude API request failed.",
                elapsed_ms=elapsed_ms,
            )
