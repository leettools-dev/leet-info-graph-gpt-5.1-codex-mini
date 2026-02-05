from __future__ import annotations

import uuid

from leettools.common.utils import time_utils
from leettools.settings import SystemSettings

from infograph.core.schemas import Source, SourceCreate
from infograph.stores.abstract_source_store import AbstractSourceStore
from infograph.stores.duckdb.base import DuckDBStoreBase
from infograph.stores.duckdb.utils import ensure_duckdb_settings


class SourceStoreDuckDB(AbstractSourceStore):
    """DuckDB-backed storage for Source records."""

    def __init__(self, settings: SystemSettings | None = None) -> None:
        self.settings = ensure_duckdb_settings(settings)
        self.store = DuckDBStoreBase(Source, "sources", self.settings)

    async def create(self, create: SourceCreate) -> Source:
        now = time_utils.cur_timestamp_in_ms()
        source = Source(
            source_id=str(uuid.uuid4()),
            session_id=create.session_id,
            title=create.title,
            url=create.url,
            snippet=create.snippet,
            confidence=create.confidence,
            fetched_at=now,
        )
        self.store.client.insert_into_table(
            table_name=self.store.table_name,
            column_list=self.store.insert_columns,
            value_list=self.store._model_values(source),
        )
        return source

    async def list_for_session(self, session_id: str) -> list[Source]:
        rows = self.store.client.fetch_all_from_table(
            table_name=self.store.table_name,
            where_clause="WHERE session_id = ? ORDER BY fetched_at DESC",
            value_list=[session_id],
        )
        return [self.store._to_model(row) for row in rows if row]

    async def delete_for_session(self, session_id: str) -> None:
        self.store.client.delete_from_table(
            table_name=self.store.table_name,
            where_clause="WHERE session_id = ?",
            value_list=[session_id],
        )
