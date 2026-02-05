from __future__ import annotations

import uuid

from leettools.common.utils import time_utils
from leettools.settings import SystemSettings

from infograph.core.schemas import User, UserCreate
from infograph.stores.abstract_user_store import AbstractUserStore
from infograph.stores.duckdb.base import DuckDBStoreBase
from infograph.stores.duckdb.utils import ensure_duckdb_settings


class UserStoreDuckDB(AbstractUserStore):
    def __init__(self, settings: SystemSettings | None = None) -> None:
        self.settings = ensure_duckdb_settings(settings)
        self.store = DuckDBStoreBase(User, "users", self.settings)

    async def create(self, create: UserCreate) -> User:
        now = time_utils.cur_timestamp_in_ms()
        user = User(
            user_id=str(uuid.uuid4()),
            email=create.email,
            name=create.name,
            google_id=create.google_id,
            created_at=now,
            updated_at=now,
        )
        self.store.client.insert_into_table(
            table_name=self.store.table_name,
            column_list=self.store.insert_columns,
            value_list=self.store._model_values(user),
        )
        return user

    async def get_by_google_id(self, google_id: str) -> User | None:
        row = self.store.client.fetch_one_from_table(
            table_name=self.store.table_name,
            where_clause="WHERE google_id = ?",
            value_list=[google_id],
        )
        return self.store._to_model(row)

    async def get(self, user_id: str) -> User | None:
        row = self.store.client.fetch_one_from_table(
            table_name=self.store.table_name,
            where_clause="WHERE user_id = ?",
            value_list=[user_id],
        )
        return self.store._to_model(row)

    async def list(self) -> list[User]:
        rows = self.store.client.fetch_all_from_table(
            table_name=self.store.table_name,
            where_clause="ORDER BY created_at DESC",
        )
        return [self.store._to_model(row) for row in rows if row]

    async def update(self, user: User) -> User:
        updated_user = user.model_copy(update={"updated_at": time_utils.cur_timestamp_in_ms()})
        column_map = self.store._column_value_map(updated_user)
        column_names = [name for name in column_map.keys() if name != "user_id"]
        value_list = [column_map[name] for name in column_names]
        value_list.append(updated_user.user_id)
        self.store.client.update_table(
            table_name=self.store.table_name,
            column_list=column_names,
            value_list=value_list,
            where_clause="WHERE user_id = ?",
        )
        return updated_user

    async def delete(self, user_id: str) -> None:
        self.store.client.delete_from_table(
            table_name=self.store.table_name,
            where_clause="WHERE user_id = ?",
            value_list=[user_id],
        )
