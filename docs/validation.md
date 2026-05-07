# Validation

Validation now has a repo-standard entrypoint and a real first-pass Python var validator for the currently implemented domains.

Current local entrypoints:

- `make validate`
- `make validate-vars`
- `make validate-ansible`
- `make drift-check`

Direct script entrypoints still exist:

- `python3 tools/validate-vars.py`
- `python3 tools/drift-check.py`
- `python3 tools/import-from-f5os.py`

Current `make validate` behavior:

- runs repo Python var validation for:
  - `bootstrap`
  - `system`
  - `network`
- runs `ansible-playbook --syntax-check` for:
  - `playbooks/bootstrap.yml`
  - `playbooks/system.yml`
  - `playbooks/network.yml`

Current GitLab CI behavior:

- `validate` stage installs `ansible-core`, `PyYAML`, and the `f5networks.f5os` collection when needed, then runs `make validate`
- `drift-check` stage runs the current placeholder drift tool and stores `drift-report.txt` as an artifact

Air-gapped validation image:

- build locally with `make validate-image-build`
- run locally with `make validate-image-run`
- the image build is defined in `Dockerfile.validation`
- GitLab CI still defaults to the online install path with `VALIDATION_IMAGE=python:3.12`
- for GitLab CI in an air-gapped environment, prebuild and mirror a validation image, then override `VALIDATION_IMAGE` to that internal registry tag so the same pipeline can run without internet dependency installs

Known gap:

- `validate-vars` is now implemented for the current domains, but it is still not full parity with the reference repo's deeper tree inheritance and field-model validation
- `drift-check` and `import-from-f5os` are still scaffold-only
