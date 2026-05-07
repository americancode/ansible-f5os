"""Domain-specific validation for implemented F5OS var trees."""

from __future__ import annotations

from pathlib import Path

from tools.f5os_tools.validate.models import ValidationResult
from tools.f5os_tools.validate.tree import VARS_ROOT, collect_objects, require_keys, yaml_files


def _name(item: dict) -> str | None:
    return item.get("name") or item.get("username") or item.get("user_name") or item.get("server")


def _require_mapping(result: ValidationResult, path: Path, value: object, field_name: str, object_name: str | None) -> dict | None:
    if not isinstance(value, dict):
        result.add_error(path, f"`{field_name}` must be a mapping", object_name)
        return None
    return value


def _require_list_of_mappings(
    result: ValidationResult,
    path: Path,
    value: object,
    field_name: str,
    object_name: str | None,
) -> list[dict] | None:
    if not isinstance(value, list):
        result.add_error(path, f"`{field_name}` must be a list", object_name)
        return None
    mappings: list[dict] = []
    for index, entry in enumerate(value):
        if not isinstance(entry, dict):
            result.add_error(path, f"`{field_name}[{index}]` must be a mapping", object_name)
            continue
        mappings.append(entry)
    return mappings


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
        if platform and platform not in {"rseries", "velos-controller"}:
            result.add_error(path, "`platform` must be `rseries` or `velos-controller`", _name(item))
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
            continue
        for server in item.get("servers", []) or []:
            if not isinstance(server, dict):
                result.add_error(path, "`servers` entries must be mappings", _name(item))
                continue
            require_keys(result, path, server, ["address"], _name(item))
            if "protocol" in server and server["protocol"] not in {"tcp", "udp"}:
                result.add_error(path, "`servers.protocol` must be `tcp` or `udp`", _name(item))
            log_entries = _require_list_of_mappings(result, path, server.get("logs", []), "servers.logs", _name(item))
            for log_entry in log_entries or []:
                require_keys(result, path, log_entry, ["facility", "severity"], _name(item))

    allowed_ip_objects = collect_objects(VARS_ROOT / "system" / "allowed_ips", "allowed_ip_sets", result)
    for path, item in allowed_ip_objects:
        require_keys(result, path, item, ["allowed"], _name(item))
        if not isinstance(item.get("allowed"), list):
            result.add_error(path, "`allowed` must be a list", _name(item))
            continue
        for allowed_entry in item["allowed"]:
            if not isinstance(allowed_entry, dict):
                result.add_error(path, "`allowed` entries must be mappings", _name(item))
                continue
            require_keys(result, path, allowed_entry, ["name"], _name(item))
            has_ipv4 = "ipv4" in allowed_entry
            has_ipv6 = "ipv6" in allowed_entry
            if not (has_ipv4 or has_ipv6):
                result.add_error(path, "allowed entry must define `ipv4` or `ipv6`", _name(item))
            for address_family in ("ipv4", "ipv6"):
                if address_family not in allowed_entry:
                    continue
                af_value = _require_mapping(result, path, allowed_entry[address_family], f"allowed.{address_family}", _name(item))
                if not af_value:
                    continue
                require_keys(result, path, af_value, ["address", "prefix"], _name(item))

    auth_objects = collect_objects(VARS_ROOT / "system" / "auth", "auth_configs", result)
    for path, item in auth_objects:
        require_keys(result, path, item, ["auth_order"], _name(item))
        if "auth_order" in item and not isinstance(item["auth_order"], list):
            result.add_error(path, "`auth_order` must be a list", _name(item))
        remote_roles = item.get("remote_roles", [])
        if remote_roles and not isinstance(remote_roles, list):
            result.add_error(path, "`remote_roles` must be a list", _name(item))
        for role_entry in remote_roles if isinstance(remote_roles, list) else []:
            if not isinstance(role_entry, dict):
                result.add_error(path, "`remote_roles` entries must be mappings", _name(item))
                continue
            require_keys(result, path, role_entry, ["rolename"], _name(role_entry))
            if "remote_gid" not in role_entry and "ldap_group" not in role_entry:
                result.add_error(path, "remote role must define `remote_gid` or `ldap_group`", _name(item))
        password_policy = item.get("password_policy")
        if password_policy is not None:
            policy = _require_mapping(result, path, password_policy, "password_policy", _name(item))
            if policy:
                for field_name in ("min_length", "min_lower", "min_upper", "min_number", "min_special", "unlock_time"):
                    if field_name in policy and not isinstance(policy[field_name], int):
                        result.add_error(path, f"`password_policy.{field_name}` must be an integer", _name(item))

    auth_server_objects = collect_objects(VARS_ROOT / "system" / "auth_servers", "auth_servers", result)
    auth_server_names: set[str] = set()
    for path, item in auth_server_objects:
        require_keys(result, path, item, ["name", "provider_type", "server"], _name(item))
        if "name" in item:
            auth_server_names.add(item["name"])
        if "server" in item and not isinstance(item["server"], list):
            result.add_error(path, "`server` must be a list", _name(item))
            continue
        for server_entry in item.get("server", []) or []:
            if not isinstance(server_entry, dict):
                result.add_error(path, "`server` entries must be mappings", _name(item))
                continue
            require_keys(result, path, server_entry, ["server_ip"], _name(item))

    # Warn when auth_order references remote providers without a matching server group.
    remote_providers = {"radius", "ldap", "tacacs"}
    if auth_objects and not auth_server_names:
        for path, item in auth_objects:
            if any(provider in remote_providers for provider in item.get("auth_order", [])):
                result.add_warning(path, "remote auth is configured but no auth server groups exist under vars/system/auth_servers", _name(item))

    auth_ldap_objects = collect_objects(VARS_ROOT / "system" / "auth_ldap", "auth_ldap_configs", result, allowed_states=None)
    for path, item in auth_ldap_objects:
        if not any(
            key in item
            for key in (
                "active_directory",
                "base_dn",
                "bind_dn",
                "bind_password",
                "bind_timeout",
                "chase_referrals",
                "idle_timeout",
                "ldap_version",
                "read_timeout",
                "tls",
                "tls_certificate",
                "tls_certificate_validation",
                "tls_ciphers",
                "tls_key",
                "unix_attributes",
            )
        ):
            result.add_error(path, "auth_ldap object must define at least one LDAP configuration field", _name(item))
        if "tls" in item and item["tls"] not in {"start_tls", "off", "on"}:
            result.add_error(path, "`tls` must be `start_tls`, `off`, or `on`", _name(item))
        if "tls_certificate_validation" in item and item["tls_certificate_validation"] not in {"never", "allow", "try", "hard", "demand"}:
            result.add_error(path, "`tls_certificate_validation` must be a valid f5os_auth_ldap choice", _name(item))

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
        if "key_type" in item and item["key_type"] not in {"rsa", "encrypted-rsa", "ecdsa", "encrypted-ecdsa"}:
            result.add_error(path, "`key_type` must be a valid f5os_tls_cert_key choice", _name(item))
        if item.get("key_type") in {"rsa", "encrypted-rsa"} and "key_size" in item and item["key_size"] not in {2048, 3072, 4096}:
            result.add_error(path, "`key_size` must be 2048, 3072, or 4096", _name(item))
        if item.get("key_type") in {"ecdsa", "encrypted-ecdsa"} and "key_curve" in item and item["key_curve"] not in {"prime256v1", "secp384r1"}:
            result.add_error(path, "`key_curve` must be `prime256v1` or `secp384r1`", _name(item))

    snmp_objects = collect_objects(VARS_ROOT / "system" / "snmp", "snmp_configs", result)
    for path, item in snmp_objects:
        if not any(key in item for key in ("snmp_mib", "snmp_community", "snmp_target", "snmp_user")):
            result.add_error(path, "snmp object must define at least one snmp_* section", _name(item))
        if "snmp_mib" in item:
            _require_mapping(result, path, item["snmp_mib"], "snmp_mib", _name(item))
        community_entries = _require_list_of_mappings(result, path, item.get("snmp_community", []), "snmp_community", _name(item)) if "snmp_community" in item else []
        for community in community_entries or []:
            require_keys(result, path, community, ["name"], _name(item))
            if "security_model" in community and not isinstance(community["security_model"], list):
                result.add_error(path, "`snmp_community.security_model` must be a list", _name(item))
        target_entries = _require_list_of_mappings(result, path, item.get("snmp_target", []), "snmp_target", _name(item)) if "snmp_target" in item else []
        for target in target_entries or []:
            require_keys(result, path, target, ["name", "security_model"], _name(item))
            if "ipv4_address" not in target and "ipv6_address" not in target:
                result.add_error(path, "snmp_target entry must define `ipv4_address` or `ipv6_address`", _name(item))
        user_entries = _require_list_of_mappings(result, path, item.get("snmp_user", []), "snmp_user", _name(item)) if "snmp_user" in item else []
        for user in user_entries or []:
            require_keys(result, path, user, ["name"], _name(item))

    imported_tls_objects = collect_objects(
        VARS_ROOT / "system" / "imported_tls",
        "imported_tls_cert_keys",
        result,
        allowed_states={"present", "absent"},
    )
    for path, item in imported_tls_objects:
        require_keys(result, path, item, ["certificate", "key"], _name(item))
        if "verify_client" in item and not isinstance(item["verify_client"], bool):
            result.add_error(path, "`verify_client` must be a boolean", _name(item))
        if "verify_client_depth" in item and not isinstance(item["verify_client_depth"], int):
            result.add_error(path, "`verify_client_depth` must be an integer", _name(item))


