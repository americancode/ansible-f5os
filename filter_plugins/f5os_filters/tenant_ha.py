"""Compiler helpers for BIG-IP tenant HA intent objects."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .common import deep_merge_dicts


def _clean_none_values(item: dict[str, Any]) -> dict[str, Any]:
    """Return a copy without keys whose value is None."""
    return {key: value for key, value in item.items() if value is not None}


def compile_tenant_ha_intents(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Compile HA pair intents into canonical runtime object collections."""
    compiled: dict[str, list[dict[str, Any]]] = {
        "tenant_images": [],
        "tenants": [],
        "tenant_waits": [],
        "tenant_console_users": [],
        "bigip_handoffs": [],
    }

    for pair in items or []:
        if not isinstance(pair, dict):
            continue

        platform = pair.get("platform", "rseries")
        pair_name = pair.get("name")
        image = deepcopy(pair.get("image") or {})
        tenant_defaults = deepcopy(pair.get("tenant_defaults") or {})
        tenants = deepcopy(pair.get("tenants") or [])
        wait = deepcopy(pair.get("wait") or {})
        console = deepcopy(pair.get("tenant_console") or {})
        handoff = deepcopy(pair.get("bigip_handoff") or {})
        image_name = image.get("image_name") or tenant_defaults.get("image_name")

        if image:
            image_object = deep_merge_dicts({"platform": platform}, image)
            compiled["tenant_images"].append(_clean_none_values(image_object))

        for tenant in tenants:
            if not isinstance(tenant, dict):
                continue
            tenant_object = deep_merge_dicts(
                {
                    "platform": platform,
                    "image_name": image_name,
                    "state": "present",
                },
                tenant_defaults,
            )
            tenant_object = deep_merge_dicts(tenant_object, tenant)
            compiled["tenants"].append(_clean_none_values(tenant_object))

            tenant_name = tenant.get("name")
            if tenant_name and wait:
                wait_object = deep_merge_dicts(
                    {
                        "name": tenant_name,
                        "platform": platform,
                    },
                    wait,
                )
                compiled["tenant_waits"].append(_clean_none_values(wait_object))

            if tenant_name and console:
                console_object = deep_merge_dicts(
                    {
                        "tenant_username": tenant_name,
                        "platform": platform,
                    },
                    console,
                )
                compiled["tenant_console_users"].append(_clean_none_values(console_object))

        if handoff:
            handoff_object = deep_merge_dicts(
                {
                    "name": pair_name,
                    "platform": platform,
                    "tenants": tenants,
                },
                handoff,
            )
            compiled["bigip_handoffs"].append(_clean_none_values(handoff_object))

    return compiled
