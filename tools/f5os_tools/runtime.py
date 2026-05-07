"""Runtime handlers for helper-tool entrypoints."""

from tools.f5os_tools.specs import COVERAGE
from tools.f5os_tools.validate.validator import Validator


def _print_placeholder(tool_name: str) -> int:
    print(f"{tool_name} is scaffolded but not implemented yet.")
    for status in COVERAGE:
        print(f"- {status.domain}: {status.fidelity}")
    return 0


def run_validate() -> int:
    """Run repo var validation."""
    return Validator().run()
