from __future__ import annotations

from pathlib import Path

from leettools.settings import SystemSettings


def ensure_duckdb_settings(
    settings: SystemSettings | None = None,
    base_dir: Path | None = None,
) -> SystemSettings:
    """Ensure SystemSettings have DuckDB configuration and required directories."""

    settings = settings or SystemSettings()
    base_dir = base_dir or Path.cwd()

    if not settings.DATA_ROOT:
        settings.DATA_ROOT = str((base_dir / "data").resolve())
    if not settings.LOG_ROOT:
        settings.LOG_ROOT = str((Path(settings.DATA_ROOT) / "logs").resolve())
    if not settings.DUCKDB_PATH:
        settings.DUCKDB_PATH = str((Path(settings.DATA_ROOT) / "duckdb").resolve())

    Path(settings.DUCKDB_PATH).mkdir(parents=True, exist_ok=True)

    return settings


def strip_db_schema(schema: dict[str, str]) -> dict[str, str]:
    """Return only the real columns from a DuckDB schema definition."""

    return {
        name: definition
        for name, definition in schema.items()
        if name != "PRIMARY KEY" and not name.startswith("INDEX_")
    }
