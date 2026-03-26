"""Sembol modelleri — fonksiyon, sınıf, değişken, import tanımları."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SymbolKind(str, Enum):
    """Sembol türleri."""

    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    PROPERTY = "property"
    VARIABLE = "variable"
    CONSTANT = "constant"
    IMPORT = "import"
    MODULE = "module"
    DECORATOR = "decorator"


@dataclass
class Symbol:
    """Kod sembolü — fonksiyon, sınıf, metod veya değişken."""

    name: str
    kind: SymbolKind
    file_path: str
    line_start: int
    line_end: int
    signature: str = ""
    docstring: str | None = None
    decorators: list[str] = field(default_factory=list)
    parent: str | None = None  # Enclosing class/function name
    is_exported: bool = True
    is_async: bool = False
    parameters: list[ParameterInfo] = field(default_factory=list)
    return_type: str | None = None

    @property
    def qualified_name(self) -> str:
        """Tam nitelikli sembol adı (parent.name)."""
        if self.parent:
            return f"{self.parent}.{self.name}"
        return self.name

    @property
    def unique_id(self) -> str:
        """Benzersiz sembol tanımlayıcısı (file:qualified_name)."""
        return f"{self.file_path}:{self.qualified_name}"

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "kind": self.kind.value,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "signature": self.signature,
            "docstring": self.docstring,
            "decorators": self.decorators,
            "parent": self.parent,
            "is_exported": self.is_exported,
            "is_async": self.is_async,
            "qualified_name": self.qualified_name,
        }


@dataclass
class ParameterInfo:
    """Fonksiyon parametresi bilgisi."""

    name: str
    type_hint: str | None = None
    default_value: str | None = None
    is_variadic: bool = False  # *args
    is_keyword: bool = False  # **kwargs


@dataclass
class ImportInfo:
    """Import ifadesi bilgisi."""

    module: str  # import modülü (e.g., "os.path")
    name: str | None = None  # imported name (e.g., "join") — None for "import os"
    alias: str | None = None  # "as" alias
    is_relative: bool = False  # relative import (from . import x)
    relative_level: int = 0  # relative import level (dots count)
    line: int = 0
    file_path: str = ""

    @property
    def resolved_name(self) -> str:
        """İmport edilen gerçek isim."""
        if self.alias:
            return self.alias
        if self.name:
            return self.name
        return self.module.split(".")[-1]

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "module": self.module,
            "name": self.name,
            "alias": self.alias,
            "is_relative": self.is_relative,
            "line": self.line,
        }
