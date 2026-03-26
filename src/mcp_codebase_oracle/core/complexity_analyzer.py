"""Karmaşıklık analizi motoru — cyclomatic, cognitive complexity, code smells."""

from __future__ import annotations

import ast
import logging

from mcp_codebase_oracle.models.analysis import CodeSmellCategory, CodeSmellReport, RiskLevel
from mcp_codebase_oracle.models.metrics import ComplexityMetrics

logger = logging.getLogger(__name__)


class ComplexityAnalyzer:
    """AST tabanlı karmaşıklık metrikleri ve code smell tespiti."""

    def analyze_function(self, source: str, function_name: str | None = None) -> ComplexityMetrics:
        """Fonksiyon karmaşıklığını analiz et."""
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return ComplexityMetrics()

        # Find the target function
        target = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if function_name is None or node.name == function_name:
                    target = node
                    break

        if target is None:
            return ComplexityMetrics()

        cyclomatic = self._cyclomatic_complexity(target)
        cognitive = self._cognitive_complexity(target)
        nesting = self._max_nesting_depth(target)
        loc = (target.end_lineno or target.lineno) - target.lineno + 1
        param_count = len(target.args.args)

        # Maintainability Index (simplified Microsoft formula)
        import math

        volume = loc * math.log2(max(cyclomatic, 1)) if loc > 0 else 0
        mi = max(
            0,
            (
                171
                - 5.2 * math.log(max(volume, 1))
                - 0.23 * cyclomatic
                - 16.2 * math.log(max(loc, 1))
            )
            * 100
            / 171,
        )

        return ComplexityMetrics(
            cyclomatic=cyclomatic,
            cognitive=cognitive,
            lines_of_code=loc,
            parameter_count=param_count,
            nesting_depth=nesting,
            maintainability_index=mi,
        )

    def detect_smells(self, source: str, file_path: str) -> list[CodeSmellReport]:
        """Code smell'leri tespit et."""
        smells: list[CodeSmellReport] = []

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return smells

        lines = source.split("\n")

        # Large file check
        if len(lines) > 500:
            smells.append(
                CodeSmellReport(
                    category=CodeSmellCategory.LARGE_FILE,
                    file_path=file_path,
                    severity=RiskLevel.MEDIUM if len(lines) < 1000 else RiskLevel.HIGH,
                    description=f"Dosya {len(lines)} satır — çok büyük",
                    suggestion="Dosyayı daha küçük modüllere böl",
                )
            )

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                # Long method
                func_lines = (node.end_lineno or node.lineno) - node.lineno + 1
                if func_lines > 50:
                    smells.append(
                        CodeSmellReport(
                            category=CodeSmellCategory.LONG_METHOD,
                            file_path=file_path,
                            symbol_name=node.name,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            severity=RiskLevel.MEDIUM if func_lines < 100 else RiskLevel.HIGH,
                            description=f"`{node.name}` fonksiyonu {func_lines} satır",
                            suggestion="Fonksiyonu daha küçük helper fonksiyonlara böl",
                        )
                    )

                # Too many parameters
                param_count = len([a for a in node.args.args if a.arg not in ("self", "cls")])
                if param_count > 5:
                    smells.append(
                        CodeSmellReport(
                            category=CodeSmellCategory.TOO_MANY_PARAMETERS,
                            file_path=file_path,
                            symbol_name=node.name,
                            line_start=node.lineno,
                            severity=RiskLevel.MEDIUM,
                            description=f"`{node.name}` fonksiyonu {param_count} parametre alıyor",
                            suggestion="Parametreleri bir dataclass/dict'e topla",
                        )
                    )

                # Deep nesting
                depth = self._max_nesting_depth(node)
                if depth > 4:
                    smells.append(
                        CodeSmellReport(
                            category=CodeSmellCategory.DEEP_NESTING,
                            file_path=file_path,
                            symbol_name=node.name,
                            line_start=node.lineno,
                            severity=RiskLevel.MEDIUM if depth < 6 else RiskLevel.HIGH,
                            description=f"`{node.name}` fonksiyonu {depth} seviye iç içe geçme",
                            suggestion="Early return pattern'i ile iç içe geçmeyi azalt",
                        )
                    )

            elif isinstance(node, ast.ClassDef):
                # God class — too many methods
                methods = [
                    n for n in node.body if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
                ]
                if len(methods) > 20:
                    smells.append(
                        CodeSmellReport(
                            category=CodeSmellCategory.GOD_CLASS,
                            file_path=file_path,
                            symbol_name=node.name,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            severity=RiskLevel.HIGH,
                            description=f"`{node.name}` sınıfı {len(methods)} metod içeriyor",
                            suggestion="Single Responsibility Principle'a göre sınıfı böl",
                        )
                    )

        return smells

    def _cyclomatic_complexity(self, node: ast.AST) -> int:
        """McCabe cyclomatic complexity hesapla."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)) or isinstance(
                child, ast.ExceptHandler
            ):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Assert):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
                if child.ifs:
                    complexity += len(child.ifs)

        return complexity

    def _cognitive_complexity(self, node: ast.AST) -> int:
        """SonarQube cognitive complexity hesapla."""
        return self._cognitive_walk(node, 0)

    def _cognitive_walk(self, node: ast.AST, nesting: int) -> int:
        """Recursive cognitive complexity traversal."""
        total = 0

        for child in ast.iter_child_nodes(node):
            increment = 0
            nesting_increment = False

            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)) or isinstance(
                child, ast.ExceptHandler
            ):
                increment = 1 + nesting
                nesting_increment = True
            elif isinstance(child, ast.BoolOp) or isinstance(child, (ast.Break, ast.Continue)):
                increment = 1

            total += increment

            if nesting_increment:
                total += self._cognitive_walk(child, nesting + 1)
            else:
                total += self._cognitive_walk(child, nesting)

        return total

    def _max_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Maksimum iç içe geçme derinliğini hesapla."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.Try)):
                depth = self._max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, depth)
            else:
                depth = self._max_nesting_depth(child, current_depth)
                max_depth = max(max_depth, depth)

        return max_depth
