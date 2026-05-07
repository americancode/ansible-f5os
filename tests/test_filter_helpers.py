"""Unit tests for repo-local filter helpers."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from filter_plugins.f5os_filters.common import deep_merge_dicts
from filter_plugins.f5os_filters.fragments import aggregate_settings_fragments, classify_fragment_operations
from filter_plugins.f5os_filters.settings import load_settings_hierarchy


class DeepMergeTests(unittest.TestCase):
    """Validate recursive merge behavior used by settings inheritance."""

    def test_deep_merge_dicts_overlays_nested_values(self) -> None:
        merged = deep_merge_dicts(
            {"a": 1, "nested": {"left": "keep", "right": "old"}},
            {"nested": {"right": "new", "extra": True}},
        )
        self.assertEqual(
            merged,
            {"a": 1, "nested": {"left": "keep", "right": "new", "extra": True}},
        )


class SettingsHierarchyTests(unittest.TestCase):
    """Validate layered settings discovery from tree root to leaf."""

    def test_load_settings_hierarchy_merges_root_to_leaf(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir) / "vars" / "network" / "vlans"
            site = root / "region" / "site"
            site.mkdir(parents=True)

            (root / "settings.yml").write_text("defaults:\n  color: blue\n  nested:\n    a: 1\n", encoding="utf-8")
            ((root / "region") / "settings.yml").write_text("defaults:\n  nested:\n    b: 2\n", encoding="utf-8")
            (site / "settings.yml").write_text("defaults:\n  color: green\n", encoding="utf-8")
            fragment = site / "leaf.yml"
            fragment.write_text("items: []\n", encoding="utf-8")

            payload = load_settings_hierarchy(str(fragment), str(root))

        self.assertEqual(payload, {"defaults": {"color": "green", "nested": {"a": 1, "b": 2}}})


class FragmentAggregationTests(unittest.TestCase):
    """Validate fragment aggregation and operation classification."""

    def test_aggregate_settings_fragments_applies_defaults_and_deletion_state(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir) / "vars" / "system" / "users"
            root.mkdir(parents=True)
            (root / "settings.yml").write_text("user_defaults:\n  role: admin\n", encoding="utf-8")
            fragment = root / "users.yml"
            fragment.write_text("users: []\n", encoding="utf-8")

            include_results = [
                {
                    "item": str(fragment),
                    "ansible_facts": {
                        "user_fragment": {
                            "users": [
                                {"username": "alice"},
                            ]
                        }
                    },
                }
            ]

            aggregated = aggregate_settings_fragments(
                include_results,
                str(root),
                "user_fragment",
                "users",
                "user_defaults",
                deletion_mode=True,
            )

        self.assertEqual(
            aggregated,
            [{"username": "alice", "role": "admin", "state": "absent"}],
        )

    def test_classify_fragment_operations_treats_non_absent_as_apply(self) -> None:
        items = [
            {"name": "one", "state": "present"},
            {"name": "two", "state": "import"},
            {"name": "three", "state": "enabled"},
            {"name": "four", "state": "absent"},
        ]

        self.assertEqual(
            [item["name"] for item in classify_fragment_operations(items, "present")],
            ["one", "two", "three"],
        )
        self.assertEqual(
            [item["name"] for item in classify_fragment_operations(items, "delete")],
            ["four"],
        )


if __name__ == "__main__":
    unittest.main()
