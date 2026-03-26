"""Analiz rapor modelleri — impact, architecture, code smell."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(str, Enum):
    """Değişiklik risk seviyeleri."""

    LOW = "low"  # 🟢 Güvenli
    MEDIUM = "medium"  # 🟡 Dikkatli ilerle
    HIGH = "high"  # 🟠 Kapsamlı test gerekli
    CRITICAL = "critical"  # 🔴 Çok sayıda bağımlılık etkilenecek

    @property
    def emoji(self) -> str:
        emojis = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴",
        }
        return emojis.get(self.value, "⚪")


@dataclass
class AffectedItem:
    """Etkilenen bir öğe."""

    file_path: str
    symbol_name: str | None = None
    relationship: str = ""  # Nasıl etkileniyor (imports, calls, inherits)
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "symbol_name": self.symbol_name,
            "relationship": self.relationship,
            "description": self.description,
        }


@dataclass
class ImpactReport:
    """Değişiklik etki analizi raporu."""

    target_file: str
    target_symbol: str | None = None
    change_type: str = "modify"  # modify, delete, rename
    directly_affected: list[AffectedItem] = field(default_factory=list)
    indirectly_affected: list[AffectedItem] = field(default_factory=list)
    test_files_to_run: list[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    risk_explanation: str = ""
    mermaid_diagram: str = ""

    @property
    def total_affected(self) -> int:
        return len(self.directly_affected) + len(self.indirectly_affected)

    def to_dict(self) -> dict:
        return {
            "target_file": self.target_file,
            "target_symbol": self.target_symbol,
            "change_type": self.change_type,
            "risk_level": f"{self.risk_level.emoji} {self.risk_level.value}",
            "risk_explanation": self.risk_explanation,
            "directly_affected": [a.to_dict() for a in self.directly_affected],
            "indirectly_affected": [a.to_dict() for a in self.indirectly_affected],
            "test_files_to_run": self.test_files_to_run,
            "total_affected": self.total_affected,
            "mermaid_diagram": self.mermaid_diagram,
        }


@dataclass
class ArchitectureReport:
    """Mimari tespit raporu."""

    pattern: str  # MVC, Layered, Hexagonal, etc.
    confidence: float = 0.0  # 0.0 - 1.0
    evidence: list[str] = field(default_factory=list)
    layer_map: dict[str, list[str]] = field(default_factory=dict)  # layer_name -> [files]
    suggestions: list[str] = field(default_factory=list)
    mermaid_diagram: str = ""

    def to_dict(self) -> dict:
        return {
            "pattern": self.pattern,
            "confidence": round(self.confidence, 2),
            "evidence": self.evidence,
            "layer_map": self.layer_map,
            "suggestions": self.suggestions,
            "mermaid_diagram": self.mermaid_diagram,
        }


class CodeSmellCategory(str, Enum):
    """Code smell kategorileri."""

    GOD_CLASS = "god_class"
    LONG_METHOD = "long_method"
    FEATURE_ENVY = "feature_envy"
    SHOTGUN_SURGERY = "shotgun_surgery"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    DEEP_NESTING = "deep_nesting"
    DUPLICATE_CODE = "duplicate_code"
    DEAD_CODE = "dead_code"
    LARGE_FILE = "large_file"
    TOO_MANY_PARAMETERS = "too_many_parameters"


@dataclass
class CodeSmellReport:
    """Tek bir code smell tespiti."""

    category: CodeSmellCategory
    file_path: str
    symbol_name: str | None = None
    line_start: int = 0
    line_end: int = 0
    severity: RiskLevel = RiskLevel.LOW
    description: str = ""
    suggestion: str = ""

    def to_dict(self) -> dict:
        return {
            "category": self.category.value,
            "file_path": self.file_path,
            "symbol_name": self.symbol_name,
            "severity": f"{self.severity.emoji} {self.severity.value}",
            "description": self.description,
            "suggestion": self.suggestion,
            "line_start": self.line_start,
            "line_end": self.line_end,
        }
