from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class MessageCreate(BaseModel):
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str


class Message(BaseModel):
    message_id: str
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: int
