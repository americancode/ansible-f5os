"""Domain-specific validation for implemented F5OS var trees."""

from __future__ import annotations

from pathlib import Path

from tools.f5os_tools.validate.models import ValidationResult
from tools.f5os_tools.validate.tree import VARS_ROOT, collect_objects, require_keys, yaml_files


def _name(item: dict) -> str | None:
    return item.get("name") or item.get("username") or item.get("user_name") or item.get("server")


def validate_bootstrap(result: ValidationResult) -> None:
    """Validate bootstrap var trees."""
    license_objects = collect_objects(VARS_ROOT / "bootstrap" / "license", "licenses", result)
    for path, item in license_objects:
        require_keys(result, path, item, ["registration_key"], _name(item))

    primary_keys = collect_objects(VARS_ROOT / "bootstrap" / "primarykey", "primary_keys", result)
    for path, item in primary_keys:
        require_keys(result, path, item, ["passphrase", "salt"], _name(item))

    mgmt_objects = collect_objects(
        VARS_ROOT / "bootstrap" / "management_interfaces",
        "management_interfaces",
        result,
    )
    for path, item in mgmt_objects:
        require_keys(result, path, item, ["dhcp"], _name(item))
        platform = item.get("platform")
        if platform and platform not in {"rseries", "velos"}:
            result.add_error(path, "`platform` must be `rseries` or `velos`", _name(item))
        if item.get("dhcp") is False and not any(item.get(key) for key in ("ipv4", "ipv6")):
            result.add_error(path, "static management config requires `ipv4` or `ipv6`", _name(item))


def validate_system(result: ValidationResult) -> None:
    """Validate system var trees."""
    system_objects = collect_objects(VARS_ROOT / "system" / "system", "systems", result)
    for path, item in system_objects:
        if not any(key in item for key in ("hostname", "timezone", "motd", "login_banner", "gui_advisory")):
            result.add_error(path, "system object must define at least one configurable field", _name(item))

    dns_objects = collect_objects(VARS_ROOT / "system" / "dns", "dns_servers", result)
    for path, item in dns_objects:
        require_keys(result, path, item, ["dns_servers"], _name(item))
        if not isinstance(item.get("dns_servers"), list):
            result.add_error(path, "`dns_servers` must be a list", _name(item))

    ntp_objects = collect_objects(VARS_ROOT / "system" / "ntp_servers", "ntp_servers", result)
    for path, item in ntp_objects:
        require_keys(result, path, item, ["server"], _name(item))

    logging_objects = collect_objects(VARS_ROOT / "system" / "logging", "logging_profiles", result)
    for path, item in logging_objects:
        if "servers" in item and not isinstance(item["servers"], list):
            result.add_error(path, "`servers` must be a list when provided", _name(item))

    allowed_ip_objects = collect_objects(VARS_ROOT / "system" / "allowed_ips", "allowed_ip_sets", result)
    for path, item in allowed_ip_objects:
        require_keys(result, path, item, ["allowed"], _name(item))
        if not isinstance(item.get("allowed"), list):
            result.add_error(path, "`allowed` must be a list", _name(item))

    auth_objects = collect_objects(VARS_ROOT / "system" / "auth", "auth_configs", result)
    for path, item in auth_objects:
        require_keys(result, path, item, ["auth_order"], _name(item))
        if "auth_order" in item and not isinstance(item["auth_order"], list):
            result.add_error(path, "`auth_order` must be a list", _name(item))

    auth_server_objects = collect_objects(VARS_ROOT / "system" / "auth_servers", "auth_servers", result)
    auth_server_names: set[str] = set()
    for path, item in auth_server_objects:
        require_keys(result, path, item, ["name", "provider_type", "server"], _name(item))
        if "name" in item:
            auth_server_names.add(item["name"])
        if "server" in item and not isinstance(item["server"], list):
            result.add_error(path, "`server` must be a list", _name(item))

    # Warn when auth_order references remote providers without a matching server group.
    remote_providers = {"radius", "ldap", "tacacs"}
    if auth_objects and not auth_server_names:
        for path, item in auth_objects:
            if any(provider in remote_providers for provider in item.get("auth_order", [])):
                result.add_warning(path, "remote auth is configured but no auth server groups exist under vars/system/auth_servers", _name(item))

    user_objects = collect_objects(VARS_ROOT / "system" / "users", "users", result)
    usernames: set[str] = set()
    for path, item in user_objects:
        require_keys(result, path, item, ["username", "role"], _name(item))
        username = item.get("username")
        if username:
            usernames.add(username)

    password_change_objects = collect_objects(
        VARS_ROOT / "system" / "user_password_changes",
        "user_password_changes",
        result,
    )
    for path, item in password_change_objects:
        require_keys(result, path, item, ["user_name", "old_password", "new_password"], _name(item))
        if usernames and item.get("user_name") not in usernames:
            result.add_warning(path, "password change references a user not defined under vars/system/users", _name(item))

    tls_objects = collect_objects(VARS_ROOT / "system" / "tls", "tls_cert_keys", result)
    for path, item in tls_objects:
        require_keys(result, path, item, ["name"], _name(item))

    snmp_objects = collect_objects(VARS_ROOT / "system" / "snmp", "snmp_configs", result)
    for path, item in snmp_objects:
        if not any(key in item for key in ("snmp_mib", "snmp_community", "snmp_target", "snmp_user")):
            result.add_error(path, "snmp object must define at least one snmp_* section", _name(item))


