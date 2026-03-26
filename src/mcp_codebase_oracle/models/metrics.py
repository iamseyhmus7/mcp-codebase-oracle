"""Metrik modelleri — karmaşıklık, coupling, maintainability."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ComplexityMetrics:
    """Bir fonksiyon/sınıf için karmaşıklık metrikleri."""

    cyclomatic: int = 1  # Cyclomatic complexity (McCabe)
    cognitive: int = 0  # Cognitive complexity (SonarQube)
    lines_of_code: int = 0  # Logical LOC
    comment_lines: int = 0  # Yorum satırları
    blank_lines: int = 0  # Boş satırlar
    parameter_count: int = 0  # Parametre sayısı
    nesting_depth: int = 0  # Maksimum iç içe geçme derinliği
    maintainability_index: float = 100.0  # 0-100, yüksek = iyi

    @property
    def is_complex(self) -> bool:
        """Karmaşıklık eşiklerini aşıyor mu?"""
        return self.cyclomatic > 10 or self.cognitive > 15 or self.nesting_depth > 4

    @property
    def complexity_level(self) -> str:
        """İnsan tarafından okunabilir karmaşıklık seviyesi."""
        if self.cyclomatic <= 5:
            return "simple"
        if self.cyclomatic <= 10:
            return "moderate"
        if self.cyclomatic <= 20:
            return "complex"
        return "very_complex"

    def to_dict(self) -> dict:
        return {
            "cyclomatic": self.cyclomatic,
            "cognitive": self.cognitive,
            "lines_of_code": self.lines_of_code,
            "nesting_depth": self.nesting_depth,
            "maintainability_index": round(self.maintainability_index, 1),
            "complexity_level": self.complexity_level,
        }


@dataclass
class CouplingMetrics:
    """Modüller arası bağlılık (coupling) metrikleri."""

    afferent: int = 0  # Ca: Modüle bağımlı modül sayısı (incoming)
    efferent: int = 0  # Ce: Modülün bağımlı olduğu modül sayısı (outgoing)

    @property
    def instability(self) -> float:
        """Robert Martin instability metriği: Ce / (Ca + Ce). 0=kararlı, 1=değişken."""
        total = self.afferent + self.efferent
        if total == 0:
            return 0.0
        return self.efferent / total

    @property
    def coupling_level(self) -> str:
        """Bağlılık seviyesi."""
        total = self.afferent + self.efferent
        if total <= 3:
            return "low"
        if total <= 8:
            return "moderate"
        if total <= 15:
            return "high"
        return "very_high"

    def to_dict(self) -> dict:
        return {
            "afferent_coupling": self.afferent,
            "efferent_coupling": self.efferent,
            "instability": round(self.instability, 3),
            "coupling_level": self.coupling_level,
        }
