"""Thin command dispatcher for repo-local helper tooling."""

from __future__ import annotations

import argparse

from tools.f5os_tools.runtime import run_validate


def main(argv: list[str] | None = None) -> int:
    """Parse one repo helper subcommand and dispatch to the runtime layer."""
    parser = argparse.ArgumentParser(prog="f5os-tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate-vars")

    args = parser.parse_args(argv)

    return run_validate()
