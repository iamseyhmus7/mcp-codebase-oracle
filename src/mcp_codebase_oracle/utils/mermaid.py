"""Mermaid diagram üretici — CodeGraph'tan Mermaid formatında diagram oluşturur."""

from __future__ import annotations


def generate_flowchart(
    nodes: list[dict],
    edges: list[dict],
    direction: str = "TD",
    title: str | None = None,
    max_nodes: int = 50,
) -> str:
    """Flowchart diyagramı üret."""
    lines = []
    if title:
        lines.append(f"---\ntitle: {title}\n---")
    lines.append(f"flowchart {direction}")

    displayed_ids = set()
    for node in nodes[:max_nodes]:
        nid = _safe_id(node.get("id", ""))
        label = node.get("name", node.get("id", "?"))
        kind = node.get("kind", "")
        displayed_ids.add(node.get("id", ""))

        if kind == "class":
            lines.append(f'    {nid}["{label}"]:::classNode')
        elif kind in ("function", "method"):
            lines.append(f'    {nid}("{label}"):::funcNode')
        else:
            lines.append(f'    {nid}["{label}"]')

    for edge in edges:
        src = edge.get("source", "")
        tgt = edge.get("target", "")
        if src in displayed_ids and tgt in displayed_ids:
            kind = edge.get("kind", "")
            label = f"|{kind}|" if kind else ""
            lines.append(f"    {_safe_id(src)} -->{label} {_safe_id(tgt)}")

    # Styles
    lines.append("")
    lines.append("    classDef classNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px")
    lines.append("    classDef funcNode fill:#f3e5f5,stroke:#4a148c,stroke-width:1px")

    if len(nodes) > max_nodes:
        lines.append(f'    note["... ve {len(nodes) - max_nodes} node daha"]')

    return "\n".join(lines)


def generate_class_diagram(
    classes: list[dict],
    relationships: list[dict],
    title: str | None = None,
) -> str:
    """Sınıf diyagramı üret."""
    lines = ["classDiagram"]
    if title:
        lines.insert(0, f"---\ntitle: {title}\n---")

    for cls in classes:
        name = cls.get("name", "")
        lines.append(f"    class {_safe_class_id(name)}")

        # Methods
        methods = cls.get("methods", [])
        for method in methods:
            visibility = "+"  # public default
            if method.startswith("_"):
                visibility = "-"
            lines.append(f"    {_safe_class_id(name)} : {visibility}{method}()")

    for rel in relationships:
        src = _safe_class_id(rel.get("source", ""))
        tgt = _safe_class_id(rel.get("target", ""))
        kind = rel.get("kind", "")

        if kind == "inherits":
            lines.append(f"    {tgt} <|-- {src}")
        elif kind == "implements":
            lines.append(f"    {tgt} <|.. {src}")
        elif kind == "uses":
            lines.append(f"    {src} --> {tgt}")
        elif kind == "contains":
            lines.append(f"    {src} *-- {tgt}")

    return "\n".join(lines)


def generate_dependency_diagram(
    modules: list[str],
    dependencies: list[tuple[str, str]],
    title: str = "Module Dependencies",
) -> str:
    """Modül bağımlılık diyagramı üret."""
    lines = [f"---\ntitle: {title}\n---", "flowchart LR"]

    for mod in modules:
        mid = _safe_id(mod)
        label = mod.split("/")[-1] if "/" in mod else mod
        lines.append(f'    {mid}["{label}"]')

    for src, tgt in dependencies:
        lines.append(f"    {_safe_id(src)} --> {_safe_id(tgt)}")

    return "\n".join(lines)


def generate_impact_diagram(
    target: str,
    direct: list[str],
    indirect: list[str],
    risk_level: str = "low",
) -> str:
    """Etki analizi diyagramı üret."""
    colors = {
        "low": "#a5d6a7",
        "medium": "#fff59d",
        "high": "#ffcc80",
        "critical": "#ef9a9a",
    }
    color = colors.get(risk_level, "#e0e0e0")

    lines = [
        "flowchart TD",
        f'    TARGET["{target}"]:::targetNode',
    ]

    for i, item in enumerate(direct[:15]):
        nid = f"D{i}"
        label = item.split("/")[-1] if "/" in item else item
        lines.append(f'    {nid}["{label}"]:::directNode')
        lines.append(f"    TARGET --> {nid}")

    for i, item in enumerate(indirect[:10]):
        nid = f"I{i}"
        label = item.split("/")[-1] if "/" in item else item
        lines.append(f'    {nid}["{label}"]:::indirectNode')
        # Connect to a direct node if possible
        if direct:
            lines.append(f"    D0 -.-> {nid}")

    lines.append("")
    lines.append(f"    classDef targetNode fill:{color},stroke:#333,stroke-width:3px")
    lines.append("    classDef directNode fill:#ffcdd2,stroke:#c62828")
    lines.append("    classDef indirectNode fill:#fff9c4,stroke:#f57f17")

    return "\n".join(lines)


def _safe_id(text: str) -> str:
    """Mermaid-safe node ID oluştur."""
    safe = text.replace("/", "_").replace("\\", "_").replace(":", "_")
    safe = safe.replace(".", "_").replace("-", "_").replace(" ", "_")
    safe = safe.replace("(", "").replace(")", "")
    return safe or "unknown"


def _safe_class_id(text: str) -> str:
    """Sınıf diyagramı için safe ID."""
    return text.replace(".", "_").replace("-", "_").replace("/", "_")
