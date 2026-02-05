from __future__ import annotations

import pytest

from infograph.core.schemas import MessageCreate
from infograph.stores.duckdb.message_store_duckdb import MessageStoreDuckDB


@pytest.mark.asyncio
async def test_message_store_operations(duckdb_settings):
    store = MessageStoreDuckDB(duckdb_settings)

    message = await store.create(
        MessageCreate(
            session_id='session-xyz',
            role='user',
            content='Hello world',
        )
    )

    assert message.role == 'user'

    messages = await store.list_for_session('session-xyz')
    assert len(messages) == 1

    await store.delete_for_session('session-xyz')
    assert await store.list_for_session('session-xyz') == []
