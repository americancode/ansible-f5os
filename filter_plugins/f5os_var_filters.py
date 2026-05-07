"""Thin Ansible filter entrypoint for F5OS var-tree helpers."""

from filter_plugins.f5os_filters.fragments import (
    aggregate_settings_fragments,
    classify_fragment_operations,
    discover_yaml_fragments,
)
from filter_plugins.f5os_filters.settings import load_settings_hierarchy


class FilterModule:
    """Expose repo filter helpers to Ansible."""

    def filters(self):
        return {
            "discover_yaml_fragments": discover_yaml_fragments,
            "aggregate_settings_fragments": aggregate_settings_fragments,
            "classify_fragment_operations": classify_fragment_operations,
            "load_settings_hierarchy": load_settings_hierarchy,
        }