def validate_network(result: ValidationResult) -> None:
    """Validate network var trees and simple cross-object references."""
    interface_objects = collect_objects(VARS_ROOT / "network" / "interfaces", "interfaces", result)
    interface_names: set[str] = set()
    for path, item in interface_objects:
        require_keys(result, path, item, ["name"], _name(item))
        if "name" in item:
            interface_names.add(item["name"])
        if "trunk_vlans" in item and not isinstance(item["trunk_vlans"], list):
            result.add_error(path, "`trunk_vlans` must be a list", _name(item))

    lag_objects = collect_objects(VARS_ROOT / "network" / "lags", "lags", result)
    lag_names: set[str] = set()
    for path, item in lag_objects:
        require_keys(result, path, item, ["name", "lag_type", "config_members"], _name(item))
        if "name" in item:
            lag_names.add(item["name"])
        members = item.get("config_members", [])
        if not isinstance(members, list):
            result.add_error(path, "`config_members` must be a list", _name(item))
            continue
        for member in members:
            if member not in interface_names:
                result.add_error(path, f"LAG member `{member}` is not defined under vars/network/interfaces", _name(item))
        if "trunk_vlans" in item and not isinstance(item["trunk_vlans"], list):
            result.add_error(path, "`trunk_vlans` must be a list", _name(item))

    vlan_objects = collect_objects(VARS_ROOT / "network" / "vlans", "vlans", result)
    vlan_ids: set[int] = set()
    for path, item in vlan_objects:
        require_keys(result, path, item, ["name", "vlan_id"], _name(item))
        vlan_id = item.get("vlan_id")
        if isinstance(vlan_id, int):
            vlan_ids.add(vlan_id)

    fdb_objects = collect_objects(VARS_ROOT / "network" / "fdb", "fdb_entries", result)
    for path, item in fdb_objects:
        require_keys(result, path, item, ["name", "mac_address", "vlan_id", "interface"], _name(item))
        if isinstance(item.get("vlan_id"), int) and item["vlan_id"] not in vlan_ids:
            result.add_error(path, f"FDB vlan_id `{item['vlan_id']}` is not defined under vars/network/vlans", _name(item))
        if item.get("interface") and item["interface"] not in interface_names and item["interface"] not in lag_names:
            result.add_error(path, f"FDB interface `{item['interface']}` is not a known interface or LAG", _name(item))

    for collection_key, subdir in (("lldp_configs", "lldp"), ("stp_configs", "stp")):
        policy_objects = collect_objects(VARS_ROOT / "network" / subdir, collection_key, result)
        for path, item in policy_objects:
            require_keys(result, path, item, ["name"], _name(item))
            if "interfaces" in item and not isinstance(item["interfaces"], dict):
                result.add_error(path, "`interfaces` must be a dictionary", _name(item))


