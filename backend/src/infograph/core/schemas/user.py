from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    name: str
    google_id: str


class User(BaseModel):
    user_id: str
    email: str
    name: str
    google_id: str
    created_at: int
    updated_at: int
