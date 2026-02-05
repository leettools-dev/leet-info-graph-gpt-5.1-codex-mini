from __future__ import annotations

import re
from typing import Iterable, Sequence

from infograph.core.schemas import Source, SourceCreate
from infograph.stores.abstract_source_store import AbstractSourceStore
from infograph.stores.duckdb.source_store_duckdb import SourceStoreDuckDB


class SearchService:
    """Simple web search simulator that persists sources for a session."""

    def __init__(self, source_store: AbstractSourceStore | None = None) -> None:
        self.source_store = source_store or SourceStoreDuckDB()

    async def gather_sources(self, session_id: str, prompt: str) -> list[Source]:
        """Generate candidate sources related to the prompt and store them."""

        slug = self._slugify(prompt)
        template_data: list[dict[str, object]] = [
            {
                "title": f"{prompt} — Research overview",
                "url": f"https://research.example.com/{slug}/overview",
                "snippet": f"An authoritative overview of {prompt} with immediate takeaways.",
                "confidence": 0.92,
            },
            {
                "title": f"{prompt} — Expert insights",
                "url": f"https://insights.example.com/{slug}/experts",
                "snippet": f"Experts share best practices and emerging trends for {prompt}.",
                "confidence": 0.86,
            },
            {
                "title": f"{prompt} — Data & timelines",
                "url": f"https://data.example.com/{slug}/timeline",
                "snippet": f"Latest data, milestones, and forecasts that shape {prompt} initiatives.",
                "confidence": 0.79,
            },
        ]

        created_sources: list[Source] = []
        for data in template_data:
            payload = SourceCreate(
                session_id=session_id,
                title=data["title"],
                url=data["url"],
                snippet=data["snippet"],
                confidence=float(data["confidence"]),
            )
            created_sources.append(await self.source_store.create(payload))

        return created_sources

    def _slugify(self, prompt: str) -> str:
        normalized = prompt.strip().lower()
        slug = re.sub(r"[^a-z0-9]+", "-", normalized)
        return slug.strip("-") or "research"
