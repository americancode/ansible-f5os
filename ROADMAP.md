# F5OS Enterprise GitOps Roadmap

## To Do

1. Add immediate repository parity for CI and helper-tool execution.
   - Add `.gitlab-ci.yml` equivalent to the reference repo's validate and drift stages.
   - Add `Makefile` targets equivalent to:
     - `validate`
     - `validate-vars`
     - `validate-ansible`
   - Add syntax-check coverage for the currently implemented canonical playbooks:
     - `playbooks/bootstrap.yml`
     - `playbooks/system.yml`
     - `playbooks/network.yml`
   - Keep the CI and local validation contract aligned so `make validate` is the single operator entrypoint both locally and in GitLab CI.

2. Replace placeholder Python tooling with real F5OS-aware implementations.
   - Convert `tools/validate-vars.py` plus `tools/f5os_tools/` into a real validator package with domain-aware checks for:
     - `bootstrap`
     - `system`
     - `network`
   - Decide and document initial helper-tool fidelity per implemented domain:
     - `bootstrap`: likely `unsupported` or `runtime+validation` only
     - `system`: `unsupported` or `identity-only` until a real drift model exists
     - `network`: `unsupported` or `identity-only` until a real drift model exists
   - Replace placeholder `drift-check` behavior with an explicit F5OS coverage contract instead of generic placeholder output.
   - Replace placeholder `import-from-f5os` behavior with an explicit F5OS coverage contract instead of generic placeholder output.

3. Build the `network` domain for platform networking primitives.
   - Completion target: `runtime+validation+helper-tools`
   - Initial helper-tool fidelity target: `basic field drift`
   - Module coverage:
     - `f5os_interface`
     - `f5os_lag`
     - `f5os_vlan`
     - `f5os_fdb`
     - `f5os_lldp_config`
     - `f5os_stp_config`
   - Expected dependency order:
     - interfaces
     - lags
     - vlans
     - fdb entries
   - Var tree targets:
     - `vars/network/interfaces/`
     - `vars/network/lags/`
     - `vars/network/vlans/`
     - `vars/network/fdb/`
     - `vars/network/lldp/`
     - `vars/network/stp/`
     - `vars/network/deletions/<type>/`

4. Raise the shared loader and var-tree behavior to reference-repo parity.
   - The current recursive fragment/filter layer is only scaffold-level.
   - Add real hierarchical `settings.yml` inheritance across nested directories.
   - Add domain-aware validation for fragment shapes, required fields, and cross-file references.
   - Keep the runtime field model, example var files, and validation logic aligned.

5. Build a dedicated `qos` domain unless early implementation shows the objects fit cleanly inside `network` without making it noisy.
   - Completion target: `runtime+validation+helper-tools`
   - Initial helper-tool fidelity target: `identity-only`, then `basic field drift`
   - Module coverage:
     - `f5os_qos_mapping`
     - `f5os_qos_meter_group`
     - `f5os_qos_traffic_priority`
   - Var tree targets:
     - `vars/qos/mappings/`
     - `vars/qos/meter_groups/`
     - `vars/qos/traffic_priorities/`
     - `vars/qos/deletions/<type>/`

6. Build the `tenants` domain for tenant and chassis-partition lifecycle.
   - Completion target: `runtime+validation+helper-tools`
   - Initial helper-tool fidelity target: `basic field drift`
   - Module coverage:
     - `f5os_tenant`
     - `f5os_tenant_console_enable`
     - `f5os_tenant_wait`
     - `velos_partition`
     - `velos_partition_change_password`
     - `velos_partition_ha_config`
     - `velos_partition_wait`
   - Keep platform-specific object families explicit rather than hiding them behind one oversized schema.
   - Introduce intent-style authoring only if it compiles into canonical tenant or partition objects cleanly.
   - Var tree targets:
     - `vars/tenants/tenants/`
     - `vars/tenants/tenant_console/`
     - `vars/tenants/tenant_wait/`
     - `vars/tenants/velos_partitions/`
     - `vars/tenants/velos_partition_passwords/`
     - `vars/tenants/velos_partition_ha/`
     - `vars/tenants/velos_partition_wait/`
     - `vars/tenants/deletions/<type>/`

7. Build the `software_lifecycle` domain for software and image workflows.
   - Completion target: `runtime+validation`
   - Add helper-tool support later only if brownfield lifecycle management becomes part of the normal GitOps loop.
   - Module coverage:
     - `f5os_system_image_import`
     - `f5os_system_image_install`
     - `f5os_tenant_image`
     - `velos_partition_image`
   - Decide whether image import/install should remain one playbook or split into `images` and `upgrades` if execution safety requires narrower blast radius.
   - Var tree targets:
     - `vars/software_lifecycle/system_images/`
     - `vars/software_lifecycle/system_installs/`
     - `vars/software_lifecycle/tenant_images/`
     - `vars/software_lifecycle/velos_partition_images/`
     - `vars/software_lifecycle/deletions/`

8. Build the `observability` domain for diagnostics, exports, and non-config runtime collection tasks.
   - Completion target: `runtime+validation`
   - Module coverage:
     - `f5os_device_info`
     - `f5os_qkview`
     - `f5os_config_backup`
   - Treat this domain as operational tooling first, not config convergence.
   - Decide how much of it belongs in canonical playbooks versus `tools/` wrappers for export, collection, and artifact naming.
   - Var tree targets:
     - `vars/observability/device_info/`
     - `vars/observability/qkview/`
     - `vars/observability/config_backups/`

9. Add cross-platform modeling rules before implementation spreads.
   - Keep rSeries and VELOS differences visible in vars and docs rather than relying on hidden branching in tasks.
   - Decide whether platform splits belong in:
     - separate trees like `vars/rseries/...` and `vars/velos/...`
     - per-domain platform categories like `vars/tenants/velos_partitions/...`
     - shared canonical trees with explicit `platform` selectors
   - Document one repo-wide answer before multiple domains are implemented.

10. Add validation, drift, and import contracts per domain before claiming parity.
   - `validate-vars` must understand recursive var discovery and layered `settings.yml`.
   - `drift-check` must declare coverage domain by domain:
     - unsupported
     - `identity-only`
     - `basic field drift`
     - `model-aware`
     - `import-from-f5os` must use the same canonical var model that runtime playbooks consume.
   - Do not mark a domain complete if runtime schemas and helper-tool schemas diverge.

11. Add the supporting documentation set after the first domain skeletons exist.
   - `docs/index.md`
   - `docs/playbook-structure.md`
   - `docs/var-layout.md`
   - `docs/validation.md`
     - one domain doc per canonical playbook
   - AWX operating model and bootstrap handoff docs adapted from the BIG-IP repo where the workflow still applies

12. Add repository tooling and developer ergonomics to match the reference repo's standard.
   - Python packaging and lint/test targets for helper tools
   - example inventory and AWX-safe execution patterns
   - `audit_mode` support across canonical playbooks

## Proposals

1. Keep the first implementation pass narrow: build `bootstrap`, `system`, and `network` first, then add `tenants`.

2. Split tenant lifecycle by platform if the VELOS partition model and the generic tenant model force materially different var schemas or execution ordering.
   - `tenants-rseries`
   - `tenants-velos`

3. Split `software_lifecycle` if image import, install, and activation operations prove too risky to keep behind one playbook.
   - `images`
   - `upgrades`
   - `recovery`

4. Keep `observability` separate from `system` even if some modules feel adjacent.
   - `f5os_device_info`, `f5os_qkview`, and `f5os_config_backup` are operator workflows, not normal convergence primitives.

5. Add future dedicated domains only if they become operationally distinct enough to justify them.
   - backup retention and artifact shipping workflows
   - tenant promotion pipelines
   - certificate rotation workflows
   - compliance reporting and evidence export

6. Introduce intent/compiler trees only after the canonical runtime object model is stable in a domain.
   - Good candidates later:
     - tenant bundles
     - cluster onboarding patterns
     - platform baseline hardening bundles

7. Prefer host-scoped overlays or inventory grouping over embedding execution selectors on every object unless platform scale proves that object-level targeting is necessary.

8. Keep unsupported or awkward F5OS module surfaces visible in the roadmap instead of hiding them in ad hoc scripts.
   - If a module is collection-supported but does not fit the canonical GitOps lifecycle well, document that limitation explicitly before implementing more domains around it.
