"""Abstract base parser — tüm dil parser'ları bu sınıftan türer."""

from __future__ import annotations

from abc import ABC, abstractmethod

from mcp_codebase_oracle.models.relationships import Relationship
from mcp_codebase_oracle.models.symbols import ImportInfo, Symbol


class ParseResult:
    """Bir dosyanın parse sonucu."""

    def __init__(self) -> None:
        self.symbols: list[Symbol] = []
        self.imports: list[ImportInfo] = []
        self.relationships: list[Relationship] = []
        self.errors: list[str] = []


class BaseParser(ABC):
    """Abstract base parser — tüm dil-spesifik parser'lar bu sınıftan türer.

    Yeni bir dil eklemek için:
    1. Bu sınıfı extend et
    2. parse_file, get_supported_extensions implement et
    3. parsers/__init__.py'de registry'ye kaydet
    """

    @abstractmethod
    def parse_file(self, file_path: str, content: str) -> ParseResult:
        """Dosya içeriğini parse et ve sembol/ilişki çıkar.

        Args:
            file_path: Dosyanın proje-relative yolu
            content: Dosyanın metin içeriği

        Returns:
            ParseResult: Bulunan semboller, importlar ve ilişkiler
        """
        ...

    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        """Bu parser'ın desteklediği dosya uzantılarını döndür.

        Returns:
            Örn: [".py", ".pyi"]
        """
        ...
