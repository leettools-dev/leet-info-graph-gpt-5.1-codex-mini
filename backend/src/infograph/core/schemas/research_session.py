from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


class ResearchSessionCreate(BaseModel):
    prompt: str


class ResearchSessionUpdate(BaseModel):
    status: Optional[Literal["pending", "searching", "generating", "completed", "failed"]]


class ResearchSession(BaseModel):
    session_id: str
    user_id: str
    prompt: str
    status: Literal["pending", "searching", "generating", "completed", "failed"]
    created_at: int
    updated_at: int
