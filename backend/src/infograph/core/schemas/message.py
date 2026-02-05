from __future__ import annotations

from typing import Literal

from leettools.common.utils.obj_utils import add_fieldname_constants
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str


@add_fieldname_constants
class Message(BaseModel):
    message_id: str = Field(..., json_schema_extra={"primary_key": True})
    session_id: str = Field(..., json_schema_extra={"index": True})
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: int = Field(..., json_schema_extra={"db_type": "UINT64"})
