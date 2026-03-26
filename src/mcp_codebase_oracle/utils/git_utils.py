"""Git entegrasyonu — blame, log, diff, hotspot detection."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class GitBlameInfo:
    """Bir satırın git blame bilgisi."""

    commit_hash: str = ""
    author: str = ""
    date: str = ""
    line_number: int = 0


@dataclass
class GitHotspot:
    """Sık değişen dosya — hotspot."""

    file_path: str
    change_count: int = 0
    unique_authors: int = 0
    last_modified: str = ""

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "change_count": self.change_count,
            "unique_authors": self.unique_authors,
            "last_modified": self.last_modified,
        }


@dataclass
class GitInfo:
    """Projenin git bilgileri."""

    is_git_repo: bool = False
    branch: str = ""
    total_commits: int = 0
    contributors: list[str] = field(default_factory=list)
    hotspots: list[GitHotspot] = field(default_factory=list)


def get_git_info(root_path: str) -> GitInfo:
    """Proje git bilgilerini getir."""
    info = GitInfo()

    try:
        import git

        repo = git.Repo(root_path, search_parent_directories=True)
        info.is_git_repo = True
        info.branch = str(repo.active_branch) if not repo.head.is_detached else "HEAD"

        # Commit count (limit 1000)
        commits = list(repo.iter_commits(max_count=1000))
        info.total_commits = len(commits)

        # Contributors
        authors = set()
        for commit in commits[:500]:
            if commit.author:
                authors.add(str(commit.author))
        info.contributors = sorted(authors)

    except ImportError:
        logger.debug("gitpython not installed — git features disabled")
    except Exception as e:
        logger.debug(f"Git info failed: {e}")

    return info


def get_hotspots(root_path: str, top_n: int = 20) -> list[GitHotspot]:
    """En sık değişen dosyaları bul (hotspot detection)."""
    hotspots: dict[str, GitHotspot] = {}

    try:
        import git

        repo = git.Repo(root_path, search_parent_directories=True)
        commits = list(repo.iter_commits(max_count=500))

        for commit in commits:
            if commit.parents:
                try:
                    diffs = commit.parents[0].diff(commit)
                    for diff in diffs:
                        path = diff.b_path or diff.a_path
                        if not path:
                            continue
                        if path not in hotspots:
                            hotspots[path] = GitHotspot(file_path=path)
                        hotspots[path].change_count += 1
                        if not hotspots[path].last_modified:
                            hotspots[path].last_modified = commit.committed_datetime.isoformat()
                except Exception:
                    continue

        # Sort by change count
        sorted_hotspots = sorted(hotspots.values(), key=lambda h: h.change_count, reverse=True)
        return sorted_hotspots[:top_n]

    except ImportError:
        logger.debug("gitpython not installed")
        return []
    except Exception as e:
        logger.debug(f"Hotspot detection failed: {e}")
        return []


def get_file_blame(root_path: str, file_path: str) -> list[GitBlameInfo]:
    """Bir dosyanın git blame bilgisini getir."""
    try:
        import git

        repo = git.Repo(root_path, search_parent_directories=True)
        full_path = Path(root_path) / file_path

        if not full_path.exists():
            return []

        blame = repo.blame("HEAD", file_path)
        results: list[GitBlameInfo] = []
        line_num = 1

        for commit, lines in blame:
            for _ in lines:
                results.append(
                    GitBlameInfo(
                        commit_hash=str(commit)[:8],
                        author=str(commit.author),
                        date=commit.committed_datetime.strftime("%Y-%m-%d"),
                        line_number=line_num,
                    )
                )
                line_num += 1

        return results

    except ImportError:
        return []
    except Exception:
        return []
