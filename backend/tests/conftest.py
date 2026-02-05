"""Test configuration for the Infograph service."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from leettools.settings import SystemSettings


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture
def duckdb_settings(tmp_path: Path) -> SystemSettings:
    settings = SystemSettings()
    settings.is_test = True
    settings.DATA_ROOT = str(tmp_path / "data")
    settings.LOG_ROOT = str(tmp_path / "logs")
    settings.DUCKDB_PATH = str(tmp_path / "duckdb")
    return settings