def validate_qos(result: ValidationResult) -> None:
    """Validate QoS var trees and cross-object references."""
    traffic_priority_objects = collect_objects(
        VARS_ROOT / "qos" / "traffic_priorities",
        "traffic_priorities",
        result,
    )
    traffic_priority_names: set[str] = set()
    for path, item in traffic_priority_objects:
        require_keys(result, path, item, ["name"], _name(item))
        if "name" in item:
            traffic_priority_names.add(item["name"])
        if "default_qos" in item and item["default_qos"] not in {"802.1p", "dscp"}:
            result.add_error(path, "`default_qos` must be `802.1p` or `dscp`", _name(item))
        if "qos_status" in item and item["qos_status"] not in {"disable", "802.1p", "dscp"}:
            result.add_error(path, "`qos_status` must be `disable`, `802.1p`, or `dscp`", _name(item))

    mapping_objects = collect_objects(VARS_ROOT / "qos" / "mappings", "qos_mappings", result)
    for path, item in mapping_objects:
        require_keys(result, path, item, ["mapping_type", "traffic_priority"], _name(item))
        if item.get("mapping_type") not in {"802.1p", "dscp"}:
            result.add_error(path, "`mapping_type` must be `802.1p` or `dscp`", _name(item))
        if item.get("traffic_priority") not in traffic_priority_names:
            result.add_error(path, "mapping references an unknown traffic priority", _name(item))
        if "mapping_values" in item and not isinstance(item["mapping_values"], list):
            result.add_error(path, "`mapping_values` must be a list", _name(item))

    meter_group_objects = collect_objects(VARS_ROOT / "qos" / "meter_groups", "meter_groups", result)
    for path, item in meter_group_objects:
        require_keys(result, path, item, ["name"], _name(item))
        if "interfaces" in item and not isinstance(item["interfaces"], list):
            result.add_error(path, "`interfaces` must be a list", _name(item))
        if "meters" in item and not isinstance(item["meters"], list):
            result.add_error(path, "`meters` must be a list", _name(item))
            continue
        for meter in item.get("meters", []) or []:
            if not isinstance(meter, dict):
                result.add_error(path, "`meters` entries must be mappings", _name(item))
                continue
            require_keys(result, path, meter, ["name", "weight"], _name(item))
            if meter.get("name") not in traffic_priority_names:
                result.add_error(path, f"meter references unknown traffic priority `{meter.get('name')}`", _name(item))


