from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def captured_at() -> datetime:
    return datetime(2026, 10, 21, 8, 7, tzinfo=UTC)


@pytest.fixture
def load_fixture():
    def _load(name: str):
        return json.loads((FIXTURES / name).read_text())

    return _load
