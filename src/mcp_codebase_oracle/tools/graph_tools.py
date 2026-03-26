"""Graf sorgulama tool'ları — dependency graph, call graph, class hierarchy."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_codebase_oracle.core.indexer import get_indexer
from mcp_codebase_oracle.utils.mermaid import generate_dependency_diagram


def register_graph_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def get_dependency_graph(
        path: str,
        root_file: str | None = None,
        depth: int = 3,
    ) -> str:
        """Modüller arası bağımlılık grafını döndürür.

        Args:
            path: Proje kök dizini
            root_file: Başlangıç dosyası (None ise tüm proje)
            depth: Maksimum derinlik

        Returns:
            Bağımlılık grafı — node listesi, edge listesi ve Mermaid diyagramı
        """
        indexer = get_indexer()
        graph = indexer.get_graph(path)
        if not graph:
            return "⚠️ Proje taranmamış."

        if root_file:
            deps = graph.get_dependencies(root_file)
            diagram = generate_dependency_diagram(
                modules=[root_file] + deps,
                dependencies=[(root_file, d) for d in deps],
                title=f"Dependencies of {root_file}",
            )
            return (
                f"## 🕸️ Bağımlılık Grafı: `{root_file}`\n\n"
                f"**Bağımlılık sayısı:** {len(deps)}\n\n"
                f"```mermaid\n{diagram}\n```\n\n"
                f"### Bağımlılıklar\n" + "\n".join(f"- `{d}`" for d in deps)
            )
        else:
            # Full project graph summary
            all_files = list(graph._file_symbols.keys())
            all_deps: list[tuple[str, str]] = []
            for f in all_files[:50]:
                deps = graph.get_dependencies(f)
                for d in deps:
                    all_deps.append((f, d))

            diagram = generate_dependency_diagram(
                modules=all_files[:30],
                dependencies=all_deps[:50],
                title="Project Dependency Graph",
            )
            return (
                f"## 🕸️ Proje Bağımlılık Grafı\n\n"
                f"**Dosya sayısı:** {len(all_files)}\n"
                f"**Bağımlılık sayısı:** {len(all_deps)}\n\n"
                f"```mermaid\n{diagram}\n```"
            )

    @mcp.tool()
    def get_call_graph(
        path: str,
        function_name: str,
        direction: str = "both",
        depth: int = 3,
    ) -> str:
        """Fonksiyon çağrı grafını döndürür.

        Args:
            path: Proje kök dizini
            function_name: Hedef fonksiyon adı
            direction: "callers" (çağıranlar), "callees" (çağrılanlar) veya "both"
            depth: Maksimum derinlik

        Returns:
            Çağrı grafı — Mermaid diyagramı ve detaylar
        """
        indexer = get_indexer()
        graph = indexer.get_graph(path)
        if not graph:
            return "⚠️ Proje taranmamış."

        matches = graph.find_symbols_by_name(function_name)
        if not matches:
            return f"⚠️ `{function_name}` fonksiyonu bulunamadı."

        lines = [f"## 📞 Çağrı Grafı: `{function_name}`\n"]

        for sym in matches[:3]:
            if direction in ("callers", "both"):
                callers = graph.get_callers(sym.unique_id)
                if callers:
                    lines.append(f"\n### 📥 Çağıranlar ({len(callers)})")
                    for c in callers:
                        lines.append(f"- `{c}`")

            if direction in ("callees", "both"):
                callees = graph.get_callees(sym.unique_id)
                if callees:
                    lines.append(f"\n### 📤 Çağrılanlar ({len(callees)})")
                    for c in callees:
                        lines.append(f"- `{c}`")

        return "\n".join(lines)

    @mcp.tool()
    def get_class_hierarchy(
        path: str,
        class_name: str | None = None,
    ) -> str:
        """Sınıf kalıtım hiyerarşisini döndürür.

        Args:
            path: Proje kök dizini
            class_name: Belirli bir sınıf (None ise tüm sınıflar)

        Returns:
            Sınıf hiyerarşisi — Mermaid class diagram
        """
        indexer = get_indexer()
        graph = indexer.get_graph(path)
        if not graph:
            return "⚠️ Proje taranmamış."

        classes = [s for s in graph._symbols.values() if s.kind.value == "class"]

        if class_name:
            classes = [c for c in classes if c.name == class_name]

        if not classes:
            return "🏛️ Sınıf bulunamadı."

        lines = ["## 🏛️ Sınıf Hiyerarşisi\n"]
        mermaid_lines = ["classDiagram"]

        for cls in classes[:20]:
            mermaid_lines.append(f"    class {cls.name}")
            rels = graph.get_relationships(cls.unique_id)
            for rel in rels:
                if rel.get("kind") == "inherits":
                    parent = rel.get("target", "").split(":")[-1]
                    mermaid_lines.append(f"    {parent} <|-- {cls.name}")

        lines.append("```mermaid\n" + "\n".join(mermaid_lines) + "\n```")
        return "\n".join(lines)

    @mcp.tool()
    def find_circular_dependencies(path: str) -> str:
        """Döngüsel bağımlılıkları tespit eder.

        Args:
            path: Proje kök dizini

        Returns:
            Tespit edilen döngüsel bağımlılık listesi ve öneriler
        """
        indexer = get_indexer()
        graph = indexer.get_graph(path)
        if not graph:
            return "⚠️ Proje taranmamış."

        cycles = graph.find_cycles()

        if not cycles:
            return "✅ Döngüsel bağımlılık tespit edilmedi — harika!"

        lines = [
            f"## ⚠️ Döngüsel Bağımlılıklar ({len(cycles)} adet)\n",
        ]

        for i, cycle in enumerate(cycles[:10], 1):
            cycle_str = " → ".join(c.split(":")[-1] for c in cycle)
            lines.append(f"**Döngü {i}:** `{cycle_str}`")

        lines.append("\n### 💡 Öneriler")
        lines.append("- Dependency Inversion Principle uygulayın")
        lines.append("- Ortak bağımlılıkları ayrı bir modüle çıkarın")
        lines.append("- Interface/protocol tabanlı soyutlama kullanın")

        return "\n".join(lines)
