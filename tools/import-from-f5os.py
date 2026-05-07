#!/usr/bin/env python3
"""Compatibility entrypoint for repository brownfield import."""

from tools.f5os_tools.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["import-from-f5os"]))