def validate_network(result: ValidationResult) -> None:
    """Validate network var trees and simple cross-object references."""
    interface_objects = collect_objects(VARS_ROOT / "network" / "interfaces", "interfaces", result)
    interface_names: set[str] = set()
    for path, item in interface_objects:
        require_keys(result, path, item, ["name"], _name(item))
        if "name" in item:
            interface_names.add(item["name"])

    lag_objects = collect_objects(VARS_ROOT / "network" / "lags", "lags", result)
    lag_names: set[str] = set()
    for path, item in lag_objects:
        require_keys(result, path, item, ["name", "members"], _name(item))
        if "name" in item:
            lag_names.add(item["name"])
        members = item.get("members", [])
        if not isinstance(members, list):
            result.add_error(path, "`members` must be a list", _name(item))
            continue
        for member in members:
            if member not in interface_names:
                result.add_error(path, f"LAG member `{member}` is not defined under vars/network/interfaces", _name(item))

    vlan_objects = collect_objects(VARS_ROOT / "network" / "vlans", "vlans", result)
    vlan_names: set[str] = set()
    for path, item in vlan_objects:
        require_keys(result, path, item, ["name", "vlan_id", "interfaces"], _name(item))
        if "name" in item:
            vlan_names.add(item["name"])
        for attachment in item.get("interfaces", []) or []:
            if attachment not in interface_names and attachment not in lag_names:
                result.add_error(path, f"VLAN attachment `{attachment}` is not a known interface or LAG", _name(item))

    fdb_objects = collect_objects(VARS_ROOT / "network" / "fdb", "fdb_entries", result)
    for path, item in fdb_objects:
        require_keys(result, path, item, ["name", "mac_address", "vlan", "interface"], _name(item))
        if item.get("vlan") and item["vlan"] not in vlan_names:
            result.add_error(path, f"FDB vlan `{item['vlan']}` is not defined under vars/network/vlans", _name(item))
        if item.get("interface") and item["interface"] not in interface_names and item["interface"] not in lag_names:
            result.add_error(path, f"FDB interface `{item['interface']}` is not a known interface or LAG", _name(item))

    for collection_key, subdir in (("lldp_configs", "lldp"), ("stp_configs", "stp")):
        policy_objects = collect_objects(VARS_ROOT / "network" / subdir, collection_key, result)
        for path, item in policy_objects:
            require_keys(result, path, item, ["name"], _name(item))


def validate_deletion_trees(result: ValidationResult) -> None:
    """Validate that deletion trees contain parseable YAML only."""
    deletions_root = VARS_ROOT
    for path in yaml_files(deletions_root):
        if ".gitkeep" in str(path):
            continue
        # Non-settings files are already validated by domain loaders. This only
        # ensures nested settings files inside deletion trees are not malformed.
        if path.name == "settings.yml":
            continue
