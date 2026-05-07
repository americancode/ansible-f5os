"""Runtime handlers for helper-tool entrypoints."""

from tools.f5os_tools.specs import COVERAGE


def _print_placeholder(tool_name: str) -> int:
    print(f"{tool_name} is scaffolded but not implemented yet.")
    for status in COVERAGE:
        print(f"- {status.domain}: {status.fidelity}")
    return 0


def run_validate() -> int:
    """Run placeholder var validation."""
    return _print_placeholder("validate-vars")


def run_drift_check() -> int:
    """Run placeholder drift detection."""
    return _print_placeholder("drift-check")


def run_import() -> int:
    """Run placeholder brownfield import."""
    return _print_placeholder("import-from-f5os")
