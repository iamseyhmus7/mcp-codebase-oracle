"""Etki analizi motoru — bir değişikliğin dalga etkisini hesaplar."""

from __future__ import annotations

import logging

from mcp_codebase_oracle.models.analysis import AffectedItem, ImpactReport, RiskLevel
from mcp_codebase_oracle.models.graph import CodeGraph
from mcp_codebase_oracle.utils.mermaid import generate_impact_diagram

logger = logging.getLogger(__name__)


class ImpactAnalyzer:
    """Bir dosya veya sembol değişikliğinin etkisini analiz eder."""

    def __init__(self, graph: CodeGraph) -> None:
        self._graph = graph

    def analyze_impact(
        self,
        file_path: str,
        symbol_name: str | None = None,
        change_type: str = "modify",
    ) -> ImpactReport:
        """Değişiklik etki analizi yap."""
        report = ImpactReport(
            target_file=file_path,
            target_symbol=symbol_name,
            change_type=change_type,
        )

        # Direct dependents
        direct_files = self._graph.get_dependents(file_path)
        for dep_file in direct_files:
            report.directly_affected.append(
                AffectedItem(
                    file_path=dep_file,
                    relationship="imports",
                    description=f"Bu dosya {file_path} dosyasını import ediyor",
                )
            )

        # Symbol-level analysis if symbol provided
        if symbol_name:
            self._analyze_symbol_impact(file_path, symbol_name, report)

        # Transitive dependents (indirect)
        transitive = self._graph.get_transitive_dependents(file_path, max_depth=5)
        for dep_file in transitive:
            if dep_file not in direct_files:
                report.indirectly_affected.append(
                    AffectedItem(
                        file_path=dep_file,
                        relationship="transitive",
                        description="Transitif bağımlılık yoluyla etkilenir",
                    )
                )

        # Test files to run
        all_affected = set(direct_files) | set(transitive)
        report.test_files_to_run = [f for f in all_affected if self._is_test_file(f)]

        # Also check if target file itself has tests
        if self._is_test_file(file_path):
            report.test_files_to_run.insert(0, file_path)

        # Risk scoring
        report.risk_level = self._calculate_risk(report, change_type)
        report.risk_explanation = self._explain_risk(report)

        # Mermaid diagram
        report.mermaid_diagram = generate_impact_diagram(
            target=file_path,
            direct=[a.file_path for a in report.directly_affected],
            indirect=[a.file_path for a in report.indirectly_affected],
            risk_level=report.risk_level.value,
        )

        return report

    def what_if_delete(self, target: str, target_type: str = "file") -> dict:
        """Silme senaryosu — ne bozulur?"""
        broken_imports: list[str] = []
        broken_calls: list[str] = []
        orphaned_code: list[str] = []

        if target_type == "file":
            # Bu dosyayı import eden dosyalar
            dependents = self._graph.get_dependents(target)
            broken_imports = dependents

            # Bu dosyadaki sembolleri çağıran yerler
            symbols = self._graph.get_file_symbols(target)
            for sym in symbols:
                callers = self._graph.get_callers(sym.unique_id)
                broken_calls.extend(callers)

        elif target_type in ("function", "class"):
            # Bu sembolü çağıran/kullanan yerler
            matches = self._graph.find_symbols_by_name(target)
            for sym in matches:
                callers = self._graph.get_callers(sym.unique_id)
                broken_calls.extend(callers)
                # Bu sembolden inherit eden sınıflar
                rels = self._graph.get_relationships(sym.unique_id)
                for rel in rels:
                    if rel.get("kind") == "inherits" and rel.get("target") == sym.unique_id:
                        orphaned_code.append(rel.get("source", ""))

        safe_to_delete = len(broken_imports) == 0 and len(broken_calls) == 0
        explanation = self._explain_deletion(
            target, safe_to_delete, broken_imports, broken_calls, orphaned_code
        )

        return {
            "target": target,
            "target_type": target_type,
            "broken_imports": broken_imports,
            "broken_calls": list(set(broken_calls)),
            "orphaned_code": orphaned_code,
            "safe_to_delete": safe_to_delete,
            "explanation": explanation,
        }

    def find_dead_code(self, file_path: str | None = None) -> dict:
        """Kullanılmayan kodu tespit et."""
        unused_functions: list[str] = []
        unused_classes: list[str] = []

        symbols = (
            self._graph.get_file_symbols(file_path)
            if file_path
            else list(self._graph._symbols.values())
        )

        for sym in symbols:
            # Skip private, dunder, and test symbols
            if sym.name.startswith("_") and not sym.name.startswith("__"):
                continue
            if sym.name.startswith("test_"):
                continue

            callers = self._graph.get_callers(sym.unique_id)
            in_degree = self._graph.get_node_in_degree(sym.unique_id)

            if in_degree == 0 and not callers:
                if sym.kind.value in ("function", "method"):
                    # Skip dunder methods and main
                    if not sym.name.startswith("__") and sym.name != "main":
                        unused_functions.append(
                            f"{sym.file_path}:{sym.name} (line {sym.line_start})"
                        )
                elif sym.kind.value == "class":
                    unused_classes.append(f"{sym.file_path}:{sym.name} (line {sym.line_start})")

        return {
            "unused_functions": unused_functions,
            "unused_classes": unused_classes,
            "total_unused": len(unused_functions) + len(unused_classes),
        }

    def _analyze_symbol_impact(
        self, file_path: str, symbol_name: str, report: ImpactReport
    ) -> None:
        """Sembol seviyesinde etki analizi."""
        symbols = self._graph.find_symbols_by_name(symbol_name)
        for sym in symbols:
            if sym.file_path == file_path:
                callers = self._graph.get_callers(sym.unique_id)
                for caller_id in callers:
                    caller_sym = self._graph.get_symbol(caller_id)
                    if caller_sym:
                        report.directly_affected.append(
                            AffectedItem(
                                file_path=caller_sym.file_path,
                                symbol_name=caller_sym.name,
                                relationship="calls",
                                description=f"{caller_sym.qualified_name} bu sembolü çağırıyor",
                            )
                        )

    def _calculate_risk(self, report: ImpactReport, change_type: str) -> RiskLevel:
        """Risk seviyesini hesapla."""
        total = report.total_affected

        # Delete is always riskier
        if change_type == "delete":
            if total == 0:
                return RiskLevel.LOW
            elif total <= 3:
                return RiskLevel.MEDIUM
            elif total <= 10:
                return RiskLevel.HIGH
            return RiskLevel.CRITICAL

        # Modify/Rename
        if total == 0:
            return RiskLevel.LOW
        elif total <= 5:
            return RiskLevel.MEDIUM
        elif total <= 15:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL

    def _explain_risk(self, report: ImpactReport) -> str:
        """Risk açıklaması oluştur."""
        parts = [
            f"Bu değişiklik {len(report.directly_affected)} dosyayı doğrudan, "
            f"{len(report.indirectly_affected)} dosyayı dolaylı olarak etkileyecek."
        ]
        if report.test_files_to_run:
            parts.append(
                f"Çalıştırılması gereken {len(report.test_files_to_run)} test dosyası var."
            )
        return " ".join(parts)

    def _explain_deletion(
        self,
        target: str,
        safe: bool,
        broken_imports: list[str],
        broken_calls: list[str],
        orphaned: list[str],
    ) -> str:
        """Silme senaryosu açıklaması."""
        if safe:
            return f"✅ `{target}` güvenle silinebilir — hiçbir yer bu koda bağımlı değil."

        parts = [f"⚠️ `{target}` silinmesi risk taşıyor:"]
        if broken_imports:
            parts.append(f"- {len(broken_imports)} dosyanın import'ları bozulacak")
        if broken_calls:
            parts.append(f"- {len(broken_calls)} yerdeki çağrılar başarısız olacak")
        if orphaned:
            parts.append(f"- {len(orphaned)} kod parçası yetim kalacak")
        return "\n".join(parts)

    def _is_test_file(self, path: str) -> bool:
        """Basit test dosyası kontrolü."""
        name = path.split("/")[-1].lower()
        return (
            name.startswith("test_")
            or name.endswith("_test.py")
            or "/tests/" in path.lower()
            or "/test/" in path.lower()
        )
