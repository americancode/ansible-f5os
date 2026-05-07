"""Shared utility helpers for F5OS filter modules."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def deep_merge_dicts(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge two dictionaries with overlay precedence.

    Nested dictionaries are merged, while all other values from `overlay`
    replace the values from `base`.
    """
    merged = deepcopy(base)
    for key, value in (overlay or {}).items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = deep_merge_dicts(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged
