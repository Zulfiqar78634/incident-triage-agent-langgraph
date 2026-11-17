"""Domain exceptions."""

from __future__ import annotations


class DomainError(Exception):
    pass


class ToolValidationError(DomainError):
    pass


class UnknownToolError(DomainError):
    pass
