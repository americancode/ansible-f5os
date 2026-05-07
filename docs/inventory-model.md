# Inventory Model

This repo assumes inventory hosts represent real F5OS execution contexts.

Preferred host model:

- one host per rSeries platform
- one host per VELOS controller
- one host per VELOS partition execution context

Required host vars:

- `f5_host`
- `f5_platform_type`

Allowed `f5_platform_type` values:

- `rseries`
- `velos-controller`
- `velos-partition`

Example inventory:

```yaml
all:
  children:
    rseries:
      hosts:
        r5900-a:
          f5_host: 192.0.2.10
          f5_platform_type: rseries

    velos_controllers:
      hosts:
        velos-controller-a:
          f5_host: 192.0.2.20
          f5_platform_type: velos-controller

    velos_partitions:
      hosts:
        velos-partition-edge-a:
          f5_host: 192.0.2.30
          f5_platform_type: velos-partition
```

Recommended playbook targeting:

- `bootstrap`
  - target `rseries` or `velos_controllers`
- `system`
  - target whichever host context actually owns the system settings you want to manage
- `network`
  - target the host context where those layer-2 objects exist
- `qos`
  - target the host context where those QoS objects exist
- `tenants`
  - target `rseries`, `velos_partitions`, or `velos_controllers` depending on the object family
- `software_lifecycle`
  - target the host context where the image or install action runs
- `observability`
  - target any host context for operational collection/export tasks

When to use object-level `platform`:

- use it in `tenants` when one `tenants` run intentionally includes both:
  - controller-side VELOS partition objects
  - tenant-side objects
- use it in `software_lifecycle` when one run intentionally includes both:
  - controller-side VELOS partition images
  - tenant-side images

When not to use object-level `platform`:

- do not add `platform` to every object by habit
- do not rely on mixed object families when separate inventory hosts and separate job templates are clearer
- do not encode inventory design mistakes into var files

AWX guidance:

- create separate inventories or groups for:
  - rSeries platform hosts
  - VELOS controllers
  - VELOS partition targets
- bind the job template to the narrowest inventory group that matches the playbook intent
- prefer separate job templates over one broad template with heavily mixed extra vars
