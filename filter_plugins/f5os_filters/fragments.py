"""Helpers for recursive fragment discovery and lightweight runtime shaping."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def discover_yaml_fragments(root: str) -> list[str]:
    """Return recursively discovered YAML fragment files under `root`."""
    if not root:
        return []
    root_path = Path(root)
    if not root_path.exists():
        return []
    return sorted(
        str(path)
        for path in root_path.rglob("*")
        if path.is_file()
        and path.suffix in {".yml", ".yaml"}
        and path.name != "settings.yml"
    )


def aggregate_settings_fragments(
    include_results: list[dict[str, Any]],
    source_root: str,
    fragment_var_name: str,
    collection_key: str,
    defaults_key: str,
    deletion_mode: bool = False,
) -> list[dict[str, Any]]:
    """Flatten included fragment payloads into one runtime collection.

    This placeholder implementation keeps the contract simple for initial
    scaffolding: it merges top-level collection lists and applies defaults only
    when they already exist inline in a fragment payload.
    """
    aggregated: list[dict[str, Any]] = []
    for result in include_results or []:
      payload = (result.get("ansible_facts") or {}).get(fragment_var_name) or {}
      defaults = payload.get(defaults_key, {}) or {}
      for item in payload.get(collection_key, []) or []:
          merged = dict(defaults)
          merged.update(item or {})
          if deletion_mode and "state" not in merged:
              merged["state"] = "absent"
          aggregated.append(merged)
    return aggregated


def classify_fragment_operations(items: list[dict[str, Any]], operation: str) -> list[dict[str, Any]]:
    """Filter fragment items into present or delete runtime collections."""
    normalized_operation = operation.strip().lower()
    target_state = "present" if normalized_operation == "present" else "absent"
    filtered: list[dict[str, Any]] = []
    for item in items or []:
        state = str((item or {}).get("state", "present")).strip().lower()
        if state == target_state:
            filtered.append(item)
    return filtered
