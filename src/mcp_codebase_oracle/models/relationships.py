"""İlişki modelleri — semboller arası bağlantılar (call, import, inherit vb.)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RelationshipKind(str, Enum):
    """İlişki türleri."""

    CALLS = "calls"  # Fonksiyon A, Fonksiyon B'yi çağırır
    IMPORTS = "imports"  # Modül A, Modül B'yi import eder
    INHERITS = "inherits"  # Sınıf A, Sınıf B'den türer
    IMPLEMENTS = "implements"  # Sınıf A, Interface B'yi implement eder
    USES = "uses"  # Sembol A, Sembol B'yi kullanır (genel)
    DECORATES = "decorates"  # Decorator A, Sembol B'yi dekore eder
    INSTANTIATES = "instantiates"  # Fonksiyon A, Sınıf B'yi instantiate eder
    CONTAINS = "contains"  # Sınıf A, Method B'yi içerir
    DEPENDS_ON = "depends_on"  # Modül-level bağımlılık


@dataclass
class Relationship:
    """İki sembol/dosya arasındaki ilişki."""

    source: str  # Source symbol unique_id or file path
    target: str  # Target symbol unique_id or file path
    kind: RelationshipKind
    file_path: str = ""  # İlişkinin tanımlandığı dosya
    line: int = 0  # İlişkinin tanımlandığı satır
    metadata: dict = field(default_factory=dict)

    @property
    def edge_id(self) -> str:
        """Benzersiz kenar tanımlayıcısı."""
        return f"{self.source}-[{self.kind.value}]->{self.target}"

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "kind": self.kind.value,
            "file_path": self.file_path,
            "line": self.line,
            "metadata": self.metadata,
        }
