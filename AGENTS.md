# Agent Instructions

These rules apply to any AI agent working in this repository.

## Project Overview

This repository manages F5OS-based platforms through declarative Ansible playbooks organized for GitOps-style operations. It targets F5 rSeries and VELOS systems, with AWX as the primary control plane and CLI fallback for bootstrap and recovery.

## Intended Core Structure

- `playbooks/` — canonical playbooks such as `bootstrap`, `system`, `network`, `tenants`, `software_lifecycle`, and `observability`
- `vars/` — split var trees organized by domain with layered `settings.yml` inheritance
- `docs/` — all operational documentation
- `tools/` — validation, drift, import, and utility scripts
- `ROADMAP.md` — concrete implementation backlog and proposals

## Implementation Integrity Rules

These are binding. A feature is not complete just because a playbook exists.

- Every implementation must declare its completion class in repo terms:
  - `runtime-only` — playbook behavior exists, but validator and/or helper-tool lifecycle support is intentionally incomplete
  - `runtime+validation` — playbook behavior and `tools/validate-vars.py` support exist, but helper-tool lifecycle support is intentionally incomplete
  - `runtime+validation+helper-tools` — runtime, validator, drift detection, and import coverage exist
  - `full parity` — runtime, validator, helper tools, docs, examples, README, and roadmap are all aligned

- Every helper-tool change must declare its fidelity level:
  - `identity-only` — existence/name/platform parity only
  - `basic field drift` — a limited, explicit field subset is compared or imported
  - `model-aware` — nested structures and cross-object linkages are reconstructed in the repo's actual field model

- Do not silently upgrade a feature's claimed completion class or helper-tool fidelity. If the repo only supports `runtime-only` or `identity-only`, that limitation must remain explicit in `ROADMAP.md` and the relevant docs.

- For every normal feature change, all repo Python tooling must be considered part of the implementation surface:
  - `tools/validate-vars.py`
  - supporting filter or helper modules such as `filter_plugins/f5os_var_filters.py` and split support packages under `filter_plugins/f5os_filters/`

- Do not mark a roadmap item complete unless the feature is operationally complete across the repo model:
  - `prep.yml` loads and classifies the data the runtime tasks actually consume
  - `tasks/apply.yml` supports create/update behavior
  - `tasks/delete.yml` supports reverse-order deletion behavior unless the roadmap documents an exception
  - `tasks/manage.yml` preserves repo-standard ordering and config save behavior
  - `tools/validate-vars.py` validates the tree and its references
  - docs and example var files describe the same field model that the runtime tasks actually use

- Preserve repo-wide contracts when adding a new domain or refactoring an existing one:
  - use a repo-wide `provider` variable from `vars/common.yml`
  - keep `tasks/manage.yml` as delete-first then apply-second unless `ROADMAP.md` explicitly documents an exception
  - preserve `audit_mode` behavior so every canonical playbook can render a no-change execution preview from the same prep-built runtime collections
  - keep top-level `prep.yml` files as documented orchestrators when prep logic grows; split heavier discovery/loading/classification flows into focused `prep/*.yml` snippets
  - when prep logic is the same across domains, prefer shared prep snippets under `playbooks/shared/prep/` plus shared Python-backed helpers under `filter_plugins/f5os_filters/`
  - nested var-tree directories are a supported authoring pattern; loaders should discover fragment files recursively and apply hierarchical `settings.yml` inheritance from the subtree root through intermediate directories

- Preserve the separation between canonical runtime objects and higher-level convenience authoring:
  - canonical playbooks should operate on normalized first-class F5OS objects
  - do not keep adding shortcut-specific branching directly into `tasks/apply.yml` or `tasks/delete.yml`
  - when a new “simple thing” or common pattern is needed, prefer adding it as an intent/compiler layer ahead of runtime tasks
  - do not place concrete intent files directly under `vars/<domain>/intents/`; place them under a first-level category such as `vars/<domain>/intents/clusters/...` or `vars/<domain>/intents/appliances/...`

- `bootstrap` is the expected documented exception to normal delete/apply semantics:
  - keep `playbooks/bootstrap/tasks/delete.yml` intentionally empty for day-0 actions that should not be reversed automatically
  - do not invent destructive rollback for first management reachability, license activation, or chassis primary-key seeding
  - keep that exception documented in `ROADMAP.md` and future bootstrap docs

## Documentation Rules

- Every new domain/playbook must produce a `docs/<domain>.md` file that covers:
  - overview of what the playbook manages
  - playbook structure diagram
  - var tree layout
  - object type reference table
  - authoring patterns and dependency order

- Every example var file should start with a short YAML comment header that explains:
  - what object family the file is for
  - which other objects it references or is referenced by
  - the top-level fields the objects in the file accept

- Keep code paths explorable:
  - Python helper functions in `filter_plugins/` and `tools/` should have function-level documentation
  - add YAML comments where prep ordering, normalization, or dependency handling would otherwise require reverse-engineering

## Python Tooling Structure Rule

This is binding for future modifications:

- all Python tooling changes must follow a modular package pattern with a thin compatibility entrypoint plus split modules by concern such as CLI, models, specs/constants, transforms/helpers, and runtime/orchestration
- avoid large monolithic scripts after a package split
- for `filter_plugins`, keep `filter_plugins/f5os_var_filters.py` as the thin Ansible entrypoint and place non-trivial implementation under `filter_plugins/f5os_filters/`

## Roadmap Maintenance

- keep `ROADMAP.md` limited to concrete `To Do` items and `Proposals`
- if work is completed, remove it from `ROADMAP.md` instead of keeping historical status sections there
- if a discovered gap changes the real delivery story, record it in `ROADMAP.md` before expanding into more feature work

## Mandatory Post-Change Checklist

### Playbooks

- [ ] `playbooks/<domain>.yml` or root wrapper exists
- [ ] `playbooks/<domain>/prep.yml` loads and shapes all new var trees
- [ ] `playbooks/<domain>/tasks/apply.yml` supports `state: present`
- [ ] `playbooks/<domain>/tasks/delete.yml` supports `state: absent` unless the roadmap documents a bootstrap exception
- [ ] `playbooks/<domain>/tasks/manage.yml` includes config save conditions for present/delete variables
- [ ] `playbooks/<domain>/tasks/audit.yml` exposes the same runtime collections for `audit_mode`

### Var Trees

- [ ] `vars/<domain>/<type>/` exists with example data and `settings.yml`
- [ ] `vars/<domain>/deletions/<type>/` exists with `.gitkeep` if empty
- [ ] example field names match the fields actually consumed by runtime tasks

### Python Tooling

- [ ] `tools/validate-vars.py` understands the new tree

### Docs

- [ ] `README.md` reflects the new playbook or object coverage
- [ ] `ROADMAP.md` reflects the remaining gaps honestly
- [ ] `docs/<domain>.md` and shared structural docs are aligned with runtime behavior
