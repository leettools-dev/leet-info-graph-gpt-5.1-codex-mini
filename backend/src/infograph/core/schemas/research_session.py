from __future__ import annotations

from typing import Literal

from leettools.common.utils.obj_utils import add_fieldname_constants
from pydantic import BaseModel, Field


class ResearchSessionCreate(BaseModel):
    prompt: str


class ResearchSessionUpdate(BaseModel):
    status: Literal["pending", "searching", "generating", "completed", "failed"] | None = None


@add_fieldname_constants
class ResearchSession(BaseModel):
    session_id: str = Field(..., json_schema_extra={"primary_key": True})
    user_id: str = Field(..., json_schema_extra={"index": True})
    prompt: str
    status: Literal["pending", "searching", "generating", "completed", "failed"]
    created_at: int = Field(..., json_schema_extra={"db_type": "UINT64"})
    updated_at: int = Field(..., json_schema_extra={"db_type": "UINT64"})
