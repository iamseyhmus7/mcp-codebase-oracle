"""Python AST parser — Python'un built-in ast modülü ile tam parsing."""

from __future__ import annotations

import ast
from typing import Any

from mcp_codebase_oracle.models.relationships import Relationship, RelationshipKind
from mcp_codebase_oracle.models.symbols import ImportInfo, ParameterInfo, Symbol, SymbolKind
from mcp_codebase_oracle.parsers.base_parser import BaseParser, ParseResult


class PythonParser(BaseParser):
    """Python kaynak kodu parser'ı — ast modülü ile tam destekli parsing."""

    def get_supported_extensions(self) -> list[str]:
        return [".py", ".pyi"]

    def parse_file(self, file_path: str, content: str) -> ParseResult:
        result = ParseResult()
        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError as e:
            result.errors.append(f"SyntaxError in {file_path}: {e}")
            return result

        self._extract_symbols(tree, file_path, content, result)
        self._extract_imports(tree, file_path, result)
        self._extract_calls(tree, file_path, result)
        return result

    def _extract_symbols(
        self,
        tree: ast.Module,
        file_path: str,
        content: str,
        result: ParseResult,
        parent_name: str | None = None,
    ) -> None:
        """AST'den fonksiyon, sınıf ve değişken sembollerini çıkar."""
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                symbol = self._make_function_symbol(node, file_path, content, parent_name)
                result.symbols.append(symbol)

                # Method'ların içindeki nested fonksiyonları da tara
                self._extract_symbols(node, file_path, content, result, symbol.name)

            elif isinstance(node, ast.ClassDef):
                symbol = self._make_class_symbol(node, file_path, content)
                result.symbols.append(symbol)

                # İnheritance relationships
                for base in node.bases:
                    base_name = self._get_name(base)
                    if base_name:
                        result.relationships.append(
                            Relationship(
                                source=f"{file_path}:{node.name}",
                                target=base_name,
                                kind=RelationshipKind.INHERITS,
                                file_path=file_path,
                                line=node.lineno,
                            )
                        )

                # Sınıf içindeki method'ları tara
                self._extract_symbols(node, file_path, content, result, node.name)

            elif isinstance(node, ast.Assign) and parent_name is None:
                # Top-level değişkenler (module-level constants)
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        kind = SymbolKind.CONSTANT if target.id.isupper() else SymbolKind.VARIABLE
                        result.symbols.append(
                            Symbol(
                                name=target.id,
                                kind=kind,
                                file_path=file_path,
                                line_start=node.lineno,
                                line_end=node.end_lineno or node.lineno,
                            )
                        )

    def _make_function_symbol(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: str,
        content: str,
        parent_name: str | None,
    ) -> Symbol:
        """FunctionDef AST node'unu Symbol'e çevir."""
        is_method = parent_name is not None
        kind = SymbolKind.METHOD if is_method else SymbolKind.FUNCTION

        # Property decorator kontrolü
        decorators = [self._get_name(d) or "" for d in node.decorator_list]
        if "property" in decorators:
            kind = SymbolKind.PROPERTY

        # Parametre bilgilerini çıkar
        parameters = self._extract_parameters(node.args)

        # Return type
        return_type = None
        if node.returns:
            return_type = self._get_annotation_str(node.returns)

        # Signature oluştur
        sig = self._build_signature(node.name, parameters, return_type)

        # Docstring
        docstring = ast.get_docstring(node)

        return Symbol(
            name=node.name,
            kind=kind,
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            signature=sig,
            docstring=docstring,
            decorators=decorators,
            parent=parent_name,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            parameters=parameters,
            return_type=return_type,
        )

    def _make_class_symbol(
        self,
        node: ast.ClassDef,
        file_path: str,
        content: str,
    ) -> Symbol:
        """ClassDef AST node'unu Symbol'e çevir."""
        bases = [self._get_name(b) or "?" for b in node.bases]
        sig = f"class {node.name}"
        if bases:
            sig += f"({', '.join(bases)})"

        decorators = [self._get_name(d) or "" for d in node.decorator_list]
        docstring = ast.get_docstring(node)

        return Symbol(
            name=node.name,
            kind=SymbolKind.CLASS,
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            signature=sig,
            docstring=docstring,
            decorators=decorators,
        )

    def _extract_parameters(self, args: ast.arguments) -> list[ParameterInfo]:
        """Fonksiyon parametrelerini çıkar."""
        params: list[ParameterInfo] = []
        defaults_offset = len(args.args) - len(args.defaults)

        for i, arg in enumerate(args.args):
            if arg.arg == "self" or arg.arg == "cls":
                continue
            type_hint = self._get_annotation_str(arg.annotation) if arg.annotation else None
            default = None
            if i >= defaults_offset:
                default = self._get_name(args.defaults[i - defaults_offset]) or "..."

            params.append(ParameterInfo(name=arg.arg, type_hint=type_hint, default_value=default))

        if args.vararg:
            params.append(ParameterInfo(name=f"*{args.vararg.arg}", is_variadic=True))
        if args.kwarg:
            params.append(ParameterInfo(name=f"**{args.kwarg.arg}", is_keyword=True))

        return params

    def _extract_imports(self, tree: ast.Module, file_path: str, result: ParseResult) -> None:
        """Import ifadelerini çıkar."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result.imports.append(
                        ImportInfo(
                            module=alias.name,
                            alias=alias.asname,
                            line=node.lineno,
                            file_path=file_path,
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    result.imports.append(
                        ImportInfo(
                            module=module,
                            name=alias.name,
                            alias=alias.asname,
                            is_relative=node.level > 0,
                            relative_level=node.level,
                            line=node.lineno,
                            file_path=file_path,
                        )
                    )

    def _extract_calls(self, tree: ast.Module, file_path: str, result: ParseResult) -> None:
        """Fonksiyon çağrılarını traversal ile tespit et."""
        # Hangi fonksiyon içinde olduğumuzu takip et
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                caller_name = node.name
                # İç içe walk ile bu fonksiyondaki çağrıları bul
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        callee_name = self._get_call_name(child)
                        if callee_name and callee_name != caller_name:
                            result.relationships.append(
                                Relationship(
                                    source=f"{file_path}:{caller_name}",
                                    target=callee_name,
                                    kind=RelationshipKind.CALLS,
                                    file_path=file_path,
                                    line=child.lineno,
                                )
                            )

    def _get_call_name(self, node: ast.Call) -> str | None:
        """Call node'undan fonksiyon adını çıkar."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            value = self._get_name(node.func.value)
            if value:
                return f"{value}.{node.func.attr}"
            return node.func.attr
        return None

    def _get_name(self, node: Any) -> str | None:
        """AST node'undan isim string'ini çıkar."""
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            value = self._get_name(node.value)
            if value:
                return f"{value}.{node.attr}"
            return node.attr
        if isinstance(node, ast.Call):
            return self._get_name(node.func)
        if isinstance(node, ast.Constant):
            return repr(node.value)
        if isinstance(node, ast.Subscript):
            return self._get_name(node.value)
        return None

    def _get_annotation_str(self, node: Any) -> str:
        """Type annotation'ı string'e çevir."""
        name = self._get_name(node)
        return name if name else "Any"

    def _build_signature(
        self, name: str, params: list[ParameterInfo], return_type: str | None
    ) -> str:
        """Fonksiyon signature string'i oluştur."""
        parts = []
        for p in params:
            part = p.name
            if p.type_hint:
                part += f": {p.type_hint}"
            if p.default_value:
                part += f" = {p.default_value}"
            parts.append(part)

        sig = f"def {name}({', '.join(parts)})"
        if return_type:
            sig += f" -> {return_type}"
        return sig
