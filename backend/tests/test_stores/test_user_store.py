from __future__ import annotations

import pytest

from infograph.core.schemas import UserCreate
from infograph.stores.duckdb.user_store_duckdb import UserStoreDuckDB


@pytest.mark.asyncio
async def test_user_store_crud(duckdb_settings):
    store = UserStoreDuckDB(duckdb_settings)

    user = await store.create(UserCreate(email="user@example.com", name="Tester", google_id="google-123"))
    assert user.email == "user@example.com"

    fetched = await store.get(user.user_id)
    assert fetched is not None
    assert fetched.user_id == user.user_id

    updated = await store.update(fetched.model_copy(update={"name": "Updated"}))
    assert updated.name == "Updated"

    all_users = await store.list()
    assert any(u.user_id == user.user_id for u in all_users)

    await store.delete(user.user_id)
    assert await store.get(user.user_id) is None
