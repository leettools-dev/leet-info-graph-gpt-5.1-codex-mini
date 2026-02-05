from __future__ import annotations

from pydantic import BaseModel


class SourceCreate(BaseModel):
    session_id: str
    title: str
    url: str
    snippet: str
    confidence: float


class Source(BaseModel):
    source_id: str
    session_id: str
    title: str
    url: str
    snippet: str
    confidence: float
    fetched_at: int
