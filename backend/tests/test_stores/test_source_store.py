from __future__ import annotations

import pytest

from infograph.core.schemas import SourceCreate
from infograph.stores.duckdb.source_store_duckdb import SourceStoreDuckDB


@pytest.mark.asyncio
async def test_source_store_crud(duckdb_settings):
    store = SourceStoreDuckDB(duckdb_settings)

    source = await store.create(
        SourceCreate(
            session_id='session-123',
            title='Research Source',
            url='https://example.com',
            snippet='Example snippet',
            confidence=0.85,
        )
    )

    assert source.session_id == 'session-123'

    results = await store.list_for_session('session-123')
    assert len(results) == 1

    await store.delete_for_session('session-123')
    assert await store.list_for_session('session-123') == []
