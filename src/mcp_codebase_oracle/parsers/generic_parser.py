"""Generic regex-based parser — desteklenmeyen diller için fallback."""

from __future__ import annotations

import re

from mcp_codebase_oracle.models.symbols import ImportInfo, Symbol, SymbolKind
from mcp_codebase_oracle.parsers.base_parser import BaseParser, ParseResult

# Common patterns across languages
PATTERNS = {
    "function": [
        # Python: def function_name(
        re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(", re.MULTILINE),
        # JS/TS: function name(  | const name = (  | export function name(
        re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(", re.MULTILINE),
        re.compile(
            r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(", re.MULTILINE
        ),
        # Go: func Name(
        re.compile(r"^\s*func\s+(\w+)\s*\(", re.MULTILINE),
        # Rust: fn name(  | pub fn name(
        re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*[<(]", re.MULTILINE),
        # Java/C#: public void Name(  | private int Name(
        re.compile(
            r"^\s*(?:public|private|protected|static|final|abstract|override|virtual|async)*\s+"
            r"(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\(",
            re.MULTILINE,
        ),
    ],
    "class": [
        # Python: class ClassName
        re.compile(r"^\s*class\s+(\w+)\s*[:(]", re.MULTILINE),
        # JS/TS: class ClassName | export class
        re.compile(r"^\s*(?:export\s+)?(?:abstract\s+)?class\s+(\w+)", re.MULTILINE),
        # Java/C#: public class Name | class Name
        re.compile(
            r"^\s*(?:public|private|protected|abstract|final|sealed|static)*\s*"
            r"(?:class|interface|enum|struct|record)\s+(\w+)",
            re.MULTILINE,
        ),
        # Rust: struct Name | enum Name | trait Name
        re.compile(r"^\s*(?:pub\s+)?(?:struct|enum|trait)\s+(\w+)", re.MULTILINE),
        # Go: type Name struct
        re.compile(r"^\s*type\s+(\w+)\s+(?:struct|interface)", re.MULTILINE),
    ],
    "import": [
        # Python
        re.compile(r"^\s*(?:from\s+(\S+)\s+)?import\s+(.+)$", re.MULTILINE),
        # JS/TS
        re.compile(r"^\s*import\s+.*?\s+from\s+['\"](.+?)['\"]", re.MULTILINE),
        re.compile(r"^\s*(?:const|let|var)\s+.*?=\s*require\s*\(['\"](.+?)['\"]\)", re.MULTILINE),
        # Go
        re.compile(r'^\s*"(.+?)"', re.MULTILINE),
        # Java/C#
        re.compile(r"^\s*(?:using|import)\s+(.+?);", re.MULTILINE),
        # Rust
        re.compile(r"^\s*use\s+(.+?);", re.MULTILINE),
    ],
}


class GenericParser(BaseParser):
    """Regex tabanlı generic parser — tüm diller için temel destek."""

    def get_supported_extensions(self) -> list[str]:
        return ["*"]  # Tüm uzantılar

    def parse_file(self, file_path: str, content: str) -> ParseResult:
        result = ParseResult()
        lines = content.split("\n")

        # Fonksiyonları tara
        for pattern in PATTERNS["function"]:
            for match in pattern.finditer(content):
                name = match.group(1)
                line_num = content[: match.start()].count("\n") + 1
                end_line = self._estimate_end_line(lines, line_num - 1)
                result.symbols.append(
                    Symbol(
                        name=name,
                        kind=SymbolKind.FUNCTION,
                        file_path=file_path,
                        line_start=line_num,
                        line_end=end_line,
                    )
                )

        # Sınıfları tara
        for pattern in PATTERNS["class"]:
            for match in pattern.finditer(content):
                name = match.group(1)
                line_num = content[: match.start()].count("\n") + 1
                end_line = self._estimate_end_line(lines, line_num - 1)
                result.symbols.append(
                    Symbol(
                        name=name,
                        kind=SymbolKind.CLASS,
                        file_path=file_path,
                        line_start=line_num,
                        line_end=end_line,
                    )
                )

        # Import'ları tara (basitleştirilmiş)
        for pattern in PATTERNS["import"]:
            for match in pattern.finditer(content):
                groups = match.groups()
                module = groups[0] if groups[0] else (groups[1] if len(groups) > 1 else "")
                if module:
                    line_num = content[: match.start()].count("\n") + 1
                    result.imports.append(
                        ImportInfo(
                            module=module.strip(),
                            line=line_num,
                            file_path=file_path,
                        )
                    )

        # De-duplicate by name + line
        seen = set()
        unique_symbols = []
        for s in result.symbols:
            key = (s.name, s.line_start)
            if key not in seen:
                seen.add(key)
                unique_symbols.append(s)
        result.symbols = unique_symbols

        return result

    def _estimate_end_line(self, lines: list[str], start_idx: int) -> int:
        """Bir sembolün bitiş satırını tahmin et (indentation tabanlı)."""
        if start_idx >= len(lines):
            return start_idx + 1

        start_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())

        for i in range(start_idx + 1, min(start_idx + 500, len(lines))):
            line = lines[i]
            if not line.strip():
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= start_indent and line.strip():
                return i  # 1-indexed already from offset

        return min(start_idx + 20, len(lines))
