# Tenant Lifecycle

This repo manages BIG-IP tenant lifecycle on F5OS through `software_lifecycle` and `tenants`.

Normal lifecycle order:

1. upload tenant image
2. create tenant object
3. wait for the requested tenant state
4. enable or lock tenant-console access as needed
5. perform later updates through the same canonical vars
6. delete tenant cleanly when required

Recommended playbook flow:

1. run `software_lifecycle` for `tenant_images`
2. run `tenants` for `tenants`
3. run `tenants` for `tenant_wait`
4. run `tenants` for `tenant_console`

rSeries / VELOS partition side:

- `f5os_tenant`
- `f5os_tenant_wait`
- `f5os_tenant_console_enable`
- `f5os_tenant_image`

VELOS controller side:

- `velos_partition`
- `velos_partition_wait`
- `velos_partition_ha_config`
- `velos_partition_change_password`
- `velos_partition_image`

Safe authoring guidance:

- upload images before declaring a tenant that depends on them
- keep tenant create/update objects in `vars/tenants/tenants/`
- keep wait objects in `vars/tenants/tenant_wait/`
- keep tenant-console objects in `vars/tenants/tenant_console/`
- keep VELOS partition controller objects in the `velos_partitions*` trees

Safe update guidance:

- use `audit_mode=true` before changing:
  - tenant image versions
  - management IPs
  - node placement
  - VELOS partition placement or HA preferences
- treat `running_state` changes as operationally significant
- keep image workflow and tenant declaration changes in the same change set when they are coupled

Safe delete guidance:

- put tenant removals in `vars/tenants/deletions/tenants/`
- use controller-side deletion trees only for real VELOS partition removal objects
- do not use deletion trees for:
  - `tenant_console`
  - `tenant_wait`
  - `velos_partition_wait`
  - `velos_partition_change_password`
  - `velos_partition_ha`

Operational cautions:

- `f5os_tenant_wait` and `velos_partition_wait` are operational wait helpers, not reversible state
- password change modules are not idempotent
- controller-side and tenant-side objects should be separated by inventory target whenever possible
- this repo manages tenant lifecycle on F5OS, not BIG-IP application configuration inside the tenant
