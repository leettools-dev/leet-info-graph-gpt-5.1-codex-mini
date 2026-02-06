from __future__ import annotations

from typing import Iterable
import uuid

from leettools.common.utils import time_utils
from leettools.settings import SystemSettings

from infograph.core.schemas import (
    ResearchSession,
    ResearchSessionCreate,
    ResearchSessionUpdate,
)
from infograph.stores.abstract_session_store import AbstractSessionStore
from infograph.stores.duckdb.base import DuckDBStoreBase
from infograph.stores.duckdb.utils import ensure_duckdb_settings


class SessionStoreDuckDB(AbstractSessionStore):
    def __init__(self, settings: SystemSettings | None = None) -> None:
        self.settings = ensure_duckdb_settings(settings)
        self.store = DuckDBStoreBase(ResearchSession, "research_sessions", self.settings)

    async def create(self, create: ResearchSessionCreate, user_id: str) -> ResearchSession:
        now = time_utils.cur_timestamp_in_ms()
        session = ResearchSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            prompt=create.prompt,
            status="pending",
            created_at=now,
            updated_at=now,
        )
        self.store.client.insert_into_table(
            table_name=self.store.table_name,
            column_list=self.store.insert_columns,
            value_list=self.store._model_values(session),
        )
        return session

    async def get(self, session_id: str) -> ResearchSession | None:
        row = self.store.client.fetch_one_from_table(
            table_name=self.store.table_name,
            where_clause="WHERE session_id = ?",
            value_list=[session_id],
        )
        return self.store._to_model(row)

    async def list_for_user(
        self,
        user_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        start_timestamp: int | None = None,
        end_timestamp: int | None = None,
    ) -> Iterable[ResearchSession]:
        clauses = ["WHERE user_id = ?"]
        values: list[object] = [user_id]

        if search:
            clauses.append("AND prompt ILIKE ?")
            values.append(f"%{search}%")

        if start_timestamp is not None:
            clauses.append("AND created_at >= ?")
            values.append(start_timestamp)

        if end_timestamp is not None:
            clauses.append("AND created_at <= ?")
            values.append(end_timestamp)

        where_clause = " ".join(clauses) + " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        values.extend([limit, offset])

        rows = self.store.client.fetch_all_from_table(
            table_name=self.store.table_name,
            where_clause=where_clause,
            value_list=values,
        )
        return [self.store._to_model(row) for row in rows]

    async def update(self, session_id: str, update: ResearchSessionUpdate) -> ResearchSession:
        existing = await self.get(session_id)
        if existing is None:
            raise ValueError(f"Session {session_id} not found")
        if update.status is None:
            return existing
        updated_at = time_utils.cur_timestamp_in_ms()
        self.store.client.update_table(
            table_name=self.store.table_name,
            column_list=["status", "updated_at"],
            value_list=[update.status, updated_at, session_id],
            where_clause="WHERE session_id = ?",
        )
        return ResearchSession(
            session_id=existing.session_id,
            user_id=existing.user_id,
            prompt=existing.prompt,
            status=update.status,
            created_at=existing.created_at,
            updated_at=updated_at,
        )

    async def delete(self, session_id: str) -> None:
        self.store.client.delete_from_table(
            table_name=self.store.table_name,
            where_clause="WHERE session_id = ?",
            value_list=[session_id],
        )
