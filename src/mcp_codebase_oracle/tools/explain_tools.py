"""Kod aciklama toollari - Legacy kodu anlasilir hale getiren MCP araclari."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_codebase_oracle.core.indexer import get_indexer


def register_explain_tools(mcp: FastMCP) -> None:
    """Aciklama araclarini MCP sunucusuna kaydet."""

    @mcp.tool()
    def explain_file(path: str, file_path: str, detail_level: str = "detailed") -> str:
        """Bir dosyayi insan tarafindan anlasilir sekilde aciklar.

        Args:
            path: Proje kok dizini
            file_path: Analiz edilecek dosya yolu
            detail_level: Detay seviyesi (brief, detailed, comprehensive)
        """
        indexer = get_indexer()
        project = indexer.get_project(path)
        if not project:
            return f"Proje bulunamadi: {path}. Once scan_project ile tarayin."

        graph = indexer.get_graph(path)
        if not graph:
            return "Graf bulunamadi."

        # Dosya bilgisini bul
        target_file = None
        for f in project.files:
            if f.path.endswith(file_path) or file_path in f.path:
                target_file = f
                break

        if not target_file:
            return f"Dosya bulunamadi: {file_path}"

        lines = []
        lines.append(f"# Dosya Analizi: `{target_file.path}`")
        lines.append("")
        lines.append(f"- **Dil:** {target_file.language}")
        lines.append(f"- **Boyut:** {target_file.size_bytes} byte")
        lines.append(f"- **Satir Sayisi:** {target_file.line_count}")
        lines.append("")

        # Sembolleri listele
        file_symbols = [
            s for s in project.symbols if s.file_path == target_file.path
        ]

        if file_symbols:
            classes = [s for s in file_symbols if s.kind == "class"]
            functions = [s for s in file_symbols if s.kind == "function"]
            methods = [s for s in file_symbols if s.kind == "method"]

            if classes:
                lines.append("## Siniflar")
                for c in classes:
                    doc = f" - {c.docstring[:80]}..." if c.docstring else ""
                    lines.append(f"- `{c.name}` (satir {c.start_line}){doc}")
                lines.append("")

            if functions:
                lines.append("## Fonksiyonlar")
                for fn in functions:
                    doc = f" - {fn.docstring[:80]}..." if fn.docstring else ""
                    lines.append(f"- `{fn.name}` (satir {fn.start_line}){doc}")
                lines.append("")

            if methods:
                lines.append("## Metodlar")
                for m in methods:
                    lines.append(f"- `{m.name}` (satir {m.start_line})")
                lines.append("")

        # Bagimliliklar
        deps = graph.get_dependencies(target_file.path)
        if deps:
            lines.append("## Bagimliliklari")
            for d in deps[:15]:
                lines.append(f"- `{d}`")
            lines.append("")

        return "\n".join(lines)

    @mcp.tool()
    def explain_function(
        path: str, file_path: str, function_name: str
    ) -> str:
        """Bir fonksiyonun ne yaptigini, parametrelerini ve yan etkilerini aciklar.

        Args:
            path: Proje kok dizini
            file_path: Fonksiyonun bulundugu dosya
            function_name: Aciklanacak fonksiyon adi
        """
        indexer = get_indexer()
        project = indexer.get_project(path)
        if not project:
            return f"Proje bulunamadi: {path}. Once scan_project ile tarayin."

        # Sembolu bul
        target_sym = None
        for s in project.symbols:
            if s.name == function_name and (
                file_path in s.file_path or s.file_path.endswith(file_path)
            ):
                target_sym = s
                break

        if not target_sym:
            return f"'{function_name}' fonksiyonu {file_path} icinde bulunamadi."

        lines = [
            f"# Fonksiyon: `{function_name}`",
            "",
            f"**Dosya:** `{target_sym.file_path}`",
            f"**Satir:** {target_sym.start_line} - {target_sym.end_line}",
            f"**Tur:** {target_sym.kind}",
            "",
        ]

        if target_sym.docstring:
            lines.append("## Dokumantasyon")
            lines.append(target_sym.docstring)
            lines.append("")

        if target_sym.complexity:
            lines.append(f"**Karmasiklik Skoru:** {target_sym.complexity}")

        return "\n".join(lines)

    @mcp.tool()
    def generate_onboarding_guide(path: str) -> str:
        """Yeni gelistiriciler icin projenin genel calisma mantigini anlatan bir rehber olusturur.

        Args:
            path: Proje kok dizini
        """
        indexer = get_indexer()
        project = indexer.get_project(path)
        if not project:
            return f"Proje bulunamadi: {path}. Once scan_project ile tarayin."

        lines = [
            "# Proje Onboarding Rehberi",
            "",
            f"## Genel Bakis",
            f"- **Proje:** {project.name}",
            f"- **Toplam Dosya:** {project.total_files}",
            f"- **Toplam Sembol:** {project.total_symbols}",
            "",
        ]

        # Dil dagilimi
        if project.language_stats:
            lines.append("## Dil Dagilimi")
            for lang, count in sorted(
                project.language_stats.items(), key=lambda x: -x[1]
            ):
                lines.append(f"- **{lang}:** {count} dosya")
            lines.append("")

        # Onemli dizinler
        dirs: dict[str, int] = {}
        for f in project.files:
            parts = f.path.replace("\\", "/").split("/")
            if len(parts) > 1:
                d = parts[0]
                dirs[d] = dirs.get(d, 0) + 1

        if dirs:
            lines.append("## Dizin Yapisi")
            for d, count in sorted(dirs.items(), key=lambda x: -x[1])[:8]:
                lines.append(f"- `{d}/` ({count} dosya)")
            lines.append("")

        lines.append("> Projeyi anlamaya giris noktasi dosyalarindan baslayin.")

        return "\n".join(lines)
