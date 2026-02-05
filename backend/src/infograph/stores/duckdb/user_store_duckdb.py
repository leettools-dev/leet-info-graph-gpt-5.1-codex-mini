from __future__ import annotations

from typing import Any
import uuid

from leettools.common.duckdb.duckdb_client import DuckDBClient
from leettools.common.duckdb.duckdb_schema_utils import (
    duckdb_data_to_pydantic_obj,
    pydantic_obj_to_duckdb_data,
)
from leettools.common.utils import time_utils
from leettools.common.utils.obj_utils import TypeVar_BaseModel
from leettools.settings import SystemSettings

from infograph.core.schemas import User, UserCreate
from infograph.stores.abstract_user_store import AbstractUserStore
from infograph.stores.duckdb.base import DuckDBStoreBase
from infograph.stores.duckdb.utils import ensure_duckdb_settings


class UserStoreDuckDB(AbstractUserStore):
    def __init__(
        self,
        settings: SystemSettings | None = None,
    ) -> None:
        self.settings = ensure_duckdb_settings(settings)
        self.store = DuckDBStoreBase(User, "users", self.settings)

    async def create(self, create: UserCreate) -> User:
        user = User(
            user_id=str(uuid.uuid4()),
            email=create.email,
            name=create.name,
            google_id=create.google_id,
            created_at=time_utils.cur_timestamp_in_ms(),
            updated_at=time_utils.cur_timestamp_in_ms(),
        )
        self.store.client.insert_into_table(
            table_name=self.store.table_name,
            column_list=self.store.insert_columns,
            value_list=self.store._model_values(user),
        )
        return user
