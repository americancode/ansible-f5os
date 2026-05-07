# Validation

Validation now has a repo-standard entrypoint and a real first-pass Python var validator for the currently implemented domains.

Current local entrypoints:

- `make validate`
- `make validate-vars`
- `make validate-ansible`

Direct script entrypoints still exist:

- `python3 tools/validate-vars.py`

Current `make validate` behavior:

- runs repo Python var validation for:
  - `bootstrap`
  - `system`
  - `network`
  - `qos`
  - `tenants`
  - `software_lifecycle`
  - `observability`
- runs `ansible-playbook --syntax-check` for:
  - `playbooks/bootstrap.yml`
  - `playbooks/system.yml`
  - `playbooks/network.yml`
  - `playbooks/qos.yml`
  - `playbooks/tenants.yml`
  - `playbooks/software_lifecycle.yml`
  - `playbooks/observability.yml`

Current validator depth:

- recursive fragment discovery and layered `settings.yml` inheritance
- top-level collection and state checks
- domain-specific field checks
- selected nested schema checks for higher-risk object families such as:
  - system logging
  - allowed IPs
  - auth and auth server objects
  - TLS objects
  - SNMP objects
  - software lifecycle transport/state fields
  - observability request shapes

Current GitLab CI behavior:

- `validate` stage installs `ansible-core`, `PyYAML`, and the `f5networks.f5os` collection when needed, then runs `make validate`

Air-gapped validation image:

- build locally with `make validate-image-build`
- run locally with `make validate-image-run`
- the image build is defined in `Dockerfile.validation`
- GitLab CI still defaults to the online install path with `VALIDATION_IMAGE=python:3.12`
- for GitLab CI in an air-gapped environment, prebuild and mirror a validation image, then override `VALIDATION_IMAGE` to that internal registry tag so the same pipeline can run without internet dependency installs

Known gap:

- `validate-vars` now covers the current runtime model with nested checks in several high-risk areas, but it is still not full parity with any future compiler/intent layers or live-device semantic validation
