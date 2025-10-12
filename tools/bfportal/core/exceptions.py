#!/usr/bin/env python3
"""Custom exceptions for the BF Portal conversion toolset."""


class BFPortalError(Exception):
    """Base exception for all BF Portal toolset errors."""


class ParseError(BFPortalError):
    """Raised when a file cannot be parsed."""


class MappingError(BFPortalError):
    """Raised when asset mapping fails."""


class OutOfBoundsError(BFPortalError):
    """Raised when an object is outside valid bounds."""


class TerrainError(BFPortalError):
    """Raised when terrain queries fail."""


class ValidationError(BFPortalError):
    """Raised when validation fails."""


class ConfigurationError(BFPortalError):
    """Raised when configuration is invalid."""
