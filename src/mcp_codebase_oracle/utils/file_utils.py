"""Dosya okuma/yazma, gitignore desteği, language detection."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pathspec

from mcp_codebase_oracle.config import LANGUAGE_EXTENSIONS

# Binary file markers
BINARY_EXTENSIONS: set[str] = {
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".exe",
    ".bin",
    ".dat",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".webp",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".wav",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".rar",
    ".7z",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".lock",
}


def is_binary_file(file_path: str) -> bool:
    """Dosyanın binary olup olmadığını kontrol et."""
    ext = Path(file_path).suffix.lower()
    if ext in BINARY_EXTENSIONS:
        return True

    # İçerik tabanlı kontrol (ilk 1024 byte)
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
    except (OSError, PermissionError):
        return True

    return False


def detect_language(file_path: str) -> str:
    """Dosya uzantısından dili tespit et."""
    ext = Path(file_path).suffix.lower()
    return LANGUAGE_EXTENSIONS.get(ext, "unknown")


def is_test_file(file_path: str) -> bool:
    """Dosyanın test dosyası olup olmadığını kontrol et."""
    path = Path(file_path)
    name = path.name.lower()
    parts = [p.lower() for p in path.parts]

    # File name patterns
    if name.startswith("test_") or name.endswith("_test.py"):
        return True
    if name.startswith("test") and name.endswith(".py"):
        return True
    if name.endswith(".test.js") or name.endswith(".test.ts"):
        return True
    if name.endswith(".spec.js") or name.endswith(".spec.ts"):
        return True
    if name == "conftest.py":
        return True

    # Directory patterns
    if "tests" in parts or "test" in parts or "__tests__" in parts:
        return True

    return False


def safe_read_file(file_path: str, max_size: int = 5 * 1024 * 1024) -> str | None:
    """Dosyayı güvenli oku — boyut limiti, encoding detection."""
    try:
        size = os.path.getsize(file_path)
        if size > max_size:
            return None
        if size == 0:
            return ""

        # UTF-8 dene
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            pass

        # Latin-1 fallback
        try:
            with open(file_path, encoding="latin-1") as f:
                return f.read()
        except UnicodeDecodeError:
            return None

    except (OSError, PermissionError):
        return None


def file_hash(file_path: str) -> str:
    """Dosyanın SHA256 hash'ini hesapla (incremental indexing için)."""
    try:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()[:16]
    except (OSError, PermissionError):
        return ""


def load_gitignore_spec(root_path: str) -> pathspec.PathSpec | None:
    """Proje kök dizininden .gitignore pattern'lerini yükle."""
    gitignore_path = Path(root_path) / ".gitignore"
    if not gitignore_path.exists():
        return None

    try:
        with open(gitignore_path) as f:
            return pathspec.PathSpec.from_lines("gitwildmatch", f)
    except (OSError, pathspec.PatternError):
        return None


def discover_files(
    root_path: str,
    exclude_patterns: list[str] | None = None,
    max_files: int = 100_000,
    max_depth: int = 50,
) -> list[str]:
    """Proje dizinini tarayarak tüm kaynak dosyalarını bul.

    Returns:
        Proje-relative dosya yolları listesi
    """
    root = Path(root_path).resolve()
    if not root.is_dir():
        return []

    # .gitignore + custom patterns
    gitignore_spec = load_gitignore_spec(str(root))
    extra_spec = None
    if exclude_patterns:
        try:
            extra_spec = pathspec.PathSpec.from_lines("gitwildmatch", exclude_patterns)
        except pathspec.PatternError:
            pass

    files: list[str] = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Depth check
        depth = len(Path(dirpath).relative_to(root).parts)
        if depth > max_depth:
            dirnames.clear()
            continue

        rel_dir = str(Path(dirpath).relative_to(root))

        # Filter directories
        dirnames[:] = [
            d
            for d in dirnames
            if not d.startswith(".")
            and not _is_excluded(
                f"{rel_dir}/{d}" if rel_dir != "." else d, gitignore_spec, extra_spec
            )
        ]

        for filename in filenames:
            if len(files) >= max_files:
                return files

            rel_path = str(Path(dirpath, filename).relative_to(root))

            # Skip hidden files
            if filename.startswith("."):
                continue

            # Skip excluded
            if _is_excluded(rel_path, gitignore_spec, extra_spec):
                continue

            # Skip binary
            full_path = os.path.join(dirpath, filename)
            if is_binary_file(full_path):
                continue

            files.append(rel_path.replace("\\", "/"))

    return sorted(files)


def _is_excluded(
    rel_path: str,
    gitignore_spec: pathspec.PathSpec | None,
    extra_spec: pathspec.PathSpec | None,
) -> bool:
    """Dosyanın exclude pattern'lere uyup uymadığını kontrol et."""
    if gitignore_spec and gitignore_spec.match_file(rel_path):
        return True
    if extra_spec and extra_spec.match_file(rel_path):
        return True
    return False
