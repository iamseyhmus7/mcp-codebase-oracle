"""Codebase modelleri — dosya, modül ve proje bilgileri."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mcp_codebase_oracle.models.symbols import ImportInfo, Symbol


@dataclass
class FileInfo:
    """Tek bir dosyanın analiz bilgisi."""

    path: str
    language: str
    size_bytes: int = 0
    line_count: int = 0
    symbols: list[Symbol] = field(default_factory=list)
    imports: list[ImportInfo] = field(default_factory=list)
    is_test: bool = False
    encoding: str = "utf-8"
    hash: str = ""  # Content hash for incremental re-indexing

    @property
    def filename(self) -> str:
        return Path(self.path).name

    @property
    def relative_path(self) -> str:
        """Dosya adını path'ten ayır."""
        return self.path

    @property
    def function_count(self) -> int:
        return sum(1 for s in self.symbols if s.kind.value in ("function", "method"))

    @property
    def class_count(self) -> int:
        return sum(1 for s in self.symbols if s.kind.value == "class")

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "language": self.language,
            "size_bytes": self.size_bytes,
            "line_count": self.line_count,
            "symbol_count": len(self.symbols),
            "import_count": len(self.imports),
            "is_test": self.is_test,
            "function_count": self.function_count,
            "class_count": self.class_count,
        }


@dataclass
class ModuleInfo:
    """Bir modül (Python package, JS module) bilgisi."""

    name: str
    path: str
    files: list[FileInfo] = field(default_factory=list)
    sub_modules: list[ModuleInfo] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        count = len(self.files)
        for sub in self.sub_modules:
            count += sub.total_files
        return count

    @property
    def total_lines(self) -> int:
        lines = sum(f.line_count for f in self.files)
        for sub in self.sub_modules:
            lines += sub.total_lines
        return lines

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "sub_modules": [s.name for s in self.sub_modules],
        }


@dataclass
class ProjectInfo:
    """Analiz edilmiş bir projenin tam bilgisi."""

    name: str
    root_path: str
    files: list[FileInfo] = field(default_factory=list)
    modules: list[ModuleInfo] = field(default_factory=list)
    language_breakdown: dict[str, int] = field(default_factory=dict)  # lang -> file count
    total_lines: int = 0
    total_symbols: int = 0
    framework_hints: list[str] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        return len(self.files)

    @property
    def primary_language(self) -> str:
        """En çok dosyaya sahip dil."""
        if not self.language_breakdown:
            return "unknown"
        return max(self.language_breakdown, key=self.language_breakdown.get)  # type: ignore

    def get_files_by_language(self, language: str) -> list[FileInfo]:
        """Belirli bir dildeki dosyaları döndür."""
        return [f for f in self.files if f.language == language]

    def get_test_files(self) -> list[FileInfo]:
        """Test dosyalarını döndür."""
        return [f for f in self.files if f.is_test]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "root_path": self.root_path,
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "total_symbols": self.total_symbols,
            "primary_language": self.primary_language,
            "language_breakdown": self.language_breakdown,
            "framework_hints": self.framework_hints,
            "test_file_count": len(self.get_test_files()),
        }
