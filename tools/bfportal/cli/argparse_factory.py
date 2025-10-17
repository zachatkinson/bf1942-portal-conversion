#!/usr/bin/env python3
"""Argument parser factory for consistent CLI argument handling.

Single Responsibility: Provide reusable argparse configuration.
Eliminates duplicate argparse setup across CLI scripts (DRY principle).

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-17
"""

import argparse
from pathlib import Path


def create_base_parser(
    description: str,
    add_verbose: bool = True,
    add_output_dir: bool = False,
) -> argparse.ArgumentParser:
    """Create a base argument parser with common arguments.

    Args:
        description: Description of the CLI tool
        add_verbose: Add -v/--verbose flag (default: True)
        add_output_dir: Add -o/--output-dir argument (default: False)

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    if add_verbose:
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Enable verbose output with detailed logging",
        )

    if add_output_dir:
        parser.add_argument(
            "-o",
            "--output-dir",
            type=Path,
            help="Output directory for generated files",
        )

    return parser


def add_map_argument(parser: argparse.ArgumentParser, required: bool = True) -> None:
    """Add map name argument to parser.

    Args:
        parser: ArgumentParser to add argument to
        required: Whether the argument is required (default: True)
    """
    parser.add_argument(
        "--map",
        "-m",
        type=str,
        required=required,
        help="Map name (e.g., Kursk, Wake_Island, El_Alamein)",
    )


def add_terrain_argument(parser: argparse.ArgumentParser, required: bool = True) -> None:
    """Add base terrain argument to parser.

    Args:
        parser: ArgumentParser to add argument to
        required: Whether the argument is required (default: True)
    """
    parser.add_argument(
        "--base-terrain",
        "-t",
        type=str,
        required=required,
        choices=[
            "MP_Tungsten",
            "MP_Aftermath",
            "MP_Battery",
            "MP_FireStorm",
            "MP_Limestone",
        ],
        help="BF6 base terrain to use for the map",
    )


def add_terrain_size_argument(parser: argparse.ArgumentParser) -> None:
    """Add terrain size argument to parser.

    Args:
        parser: ArgumentParser to add argument to
    """
    parser.add_argument(
        "--terrain-size",
        "-s",
        type=int,
        default=2048,
        choices=[512, 1024, 2048, 4096],
        help="Terrain size in meters (default: 2048)",
    )


def add_experience_arguments(parser: argparse.ArgumentParser) -> None:
    """Add experience creation arguments to parser.

    Args:
        parser: ArgumentParser to add argument to
    """
    parser.add_argument(
        "--base-map",
        type=str,
        default="MP_Tungsten",
        help="Base BF6 map for terrain (default: MP_Tungsten)",
    )
    parser.add_argument(
        "--max-players",
        type=int,
        default=32,
        help="Maximum players per team (default: 32)",
    )
    parser.add_argument(
        "--game-mode",
        type=str,
        default="Conquest",
        help="Game mode (default: Conquest)",
    )


def add_force_flag(parser: argparse.ArgumentParser) -> None:
    """Add --force flag to parser for overwriting existing files.

    Args:
        parser: ArgumentParser to add argument to
    """
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force overwrite existing files without prompting",
    )


def add_dry_run_flag(parser: argparse.ArgumentParser) -> None:
    """Add --dry-run flag to parser for testing without modifications.

    Args:
        parser: ArgumentParser to add argument to
    """
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Perform a dry run without modifying any files",
    )


def validate_map_name(map_name: str) -> str:
    """Validate and normalize map name.

    Args:
        map_name: Raw map name from user input

    Returns:
        Normalized map name (e.g., "wake_island" -> "Wake_Island")

    Raises:
        ValueError: If map name is invalid
    """
    if not map_name:
        raise ValueError("Map name cannot be empty")

    # Remove any file extensions
    if map_name.endswith((".tscn", ".con", ".rfa")):
        map_name = map_name.rsplit(".", 1)[0]

    # Normalize capitalization (e.g., "wake_island" -> "Wake_Island")
    if "_" in map_name:
        parts = map_name.split("_")
        map_name = "_".join(part.capitalize() for part in parts)

    return map_name


def validate_path_exists(path: Path, file_type: str = "file") -> Path:
    """Validate that a path exists.

    Args:
        path: Path to validate
        file_type: Type of path for error message (default: "file")

    Returns:
        The validated path

    Raises:
        FileNotFoundError: If path does not exist
    """
    if not path.exists():
        raise FileNotFoundError(f"{file_type.capitalize()} not found: {path}")
    return path


def validate_output_dir(output_dir: Path, create: bool = True) -> Path:
    """Validate output directory and optionally create it.

    Args:
        output_dir: Directory path to validate
        create: Create directory if it doesn't exist (default: True)

    Returns:
        The validated directory path

    Raises:
        NotADirectoryError: If path exists but is not a directory
        PermissionError: If directory cannot be created
    """
    if output_dir.exists() and not output_dir.is_dir():
        raise NotADirectoryError(f"Output path is not a directory: {output_dir}")

    if not output_dir.exists() and create:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(f"Cannot create output directory: {output_dir}") from e

    return output_dir
