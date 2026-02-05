from __future__ import annotations

from typing import Any

from leettools.common.utils.obj_utils import add_fieldname_constants
from pydantic import BaseModel, Field


class InfographicCreate(BaseModel):
    session_id: str
    template_type: str
    layout_data: dict[str, Any]


@add_fieldname_constants
class Infographic(BaseModel):
    infographic_id: str = Field(..., json_schema_extra={"primary_key": True})
    session_id: str = Field(..., json_schema_extra={"index": True})
    image_path: str
    template_type: str
    layout_data: dict[str, Any]
    created_at: int = Field(..., json_schema_extra={"db_type": "UINT64"})
