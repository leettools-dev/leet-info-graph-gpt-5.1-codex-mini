from __future__ import annotations

import pytest

from infograph.core.schemas import ResearchSessionCreate, ResearchSessionUpdate, UserCreate
from infograph.stores.duckdb.session_store_duckdb import SessionStoreDuckDB
from infograph.stores.duckdb.user_store_duckdb import UserStoreDuckDB


@pytest.mark.asyncio
async def test_session_store_crud(duckdb_settings):
    user_store = UserStoreDuckDB(duckdb_settings)
    session_store = SessionStoreDuckDB(duckdb_settings)

    user = await user_store.create(UserCreate(email="a@b.com", name="Test", google_id="google-123"))
    session = await session_store.create(ResearchSessionCreate(prompt="test prompt"), user.user_id)

    assert session.prompt == "test prompt"

    refreshed = await session_store.get(session.session_id)
    assert refreshed is not None
    assert refreshed.session_id == session.session_id

    sessions = await session_store.list_for_user(user.user_id)
    assert len(sessions) == 1

    updated = await session_store.update(session.session_id, ResearchSessionUpdate(status="completed"))
    assert updated.status == "completed"

    await session_store.delete(session.session_id)
    assert await session_store.get(session.session_id) is None
