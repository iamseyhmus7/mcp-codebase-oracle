"""Sorgulama tool'ları — sembol arama, dosya özeti."""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from mcp_codebase_oracle.core.indexer import get_indexer
from mcp_codebase_oracle.utils.file_utils import safe_read_file
from mcp_codebase_oracle.utils.formatters import format_markdown_table


def register_query_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def find_symbol(
        path: str,
        name: str,
        kind: str = "all",
    ) -> str:
        """Projede fonksiyon, sınıf veya değişken arar.

        Args:
            path: Proje kök dizini
            name: Aranacak sembol adı (kısmi eşleşme desteklenir)
            kind: Sembol türü filtresi — "function", "class", "method", "variable" veya "all"

        Returns:
            Eşleşen sembol listesi (dosya, satır, imza)
        """
        indexer = get_indexer()
        graph = indexer.get_graph(path)
        if not graph:
            return "⚠️ Proje taranmamış. Önce `scan_project` kullanın."

        matches = []
        for sym in graph._symbols.values():
            if name.lower() in sym.name.lower():
                if kind == "all" or sym.kind.value == kind:
                    matches.append(sym)

        if not matches:
            return f"🔍 `{name}` adında sembol bulunamadı."

        headers = ["Sembol", "Tür", "Dosya", "Satır", "İmza"]
        rows = []
        for s in matches[:30]:
            rows.append(
                [
                    s.name,
                    s.kind.value,
                    s.file_path,
                    str(s.line_start),
                    s.signature[:60] if s.signature else "-",
                ]
            )

        result = f"## 🔍 `{name}` arama sonuçları ({len(matches)} eşleşme)\n\n"
        result += format_markdown_table(headers, rows)
        return result

    @mcp.tool()
    def get_symbol_detail(
        path: str,
        file: str,
        name: str,
    ) -> str:
        """Bir sembolün detaylı bilgisini döndürür.

        Args:
            path: Proje kök dizini
            file: Dosya yolu (proje-relative)
            name: Sembol adı

        Returns:
            Sembol detayları — imza, docstring, callers, callees, karmaşıklık
        """
        indexer = get_indexer()
        graph = indexer.get_graph(path)
        if not graph:
            return "⚠️ Proje taranmamış."

        # Find symbol
        symbols = graph.get_file_symbols(file)
        target = None
        for s in symbols:
            if s.name == name:
                target = s
                break

        if not target:
            return f"⚠️ `{name}` sembolü `{file}` dosyasında bulunamadı."

        callers = graph.get_callers(target.unique_id)
        callees = graph.get_callees(target.unique_id)

        lines = [
            f"## 📌 {target.kind.value}: `{target.qualified_name}`",
            "",
            f"- **Dosya:** `{target.file_path}`",
            f"- **Satır:** {target.line_start}-{target.line_end}",
            f"- **Tür:** {target.kind.value}",
            f"- **Async:** {'Evet' if target.is_async else 'Hayır'}",
        ]

        if target.signature:
            lines.append(f"\n### İmza\n```python\n{target.signature}\n```")

        if target.docstring:
            lines.append(f"\n### Docstring\n> {target.docstring}")

        if target.decorators:
            lines.append(
                "\n### Dekoratörler\n- " + "\n- ".join(f"`@{d}`" for d in target.decorators)
            )

        if callers:
            lines.append(f"\n### 📥 Çağıran ({len(callers)})")
            for c in callers[:10]:
                lines.append(f"- `{c}`")

        if callees:
            lines.append(f"\n### 📤 Çağrılan ({len(callees)})")
            for c in callees[:10]:
                lines.append(f"- `{c}`")

        return "\n".join(lines)

    @mcp.tool()
    def get_file_overview(
        path: str,
        file: str,
    ) -> str:
        """Bir dosyanın yapısal özetini çıkarır.

        Args:
            path: Proje kök dizini
            file: Dosya yolu (proje-relative)

        Returns:
            Dosya yapısı — importlar, sınıflar, fonksiyonlar, exportlar
        """
        indexer = get_indexer()
        project = indexer.get_project(path)
        if not project:
            return "⚠️ Proje taranmamış."

        # Find file
        file_info = None
        for f in project.files:
            if f.path == file:
                file_info = f
                break

        if not file_info:
            return f"⚠️ `{file}` dosyası bulunamadı."

        lines = [
            f"## 📄 {file_info.filename}",
            "",
            f"- **Dil:** {file_info.language}",
            f"- **Satır:** {file_info.line_count}",
            f"- **Boyut:** {file_info.size_bytes:,} bytes",
            f"- **Test dosyası:** {'Evet' if file_info.is_test else 'Hayır'}",
        ]

        if file_info.imports:
            lines.append(f"\n### 📦 Import'lar ({len(file_info.imports)})")
            for imp in file_info.imports[:20]:
                if imp.name:
                    lines.append(f"- `from {imp.module} import {imp.name}`")
                else:
                    lines.append(f"- `import {imp.module}`")

        classes = [s for s in file_info.symbols if s.kind.value == "class"]
        if classes:
            lines.append(f"\n### 🏛️ Sınıflar ({len(classes)})")
            for cls in classes:
                doc = f" — {cls.docstring[:60]}..." if cls.docstring else ""
                lines.append(f"- `{cls.signature or cls.name}`{doc}")

        functions = [s for s in file_info.symbols if s.kind.value in ("function", "method")]
        if functions:
            lines.append(f"\n### ⚡ Fonksiyonlar ({len(functions)})")
            for fn in functions[:20]:
                doc = f" — {fn.docstring[:60]}..." if fn.docstring else ""
                lines.append(f"- `{fn.signature or fn.name}`{doc}")

        return "\n".join(lines)

    @mcp.tool()
    def search_code(
        path: str,
        query: str,
        file_pattern: str | None = None,
    ) -> str:
        """Proje dosyalarında metin/regex araması yapar.

        Args:
            path: Proje kök dizini
            query: Aranacak metin veya regex pattern
            file_pattern: Dosya filtresi (ör: "*.py", "src/*.ts")

        Returns:
            Eşleşen dosyalar ve satırlar
        """
        import re

        indexer = get_indexer()
        project = indexer.get_project(path)
        if not project:
            return "⚠️ Proje taranmamış."

        try:
            pattern = re.compile(query, re.IGNORECASE)
        except re.error:
            pattern = re.compile(re.escape(query), re.IGNORECASE)

        results: list[dict] = []
        for file_info in project.files:
            if file_pattern and not file_info.path.endswith(file_pattern.lstrip("*")):
                continue

            full_path = os.path.join(project.root_path, file_info.path)
            content = safe_read_file(full_path)
            if not content:
                continue

            for i, line in enumerate(content.split("\n"), 1):
                if pattern.search(line):
                    results.append(
                        {
                            "file": file_info.path,
                            "line": i,
                            "content": line.strip()[:100],
                        }
                    )
                    if len(results) >= 50:
                        break

            if len(results) >= 50:
                break

        if not results:
            return f"🔍 `{query}` için sonuç bulunamadı."

        lines = [f"## 🔍 Arama: `{query}` ({len(results)} sonuç)\n"]
        for r in results:
            lines.append(f"- **{r['file']}:{r['line']}** — `{r['content']}`")

        return "\n".join(lines)
