"""CodeGraph — NetworkX tabanlı ana graf veri yapısı."""

from __future__ import annotations

from typing import Any

import networkx as nx

from mcp_codebase_oracle.models.relationships import Relationship, RelationshipKind
from mcp_codebase_oracle.models.symbols import Symbol


class CodeGraph:
    """Codebase'in graf temsili — semboller node, ilişkiler edge olarak tutulur.

    NetworkX DiGraph üzerine inşa edilmiş high-level arayüz.
    """

    def __init__(self) -> None:
        self._graph = nx.DiGraph()
        self._symbols: dict[str, Symbol] = {}
        self._file_symbols: dict[str, list[str]] = {}  # file_path -> [symbol_ids]

    @property
    def node_count(self) -> int:
        return self._graph.number_of_nodes()

    @property
    def edge_count(self) -> int:
        return self._graph.number_of_edges()

    # ─── Node Operations ─────────────────────────────────────────────

    def add_symbol(self, symbol: Symbol) -> None:
        """Grafa bir sembol (node) ekle."""
        uid = symbol.unique_id
        self._graph.add_node(uid, **symbol.to_dict())
        self._symbols[uid] = symbol

        # File → symbol mapping
        file_path = symbol.file_path
        if file_path not in self._file_symbols:
            self._file_symbols[file_path] = []
        self._file_symbols[file_path].append(uid)

    def get_symbol(self, unique_id: str) -> Symbol | None:
        """Benzersiz ID ile sembol getir."""
        return self._symbols.get(unique_id)

    def find_symbols_by_name(self, name: str) -> list[Symbol]:
        """İsme göre sembol ara."""
        return [s for s in self._symbols.values() if s.name == name]

    def get_file_symbols(self, file_path: str) -> list[Symbol]:
        """Bir dosyadaki tüm sembolleri getir."""
        ids = self._file_symbols.get(file_path, [])
        return [self._symbols[uid] for uid in ids if uid in self._symbols]

    # ─── Edge Operations ─────────────────────────────────────────────

    def add_relationship(self, rel: Relationship) -> None:
        """İki sembol/dosya arasına ilişki (edge) ekle."""
        self._graph.add_edge(
            rel.source,
            rel.target,
            kind=rel.kind.value,
            file_path=rel.file_path,
            line=rel.line,
            **rel.metadata,
        )

    def get_relationships(
        self, node_id: str, kind: RelationshipKind | None = None
    ) -> list[dict[str, Any]]:
        """Bir node'un tüm ilişkilerini getir."""
        edges = []
        for _, target, data in self._graph.out_edges(node_id, data=True):
            if kind is None or data.get("kind") == kind.value:
                edges.append({"source": node_id, "target": target, **data})
        for source, _, data in self._graph.in_edges(node_id, data=True):
            if kind is None or data.get("kind") == kind.value:
                edges.append({"source": source, "target": node_id, **data})
        return edges

    # ─── Graph Queries ────────────────────────────────────────────────

    def get_callers(self, symbol_id: str) -> list[str]:
        """Bir sembolü çağıran tüm sembolleri getir."""
        callers = []
        for source, _, data in self._graph.in_edges(symbol_id, data=True):
            if data.get("kind") == RelationshipKind.CALLS.value:
                callers.append(source)
        return callers

    def get_callees(self, symbol_id: str) -> list[str]:
        """Bir sembolün çağırdığı tüm sembolleri getir."""
        callees = []
        for _, target, data in self._graph.out_edges(symbol_id, data=True):
            if data.get("kind") == RelationshipKind.CALLS.value:
                callees.append(target)
        return callees

    def get_dependencies(self, file_path: str) -> list[str]:
        """Bir dosyanın bağımlı olduğu dosyaları getir (import-based)."""
        deps = set()

        # 1. File-level import edges (source=file_path, target=file_path)
        if self._graph.has_node(file_path):
            for _, target, data in self._graph.out_edges(file_path, data=True):
                if data.get("kind") in (
                    RelationshipKind.IMPORTS.value,
                    RelationshipKind.DEPENDS_ON.value,
                ):
                    deps.add(target)

        # 2. Symbol-level edges
        symbols = self._file_symbols.get(file_path, [])
        for sid in symbols:
            for _, target, data in self._graph.out_edges(sid, data=True):
                if data.get("kind") in (
                    RelationshipKind.IMPORTS.value,
                    RelationshipKind.DEPENDS_ON.value,
                ):
                    target_sym = self._symbols.get(target)
                    if target_sym:
                        deps.add(target_sym.file_path)
        deps.discard(file_path)
        return list(deps)

    def get_dependents(self, file_path: str) -> list[str]:
        """Bir dosyaya bağımlı olan dosyaları getir (reverse dependencies)."""
        dependents = set()

        # 1. File-level import edges (source=other_file, target=file_path)
        if self._graph.has_node(file_path):
            for source, _, data in self._graph.in_edges(file_path, data=True):
                if data.get("kind") in (
                    RelationshipKind.IMPORTS.value,
                    RelationshipKind.DEPENDS_ON.value,
                ):
                    dependents.add(source)

        # 2. Symbol-level edges
        symbols = self._file_symbols.get(file_path, [])
        for sid in symbols:
            for source, _, data in self._graph.in_edges(sid, data=True):
                if data.get("kind") in (
                    RelationshipKind.IMPORTS.value,
                    RelationshipKind.DEPENDS_ON.value,
                ):
                    source_sym = self._symbols.get(source)
                    if source_sym:
                        dependents.add(source_sym.file_path)
        dependents.discard(file_path)
        return list(dependents)

    def get_transitive_dependents(self, file_path: str, max_depth: int = 10) -> list[str]:
        """Transitif bağımlıları getir (BFS)."""
        visited = set()
        queue = [file_path]
        depth = 0

        while queue and depth < max_depth:
            next_queue = []
            for fp in queue:
                if fp in visited:
                    continue
                visited.add(fp)
                dependents = self.get_dependents(fp)
                next_queue.extend(d for d in dependents if d not in visited)
            queue = next_queue
            depth += 1

        visited.discard(file_path)  # Kendisini çıkar
        return list(visited)

    def find_cycles(self) -> list[list[str]]:
        """Döngüsel bağımlılıkları tespit et."""
        try:
            return list(nx.simple_cycles(self._graph))
        except nx.NetworkXError:
            return []

    def get_subgraph(self, node_ids: list[str]) -> CodeGraph:
        """Node subset'i ile alt graf oluştur."""
        sub = CodeGraph()
        subgraph = self._graph.subgraph(node_ids)
        sub._graph = subgraph.copy()
        sub._symbols = {uid: s for uid, s in self._symbols.items() if uid in node_ids}
        for uid in node_ids:
            sym = self._symbols.get(uid)
            if sym:
                fp = sym.file_path
                if fp not in sub._file_symbols:
                    sub._file_symbols[fp] = []
                sub._file_symbols[fp].append(uid)
        return sub

    # ─── Metrics ──────────────────────────────────────────────────────

    def get_node_in_degree(self, node_id: str) -> int:
        """Afferent coupling — kaç node bu node'a bağımlı."""
        return self._graph.in_degree(node_id) if self._graph.has_node(node_id) else 0

    def get_node_out_degree(self, node_id: str) -> int:
        """Efferent coupling — bu node kaç node'a bağımlı."""
        return self._graph.out_degree(node_id) if self._graph.has_node(node_id) else 0

    # ─── Export ────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Graf'ı JSON-serializable dictionary olarak döndür."""
        nodes = []
        for uid, data in self._graph.nodes(data=True):
            nodes.append({"id": uid, **data})

        edges = []
        for source, target, data in self._graph.edges(data=True):
            edges.append({"source": source, "target": target, **data})

        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "nodes": nodes,
            "edges": edges,
        }

    def to_mermaid(
        self,
        max_nodes: int = 50,
        direction: str = "TD",
        title: str | None = None,
    ) -> str:
        """Graf'ı Mermaid flowchart formatına çevir."""
        lines = [f"flowchart {direction}"]
        if title:
            lines.insert(0, f"---\ntitle: {title}\n---")

        # Node'ları ekle (limit)
        node_ids = list(self._graph.nodes())[:max_nodes]
        for uid in node_ids:
            sym = self._symbols.get(uid)
            if sym:
                label = sym.qualified_name
                if sym.kind.value == "class":
                    lines.append(f'    {_mermaid_id(uid)}["{label}"]')
                elif sym.kind.value in ("function", "method"):
                    lines.append(f'    {_mermaid_id(uid)}("{label}")')
                else:
                    lines.append(f'    {_mermaid_id(uid)}["{label}"]')
            else:
                lines.append(f'    {_mermaid_id(uid)}["{uid}"]')

        # Edge'leri ekle
        for source, target, data in self._graph.edges(data=True):
            if source in node_ids and target in node_ids:
                kind = data.get("kind", "")
                lines.append(f"    {_mermaid_id(source)} -->|{kind}| {_mermaid_id(target)}")

        if len(self._graph.nodes()) > max_nodes:
            lines.append(f'    note["... ve {len(self._graph.nodes()) - max_nodes} node daha"]')

        return "\n".join(lines)


def _mermaid_id(uid: str) -> str:
    """UID'yi Mermaid-safe node ID'ye çevir."""
    safe = uid.replace("/", "_").replace("\\", "_").replace(":", "_").replace(".", "_")
    safe = safe.replace("-", "_").replace(" ", "_")
    return safe
