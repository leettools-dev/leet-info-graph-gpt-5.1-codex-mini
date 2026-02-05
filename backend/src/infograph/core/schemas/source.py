from __future__ import annotations

from leettools.common.utils.obj_utils import add_fieldname_constants
from pydantic import BaseModel, Field


class SourceCreate(BaseModel):
    session_id: str
    title: str
    url: str
    snippet: str
    confidence: float


@add_fieldname_constants
class Source(BaseModel):
    source_id: str = Field(..., json_schema_extra={"primary_key": True})
    session_id: str = Field(..., json_schema_extra={"index": True})
    title: str
    url: str
    snippet: str
    confidence: float
    fetched_at: int = Field(..., json_schema_extra={"db_type": "UINT64"})