def validate_tenants(result: ValidationResult) -> None:
    """Validate tenant and VELOS partition var trees and cross-object references."""
    tenant_objects = collect_objects(
        VARS_ROOT / "tenants" / "tenants",
        "tenants",
        result,
        allowed_states={"present", "absent"},
    )
    tenant_names: set[str] = set()
    for path, item in tenant_objects:
        require_keys(result, path, item, ["name", "nodes"], _name(item))
        if "name" in item:
            tenant_names.add(item["name"])
        if "nodes" in item and not isinstance(item["nodes"], list):
            result.add_error(path, "`nodes` must be a list", _name(item))
        if "nodes" in item and isinstance(item["nodes"], list):
            for node in item["nodes"]:
                if not isinstance(node, int):
                    result.add_error(path, "`nodes` entries must be integers", _name(item))
        if "running_state" in item and item["running_state"] not in {"configured", "provisioned", "deployed"}:
            result.add_error(path, "`running_state` must be `configured`, `provisioned`, or `deployed`", _name(item))
        if "platform" in item and item["platform"] not in {"rseries", "velos-partition", "velos-controller"}:
            result.add_error(path, "`platform` must be `rseries`, `velos-partition`, or `velos-controller`", _name(item))
        if item.get("platform") == "velos-controller":
            result.add_error(path, "tenant objects cannot target `velos-controller`", _name(item))
        if "cryptos" in item and item["cryptos"] not in {"enabled", "disabled"}:
            result.add_error(path, "`cryptos` must be `enabled` or `disabled`", _name(item))
        if "vlans" in item and not isinstance(item["vlans"], list):
            result.add_error(path, "`vlans` must be a list", _name(item))
        if "vlans" in item and isinstance(item["vlans"], list):
            for vlan in item["vlans"]:
                if not isinstance(vlan, int):
                    result.add_error(path, "`vlans` entries must be integers", _name(item))

    tenant_console_objects = collect_objects(
        VARS_ROOT / "tenants" / "tenant_console",
        "tenant_console_users",
        result,
        allowed_states={"enabled", "locked"},
    )
    for path, item in tenant_console_objects:
        require_keys(result, path, item, ["tenant_username"], _name(item))
        if item.get("tenant_username") not in tenant_names:
            result.add_warning(path, "tenant console entry references a tenant not defined under vars/tenants/tenants", _name(item))
        if "state" in item and item["state"] not in {"enabled", "locked"}:
            result.add_error(path, "`state` must be `enabled` or `locked`", _name(item))

    tenant_wait_objects = collect_objects(
        VARS_ROOT / "tenants" / "tenant_wait",
        "tenant_waits",
        result,
        allowed_states={"configured", "provisioned", "deployed", "ssh-ready", "api-ready"},
    )
    for path, item in tenant_wait_objects:
        require_keys(result, path, item, ["name"], _name(item))
        if item.get("name") not in tenant_names:
            result.add_warning(path, "tenant wait entry references a tenant not defined under vars/tenants/tenants", _name(item))
        if "state" in item and item["state"] not in {"configured", "provisioned", "deployed", "ssh-ready", "api-ready"}:
            result.add_error(path, "`state` must be a valid f5os_tenant_wait state", _name(item))

    partition_objects = collect_objects(
        VARS_ROOT / "tenants" / "velos_partitions",
        "velos_partitions",
        result,
        allowed_states={"present", "absent", "enabled", "disabled"},
    )
    partition_names: set[str] = set()
    for path, item in partition_objects:
        require_keys(result, path, item, ["name"], _name(item))
        if "name" in item:
            partition_names.add(item["name"])
        if "slots" in item and not isinstance(item["slots"], list):
            result.add_error(path, "`slots` must be a list", _name(item))
        if "slots" in item and isinstance(item["slots"], list):
            for slot in item["slots"]:
                if not isinstance(slot, int):
                    result.add_error(path, "`slots` entries must be integers", _name(item))
        if "platform" in item and item["platform"] != "velos-controller":
            result.add_error(path, "VELOS partition objects must target `velos-controller`", _name(item))

    partition_password_objects = collect_objects(
        VARS_ROOT / "tenants" / "velos_partition_passwords",
        "velos_partition_password_changes",
        result,
        allowed_states=None,
    )
    for path, item in partition_password_objects:
        require_keys(result, path, item, ["user_name", "old_password", "new_password"], _name(item))

    partition_ha_objects = collect_objects(
        VARS_ROOT / "tenants" / "velos_partition_ha",
        "velos_partition_ha_configs",
        result,
        allowed_states={"present"},
    )
    for path, item in partition_ha_objects:
        require_keys(result, path, item, ["prefer_node"], _name(item))
        if item.get("name") and item["name"] not in partition_names:
            result.add_warning(path, "partition HA entry references a partition not defined under vars/tenants/velos_partitions", _name(item))
        if item.get("prefer_node") not in {"prefer-1", "prefer-2", "active-controller", "auto"}:
            result.add_error(path, "`prefer_node` must be a valid velos_partition_ha_config choice", _name(item))

    partition_wait_objects = collect_objects(
        VARS_ROOT / "tenants" / "velos_partition_wait",
        "velos_partition_waits",
        result,
        allowed_states={"running", "ssh-ready"},
    )
    for path, item in partition_wait_objects:
        require_keys(result, path, item, ["name"], _name(item))
        if item.get("name") not in partition_names:
            result.add_warning(path, "partition wait entry references a partition not defined under vars/tenants/velos_partitions", _name(item))
        if "state" in item and item["state"] not in {"running", "ssh-ready"}:
            result.add_error(path, "`state` must be `running` or `ssh-ready`", _name(item))


