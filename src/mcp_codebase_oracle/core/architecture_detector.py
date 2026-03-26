"""Mimari pattern tespit motoru — dizin yapısı ve import pattern'lerinden mimari çıkarımı."""

from __future__ import annotations

import logging
from pathlib import Path

from mcp_codebase_oracle.models.analysis import ArchitectureReport
from mcp_codebase_oracle.models.codebase import ProjectInfo

logger = logging.getLogger(__name__)

# Known architectural patterns and their directory signatures
ARCHITECTURE_PATTERNS = {
    "MVC": {
        "directories": ["models", "views", "controllers", "templates"],
        "files": ["urls.py", "routes.py"],
        "weight": 1.0,
    },
    "Layered": {
        "directories": [
            "presentation",
            "business",
            "data",
            "domain",
            "api",
            "services",
            "repositories",
            "entities",
        ],
        "files": [],
        "weight": 0.9,
    },
    "Clean Architecture": {
        "directories": [
            "entities",
            "use_cases",
            "usecases",
            "interfaces",
            "adapters",
            "infrastructure",
            "domain",
            "application",
        ],
        "files": [],
        "weight": 0.95,
    },
    "Hexagonal": {
        "directories": [
            "ports",
            "adapters",
            "domain",
            "application",
            "inbound",
            "outbound",
        ],
        "files": [],
        "weight": 0.95,
    },
    "Microservices": {
        "directories": ["services", "gateway", "common", "shared", "proto"],
        "files": ["docker-compose.yml", "docker-compose.yaml"],
        "weight": 0.85,
    },
    "Plugin-based": {
        "directories": ["plugins", "extensions", "addons", "modules"],
        "files": ["plugin.py", "plugin.json"],
        "weight": 0.8,
    },
    "Event-Driven": {
        "directories": ["events", "handlers", "listeners", "subscribers", "publishers"],
        "files": [],
        "weight": 0.85,
    },
    "Monolith": {
        "directories": [],
        "files": [],
        "weight": 0.5,  # Default fallback
    },
}


