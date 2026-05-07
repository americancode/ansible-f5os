# QoS

The QoS domain manages traffic priorities, mapping rules, and meter groups on F5OS.

Current object families:

- traffic priorities
- mappings
- meter groups

Current implementation status:

- canonical prep and runtime skeleton exists
- real apply/delete tasks exist for:
  - `f5os_qos_traffic_priority`
  - `f5os_qos_mapping`
  - `f5os_qos_meter_group`

Dependency order:

- apply traffic priorities first
- then mappings
- then meter groups

Delete order is the reverse:

- meter groups
- mappings
- traffic priorities
