#!/usr/bin/env python3
"""Compatibility entrypoint for repository drift detection."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.f5os_tools.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["drift-check"]))
