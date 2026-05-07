"""Shared tooling data models for validator support."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CoverageStatus:
    """Describe current helper-tool support for a domain or object family."""

    domain: str
    fidelity: str
    implemented: bool