def validate_software_lifecycle(result: ValidationResult) -> None:
    """Validate software lifecycle var trees and execution-context boundaries."""
    system_image_objects = collect_objects(
        VARS_ROOT / "software_lifecycle" / "system_images",
        "system_images",
        result,
        allowed_states={"import", "present", "absent"},
    )
    for path, item in system_image_objects:
        require_keys(result, path, item, ["remote_image_url"], _name(item))
        if "local_path" in item and item["local_path"] not in {"images/import", "images/staging", "images/tenant", "images"}:
            result.add_error(path, "`local_path` must be a valid f5os_system_image_import path", _name(item))
        if "timeout" in item and not isinstance(item["timeout"], int):
            result.add_error(path, "`timeout` must be an integer", _name(item))

    system_install_objects = collect_objects(
        VARS_ROOT / "software_lifecycle" / "system_installs",
        "system_installs",
        result,
        allowed_states={"install", "present"},
    )
    for path, item in system_install_objects:
        require_keys(result, path, item, ["image_version"], _name(item))
        if "timeout" in item and not isinstance(item["timeout"], int):
            result.add_error(path, "`timeout` must be an integer", _name(item))

    tenant_image_objects = collect_objects(
        VARS_ROOT / "software_lifecycle" / "tenant_images",
        "tenant_images",
        result,
        allowed_states={"import", "present", "absent"},
    )
    for path, item in tenant_image_objects:
        require_keys(result, path, item, ["image_name"], _name(item))
        if "platform" in item and item["platform"] == "velos-controller":
            result.add_error(path, "tenant image objects cannot target `velos-controller`", _name(item))
        if "local_path" in item and item["local_path"] not in {"images/import", "images/staging", "images/tenant", "images"}:
            result.add_error(path, "`local_path` must be a valid f5os_tenant_image path", _name(item))
        if "protocol" in item and item["protocol"] not in {"scp", "sftp", "https"}:
            result.add_error(path, "`protocol` must be `scp`, `sftp`, or `https`", _name(item))
        if item.get("state") in {"import", "present"}:
            if "remote_host" not in item and item.get("state", "import") == "import":
                result.add_warning(path, "tenant image import usually requires `remote_host`", _name(item))
            if "remote_path" not in item and item.get("state", "import") == "import":
                result.add_warning(path, "tenant image import usually requires `remote_path`", _name(item))

    velos_partition_image_objects = collect_objects(
        VARS_ROOT / "software_lifecycle" / "velos_partition_images",
        "velos_partition_images",
        result,
        allowed_states={"import", "present", "absent"},
    )
    for path, item in velos_partition_image_objects:
        require_keys(result, path, item, ["image_name"], _name(item))
        if "platform" in item and item["platform"] != "velos-controller":
            result.add_error(path, "VELOS partition image objects must target `velos-controller`", _name(item))
        if "protocol" in item and item["protocol"] not in {"scp", "sftp", "https"}:
            result.add_error(path, "`protocol` must be `scp`, `sftp`, or `https`", _name(item))
        if item.get("state") in {"import", "present"}:
            if "remote_host" not in item:
                result.add_warning(path, "VELOS partition image workflow usually requires `remote_host`", _name(item))
            if "remote_path" not in item:
                result.add_warning(path, "VELOS partition image workflow usually requires `remote_path`", _name(item))