class ArchitectureDetector:
    """Proje mimarisini analiz ederek pattern tespiti yapar."""

    def detect(self, project: ProjectInfo) -> ArchitectureReport:
        """Projenin mimari pattern'ini tespit et."""
        scores: dict[str, float] = {}
        evidence: dict[str, list[str]] = {}

        # Directory structure analysis
        dir_names = self._extract_directory_names(project)

        for pattern_name, pattern_config in ARCHITECTURE_PATTERNS.items():
            score = 0.0
            pattern_evidence: list[str] = []

            # Directory matching
            matched_dirs = set(pattern_config["directories"]) & dir_names
            if pattern_config["directories"]:
                dir_ratio = len(matched_dirs) / len(pattern_config["directories"])
                score += dir_ratio * pattern_config["weight"]
                if matched_dirs:
                    pattern_evidence.append(f"Eşleşen dizinler: {', '.join(sorted(matched_dirs))}")

            # File matching
            file_names = {Path(f.path).name.lower() for f in project.files}
            matched_files = set(f.lower() for f in pattern_config["files"]) & file_names
            if matched_files:
                score += 0.3
                pattern_evidence.append(f"Eşleşen dosyalar: {', '.join(sorted(matched_files))}")

            # Framework-based hints
            framework_score = self._framework_architecture_hint(
                project.framework_hints, pattern_name
            )
            score += framework_score
            if framework_score > 0:
                pattern_evidence.append(f"Framework ipucu: {', '.join(project.framework_hints)}")

            scores[pattern_name] = score
            evidence[pattern_name] = pattern_evidence

        # Select best match
        best_pattern = max(scores, key=scores.get)  # type: ignore
        best_score = scores[best_pattern]

        # If no strong match, default to Monolith or simple structure
        if best_score < 0.3:
            best_pattern = "Monolith"
            best_score = 0.5
            evidence[best_pattern] = ["Belirgin bir mimari pattern tespit edilemedi"]

        # Layer map
        layer_map = self._build_layer_map(project, best_pattern)

        # Mermaid diagram
        mermaid = self._generate_architecture_mermaid(best_pattern, layer_map)

        return ArchitectureReport(
            pattern=best_pattern,
            confidence=min(best_score, 1.0),
            evidence=evidence.get(best_pattern, []),
            layer_map=layer_map,
            suggestions=self._generate_suggestions(best_pattern, project),
            mermaid_diagram=mermaid,
        )

    def _extract_directory_names(self, project: ProjectInfo) -> set[str]:
        """Projedeki tüm dizin adlarını çıkar."""
        dirs: set[str] = set()
        for f in project.files:
            parts = Path(f.path).parts
            for part in parts[:-1]:  # Dosya adını hariç tut
                dirs.add(part.lower())
        return dirs

    def _framework_architecture_hint(self, frameworks: list[str], pattern: str) -> float:
        """Framework'e göre mimari ipucu puanı."""
        hints = {
            "Django": {"MVC": 0.5, "Layered": 0.2},
            "Flask": {"Monolith": 0.2, "MVC": 0.2},
            "FastAPI": {"Layered": 0.3, "Clean Architecture": 0.2},
            "React": {"MVC": 0.2},
            "Next.js": {"MVC": 0.2, "Layered": 0.1},
            "Express": {"MVC": 0.3, "Layered": 0.2},
        }

        score = 0.0
        for fw in frameworks:
            if fw in hints and pattern in hints[fw]:
                score += hints[fw][pattern]
        return score

    def _build_layer_map(self, project: ProjectInfo, pattern: str) -> dict[str, list[str]]:
        """Pattern'e göre dosyaları katmanlara ayır."""
        layer_map: dict[str, list[str]] = {}

        layer_keywords = {
            "MVC": {
                "Models": ["models", "model", "entities", "entity"],
                "Views": ["views", "view", "templates", "template", "pages"],
                "Controllers": ["controllers", "controller", "routes", "urls", "api"],
            },
            "Layered": {
                "API/Presentation": ["api", "routes", "views", "presentation", "endpoints"],
                "Business/Services": ["services", "service", "business", "use_cases"],
                "Data/Repository": ["repositories", "repository", "data", "dal", "orm"],
            },
            "Clean Architecture": {
                "Domain/Entities": ["domain", "entities", "entity"],
                "Use Cases": ["use_cases", "usecases", "application"],
                "Interface Adapters": ["adapters", "interfaces", "controllers"],
                "Infrastructure": ["infrastructure", "frameworks", "drivers"],
            },
        }

        keywords = layer_keywords.get(pattern, {"Core": []})

        for layer_name, kws in keywords.items():
            matched_files = []
            for f in project.files:
                path_lower = f.path.lower()
                if any(kw in path_lower for kw in kws):
                    matched_files.append(f.path)
            if matched_files:
                layer_map[layer_name] = matched_files[:20]  # Limit

        # "Other" for unmatched files
        all_matched = set()
        for files in layer_map.values():
            all_matched.update(files)
        other = [f.path for f in project.files if f.path not in all_matched]
        if other:
            layer_map["Other"] = other[:20]

        return layer_map

    def _generate_architecture_mermaid(self, pattern: str, layer_map: dict[str, list[str]]) -> str:
        """Mimari diyagram Mermaid olarak üret."""
        lines = [
            f"---\ntitle: Architecture - {pattern}\n---",
            "flowchart TD",
        ]

        for i, (layer, files) in enumerate(layer_map.items()):
            layer_id = f"L{i}"
            file_count = len(files)
            lines.append(f'    {layer_id}["{layer}<br/>{file_count} files"]')
            if i > 0:
                lines.append(f"    L{i - 1} --> {layer_id}")

        return "\n".join(lines)

    def _generate_suggestions(self, pattern: str, project: ProjectInfo) -> list[str]:
        """Mimari iyileştirme önerileri."""
        suggestions = []

        if pattern == "Monolith":
            suggestions.append(
                "Proje belirgin bir katmanlı yapıya sahip değil. Modülerlik artırılabilir."
            )

        # Check for test coverage
        test_files = project.get_test_files()
        test_ratio = len(test_files) / max(len(project.files), 1)
        if test_ratio < 0.1:
            suggestions.append(
                f"Test kapsama oranı düşük ({test_ratio:.0%}). Daha fazla test dosyası eklenmeli."
            )

        return suggestions
