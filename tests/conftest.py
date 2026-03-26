"""Test fixtures ve configuration."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_python_code() -> str:
    """Örnek Python kodu."""
    return '''
"""Sample module for testing."""

import os
from pathlib import Path
from typing import List

CONSTANT_VALUE = 42


class BaseProcessor:
    """Base processor class."""

    def __init__(self, name: str):
        self.name = name

    def process(self, data: list) -> list:
        """Process data."""
        return [self._transform(item) for item in data]

    def _transform(self, item):
        """Transform single item."""
        return item


class DataProcessor(BaseProcessor):
    """Data processor that extends BaseProcessor."""

    def __init__(self, name: str, config: dict):
        super().__init__(name)
        self.config = config

    def process(self, data: list) -> list:
        """Override process with filtering."""
        filtered = self._filter(data)
        return super().process(filtered)

    def _filter(self, data: list) -> list:
        """Filter data based on config."""
        return [d for d in data if d is not None]


def helper_function(x: int, y: int = 10) -> int:
    """A helper function."""
    result = x + y
    return result


def main():
    """Entry point."""
    processor = DataProcessor("test", {"verbose": True})
    data = [1, 2, None, 3]
    result = processor.process(data)
    value = helper_function(len(result))
    print(f"Processed {value} items")
'''


@pytest.fixture
def tmp_python_project(tmp_path: Path, sample_python_code: str) -> Path:
    """Geçici Python projesi oluştur."""
    # Main module
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("")
    (src / "main.py").write_text(sample_python_code)

    # Utils module
    utils = src / "utils"
    utils.mkdir()
    (utils / "__init__.py").write_text("")
    (utils / "helpers.py").write_text(
        'def format_output(data):\n    """Format output."""\n    return str(data)\n'
    )

    # Tests
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "__init__.py").write_text("")
    (tests / "test_main.py").write_text("def test_helper():\n    assert True\n")

    return tmp_path


@pytest.fixture
def tmp_project_path(tmp_python_project: Path) -> str:
    """String path to temp project."""
    return str(tmp_python_project)
