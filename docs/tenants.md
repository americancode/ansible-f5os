# Tenants

The tenants domain manages two explicit execution contexts:

- `f5os_tenant*` objects on rSeries or VELOS partition/appliance targets
- `velos_partition*` objects on the VELOS controller

Current object families:

- tenants
- tenant console access
- tenant waits
- VELOS partitions
- VELOS partition password changes
- VELOS partition HA configuration
- VELOS partition waits

Current implementation status:

- `runtime+validation` is implemented
- real apply/delete tasks exist for:
  - `f5os_tenant`
  - `f5os_tenant_console_enable`
  - `f5os_tenant_wait`
  - `velos_partition`
  - `velos_partition_change_password`
  - `velos_partition_ha_config`
  - `velos_partition_wait`

Execution boundary:

- `velos_partition`, `velos_partition_change_password`, `velos_partition_ha_config`, and `velos_partition_wait` are gated to `platform: velos-controller`
- `f5os_tenant`, `f5os_tenant_console_enable`, and `f5os_tenant_wait` are gated away from `velos-controller`
- keep those object families explicit in vars instead of hiding them behind one merged schema

Operational caveats from `ansible-doc`:

- `f5os_tenant` does not execute on the VELOS controller
- `f5os_tenant_wait` is an operational wait helper, not a reversible desired-state object
- `velos_partition_change_password` is not idempotent
- `velos_partition_ha_config` supports only `state: present`
- `velos_partition_wait` is an operational wait helper, not a reversible desired-state object
