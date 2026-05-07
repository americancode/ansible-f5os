# AWX Operating Model

This repo is designed to run primarily through AWX.

Core model:

- inventory defines the execution context
- credentials provide authentication only
- Git stores desired state in `vars/`
- job templates run one canonical playbook at a time against the right inventory group

Credential model:

- create the custom credential type from [f5os-credential-config.yaml](../f5os-credential-config.yaml)
- provide:
  - `F5_USERNAME`
  - `F5_PASSWORD`
  - `F5_VALIDATE_CERTS`
- do not store host or port in the credential

Inventory model:

- set `f5_host` per host
- set `f5_platform_type` per host
- use the host model documented in [inventory-model.md](inventory-model.md)

Recommended inventory grouping:

- `rseries`
- `velos_controllers`
- `velos_partitions`

Recommended job templates:

- one template per canonical playbook
- bind each template to the narrowest inventory group that matches its intent
- avoid one giant template that targets every platform type and every domain

Recommended templates:

- `bootstrap`
- `system`
- `network`
- `qos`
- `tenants`
- `software_lifecycle`
- `observability`

Launch-time controls:

- set `audit_mode=true` to preview runtime collections without changing the device
- override only the variables needed for the specific run
- prefer inventory and git-backed vars over ad hoc extra vars for normal operations

Execution guidance:

- `bootstrap` should be run first for a new platform target
- `system`, `network`, and `qos` are normal steady-state GitOps playbooks
- `tenants` and `software_lifecycle` should be scoped carefully because they can change tenant availability
- `observability` is for collection/export workflows, not convergence

Secret handling guidance:

- keep passwords, passphrases, image-source secrets, and imported TLS material out of committed var files
- reference AWX credentials, external secret injection, or protected lookups for sensitive fields
- treat `vars/` examples as shape examples, not production secret storage
