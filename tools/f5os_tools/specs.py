"""Static helper-tool metadata used by the thin CLI runtime."""

from tools.f5os_tools.models import CoverageStatus


COVERAGE = [
    CoverageStatus(domain="bootstrap", fidelity="unsupported", implemented=False),
    CoverageStatus(domain="system", fidelity="unsupported", implemented=False),
    CoverageStatus(domain="network", fidelity="unsupported", implemented=False),
]
