from __future__ import annotations

import pytest

from infograph.core.schemas import InfographicCreate
from infograph.stores.duckdb.infographic_store_duckdb import InfographicStoreDuckDB


def _create_payload(session_id: str) -> InfographicCreate:
    return InfographicCreate(
        session_id=session_id,
        template_type='basic',
        image_path='/tmp/infographic.png',
        layout_data={'title': 'Sample', 'bullets': ['Point A', 'Point B']},
    )


@pytest.mark.asyncio
async def test_infographic_store_operations(duckdb_settings):
    store = InfographicStoreDuckDB(duckdb_settings)

    payload = _create_payload('session-abc')
    infographic = await store.create(payload)
    assert infographic.session_id == 'session-abc'

    fetched = await store.get_for_session('session-abc')
    assert fetched is not None
    assert fetched.image_path == '/tmp/infographic.png'

    recent = await store.list_recent(limit=1)
    assert len(recent) == 1
