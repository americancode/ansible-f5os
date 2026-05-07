# Observability

The observability domain manages non-convergent collection and export workflows on F5OS devices.

Current object families:

- device info requests
- facts requests
- qkview requests
- config backups

Current implementation status:

- `runtime+validation` is implemented
- real apply/delete tasks exist for:
  - `f5os_device_info`
  - `f5os_facts`
  - `f5os_qkview`
  - `f5os_config_backup`

Operational caveats from `ansible-doc`:

- `f5os_device_info` and `f5os_facts` are read-only collection modules and do not support deletions
- `f5os_qkview` creates or deletes artifacts on the device, not remote uploads
- `f5os_config_backup` creates a backup on the device and uploads it to a remote target when configured
- this domain is for operator workflows and evidence collection, not normal config convergence
