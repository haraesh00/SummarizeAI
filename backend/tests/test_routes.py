from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.providers.base import ProviderResult
from app.schemas import ProviderResultResponse, SourceInfo, SummarizeResponse


@pytest.fixture
def mock_summarize_response() -> SummarizeResponse:
    return SummarizeResponse(
        source=SourceInfo(title=None, url=None, word_count=42),
        results=[
            ProviderResultResponse(
                provider="openai",
                model="gpt-4o-mini",
                status="success",
                summary="Summary text",
                elapsed_ms=500,
            )
        ],
    )


@pytest.mark.asyncio
async def test_summarize_text_request(mock_summarize_response: SummarizeResponse):
    with patch(
        "app.api.routes.SummarizerService.summarize",
        new=AsyncMock(return_value=mock_summarize_response),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/summarize",
                json={
                    "input_type": "text",
                    "content": "Sample article content for testing the summarize endpoint.",
                    "providers": ["openai"],
                    "style": "brief",
                },
            )

    assert response.status_code == 200
    data = response.json()
    assert data["source"]["word_count"] == 42
    assert data["results"][0]["provider"] == "openai"
    assert data["results"][0]["status"] == "success"


@pytest.mark.asyncio
async def test_summarize_missing_providers():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/summarize",
            json={
                "input_type": "text",
                "content": "Sample content",
                "providers": [],
                "style": "brief",
            },
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_summarize_invalid_style():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/summarize",
            json={
                "input_type": "text",
                "content": "Sample content",
                "providers": ["openai"],
                "style": "invalid",
            },
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_summarize_validation_error():
    with patch(
        "app.api.routes.SummarizerService.summarize",
        new=AsyncMock(side_effect=ValueError("Unable to extract article text from the supplied URL.")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/summarize",
                json={
                    "input_type": "url",
                    "content": "https://example.com/bad",
                    "providers": ["openai"],
                    "style": "standard",
                },
            )
    assert response.status_code == 400
    assert "extract" in response.json()["detail"].lower()
