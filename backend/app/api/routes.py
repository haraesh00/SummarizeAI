import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from app.config import Settings, get_settings
from app.schemas import HealthResponse, SummarizeRequest, SummarizeResponse
from app.services.summarizer import SummarizerService

logger = logging.getLogger(__name__)
router = APIRouter()


def get_summarizer_service(
    settings: Settings = Depends(get_settings),
) -> SummarizerService:
    return SummarizerService(settings)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@router.post("/api/summarize", response_model=SummarizeResponse)
async def summarize(
    request: SummarizeRequest,
    summarizer: SummarizerService = Depends(get_summarizer_service),
) -> SummarizeResponse:
    try:
        return await summarizer.summarize(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
