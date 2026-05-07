# Software Lifecycle

The software lifecycle domain manages image import and software installation workflows across platform, tenant, and VELOS partition surfaces.

Current object families:

- system images
- system installs
- tenant images
- VELOS partition images

Current implementation status:

- `runtime+validation` is implemented
- real apply/delete tasks exist for:
  - `f5os_system_image_import`
  - `f5os_system_image_install`
  - `f5os_tenant_image`
  - `velos_partition_image`

Execution boundary:

- `f5os_tenant_image` is gated away from `platform: velos-controller`
- `velos_partition_image` is gated to `platform: velos-controller`
- `f5os_system_image_import` and `f5os_system_image_install` are not further platform-split in the repo today

Operational caveats from `ansible-doc`:

- `f5os_system_image_import`, `f5os_tenant_image`, and `velos_partition_image` use transitional states like `import` and `present`, not normal desired-state `present/absent`
- `f5os_system_image_install` uses `install` and `present`; its documented `absent` option is unsupported and is rejected by this repo
- repeated import requests are not immediately idempotent while an upload is still in progress
- `f5os_tenant_image` does not execute on the VELOS controller
- `velos_partition_image` can take significant time to register after upload even when transfer completes successfully
