# Variable Layout

The repo uses split var trees by domain, with room for recursive fragments and layered `settings.yml`.

Current domain roots:

- `vars/bootstrap/`
- `vars/system/`
- `vars/network/`
- `vars/qos/`
- `vars/tenants/`
- `vars/software_lifecycle/`
- `vars/observability/`

Each domain has:

- canonical object trees
- `deletions/` trees for reverse-order removal input
- support for nested directories and per-directory `settings.yml`

Current `settings.yml` behavior:

- fragment discovery is recursive within each object tree
- a fragment inherits `settings.yml` from the tree root through each intermediate directory down to its own directory
- deeper directories override higher-level defaults
- fragment object fields override inherited defaults

Example inheritance order for a fragment at `vars/network/vlans/region/site/leaf.yml`:

1. `vars/network/vlans/settings.yml`
2. `vars/network/vlans/region/settings.yml`
3. `vars/network/vlans/region/site/settings.yml`
4. object fields inside `leaf.yml`
