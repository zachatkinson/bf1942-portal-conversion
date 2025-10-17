#!/usr/bin/env python3
"""CLI error handling decorator for consistent error management.

Single Responsibility: Provide centralized error handling for CLI scripts.
Eliminates duplicate try-except blocks across CLI scripts (DRY principle).

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-17
"""

import functools
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar, cast

from .exit_codes import (
    EXIT_ASSET_ERROR,
    EXIT_CONVERSION_ERROR,
    EXIT_ERROR,
    EXIT_EXPORT_ERROR,
    EXIT_FILE_NOT_FOUND,
    EXIT_PARSE_ERROR,
    EXIT_TERRAIN_ERROR,
    EXIT_VALIDATION_ERROR,
)
from .formatters import print_error

F = TypeVar("F", bound=Callable[..., Any])


def handle_cli_errors(verbose: bool = False) -> Callable[[F], F]:
    """Decorator to handle common CLI errors consistently.

    Catches common exceptions and converts them to appropriate exit codes.
    Eliminates duplicate error handling across CLI scripts.

    Args:
        verbose: If True, print full stack traces on errors

    Returns:
        Decorated function that handles errors and exits with appropriate code

    Example:
        @handle_cli_errors(verbose=True)
        def main() -> int:
            # CLI logic here
            return 0
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> int:
            try:
                return cast(int, func(*args, **kwargs))
            except FileNotFoundError as e:
                print_error(f"File not found: {e}")
                if verbose:
                    traceback.print_exc()
                return EXIT_FILE_NOT_FOUND
            except PermissionError as e:
                print_error(f"Permission denied: {e}")
                if verbose:
                    traceback.print_exc()
                return EXIT_ERROR
            except ValueError as e:
                print_error(f"Invalid value: {e}")
                if verbose:
                    traceback.print_exc()
                return EXIT_VALIDATION_ERROR
            except KeyError as e:
                print_error(f"Missing required key: {e}")
                if verbose:
                    traceback.print_exc()
                return EXIT_PARSE_ERROR
            except Exception as e:  # noqa: BLE001
                print_error(f"Unexpected error: {e}")
                if verbose:
                    traceback.print_exc()
                return EXIT_ERROR

        return wrapper  # type: ignore[return-value]

    return decorator


class CLIError(Exception):
    """Base class for CLI errors with exit codes."""

    def __init__(self, message: str, exit_code: int = EXIT_ERROR) -> None:
        """Initialize CLI error.

        Args:
            message: Error message
            exit_code: Exit code to use when this error is raised
        """
        super().__init__(message)
        self.exit_code = exit_code


class FileNotFoundCLIError(CLIError):
    """File not found error."""

    def __init__(self, path: Path | str) -> None:
        """Initialize file not found error.

        Args:
            path: Path that was not found
        """
        super().__init__(f"File not found: {path}", EXIT_FILE_NOT_FOUND)


class ValidationCLIError(CLIError):
    """Validation error."""

    def __init__(self, message: str) -> None:
        """Initialize validation error.

        Args:
            message: Validation error message
        """
        super().__init__(f"Validation failed: {message}", EXIT_VALIDATION_ERROR)


class ParseCLIError(CLIError):
    """Parsing error."""

    def __init__(self, message: str) -> None:
        """Initialize parsing error.

        Args:
            message: Parsing error message
        """
        super().__init__(f"Parsing failed: {message}", EXIT_PARSE_ERROR)


class ConversionCLIError(CLIError):
    """Conversion error."""

    def __init__(self, message: str) -> None:
        """Initialize conversion error.

        Args:
            message: Conversion error message
        """
        super().__init__(f"Conversion failed: {message}", EXIT_CONVERSION_ERROR)


class ExportCLIError(CLIError):
    """Export error."""

    def __init__(self, message: str) -> None:
        """Initialize export error.

        Args:
            message: Export error message
        """
        super().__init__(f"Export failed: {message}", EXIT_EXPORT_ERROR)


class TerrainCLIError(CLIError):
    """Terrain processing error."""

    def __init__(self, message: str) -> None:
        """Initialize terrain error.

        Args:
            message: Terrain error message
        """
        super().__init__(f"Terrain error: {message}", EXIT_TERRAIN_ERROR)


class AssetCLIError(CLIError):
    """Asset mapping error."""

    def __init__(self, message: str) -> None:
        """Initialize asset error.

        Args:
            message: Asset error message
        """
        super().__init__(f"Asset error: {message}", EXIT_ASSET_ERROR)


def handle_cli_errors_with_custom_exceptions(verbose: bool = False) -> Callable[[F], F]:
    """Decorator to handle CLI errors including custom CLIError exceptions.

    Args:
        verbose: If True, print full stack traces on errors

    Returns:
        Decorated function that handles errors and exits with appropriate code
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> int:
            try:
                return cast(int, func(*args, **kwargs))
            except CLIError as e:
                print_error(str(e))
                if verbose:
                    traceback.print_exc()
                return e.exit_code
            except FileNotFoundError as e:
                print_error(f"File not found: {e}")
                if verbose:
                    traceback.print_exc()
                return EXIT_FILE_NOT_FOUND
            except PermissionError as e:
                print_error(f"Permission denied: {e}")
                if verbose:
                    traceback.print_exc()
                return EXIT_ERROR
            except ValueError as e:
                print_error(f"Invalid value: {e}")
                if verbose:
                    traceback.print_exc()
                return EXIT_VALIDATION_ERROR
            except KeyError as e:
                print_error(f"Missing required key: {e}")
                if verbose:
                    traceback.print_exc()
                return EXIT_PARSE_ERROR
            except Exception as e:  # noqa: BLE001
                print_error(f"Unexpected error: {e}")
                if verbose:
                    traceback.print_exc()
                return EXIT_ERROR

        return wrapper  # type: ignore[return-value]

    return decorator
