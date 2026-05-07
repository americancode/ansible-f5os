"""Shared tooling data models for future validator, drift, and import work."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CoverageStatus:
    """Describe current helper-tool support for a domain or object family."""

    domain: str
    fidelity: str
    implemented: bool
