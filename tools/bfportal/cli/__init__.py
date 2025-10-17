#!/usr/bin/env python3
"""CLI utilities package for BF Portal tools.

This package provides reusable CLI utilities following SOLID/DRY principles:
- Exit codes: Standardized exit codes for all CLI scripts
- Formatters: Consistent terminal output formatting
- Error handlers: Centralized error handling with decorators
- Argparse factory: Reusable argument parser creation

Usage:
    from bfportal.cli import (
        EXIT_SUCCESS,
        EXIT_ERROR,
        print_header,
        print_success,
        handle_cli_errors,
        create_base_parser,
    )

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-17
"""

# Exit codes
# Argparse factory
from .argparse_factory import (
    add_dry_run_flag,
    add_experience_arguments,
    add_force_flag,
    add_map_argument,
    add_terrain_argument,
    add_terrain_size_argument,
    create_base_parser,
    validate_map_name,
    validate_output_dir,
    validate_path_exists,
)

# Error handlers
from .error_handler import (
    AssetCLIError,
    CLIError,
    ConversionCLIError,
    ExportCLIError,
    FileNotFoundCLIError,
    ParseCLIError,
    TerrainCLIError,
    ValidationCLIError,
    handle_cli_errors,
    handle_cli_errors_with_custom_exceptions,
)
from .exit_codes import (
    EXIT_ASSET_ERROR,
    EXIT_CONVERSION_ERROR,
    EXIT_ERROR,
    EXIT_EXPORT_ERROR,
    EXIT_FILE_NOT_FOUND,
    EXIT_INVALID_ARGS,
    EXIT_PARSE_ERROR,
    EXIT_SUCCESS,
    EXIT_TERRAIN_ERROR,
    EXIT_VALIDATION_ERROR,
)

# Formatters
from .formatters import (
    format_count,
    format_path,
    format_percentage,
    print_divider,
    print_error,
    print_header,
    print_info,
    print_item,
    print_section,
    print_separator,
    print_subheader,
    print_success,
    print_warning,
)

__all__ = [
    # Exit codes
    "EXIT_SUCCESS",
    "EXIT_ERROR",
    "EXIT_FILE_NOT_FOUND",
    "EXIT_VALIDATION_ERROR",
    "EXIT_PARSE_ERROR",
    "EXIT_CONVERSION_ERROR",
    "EXIT_EXPORT_ERROR",
    "EXIT_INVALID_ARGS",
    "EXIT_TERRAIN_ERROR",
    "EXIT_ASSET_ERROR",
    # Formatters
    "print_header",
    "print_subheader",
    "print_success",
    "print_error",
    "print_warning",
    "print_info",
    "print_section",
    "print_item",
    "print_divider",
    "print_separator",
    "format_path",
    "format_count",
    "format_percentage",
    # Error handlers
    "handle_cli_errors",
    "handle_cli_errors_with_custom_exceptions",
    "CLIError",
    "FileNotFoundCLIError",
    "ValidationCLIError",
    "ParseCLIError",
    "ConversionCLIError",
    "ExportCLIError",
    "TerrainCLIError",
    "AssetCLIError",
    # Argparse factory
    "create_base_parser",
    "add_map_argument",
    "add_terrain_argument",
    "add_terrain_size_argument",
    "add_experience_arguments",
    "add_force_flag",
    "add_dry_run_flag",
    "validate_map_name",
    "validate_path_exists",
    "validate_output_dir",
]