def validate_observability(result: ValidationResult) -> None:
    """Validate observability var trees."""
    device_info_objects = collect_objects(
        VARS_ROOT / "observability" / "device_info",
        "device_info_requests",
        result,
        allowed_states={"present"},
    )
    valid_device_subsets = {
        "all",
        "interfaces",
        "lag-interfaces",
        "vlans",
        "controller-images",
        "partition-images",
        "partitions-info",
        "tenant-images",
        "tenants-info",
        "snmp-info",
        "qos-info",
        "system-info",
        "server-groups",
        "users",
        "fdb",
        "tls",
        "restconf-token",
        "allowed-ips",
        "!all",
        "!interfaces",
        "!lag-interfaces",
        "!vlans",
        "!controller-images",
        "!partition-images",
        "!partitions-info",
        "!tenant-images",
        "!tenants-info",
        "!snmp-info",
        "!qos-info",
        "!system-info",
        "!server-groups",
        "!users",
        "!fdb",
        "!tls",
        "!restconf-token",
        "!allowed-ips",
    }
    for path, item in device_info_objects:
        require_keys(result, path, item, ["gather_subset"], _name(item))
        if not isinstance(item.get("gather_subset"), list):
            result.add_error(path, "`gather_subset` must be a list", _name(item))
            continue
        for subset in item["gather_subset"]:
            if subset not in valid_device_subsets:
                result.add_error(path, f"unsupported device info gather subset `{subset}`", _name(item))

    facts_objects = collect_objects(
        VARS_ROOT / "observability" / "facts",
        "facts_requests",
        result,
        allowed_states=None,
    )
    for path, item in facts_objects:
        if "gather_subset" in item and not isinstance(item["gather_subset"], list):
            result.add_error(path, "`gather_subset` must be a list when provided", _name(item))

    qkview_objects = collect_objects(
        VARS_ROOT / "observability" / "qkview",
        "qkview_requests",
        result,
        allowed_states={"present", "absent"},
    )
    for path, item in qkview_objects:
        require_keys(result, path, item, ["filename"], _name(item))
        for field_name in ("max_core_size", "max_file_size", "timeout"):
            if field_name in item and not isinstance(item[field_name], int):
                result.add_error(path, f"`{field_name}` must be an integer", _name(item))

    config_backup_objects = collect_objects(
        VARS_ROOT / "observability" / "config_backups",
        "config_backups",
        result,
        allowed_states={"present", "absent"},
    )
    for path, item in config_backup_objects:
        require_keys(result, path, item, ["name"], _name(item))
        if "protocol" in item and item["protocol"] not in {"https", "scp", "sftp"}:
            result.add_error(path, "`protocol` must be `https`, `scp`, or `sftp`", _name(item))
        if item.get("state", "present") == "present":
            if "remote_host" not in item:
                result.add_warning(path, "config backup export usually requires `remote_host`", _name(item))
            if "remote_path" not in item:
                result.add_warning(path, "config backup export usually requires `remote_path`", _name(item))


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
