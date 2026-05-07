# Bootstrap Handoff

Bootstrap is the handoff from day-0 reachability work into normal GitOps operations.

Bootstrap covers:

- license activation
- primary key seeding
- initial management interface configuration

Bootstrap does not try to auto-reverse those actions.

Expected handoff sequence:

1. establish first reachable management address
2. validate AWX or CLI can authenticate over the F5OS `httpapi` connection
3. set inventory host vars:
   - `f5_host`
   - `f5_platform_type`
4. move ongoing configuration to the steady-state playbooks:
   - `system`
   - `network`
   - `qos`
   - `tenants`
   - `software_lifecycle`
   - `observability`

Recommended operator checks after bootstrap:

- run `system` in `audit_mode`
- run `network` in `audit_mode`
- confirm the host is placed in the correct inventory group
- confirm `platform_type` matches the real execution context

Platform-specific notes:

- `rseries_management_interfaces` applies only to `rseries`
- `velos_controller_management_interfaces` applies only to `velos-controller`
- VELOS partition targets are not bootstrapped through the same management-interface object family

Why the handoff matters:

- bootstrap establishes control-plane reachability
- steady-state playbooks assume a stable inventory identity and normal automation access
- mixing day-0 recovery steps into normal GitOps loops creates unnecessary risk
