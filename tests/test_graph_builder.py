"""Graph builder ve indexer testleri."""

from mcp_codebase_oracle.core.indexer import CodebaseIndexer
from mcp_codebase_oracle.models.graph import CodeGraph
from mcp_codebase_oracle.models.relationships import Relationship, RelationshipKind
from mcp_codebase_oracle.models.symbols import Symbol, SymbolKind


class TestCodeGraph:
    def test_add_symbol(self):
        graph = CodeGraph()
        sym = Symbol(
            name="foo", kind=SymbolKind.FUNCTION, file_path="test.py", line_start=1, line_end=5
        )
        graph.add_symbol(sym)
        assert graph.node_count == 1
        assert graph.get_symbol(sym.unique_id) is not None

    def test_add_relationship(self):
        graph = CodeGraph()
        s1 = Symbol(
            name="caller", kind=SymbolKind.FUNCTION, file_path="a.py", line_start=1, line_end=5
        )
        s2 = Symbol(
            name="callee", kind=SymbolKind.FUNCTION, file_path="b.py", line_start=1, line_end=5
        )
        graph.add_symbol(s1)
        graph.add_symbol(s2)
        graph.add_relationship(
            Relationship(source=s1.unique_id, target=s2.unique_id, kind=RelationshipKind.CALLS)
        )
        assert graph.edge_count == 1

    def test_get_callers(self):
        graph = CodeGraph()
        s1 = Symbol(
            name="caller", kind=SymbolKind.FUNCTION, file_path="a.py", line_start=1, line_end=5
        )
        s2 = Symbol(
            name="callee", kind=SymbolKind.FUNCTION, file_path="b.py", line_start=1, line_end=5
        )
        graph.add_symbol(s1)
        graph.add_symbol(s2)
        graph.add_relationship(
            Relationship(source=s1.unique_id, target=s2.unique_id, kind=RelationshipKind.CALLS)
        )
        callers = graph.get_callers(s2.unique_id)
        assert s1.unique_id in callers

    def test_find_symbols_by_name(self):
        graph = CodeGraph()
        s1 = Symbol(
            name="process", kind=SymbolKind.FUNCTION, file_path="a.py", line_start=1, line_end=5
        )
        s2 = Symbol(
            name="process",
            kind=SymbolKind.METHOD,
            file_path="b.py",
            line_start=10,
            line_end=15,
            parent="MyClass",
        )
        graph.add_symbol(s1)
        graph.add_symbol(s2)
        matches = graph.find_symbols_by_name("process")
        assert len(matches) == 2

    def test_to_mermaid(self):
        graph = CodeGraph()
        s1 = Symbol(
            name="main", kind=SymbolKind.FUNCTION, file_path="main.py", line_start=1, line_end=5
        )
        graph.add_symbol(s1)
        mermaid = graph.to_mermaid()
        assert "flowchart" in mermaid


class TestCodebaseIndexer:
    def test_scan_project(self, tmp_project_path: str):
        indexer = CodebaseIndexer()
        project = indexer.scan_project(tmp_project_path)
        assert project.total_files > 0
        assert project.total_lines > 0
        assert "python" in project.language_breakdown

    def test_get_project(self, tmp_project_path: str):
        indexer = CodebaseIndexer()
        indexer.scan_project(tmp_project_path)
        project = indexer.get_project(tmp_project_path)
        assert project is not None

    def test_get_graph(self, tmp_project_path: str):
        indexer = CodebaseIndexer()
        indexer.scan_project(tmp_project_path)
        graph = indexer.get_graph(tmp_project_path)
        assert graph is not None
        assert graph.node_count > 0
