"""Var-tree discovery and shape helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.f5os_tools.validate.models import ValidationResult
from tools.f5os_tools.validate.yaml_io import load_yaml_file


REPO_ROOT = Path(__file__).resolve().parents[3]
VARS_ROOT = REPO_ROOT / "vars"


def yaml_files(root: Path) -> list[Path]:
    """Return repo YAML files beneath a tree in stable order."""
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.yml") if path.is_file())


def validate_settings_file(path: Path, result: ValidationResult) -> dict[str, Any]:
    """Load and validate one `settings.yml` file."""
    data = load_yaml_file(path, result)
    if data is None:
        return {}
    if not isinstance(data, dict):
        result.add_error(path, "`settings.yml` must contain a mapping")
        return {}
    for key, value in data.items():
        if not isinstance(value, dict):
            result.add_error(path, f"settings key `{key}` must map to a dictionary")
    return data


def collect_objects(
    directory: Path,
    collection_key: str,
    result: ValidationResult,
) -> list[tuple[Path, dict[str, Any]]]:
    """Load collection objects from all non-settings files in one var tree."""
    objects: list[tuple[Path, dict[str, Any]]] = []
    for path in yaml_files(directory):
        if path.name == "settings.yml":
            validate_settings_file(path, result)
            continue
        data = load_yaml_file(path, result)
        if data is None:
            continue
        if not isinstance(data, dict):
            result.add_error(path, "var files must contain a top-level mapping")
            continue
        if collection_key not in data:
            result.add_error(path, f"missing required top-level key `{collection_key}`")
            continue
        collection = data.get(collection_key)
        if not isinstance(collection, list):
            result.add_error(path, f"`{collection_key}` must be a list")
            continue
        for index, item in enumerate(collection):
            if not isinstance(item, dict):
                result.add_error(path, f"`{collection_key}[{index}]` must be a mapping")
                continue
            state = item.get("state", "present")
            if state not in {"present", "absent"}:
                result.add_error(path, f"`state` must be `present` or `absent`, got `{state}`", item.get("name"))
            objects.append((path, item))
    return objects


def require_keys(
    result: ValidationResult,
    path: Path,
    item: dict[str, Any],
    keys: list[str],
    object_name: str | None = None,
) -> None:
    """Record missing required keys on one object."""
    for key in keys:
        if key not in item or item[key] in (None, "", []):
            result.add_error(path, f"missing required key `{key}`", object_name)
