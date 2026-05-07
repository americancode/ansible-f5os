# F5OS to BIG-IP HA Onboarding

This runbook tracks the intended handoff from F5OS tenant provisioning to BIG-IP tenant HA configuration.

Scope boundary:

- this repo provisions and prepares BIG-IP tenant VMs on F5OS
- BIG-IP HA inside those tenants is configured by the BIG-IP automation layer

Expected flow:

1. upload or verify the BIG-IP tenant image through `software_lifecycle`
2. create the two tenant VMs through `tenants`
3. wait for tenant readiness through `tenant_wait`
4. apply tenant-console policy where needed
5. hand tenant management IPs and metadata to BIG-IP automation
6. run BIG-IP onboarding, trust, failover, sync, and application configuration from the BIG-IP repo

HA intent authoring:

- author HA pairs under `vars/tenants/intents/ha_pairs/`
- the intent compiler emits canonical F5OS runtime objects for:
  - tenant image import
  - both tenant declarations
  - tenant wait objects
  - tenant-console policy
  - BIG-IP handoff metadata

Required HA intent fields:

- `name`
- `image.image_name`
- `tenant_defaults`
- exactly two tenant members unless `expected_members` is set
- unique tenant names
- unique tenant management IPs
- `wait`
- `bigip_handoff.inventory_group`
- `bigip_handoff.cluster_name`

BIG-IP handoff shape:

- `inventory_group`: downstream BIG-IP inventory group name
- `cluster_name`: BIG-IP HA cluster identifier
- `automation_repo`: repo or automation system expected to consume the handoff

Operational boundary:

- F5OS automation gets the BIG-IP tenants deployed and reachable
- BIG-IP automation configures:
  - onboarding
  - device trust
  - config sync
  - failover network
  - traffic groups
  - floating addresses
  - application services

Recommended AWX sequencing:

1. run `software_lifecycle` against the F5OS host context
2. run `tenants` against the F5OS host context
3. verify `tenant_wait` reaches the requested state
4. launch the BIG-IP automation workflow with handoff metadata from the HA intent
