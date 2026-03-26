"""Çıktı formatlama — Markdown tabloları, JSON, risk level emojiler."""

from __future__ import annotations

import json
from typing import Any


def format_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    """Markdown tablosu oluştur."""
    if not headers or not rows:
        return ""

    # Kolon genişlikleri
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))

    # Header
    header = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    separator = "|-" + "-|-".join("-" * w for w in widths) + "-|"

    # Rows
    lines = [header, separator]
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            w = widths[i] if i < len(widths) else 10
            cells.append(str(cell).ljust(w))
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


def format_risk_badge(risk_level: str) -> str:
    """Risk seviyesini emoji badge olarak formatla."""
    badges = {
        "low": "🟢 Low",
        "medium": "🟡 Medium",
        "high": "🟠 High",
        "critical": "🔴 Critical",
    }
    return badges.get(risk_level.lower(), f"⚪ {risk_level}")


def format_language_breakdown(breakdown: dict[str, int]) -> str:
    """Dil dağılımını Markdown listesi olarak formatla."""
    if not breakdown:
        return "_No files detected_"

    total = sum(breakdown.values())
    lines = []
    for lang, count in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        lines.append(f"- **{lang}**: {count} files ({pct:.1f}%) `{bar}`")

    return "\n".join(lines)


def format_file_tree(files: list[str], max_files: int = 30) -> str:
    """Dosya listesini ağaç yapısında formatla."""
    if not files:
        return "_No files_"

    tree: dict[str, Any] = {}
    for f in files[:max_files]:
        parts = f.replace("\\", "/").split("/")
        current = tree
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = None

    lines: list[str] = []
    _render_tree(tree, "", lines)

    if len(files) > max_files:
        lines.append(f"... ve {len(files) - max_files} dosya daha")

    return "\n".join(lines)


def _render_tree(tree: dict, prefix: str, lines: list[str]) -> None:
    """Tree dict'ini string olarak render et."""
    items = sorted(tree.items(), key=lambda x: (x[1] is not None, x[0]))
    for i, (name, subtree) in enumerate(items):
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{name}")
        if subtree is not None:
            extension = "    " if is_last else "│   "
            _render_tree(subtree, prefix + extension, lines)


def to_json(data: Any, indent: int = 2) -> str:
    """Pretty JSON string."""
    return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
