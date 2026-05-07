"""Data models for repository var validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ValidationMessage:
    """One validation issue tied to a file and optional object name."""

    level: str
    path: Path
    message: str
    object_name: str | None = None


@dataclass
class ValidationResult:
    """Aggregate validation findings and execution summary."""

    errors: list[ValidationMessage] = field(default_factory=list)
    warnings: list[ValidationMessage] = field(default_factory=list)
    checked_files: int = 0

    def add_error(self, path: Path, message: str, object_name: str | None = None) -> None:
        self.errors.append(ValidationMessage("error", path, message, object_name))

    def add_warning(self, path: Path, message: str, object_name: str | None = None) -> None:
        self.warnings.append(ValidationMessage("warning", path, message, object_name))

    @property
    def ok(self) -> bool:
        return not self.errors
