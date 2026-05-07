# Variable Layout

The repo uses split var trees by domain, with room for recursive fragments and layered `settings.yml`.

Current domain roots:

- `vars/bootstrap/`
- `vars/system/`
- `vars/network/`

Each domain has:

- canonical object trees
- `deletions/` trees for reverse-order removal input
- room for nested directories and per-directory `settings.yml`
