# Playbook Structure

Canonical playbooks live under `playbooks/`. Root-level `bootstrap.yml`, `system.yml`, and `network.yml` are compatibility wrappers.

Each canonical domain follows the same pattern:

- `playbooks/<domain>.yml`
- `playbooks/<domain>/prep.yml`
- `playbooks/<domain>/prep/*.yml`
- `playbooks/<domain>/tasks/manage.yml`
- `playbooks/<domain>/tasks/audit.yml`
- `playbooks/<domain>/tasks/delete.yml`
- `playbooks/<domain>/tasks/apply.yml`
