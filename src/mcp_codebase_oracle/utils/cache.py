"""Cache sistemi — diskcache wrapper ile disk-persistent cache."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_cache_instance: Any = None


def get_cache(cache_dir: Path | str | None = None) -> Any:
    """Disk cache instance'ı döndür (lazy init)."""
    global _cache_instance
    if _cache_instance is not None:
        return _cache_instance

    try:
        import diskcache

        if cache_dir is None:
            from mcp_codebase_oracle.config import get_config

            cache_dir = get_config().cache_dir

        cache_path = Path(cache_dir) / "oracle_cache"
        cache_path.mkdir(parents=True, exist_ok=True)
        _cache_instance = diskcache.Cache(str(cache_path), size_limit=500 * 1024 * 1024)  # 500MB
        logger.debug(f"Cache initialized at {cache_path}")
        return _cache_instance

    except ImportError:
        logger.debug("diskcache not installed — using in-memory dict")
        _cache_instance = {}
        return _cache_instance


def cache_get(key: str, default: Any = None) -> Any:
    """Cache'den değer oku."""
    cache = get_cache()
    try:
        if isinstance(cache, dict):
            return cache.get(key, default)
        return cache.get(key, default)
    except Exception:
        return default


def cache_set(key: str, value: Any, expire: int | None = 3600) -> None:
    """Cache'e değer yaz."""
    cache = get_cache()
    try:
        if isinstance(cache, dict):
            cache[key] = value
        else:
            cache.set(key, value, expire=expire)
    except Exception as e:
        logger.debug(f"Cache set failed: {e}")


def cache_delete(key: str) -> None:
    """Cache'den değer sil."""
    cache = get_cache()
    try:
        if isinstance(cache, dict):
            cache.pop(key, None)
        else:
            cache.delete(key)
    except Exception:
        pass


def cache_clear() -> None:
    """Tüm cache'i temizle."""
    cache = get_cache()
    try:
        if isinstance(cache, dict):
            cache.clear()
        else:
            cache.clear()
    except Exception:
        pass


def reset_cache() -> None:
    """Cache instance'ı sıfırla (testing için)."""
    global _cache_instance
    if _cache_instance is not None and not isinstance(_cache_instance, dict):
        try:
            _cache_instance.close()
        except Exception:
            pass
    _cache_instance = None
