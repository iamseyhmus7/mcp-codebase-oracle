"""Konfigürasyon yönetimi — environment variables ve default değerler."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from platformdirs import user_cache_dir

from mcp_codebase_oracle import __app_name__

# Default exclude patterns (always excluded in addition to .gitignore)
DEFAULT_EXCLUDE_PATTERNS: list[str] = [
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    "*.egg-info",
    ".oracle_cache",
]

# Language extension mapping
LANGUAGE_EXTENSIONS: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".lua": "lua",
    ".r": "r",
    ".R": "r",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".json": "json",
    ".toml": "toml",
    ".xml": "xml",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".sql": "sql",
    ".md": "markdown",
    ".rst": "restructuredtext",
}

# Supported parsable languages (languages with dedicated parsers)
PARSABLE_LANGUAGES: set[str] = {
    "python",
    # Future: "javascript", "typescript", "java", "go", "rust", "csharp"
}


@dataclass
class OracleConfig:
    """Ana konfigürasyon sınıfı — tüm ayarlar burada."""

    # Cache directory (platform-specific default)
    cache_dir: Path = field(default_factory=lambda: Path(user_cache_dir(__app_name__)))

    # Maximum file size to parse (bytes) — default 5MB
    max_file_size: int = 5 * 1024 * 1024

    # Maximum number of files to index
    max_files: int = 100_000

    # Log level
    log_level: str = "INFO"

    # Extra exclude patterns (added to defaults)
    extra_exclude_patterns: list[str] = field(default_factory=list)

    # Git integration enabled
    git_enabled: bool = True

    @property
    def exclude_patterns(self) -> list[str]:
        """Combine default and extra exclude patterns."""
        return DEFAULT_EXCLUDE_PATTERNS + self.extra_exclude_patterns

    @classmethod
    def from_env(cls) -> OracleConfig:
        """Create config from environment variables with fallback to defaults."""
        config = cls()

        if cache_dir := os.getenv("ORACLE_CACHE_DIR"):
            config.cache_dir = Path(cache_dir).expanduser()

        if max_file_size := os.getenv("ORACLE_MAX_FILE_SIZE"):
            config.max_file_size = int(max_file_size)

        if max_files := os.getenv("ORACLE_MAX_FILES"):
            config.max_files = int(max_files)

        if log_level := os.getenv("ORACLE_LOG_LEVEL"):
            config.log_level = log_level.upper()

        if exclude := os.getenv("ORACLE_EXCLUDE_PATTERNS"):
            config.extra_exclude_patterns = [p.strip() for p in exclude.split(",")]

        if git_enabled := os.getenv("ORACLE_GIT_ENABLED"):
            config.git_enabled = git_enabled.lower() in ("true", "1", "yes")

        return config


# Global config instance — lazy initialized
_config: OracleConfig | None = None


def get_config() -> OracleConfig:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = OracleConfig.from_env()
    return _config


def reset_config() -> None:
    """Reset global config (useful for testing)."""
    global _config
    _config = None
