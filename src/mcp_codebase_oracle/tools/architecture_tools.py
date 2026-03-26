"""Mimari analiz tool'ları — pattern tespiti, coupling, code smells."""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from mcp_codebase_oracle.core.architecture_detector import ArchitectureDetector
from mcp_codebase_oracle.core.complexity_analyzer import ComplexityAnalyzer
from mcp_codebase_oracle.core.indexer import get_indexer
from mcp_codebase_oracle.utils.file_utils import safe_read_file


def register_architecture_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def detect_architecture(path: str) -> str:
        """Projenin mimari pattern'ini tespit eder.

        Args:
            path: Proje kök dizini

        Returns:
            Mimari rapor — pattern, güven skoru, kanıtlar, katman haritası, diyagram
        """
        indexer = get_indexer()
        project = indexer.get_project(path)
        if not project:
            return "⚠️ Proje taranmamış."

        detector = ArchitectureDetector()
        report = detector.detect(project)

        lines = [
            f"## 🏛️ Mimari Analiz: {project.name}\n",
            f"**Pattern:** {report.pattern}",
            f"**Güven:** {report.confidence:.0%}",
            "",
        ]

        if report.evidence:
            lines.append("### 📋 Kanıtlar")
            for e in report.evidence:
                lines.append(f"- {e}")

        if report.layer_map:
            lines.append("\n### 🗂️ Katman Haritası")
            for layer, files in report.layer_map.items():
                lines.append(f"\n**{layer}** ({len(files)} dosya)")
                for f in files[:5]:
                    lines.append(f"  - `{f}`")
                if len(files) > 5:
                    lines.append(f"  - ... ve {len(files) - 5} dosya daha")

        if report.suggestions:
            lines.append("\n### 💡 Öneriler")
            for s in report.suggestions:
                lines.append(f"- {s}")

        if report.mermaid_diagram:
            lines.append(f"\n### 📊 Mimari Diyagram\n```mermaid\n{report.mermaid_diagram}\n```")

        return "\n".join(lines)

    @mcp.tool()
    def get_module_coupling(
        path: str,
        module: str,
    ) -> str:
        """Bir modülün coupling metriklerini hesaplar.

        Args:
            path: Proje kök dizini
            module: Modül/dosya yolu

        Returns:
            Coupling metrikleri — afferent, efferent, instability
        """
        indexer = get_indexer()
        graph = indexer.get_graph(path)
        if not graph:
            return "⚠️ Proje taranmamış."

        deps = graph.get_dependencies(module)
        dependents = graph.get_dependents(module)

        afferent = len(dependents)
        efferent = len(deps)
        total = afferent + efferent
        instability = efferent / total if total > 0 else 0.0

        lines = [
            f"## 🔗 Coupling Analizi: `{module}`\n",
            "| Metrik | Değer | Açıklama |",
            "|--------|-------|----------|",
            f"| Ca (Afferent) | {afferent} | Bu modüle bağımlı modül sayısı |",
            f"| Ce (Efferent) | {efferent} | Bu modülün bağımlı olduğu modül sayısı |",
            f"| Instability | {instability:.2f} | 0=kararlı, 1=değişken |",
        ]

        if dependents:
            lines.append(f"\n### 📥 Bu modüle bağımlılar ({afferent})")
            for d in dependents[:10]:
                lines.append(f"- `{d}`")

        if deps:
            lines.append(f"\n### 📤 Bağımlılıklar ({efferent})")
            for d in deps[:10]:
                lines.append(f"- `{d}`")

        return "\n".join(lines)

    @mcp.tool()
    def detect_code_smells(
        path: str,
        file: str | None = None,
    ) -> str:
        """Kod kokularını (code smells) tespit eder.

        Args:
            path: Proje kök dizini
            file: Belirli dosya (None ise tüm proje, sadece Python)

        Returns:
            Code smell listesi — kategori, şiddet, dosya, öneri
        """
        indexer = get_indexer()
        project = indexer.get_project(path)
        if not project:
            return "⚠️ Proje taranmamış."

        analyzer = ComplexityAnalyzer()
        all_smells = []

        target_files = project.files
        if file:
            target_files = [f for f in project.files if f.path == file]

        for file_info in target_files:
            if file_info.language != "python":
                continue
            full_path = os.path.join(project.root_path, file_info.path)
            content = safe_read_file(full_path)
            if content:
                smells = analyzer.detect_smells(content, file_info.path)
                all_smells.extend(smells)

        if not all_smells:
            return "✅ Code smell tespit edilmedi — temiz kod!"

        lines = [f"## 🦨 Code Smell Raporu ({len(all_smells)} adet)\n"]

        by_category: dict[str, list] = {}
        for smell in all_smells:
            cat = smell.category.value
            by_category.setdefault(cat, []).append(smell)

        for category, smells in by_category.items():
            lines.append(f"\n### {category.replace('_', ' ').title()} ({len(smells)})")
            for s in smells[:10]:
                lines.append(
                    f"- {s.severity.emoji} `{s.file_path}"
                    f"{'::' + s.symbol_name if s.symbol_name else ''}`"
                    f" — {s.description}"
                )
                if s.suggestion:
                    lines.append(f"  💡 {s.suggestion}")

        return "\n".join(lines)
