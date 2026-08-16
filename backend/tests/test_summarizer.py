from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import app
from app.providers.base import ProviderResult
from app.schemas import SummarizeRequest
from app.services.summarizer import SummarizerService


@pytest.fixture
def settings() -> Settings:
    return Settings(
        openai_api_key="test-openai",
        gemini_api_key="",
        anthropic_api_key="test-anthropic",
    )


@pytest.mark.asyncio
async def test_summarizer_runs_providers_concurrently(settings: Settings):
    service = SummarizerService(settings)

    async def mock_summarize(text: str, style: str) -> ProviderResult:
        return ProviderResult(
            provider="openai",
            model="gpt-test",
            summary="Test summary",
            status="success",
            elapsed_ms=100,
        )

    with patch.object(service._providers["openai"], "summarize", new=AsyncMock(side_effect=mock_summarize)):
        with patch.object(
            service._providers["claude"],
            "summarize",
            new=AsyncMock(
                return_value=ProviderResult(
                    provider="claude",
                    model="claude-test",
                    summary=None,
                    status="error",
                    error="Provider is not configured",
                )
            ),
        ):
            request = SummarizeRequest(
                input_type="text",
                content="This is a sample article with enough words to summarize properly for testing purposes.",
                providers=["openai", "claude"],
                style="brief",
            )
            response = await service.summarize(request)

    assert response.source.word_count > 0
    assert len(response.results) == 2
    assert response.results[0].status == "success"
    assert response.results[1].status == "error"


def test_build_prompts():
    from app.providers.prompts import build_prompts

    system, user = build_prompts("Article body", "standard")
    assert "expert article summarizer" in system.lower()
    assert "Overview" in user
    assert "Article body" in user
