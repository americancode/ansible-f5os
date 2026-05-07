"""YAML loading helpers for validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tools.f5os_tools.validate.models import ValidationResult


def load_yaml_file(path: Path, result: ValidationResult) -> dict[str, Any] | list[Any] | None:
    """Load one YAML file and record parser failures on the result object."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except Exception as exc:
        result.add_error(path, f"failed to parse YAML: {exc}")
        return None
    result.checked_files += 1
    return data
