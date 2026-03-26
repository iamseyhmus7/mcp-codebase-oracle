"""Görselleştirme tool'ları — Mermaid diyagramlar, dependency matrix, hotspot."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_codebase_oracle.core.indexer import get_indexer
from mcp_codebase_oracle.utils.git_utils import get_hotspots


def register_visualization_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def generate_architecture_diagram(path: str, style: str = "simplified") -> str:
        """Proje mimarisi diyagramını Mermaid formatında üretir.

        Args:
            path: Proje kök dizini
            style: "detailed", "simplified" veya "layers"
        """
        indexer = get_indexer()
        project = indexer.get_project(path)
        if not project:
            return "⚠️ Proje taranmamış."

        from mcp_codebase_oracle.core.architecture_detector import ArchitectureDetector

        report = ArchitectureDetector().detect(project)

        return f"## 🏛️ Mimari Diyagram\n\n```mermaid\n{report.mermaid_diagram}\n```"

    @mcp.tool()
    def generate_dependency_matrix(path: str) -> str:
        """Bağımlılık matrisini tablo olarak üretir.

        Args:
            path: Proje kök dizini
        """
        indexer = get_indexer()
        graph = indexer.get_graph(path)
        if not graph:
            return "⚠️ Proje taranmamış."

        files = list(graph._file_symbols.keys())[:20]
        lines = ["## 📊 Bağımlılık Matrisi\n"]
        header = "| | " + " | ".join(f.split("/")[-1][:10] for f in files) + " |"
        sep = "|" + "|".join(["---"] * (len(files) + 1)) + "|"
        lines.extend([header, sep])

        for f in files:
            deps = set(graph.get_dependencies(f))
            row = f"| {f.split('/')[-1][:10]} |"
            for f2 in files:
                row += " ✓ |" if f2 in deps else " · |"
            lines.append(row)

        return "\n".join(lines)

    @mcp.tool()
    def generate_hotspot_map(path: str, top_n: int = 15) -> str:
        """Kod değişiklik sıcaklık haritasını üretir (git blame tabanlı).

        Args:
            path: Proje kök dizini
            top_n: Gösterilecek hotspot sayısı
        """
        hotspots = get_hotspots(path, top_n)
        if not hotspots:
            return "⚠️ Git geçmişi bulunamadı veya gitpython yüklü değil."

        lines = [
            "## 🔥 Hotspot Haritası\n",
            "En sık değişen dosyalar:\n",
            "| Dosya | Değişiklik | Son Değişiklik |",
            "|-------|-----------|----------------|",
        ]

        for h in hotspots:
            bar = "🟥" * min(h.change_count // 5, 10)
            lines.append(f"| `{h.file_path}` | {h.change_count} {bar} | {h.last_modified[:10]} |")

        return "\n".join(lines)
