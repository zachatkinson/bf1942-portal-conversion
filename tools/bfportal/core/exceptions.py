#!/usr/bin/env python3
"""Custom exceptions for the BF Portal conversion toolset."""


class BFPortalError(Exception):
    """Base exception for all BF Portal toolset errors."""
    pass


class ParseError(BFPortalError):
    """Raised when a file cannot be parsed."""
    pass


class MappingError(BFPortalError):
    """Raised when asset mapping fails."""
    pass


class OutOfBoundsError(BFPortalError):
    """Raised when an object is outside valid bounds."""
    pass


class TerrainError(BFPortalError):
    """Raised when terrain queries fail."""
    pass


class ValidationError(BFPortalError):
    """Raised when validation fails."""
    pass


class ConfigurationError(BFPortalError):
    """Raised when configuration is invalid."""
    pass
