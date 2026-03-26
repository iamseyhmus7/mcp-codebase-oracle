"""Parser registry — dosya uzantısına göre uygun parser'ı seçer."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_codebase_oracle.parsers.base_parser import BaseParser

# Registry: language -> parser class
_PARSER_REGISTRY: dict[str, type[BaseParser]] = {}


def register_parser(language: str, parser_cls: type[BaseParser]) -> None:
    """Bir dil için parser kaydet."""
    _PARSER_REGISTRY[language] = parser_cls


def get_parser(language: str) -> BaseParser:
    """Dile göre parser instance'ı döndür. Bilinmeyen diller için generic parser kullan."""
    if language in _PARSER_REGISTRY:
        return _PARSER_REGISTRY[language]()

    # Fallback: generic parser
    from mcp_codebase_oracle.parsers.generic_parser import GenericParser

    return GenericParser()


def get_supported_languages() -> list[str]:
    """Desteklenen dilleri döndür."""
    return list(_PARSER_REGISTRY.keys())


def _auto_register() -> None:
    """Mevcut parser'ları otomatik kaydet."""
    try:
        from mcp_codebase_oracle.parsers.python_parser import PythonParser

        register_parser("python", PythonParser)
    except ImportError:
        pass


# Auto-register on import
_auto_register()
