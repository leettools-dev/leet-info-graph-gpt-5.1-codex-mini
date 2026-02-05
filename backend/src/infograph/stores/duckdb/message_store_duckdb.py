from __future__ import annotations

import uuid

from leettools.common.utils import time_utils
from leettools.settings import SystemSettings

from infograph.core.schemas import Message, MessageCreate
from infograph.stores.abstract_message_store import AbstractMessageStore
from infograph.stores.duckdb.base import DuckDBStoreBase
from infograph.stores.duckdb.utils import ensure_duckdb_settings


class MessageStoreDuckDB(AbstractMessageStore):
    """DuckDB-backed storage for chat messages."""

    def __init__(self, settings: SystemSettings | None = None) -> None:
        self.settings = ensure_duckdb_settings(settings)
        self.store = DuckDBStoreBase(Message, "messages", self.settings)

    async def create(self, create: MessageCreate) -> Message:
        created_at = time_utils.cur_timestamp_in_ms()
        message = Message(
            message_id=str(uuid.uuid4()),
            session_id=create.session_id,
            role=create.role,
            content=create.content,
            created_at=created_at,
        )
        self.store.client.insert_into_table(
            table_name=self.store.table_name,
            column_list=self.store.insert_columns,
            value_list=self.store._model_values(message),
        )
        return message

    async def list_for_session(self, session_id: str) -> list[Message]:
        rows = self.store.client.fetch_all_from_table(
            table_name=self.store.table_name,
            where_clause="WHERE session_id = ? ORDER BY created_at ASC",
            value_list=[session_id],
        )
        return [self.store._to_model(row) for row in rows if row]

    async def delete_for_session(self, session_id: str) -> None:
        self.store.client.delete_from_table(
            table_name=self.store.table_name,
            where_clause="WHERE session_id = ?",
            value_list=[session_id],
        )
