"""Top-level var validator for the current F5OS repo domains."""

from __future__ import annotations

from pathlib import Path

from tools.f5os_tools.validate.domains import (
    validate_bootstrap,
    validate_network,
    validate_observability,
    validate_qos,
    validate_software_lifecycle,
    validate_system,
    validate_tenants,
)
from tools.f5os_tools.validate.models import ValidationResult
from tools.f5os_tools.validate.tree import REPO_ROOT


class Validator:
    """Validate the repo's implemented var trees and print a human-readable report."""

    def __init__(self) -> None:
        self.result = ValidationResult()

    def run(self) -> int:
        self._validate_repo_shape()
        validate_bootstrap(self.result)
        validate_system(self.result)
        validate_network(self.result)
        validate_qos(self.result)
        validate_tenants(self.result)
        validate_software_lifecycle(self.result)
        validate_observability(self.result)
        self._print_summary()
        return 0 if self.result.ok else 1

    def _validate_repo_shape(self) -> None:
        required_paths = [
            REPO_ROOT / "vars" / "common.yml",
            REPO_ROOT / "playbooks" / "bootstrap.yml",
            REPO_ROOT / "playbooks" / "system.yml",
            REPO_ROOT / "playbooks" / "network.yml",
            REPO_ROOT / "playbooks" / "qos.yml",
            REPO_ROOT / "playbooks" / "tenants.yml",
            REPO_ROOT / "playbooks" / "software_lifecycle.yml",
            REPO_ROOT / "playbooks" / "observability.yml",
        ]
        for path in required_paths:
            if not path.exists():
                self.result.add_error(path, "required repo path is missing")

    def _print_summary(self) -> None:
        for message in self.result.errors:
            self._print_message(message.level.upper(), message.path, message.message, message.object_name)
        for message in self.result.warnings:
            self._print_message(message.level.upper(), message.path, message.message, message.object_name)

        if self.result.ok:
            print(
                "validate-vars OK: "
                f"{self.result.checked_files} YAML files checked, "
                f"{len(self.result.warnings)} warning(s)"
            )
        else:
            print(
                "validate-vars FAILED: "
                f"{len(self.result.errors)} error(s), "
                f"{len(self.result.warnings)} warning(s), "
                f"{self.result.checked_files} YAML files checked"
            )

    @staticmethod
    def _print_message(level: str, path: Path, message: str, object_name: str | None) -> None:
        suffix = f" [{object_name}]" if object_name else ""
        print(f"{level}: {path.relative_to(REPO_ROOT)}{suffix}: {message}")
