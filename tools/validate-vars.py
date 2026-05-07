#!/usr/bin/env python3
"""Compatibility entrypoint for repository var validation."""

from tools.f5os_tools.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["validate-vars"]))
