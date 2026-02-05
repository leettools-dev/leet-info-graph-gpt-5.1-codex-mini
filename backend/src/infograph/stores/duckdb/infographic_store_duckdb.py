from __future__ import annotations

import uuid

from leettools.common.utils import time_utils
from leettools.settings import SystemSettings

from infograph.core.schemas import Infographic, InfographicCreate
from infograph.stores.abstract_infographic_store import AbstractInfographicStore
from infograph.stores.duckdb.base import DuckDBStoreBase
from infograph.stores.duckdb.utils import ensure_duckdb_settings


class InfographicStoreDuckDB(AbstractInfographicStore):
    """Concrete DuckDB store for infographics."""

    def __init__(self, settings: SystemSettings | None = None) -> None:
        self.settings = ensure_duckdb_settings(settings)
        self.store = DuckDBStoreBase(Infographic, "infographics", self.settings)

    async def create(self, create: InfographicCreate) -> Infographic:
        created_at = time_utils.cur_timestamp_in_ms()
        infographic = Infographic(
            infographic_id=str(uuid.uuid4()),
            session_id=create.session_id,
            image_path=create.image_path,
            template_type=create.template_type,
            layout_data=create.layout_data,
            created_at=created_at,
        )
        self.store.client.insert_into_table(
            table_name=self.store.table_name,
            column_list=self.store.insert_columns,
            value_list=self.store._model_values(infographic),
        )
        return infographic

    async def get_for_session(self, session_id: str) -> Infographic | None:
        row = self.store.client.fetch_one_from_table(
            table_name=self.store.table_name,
            where_clause="WHERE session_id = ?",
            value_list=[session_id],
        )
        return self.store._to_model(row)

    async def list_recent(self, limit: int = 10) -> list[Infographic]:
        rows = self.store.client.fetch_all_from_table(
            table_name=self.store.table_name,
            where_clause=f"ORDER BY created_at DESC LIMIT {limit}",
        )
        return [self.store._to_model(row) for row in rows]
