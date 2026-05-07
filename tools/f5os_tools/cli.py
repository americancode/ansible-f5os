"""Thin command dispatcher for repo-local helper tooling."""

from __future__ import annotations

import argparse

from tools.f5os_tools.runtime import run_drift_check, run_import, run_validate


def main(argv: list[str] | None = None) -> int:
    """Parse one repo helper subcommand and dispatch to the runtime layer."""
    parser = argparse.ArgumentParser(prog="f5os-tools")
    parser.add_argument("command", choices=["validate-vars", "drift-check", "import-from-f5os"])
    args = parser.parse_args(argv)

    if args.command == "validate-vars":
        return run_validate()
    if args.command == "drift-check":
        return run_drift_check()
    return run_import()
