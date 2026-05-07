# ansible-f5os

Declarative Ansible playbooks for managing F5OS-based platforms in a GitOps-style repository.

This repository is being bootstrapped from the structure and operating model used in `ansible-bigip`, but adapted for F5 rSeries and VELOS platforms and for the F5OS module surface.

Current focus:

- establish the repo structure, docs, and roadmap
- mirror the reference repo's `playbooks/`, `vars/`, and Python tooling patterns
- implement canonical F5OS domains with matching split var trees and validation support

Implemented domains:

- `bootstrap`
- `system`
- `network`
- `qos`
- `tenants`
- `software_lifecycle`
- `observability`

Current next domain:

- cross-platform modeling and documentation hardening

Platform targeting uses the repo-standard selectors documented in [docs/platform-model.md](docs/platform-model.md):

- `rseries`
- `velos-controller`
- `velos-partition`

Start with [ROADMAP.md](ROADMAP.md).
