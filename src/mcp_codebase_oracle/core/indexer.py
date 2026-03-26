"""Codebase indeksleme — dosya keşfi, parsing orchestration, caching."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from mcp_codebase_oracle.config import get_config
from mcp_codebase_oracle.models.codebase import FileInfo, ProjectInfo
from mcp_codebase_oracle.models.graph import CodeGraph
from mcp_codebase_oracle.models.relationships import Relationship, RelationshipKind
from mcp_codebase_oracle.parsers import get_parser
from mcp_codebase_oracle.utils.cache import cache_set
from mcp_codebase_oracle.utils.file_utils import (
    detect_language,
    discover_files,
    file_hash,
    is_test_file,
    safe_read_file,
)

logger = logging.getLogger(__name__)


class CodebaseIndexer:
    """Projeyi tarar, parse eder ve indeksler.

    Ana iş akışı:
    1. discover_files() ile dosya keşfi
    2. Her dosyayı uygun parser ile parse et
    3. FileInfo ve ProjectInfo oluştur
    4. CodeGraph'ı inşa et
    """

    def __init__(self) -> None:
        self._config = get_config()
        self._indexed_projects: dict[str, ProjectInfo] = {}
        self._graphs: dict[str, CodeGraph] = {}
        self._file_hashes: dict[str, dict[str, str]] = {}  # project -> {file -> hash}

    def scan_project(
        self,
        root_path: str,
        exclude_patterns: list[str] | None = None,
        max_depth: int = 50,
    ) -> ProjectInfo:
        """Projeyi tara ve indeksle."""
        root = str(Path(root_path).resolve())
        project_name = Path(root).name
        logger.info(f"Scanning project: {project_name} at {root}")

        # Combine config and user-specified patterns
        all_excludes = list(self._config.exclude_patterns)
        if exclude_patterns:
            all_excludes.extend(exclude_patterns)

        # Discover files
        file_paths = discover_files(
            root,
            exclude_patterns=all_excludes,
            max_files=self._config.max_files,
            max_depth=max_depth,
        )
        logger.info(f"Discovered {len(file_paths)} files")

        # Parse each file
        files: list[FileInfo] = []
        graph = CodeGraph()
        language_breakdown: dict[str, int] = {}
        total_lines = 0
        total_symbols = 0
        framework_hints: list[str] = []
        file_hashes: dict[str, str] = {}

        for rel_path in file_paths:
            full_path = os.path.join(root, rel_path)
            language = detect_language(rel_path)

            # Read file
            content = safe_read_file(full_path, self._config.max_file_size)
            if content is None:
                continue

            # Hash for incremental re-scan
            fhash = file_hash(full_path)
            file_hashes[rel_path] = fhash

            # Parse
            parser = get_parser(language)
            try:
                result = parser.parse_file(rel_path, content)
            except Exception as e:
                logger.warning(f"Parse failed for {rel_path}: {e}")
                result = None

            line_count = content.count("\n") + 1
            total_lines += line_count

            # Create FileInfo
            file_info = FileInfo(
                path=rel_path,
                language=language,
                size_bytes=len(content.encode("utf-8")),
                line_count=line_count,
                symbols=result.symbols if result else [],
                imports=result.imports if result else [],
                is_test=is_test_file(rel_path),
                hash=fhash,
            )
            files.append(file_info)

            # Update stats
            language_breakdown[language] = language_breakdown.get(language, 0) + 1

            if result:
                total_symbols += len(result.symbols)

                # Add symbols to graph
                for symbol in result.symbols:
                    graph.add_symbol(symbol)

                # Add relationships (will be resolved later)
                for rel in result.relationships:
                    graph.add_relationship(rel)

                # Track import relationships for post-processing
                for imp in result.imports:
                    graph.add_relationship(
                        Relationship(
                            source=rel_path,
                            target=imp.module,
                            kind=RelationshipKind.IMPORTS,
                            file_path=rel_path,
                            line=imp.line,
                        )
                    )

            # Detect frameworks
            framework_hints.extend(self._detect_frameworks(rel_path, content))

        # ─── Post-processing: Resolve relationships ───────────────
        # Build module-to-file mapping for import resolution
        module_to_file = self._build_module_map(file_paths)

        # Resolve import targets: module name → actual file path
        self._resolve_imports(graph, module_to_file)

        # Resolve CALLS targets: bare function name → file:function unique_id
        self._resolve_calls(graph)

        # Create ProjectInfo
        project = ProjectInfo(
            name=project_name,
            root_path=root,
            files=files,
            language_breakdown=language_breakdown,
            total_lines=total_lines,
            total_symbols=total_symbols,
            framework_hints=list(set(framework_hints)),
        )

        # Store
        self._indexed_projects[root] = project
        self._graphs[root] = graph
        self._file_hashes[root] = file_hashes

        # Cache
        cache_set(f"project:{root}", project.to_dict(), expire=7200)

        logger.info(
            f"Scan complete: {len(files)} files, {total_symbols} symbols, "
            f"{graph.edge_count} relationships"
        )
        return project

    def rescan_project(self, root_path: str) -> dict:
        """Incremental rescan — sadece değişen dosyalar."""
        root = str(Path(root_path).resolve())
        old_hashes = self._file_hashes.get(root, {})

        if not old_hashes:
            # Full scan needed
            self.scan_project(root_path)
            return {"full_rescan": True}

        new_files = []
        modified_files = []
        deleted_files = []

        # Re-discover
        file_paths = discover_files(root, exclude_patterns=self._config.exclude_patterns)
        current = set(file_paths)
        old = set(old_hashes.keys())

        new_paths = current - old
        removed_paths = old - current

        for path in new_paths:
            new_files.append(path)

        for path in removed_paths:
            deleted_files.append(path)

        for path in current & old:
            full_path = os.path.join(root, path)
            new_hash = file_hash(full_path)
            if new_hash != old_hashes.get(path, ""):
                modified_files.append(path)

        # Full rescan if too many changes
        total_changes = len(new_files) + len(modified_files) + len(deleted_files)
        if total_changes > 100:
            self.scan_project(root_path)
            return {"full_rescan": True, "changes_detected": total_changes}

        # Could do incremental here, but for simplicity do full rescan
        if total_changes > 0:
            self.scan_project(root_path)

        return {
            "changes_detected": total_changes,
            "new_files": new_files,
            "modified_files": modified_files,
            "deleted_files": deleted_files,
        }

    def get_project(self, root_path: str) -> ProjectInfo | None:
        """Daha önce indekslenen projeyi getir."""
        root = str(Path(root_path).resolve())
        return self._indexed_projects.get(root)

    def get_graph(self, root_path: str) -> CodeGraph | None:
        """Proje code graph'ını getir."""
        root = str(Path(root_path).resolve())
        return self._graphs.get(root)

    def _build_module_map(self, file_paths: list[str]) -> dict[str, str]:
        """Python modül adlarını dosya yollarına eşle.

        Ör: 'mcp_codebase_oracle.models.graph' -> 'src/mcp_codebase_oracle/models/graph.py'
        """
        mapping: dict[str, str] = {}
        for fp in file_paths:
            if not fp.endswith(".py"):
                continue
            # src/mcp_codebase_oracle/models/graph.py -> mcp_codebase_oracle.models.graph
            parts = fp.replace("\\", "/").replace(".py", "").split("/")
            # Remove src/ prefix if present
            if parts and parts[0] == "src":
                parts = parts[1:]
            # Remove __init__ suffix (package import)
            if parts and parts[-1] == "__init__":
                module_name = ".".join(parts[:-1])
                if module_name:
                    mapping[module_name] = fp
            else:
                module_name = ".".join(parts)
                mapping[module_name] = fp
        return mapping

    def _resolve_imports(self, graph: CodeGraph, module_map: dict[str, str]) -> None:
        """Import hedeflerini gerçek dosya yollarına çözümle.

        Graph edge'lerdeki modül adlarını (ör: mcp_codebase_oracle.config)
        gerçek dosya yollarına (ör: src/mcp_codebase_oracle/config.py) çevir.
        """
        edges_to_add = []
        edges_to_remove = []

        for source, target, data in list(graph._graph.edges(data=True)):
            if data.get("kind") != RelationshipKind.IMPORTS.value:
                continue

            resolved_path = module_map.get(target)
            if resolved_path and resolved_path != source:
                edges_to_remove.append((source, target))
                edges_to_add.append((source, resolved_path, data))

        for s, t in edges_to_remove:
            try:
                graph._graph.remove_edge(s, t)
            except Exception:
                pass

        for s, t, d in edges_to_add:
            graph._graph.add_edge(s, t, **d)

    def _resolve_calls(self, graph: CodeGraph) -> None:
        """CALLS ilişkilerindeki hedef fonksiyon adlarını sembol ID'ye çözümle.

        Parser'lar call target'ı genellikle bare name olarak döndürür (ör: 'helper_func').
        Bu metod onları graph'taki gerçek unique_id'ye (ör: 'utils.py:helper_func') eşler.
        """
        # Build name -> [symbol_id] lookup
        name_to_ids: dict[str, list[str]] = {}
        for uid, sym in graph._symbols.items():
            name_to_ids.setdefault(sym.name, []).append(uid)
            # Also index qualified names (ClassName.method)
            if sym.parent:
                qname = f"{sym.parent}.{sym.name}"
                name_to_ids.setdefault(qname, []).append(uid)

        edges_to_add = []
        edges_to_remove = []

        for source, target, data in list(graph._graph.edges(data=True)):
            if data.get("kind") != RelationshipKind.CALLS.value:
                continue

            # If target is already a known symbol, skip
            if target in graph._symbols:
                continue

            # Try to resolve bare name
            bare_name = target.split(".")[-1] if "." in target else target
            candidates = name_to_ids.get(target, []) or name_to_ids.get(bare_name, [])

            if candidates:
                edges_to_remove.append((source, target))
                # Pick best candidate: same file first, otherwise first match
                source_file = source.split(":")[0] if ":" in source else source
                best = None
                for cid in candidates:
                    csym = graph._symbols.get(cid)
                    if csym and csym.file_path == source_file:
                        best = cid
                        break
                if best is None:
                    best = candidates[0]

                edges_to_add.append((source, best, data))

        for s, t in edges_to_remove:
            try:
                graph._graph.remove_edge(s, t)
            except Exception:
                pass

        for s, t, d in edges_to_add:
            if s != t:  # self-calls skip
                graph._graph.add_edge(s, t, **d)

    def _detect_frameworks(self, file_path: str, content: str) -> list[str]:
        """Dosya içeriğinden kullanılan framework'leri tespit et."""
        hints = []
        filename = Path(file_path).name.lower()

        # File-based hints
        if filename == "manage.py" or filename == "wsgi.py":
            hints.append("Django")
        elif filename in ("app.py", "wsgi.py") and "flask" in content.lower():
            hints.append("Flask")
        elif filename == "main.py" and "fastapi" in content.lower():
            hints.append("FastAPI")
        elif filename == "package.json":
            if '"react"' in content:
                hints.append("React")
            if '"next"' in content or '"next"' in content:
                hints.append("Next.js")
            if '"vue"' in content:
                hints.append("Vue")
            if '"angular"' in content:
                hints.append("Angular")
            if '"express"' in content:
                hints.append("Express")
        elif filename == "cargo.toml":
            hints.append("Rust/Cargo")
        elif filename == "go.mod":
            hints.append("Go Modules")

        # Content-based hints
        if "import django" in content or "from django" in content:
            hints.append("Django")
        if "import flask" in content or "from flask" in content:
            hints.append("Flask")
        if "import fastapi" in content or "from fastapi" in content:
            hints.append("FastAPI")
        if "import pytest" in content or "from pytest" in content:
            hints.append("pytest")
        if "import sqlalchemy" in content:
            hints.append("SQLAlchemy")

        return hints


# Global indexer instance
_indexer: CodebaseIndexer | None = None


def get_indexer() -> CodebaseIndexer:
    """Global indexer instance'ı döndür."""
    global _indexer
    if _indexer is None:
        _indexer = CodebaseIndexer()
    return _indexer
