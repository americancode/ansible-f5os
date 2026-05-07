# Bootstrap

The bootstrap domain is reserved for day-0 operations that should not be auto-reversed by the standard delete/apply lifecycle.

Planned object families:

- licensing
- primary key seeding
- management interface reachability

Current implementation status:

- canonical prep and runtime skeleton exists
- real apply tasks exist for:
  - `f5os_license`
  - `f5os_primarykey`
  - `rseries_management_interfaces`
  - `velos_controller_management_interfaces`
- delete input is rejected intentionally because these bootstrap modules do not support a normal absent lifecycle

Platform mapping:

- `rseries_management_interfaces` uses `platform: rseries`
- `velos_controller_management_interfaces` uses `platform: velos-controller`

Connection model:

- F5OS playbooks use `connection: httpapi`
- the scaffold derives `ansible_host`, `ansible_user`, `ansible_httpapi_password`, `ansible_httpapi_port`, and `ansible_network_os` from `vars/common.yml`
- default API port is `8888`; F5 documentation also notes that port `443` can be used with a different URI path
