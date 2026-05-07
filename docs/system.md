# System

The system domain manages shared appliance configuration and management-plane access policy.

Current object families:

- core system settings
- DNS and NTP
- logging
- allowed IPs
- authentication and auth servers
- users
- user password changes
- TLS cert/key material
- SNMP

Current implementation status:

- canonical prep and runtime skeleton exists
- real apply/delete tasks exist for:
  - `f5os_system`
  - `f5os_dns`
  - `f5os_ntp_server`
  - `f5os_logging`
  - `f5os_allowed_ips`
  - `f5os_auth`
  - `f5os_auth_server`
  - `f5os_user`
  - `f5os_user_password_change`
  - `f5os_tls_cert_key`
  - `f5os_snmp`
- `f5os_user_password_change` is treated as apply-only because the module is a non-idempotent operational action, not a reversible desired-state object

Known module caveats from F5 docs:

- `f5os_logging` is not idempotent due to API restrictions
- `f5os_auth` is not fully idempotent for some fields such as password policy and encrypted secrets
- `f5os_user_password_change` is not idempotent
