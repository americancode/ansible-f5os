"""Settings hierarchy helpers for recursive var-tree loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .common import deep_merge_dicts


class AnsibleVarLoader(yaml.SafeLoader):
    """YAML loader that accepts Ansible-specific custom tags."""


def construct_ansible_tag(loader: AnsibleVarLoader, tag_suffix: str, node: yaml.Node) -> Any:
    """Pass Ansible-style YAML tags through unchanged."""
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    raise TypeError(f"Unsupported YAML node type: {type(node)!r}")


AnsibleVarLoader.add_multi_constructor("!", construct_ansible_tag)


def load_settings_hierarchy(source_file: str | None, settings_root: str | None) -> dict[str, Any]:
    """Merge `settings.yml` files from a fragment directory back to the tree root.

    The root-most settings file is applied first, then each deeper directory's
    settings override it, so the closest ancestor wins.
    """
    if source_file in (None, "") or settings_root in (None, ""):
        return {}

    source_dir = Path(str(source_file)).resolve().parent
    root_dir = Path(str(settings_root)).resolve()

    try:
        source_dir.relative_to(root_dir)
    except ValueError:
        return {}

    chain: list[Path] = []
    current = source_dir
    while True:
        chain.append(current / "settings.yml")
        if current == root_dir:
            break
        if root_dir not in current.parents:
            break
        current = current.parent

    merged: dict[str, Any] = {}
    for settings_path in reversed(chain):
        if not settings_path.exists():
            continue
        payload = yaml.load(settings_path.read_text(encoding="utf-8"), Loader=AnsibleVarLoader)
        if isinstance(payload, dict):
            merged = deep_merge_dicts(merged, payload)
    return merged
