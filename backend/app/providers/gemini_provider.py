import asyncio
import logging
import time

from google import genai

from app.config import Settings
from app.providers.base import ProviderResult
from app.providers.prompts import build_prompts

logger = logging.getLogger(__name__)


class GeminiProvider:
    name = "gemini"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.model = settings.gemini_model
        self._client: genai.Client | None = None

    def is_configured(self) -> bool:
        return bool(self._settings.gemini_api_key.strip())

    def _get_client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(api_key=self._settings.gemini_api_key)
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
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        start = time.perf_counter()

        try:
            client = self._get_client()

            async def _call() -> str:
                response = await client.aio.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                )
                return (response.text or "").strip()

            summary = await asyncio.wait_for(
                _call(),
                timeout=self._settings.provider_timeout_seconds,
            )
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
            logger.warning("Gemini request timed out")
            return ProviderResult(
                provider=self.name,
                model=self.model,
                summary=None,
                status="error",
                error="Gemini API request timed out.",
                elapsed_ms=elapsed_ms,
            )
        except Exception:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            logger.exception("Gemini request failed")
            return ProviderResult(
                provider=self.name,
                model=self.model,
                summary=None,
                status="error",
                error="Gemini API request failed.",
                elapsed_ms=elapsed_ms,
            )
