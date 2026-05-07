"""Static helper-tool metadata for the current repo surface."""

from tools.f5os_tools.models import CoverageStatus


COVERAGE = [
    CoverageStatus(domain="bootstrap", fidelity="runtime+validation", implemented=True),
    CoverageStatus(domain="system", fidelity="runtime+validation", implemented=True),
    CoverageStatus(domain="network", fidelity="runtime+validation", implemented=True),
]
