# Platform Model

This repo uses one explicit platform vocabulary across vars, inventory, docs, and task gating.

Canonical platform selectors:

- `rseries`
- `velos-controller`
- `velos-partition`

Meaning:

- `rseries`: the F5OS platform host on an rSeries device
- `velos-controller`: the VELOS controller management plane
- `velos-partition`: an F5OS partition runtime context on VELOS

Repo-wide rule:

- set `platform_type` per inventory host in host vars, group vars, or AWX extra vars
- use per-object `platform` only when one host intentionally carries mixed object families
- do not introduce alternate labels like `velos` or hidden implicit platform branching in new domains

Current domain mapping:

- `bootstrap`
  - `rseries_management_interfaces` -> `rseries`
  - `velos_controller_management_interfaces` -> `velos-controller`
- `system`
  - normally shared across `rseries`, `velos-controller`, and `velos-partition`
  - object-level `platform` selectors are optional and should be added only where a module surface is truly platform-specific
- `network`
  - normally shared across the target host context
- `qos`
  - normally shared across the target host context
- `tenants`
  - `f5os_tenant`, `f5os_tenant_console_enable`, `f5os_tenant_wait` -> `rseries` or `velos-partition`
  - `velos_partition`, `velos_partition_change_password`, `velos_partition_ha_config`, `velos_partition_wait` -> `velos-controller`
- `software_lifecycle`
  - `f5os_tenant_image` -> `rseries` or `velos-partition`
  - `velos_partition_image` -> `velos-controller`
  - `f5os_system_image_import` and `f5os_system_image_install` remain host-context operations
- `observability`
  - shared across the host context unless a future object family proves platform-specific

Authoring guidance:

- prefer host-scoped targeting first:
  - inventory host represents one real execution context
  - `platform_type` describes that host
- use object-scoped `platform` only when a single canonical playbook intentionally carries both controller-side and tenant-side objects
- when an object family requires different schemas or ordering between `rseries` and VELOS contexts, split the var trees by object family rather than hiding the difference in task logic
