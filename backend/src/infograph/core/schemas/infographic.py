from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class InfographicCreate(BaseModel):
    session_id: str
    template_type: str
    layout_data: dict[str, Any]


class Infographic(BaseModel):
    infographic_id: str
    session_id: str
    image_path: str
    template_type: str
    layout_data: dict[str, Any]
    created_at: int
