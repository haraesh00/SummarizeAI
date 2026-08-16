from dataclasses import dataclass
from typing import Protocol


@dataclass
class ProviderResult:
    provider: str
    model: str
    summary: str | None
    status: str
    error: str | None = None
    elapsed_ms: int | None = None


class AIProvider(Protocol):
    name: str
    model: str

    def is_configured(self) -> bool:
        ...

    async def summarize(self, text: str, style: str) -> ProviderResult:
        ...
