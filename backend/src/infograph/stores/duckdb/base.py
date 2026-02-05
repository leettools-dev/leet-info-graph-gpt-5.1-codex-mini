from __future__ import annotations

from typing import Any, Generic

from leettools.common.db.table_schema import pydantic_to_db_schema
from leettools.common.duckdb.duckdb_client import DuckDBClient
from leettools.common.duckdb.duckdb_schema_utils import (
    duckdb_data_to_pydantic_obj,
    pydantic_obj_to_duckdb_data,
)
from leettools.common.utils.obj_utils import TypeVar_BaseModel
from leettools.settings import SystemSettings

from infograph.stores.duckdb.utils import ensure_duckdb_settings, strip_db_schema

T = TypeVar_BaseModel


class DuckDBStoreBase(Generic[T]):
    """Base class for DuckDB-backed stores."""

    def __init__(self, model: type[T], table_name: str, settings: SystemSettings | None = None) -> None:
        self.model = model
        self.settings = ensure_duckdb_settings(settings)
        self.schema = pydantic_to_db_schema(self.model)
        self.insert_schema = strip_db_schema(self.schema)
        self.insert_columns = list(self.insert_schema.keys())
        self.client = DuckDBClient(self.settings, db_name=self.settings.DB_CORE)
        self.table_name = self.client.create_table_if_not_exists(
            db_schema_name=self.settings.DB_CORE,
            table_name=table_name,
            columns=self.schema,
        )

    def _to_model(self, row: dict[str, Any] | None) -> T | None:
        if row is None:
            return None
        return duckdb_data_to_pydantic_obj(row, self.model)

    def _model_values(self, obj: T) -> list[Any]:
        return pydantic_obj_to_duckdb_data(obj, self.insert_schema)

    def _column_value_map(self, obj: T) -> dict[str, Any]:
        return dict(zip(self.insert_columns, self._model_values(obj)))

    def _current_timestamp(self) -> int:
        from leettools.common.utils import time_utils

        return time_utils.cur_timestamp_in_ms()
