# Network

The network domain manages platform networking primitives and link-layer policy objects.

Current object families:

- interfaces
- lags
- vlans
- forwarding database entries
- LLDP
- STP

Current implementation status:

- canonical prep and runtime skeleton exists
- real apply/delete tasks exist for:
  - `f5os_interface`
  - `f5os_lag`
  - `f5os_vlan`
  - `f5os_fdb`
  - `f5os_lldp_config`
  - `f5os_stp_config`

Known module caveats from F5 docs:

- `f5os_interface`, `f5os_lag`, `f5os_vlan`, and `f5os_fdb` do not execute on the VELOS controller
- `f5os_interface` does not expose MTU or interface-type mutation through the module surface
