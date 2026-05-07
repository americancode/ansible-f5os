# F5OS Enterprise GitOps Roadmap

## To Do

1. Build the `observability` domain for diagnostics, exports, and non-config runtime collection tasks.
   - Completion target: `runtime+validation`
   - Module coverage:
     - `f5os_device_info`
     - `f5os_facts`
     - `f5os_qkview`
     - `f5os_config_backup`
   - Treat this domain as operational tooling first, not config convergence.
   - Decide how much of it belongs in canonical playbooks versus `tools/` wrappers for export, collection, and artifact naming.
   - Var tree targets:
     - `vars/observability/device_info/`
     - `vars/observability/facts/`
     - `vars/observability/qkview/`
     - `vars/observability/config_backups/`

2. Add cross-platform modeling rules before implementation spreads.
   - Keep rSeries and VELOS differences visible in vars and docs rather than relying on hidden branching in tasks.
   - Decide whether platform splits belong in:
     - separate trees like `vars/rseries/...` and `vars/velos/...`
     - per-domain platform categories like `vars/tenants/velos_partitions/...`
     - shared canonical trees with explicit `platform` selectors
   - Document one repo-wide answer before multiple domains are implemented.

3. Extend validation depth as new domains land.
   - `validate-vars` already understands recursive var discovery and layered `settings.yml`.
   - Keep nested field models and cross-object references aligned with each implemented module surface.
   - Do not mark a domain complete if runtime schemas and validation schemas diverge.

4. Add the remaining supporting documentation adapted from the BIG-IP repo where the workflow still applies.
   - AWX operating model and bootstrap handoff docs
   - example inventory and execution docs for rSeries versus VELOS targets
   - tenant lifecycle docs covering image upload, tenant creation, wait sequencing, tenant-console access, and safe delete/update patterns
   - domain usage examples as each remaining domain is implemented

5. Add repository tooling and developer ergonomics to match the reference repo's standard.
   - Python packaging and lint/test targets for helper tools
   - `audit_mode` support across canonical playbooks
   - keep local validation and CI behavior aligned as the repo grows

## Proposals

1. Split `software_lifecycle` further if image import, install, and activation operations prove too risky to keep behind one playbook.
   - `images`
   - `upgrades`
   - `recovery`

2. Split tenant lifecycle by platform if the VELOS partition model and the generic tenant model force materially different var schemas or execution ordering.
   - `tenants-rseries`
   - `tenants-velos`

3. Keep `observability` separate from `system` even if some modules feel adjacent.
   - `f5os_device_info`, `f5os_qkview`, and `f5os_config_backup` are operator workflows, not normal convergence primitives.

4. Add future dedicated domains only if they become operationally distinct enough to justify them.
   - backup retention and artifact shipping workflows
   - tenant promotion pipelines
   - certificate rotation workflows
   - compliance reporting and evidence export

5. Introduce intent/compiler trees only after the canonical runtime object model is stable in a domain.
   - Good candidates later:
     - tenant bundles
     - cluster onboarding patterns
     - platform baseline hardening bundles

6. Prefer host-scoped overlays or inventory grouping over embedding execution selectors on every object unless platform scale proves that object-level targeting is necessary.

7. Keep unsupported or awkward F5OS module surfaces visible in the roadmap instead of hiding them in ad hoc scripts.
   - If a module is collection-supported but does not fit the canonical GitOps lifecycle well, document that limitation explicitly before implementing more domains around it.
