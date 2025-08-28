"""
Simple in-memory TTL cache for ROI endpoints (per-process, best-effort).
Not suitable for multi-instance production; replace with Redis if needed.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Tuple


class TTLCache:
    def __init__(self):
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if time.time() > expires_at:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = (time.time() + ttl_seconds, value)


cache = TTLCache()


