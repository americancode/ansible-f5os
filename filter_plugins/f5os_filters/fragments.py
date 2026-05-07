"""Helpers for recursive fragment discovery and runtime shaping."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import deep_merge_dicts
from .settings import load_settings_hierarchy


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
    defaults_key: str | None,
    deletion_mode: bool = False,
) -> list[dict[str, Any]]:
    """Flatten included fragment payloads and merge them with hierarchical defaults."""
    aggregated: list[dict[str, Any]] = []
    for result in include_results or []:
        if not isinstance(result, dict):
            continue
        source_file = result.get("item")
        payload = (result.get("ansible_facts") or {}).get(fragment_var_name) or {}
        fragment_items = payload.get(collection_key) or []
        settings_payload = load_settings_hierarchy(source_file, source_root)
        directory_defaults = settings_payload.get(defaults_key, {}) if defaults_key else {}

        for item in fragment_items:
            if not isinstance(item, dict):
                continue
            merged = deep_merge_dicts(directory_defaults, item)
            if deletion_mode:
                merged = deep_merge_dicts(merged, {"state": "absent"})
            aggregated.append(merged)
    return aggregated


def classify_fragment_operations(items: list[dict[str, Any]], operation: str) -> list[dict[str, Any]]:
    """Filter fragment items into present or delete runtime collections."""
    normalized_operation = operation.strip().lower()
    filtered: list[dict[str, Any]] = []
    for item in items or []:
        state = str((item or {}).get("state", "present")).strip().lower()
        if normalized_operation == "present" and state != "absent":
            filtered.append(item)
        if normalized_operation != "present" and state == "absent":
            filtered.append(item)
    return filtered
