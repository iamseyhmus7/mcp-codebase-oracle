"""Etki analizi tool'ları — değişiklik impact, what-if, dead code."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_codebase_oracle.core.impact_analyzer import ImpactAnalyzer
from mcp_codebase_oracle.core.indexer import get_indexer


def register_impact_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def analyze_impact(
        path: str,
        file: str,
        symbol: str | None = None,
        change_type: str = "modify",
    ) -> str:
        """Bir değişikliğin etkisini analiz eder — PROJENİN KALBİ.

        Args:
            path: Proje kök dizini
            file: Değiştirilecek dosya yolu
            symbol: Değiştirilecek sembol adı (opsiyonel)
            change_type: Değişiklik türü — "modify", "delete" veya "rename"

        Returns:
            Etki raporu — etkilenen dosyalar, risk seviyesi, Mermaid diyagramı
        """
        indexer = get_indexer()
        graph = indexer.get_graph(path)
        if not graph:
            return "⚠️ Proje taranmamış."

        analyzer = ImpactAnalyzer(graph)
        report = analyzer.analyze_impact(file, symbol, change_type)
        result = report.to_dict()

        lines = [
            f"## 💥 Etki Analizi: `{file}`",
            "",
            f"**Risk:** {result['risk_level']}",
            f"**Açıklama:** {result['risk_explanation']}",
            "",
        ]

        if report.directly_affected:
            lines.append(f"### 🎯 Doğrudan Etkilenen ({len(report.directly_affected)})")
            for a in report.directly_affected:
                lines.append(f"- `{a.file_path}` — {a.description}")

        if report.indirectly_affected:
            lines.append(f"\n### 🔗 Dolaylı Etkilenen ({len(report.indirectly_affected)})")
            for a in report.indirectly_affected[:10]:
                lines.append(f"- `{a.file_path}` — {a.description}")

        if report.test_files_to_run:
            lines.append("\n### 🧪 Çalıştırılması Gereken Testler")
            for t in report.test_files_to_run:
                lines.append(f"- `{t}`")

        if report.mermaid_diagram:
            lines.append(f"\n### 📊 Etki Diyagramı\n```mermaid\n{report.mermaid_diagram}\n```")

        return "\n".join(lines)

    @mcp.tool()
    def what_if_delete(
        path: str,
        target: str,
        target_type: str = "file",
    ) -> str:
        """Bu dosyayı/fonksiyonu silersem ne olur?

        Args:
            path: Proje kök dizini
            target: Silinecek hedef (dosya yolu veya sembol adı)
            target_type: Hedef türü — "file", "function" veya "class"

        Returns:
            Silme senaryosu — bozulacak importlar, çağrılar, güvenli mi?
        """
        indexer = get_indexer()
        graph = indexer.get_graph(path)
        if not graph:
            return "⚠️ Proje taranmamış."

        analyzer = ImpactAnalyzer(graph)
        result = analyzer.what_if_delete(target, target_type)

        lines = [f"## 🗑️ Silme Senaryosu: `{target}` ({target_type})\n"]
        lines.append(result["explanation"])

        if result["broken_imports"]:
            lines.append(f"\n### ❌ Bozulacak Import'lar ({len(result['broken_imports'])})")
            for imp in result["broken_imports"][:15]:
                lines.append(f"- `{imp}`")

        if result["broken_calls"]:
            lines.append(f"\n### ❌ Bozulacak Çağrılar ({len(result['broken_calls'])})")
            for call in result["broken_calls"][:15]:
                lines.append(f"- `{call}`")

        return "\n".join(lines)

    @mcp.tool()
    def what_if_rename(
        path: str,
        target: str,
        new_name: str,
    ) -> str:
        """Bu sembolü yeniden adlandırsam nereleri değiştirmem gerekir?

        Args:
            path: Proje kök dizini
            target: Yeniden adlandırılacak sembol adı
            new_name: Yeni isim

        Returns:
            Güncellenmesi gereken dosya ve satır listesi
        """
        indexer = get_indexer()
        graph = indexer.get_graph(path)
        if not graph:
            return "⚠️ Proje taranmamış."

        matches = graph.find_symbols_by_name(target)
        if not matches:
            return f"⚠️ `{target}` sembolü bulunamadı."

        files_to_update: list[str] = []
        for sym in matches:
            callers = graph.get_callers(sym.unique_id)
            files_to_update.append(f"`{sym.file_path}` (tanımlama, satır {sym.line_start})")
            for caller_id in callers:
                caller_sym = graph.get_symbol(caller_id)
                if caller_sym:
                    files_to_update.append(
                        f"`{caller_sym.file_path}` (çağrı, `{caller_sym.name}` içinde)"
                    )

        lines = [
            f"## ✏️ Yeniden Adlandırma: `{target}` → `{new_name}`\n",
            f"**Güncellenecek yer:** {len(files_to_update)}\n",
        ]
        for f in files_to_update:
            lines.append(f"- {f}")

        return "\n".join(lines)

    @mcp.tool()
    def find_dead_code(
        path: str,
        file: str | None = None,
    ) -> str:
        """Kullanılmayan (dead) kodu tespit eder.

        Args:
            path: Proje kök dizini
            file: Belirli bir dosya (None ise tüm proje)

        Returns:
            Kullanılmayan fonksiyon, sınıf ve import listesi
        """
        indexer = get_indexer()
        graph = indexer.get_graph(path)
        if not graph:
            return "⚠️ Proje taranmamış."

        analyzer = ImpactAnalyzer(graph)
        result = analyzer.find_dead_code(file)

        if result["total_unused"] == 0:
            return "✅ Kullanılmayan kod tespit edilmedi!"

        lines = ["## 💀 Dead Code Raporu\n"]

        if result["unused_functions"]:
            lines.append(f"### Kullanılmayan Fonksiyonlar ({len(result['unused_functions'])})")
            for f in result["unused_functions"][:20]:
                lines.append(f"- `{f}`")

        if result["unused_classes"]:
            lines.append(f"\n### Kullanılmayan Sınıflar ({len(result['unused_classes'])})")
            for c in result["unused_classes"][:20]:
                lines.append(f"- `{c}`")

        lines.append(
            "\n> 💡 Not: Bu analiz statik analiz bazlıdır. "
            "Dinamik çağrılar (reflection, decorator-based routing) tespit edilemeyebilir."
        )

        return "\n".join(lines)
