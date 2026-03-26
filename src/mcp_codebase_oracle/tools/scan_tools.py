"""Proje tarama ve indeksleme tool'ları."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_codebase_oracle.core.indexer import get_indexer
from mcp_codebase_oracle.utils.formatters import format_language_breakdown


def register_scan_tools(mcp: FastMCP) -> None:
    """Scan tool'larını MCP sunucusuna kaydet."""

    @mcp.tool()
    def scan_project(
        path: str,
        exclude_patterns: list[str] | None = None,
        max_depth: int = 50,
    ) -> str:
        """Bir projeyi tarar ve indeksler.

        Proje dizinindeki tüm kaynak dosyalarını bulur, parse eder,
        sembol ve ilişkileri çıkarır. Sonuçları cache'ler.

        Args:
            path: Proje kök dizini (mutlak veya relative path)
            exclude_patterns: Ek hariç tutma pattern'leri (gitignore formatı)
            max_depth: Maksimum dizin derinliği (default: 50)

        Returns:
            Proje özeti — dosya sayısı, dil dağılımı, framework tespiti
        """
        indexer = get_indexer()
        project = indexer.scan_project(path, exclude_patterns, max_depth)
        summary = project.to_dict()

        lines = [
            f"## 🔮 Proje Tarandı: {project.name}",
            "",
            f"- **Toplam dosya:** {project.total_files}",
            f"- **Toplam satır:** {project.total_lines:,}",
            f"- **Toplam sembol:** {project.total_symbols:,}",
            f"- **Ana dil:** {project.primary_language}",
            f"- **Test dosyası:** {len(project.get_test_files())}",
        ]

        if project.framework_hints:
            lines.append(f"- **Framework:** {', '.join(project.framework_hints)}")

        lines.append("")
        lines.append("### Dil Dağılımı")
        lines.append(format_language_breakdown(project.language_breakdown))

        return "\n".join(lines)

    @mcp.tool()
    def rescan_project(path: str) -> str:
        """Daha önce taranan projeyi günceller (incremental).

        Sadece değişen dosyaları yeniden parse eder.

        Args:
            path: Proje kök dizini

        Returns:
            Değişiklik raporu — yeni, değişen ve silinen dosyalar
        """
        indexer = get_indexer()
        result = indexer.rescan_project(path)

        if result.get("full_rescan"):
            return f"♻️ Tam yeniden tarama yapıldı — {result.get('changes_detected', 'çok')} değişiklik tespit edildi"

        return (
            f"## 🔄 Rescan Sonucu\n\n"
            f"- **Değişiklik:** {result.get('changes_detected', 0)}\n"
            f"- **Yeni dosya:** {len(result.get('new_files', []))}\n"
            f"- **Değişen dosya:** {len(result.get('modified_files', []))}\n"
            f"- **Silinen dosya:** {len(result.get('deleted_files', []))}"
        )

    @mcp.tool()
    def get_project_summary(path: str) -> str:
        """Taranan projenin genel özetini döndürür.

        Önce scan_project ile projeyi tarayın, sonra bu tool ile özet alın.

        Args:
            path: Proje kök dizini

        Returns:
            Proje özeti — dil, dosya sayısı, satır, metrikler
        """
        indexer = get_indexer()
        project = indexer.get_project(path)

        if project is None:
            return "⚠️ Bu proje henüz taranmamış. Önce `scan_project` tool'unu kullanın."

        summary = project.to_dict()
        lines = [
            f"## 📋 Proje Özeti: {project.name}",
            "",
            "| Metrik | Değer |",
            "|--------|-------|",
            f"| Toplam dosya | {project.total_files} |",
            f"| Toplam satır | {project.total_lines:,} |",
            f"| Toplam sembol | {project.total_symbols:,} |",
            f"| Ana dil | {project.primary_language} |",
            f"| Test dosyası | {len(project.get_test_files())} |",
            f"| Framework | {', '.join(project.framework_hints) or 'Tespit edilmedi'} |",
        ]

        lines.append("")
        lines.append("### 📊 Dil Dağılımı")
        lines.append(format_language_breakdown(project.language_breakdown))

        return "\n".join(lines)
