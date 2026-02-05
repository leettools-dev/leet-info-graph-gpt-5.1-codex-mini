from typing import Optional

from leettools.common.utils.obj_utils import add_fieldname_constants
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str
    name: str
    google_id: str


@add_fieldname_constants
class User(BaseModel):
    user_id: str = Field(..., json_schema_extra={"primary_key": True})
    email: str = Field(..., json_schema_extra={"index": True})
    name: str
    google_id: str
    created_at: int = Field(..., json_schema_extra={"db_type": "UINT64"})
    updated_at: int = Field(..., json_schema_extra={"db_type": "UINT64"})
