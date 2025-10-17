#!/usr/bin/env python3
"""CLI output formatters for consistent terminal formatting.

Single Responsibility: Provide consistent formatting for CLI output.
Eliminates duplicate formatting logic across CLI scripts (DRY principle).

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-17
"""

from typing import Any


def print_header(text: str) -> None:
    """Print a formatted header line.

    Args:
        text: Header text to display
    """
    print(f"\n{'=' * 80}")
    print(f"  {text}")
    print("=" * 80)


def print_subheader(text: str) -> None:
    """Print a formatted subheader line.

    Args:
        text: Subheader text to display
    """
    print(f"\n{'-' * 80}")
    print(f"  {text}")
    print("-" * 80)


def print_success(message: str) -> None:
    """Print a success message.

    Args:
        message: Success message to display
    """
    print(f"✓ {message}")


def print_error(message: str) -> None:
    """Print an error message.

    Args:
        message: Error message to display
    """
    print(f"✗ ERROR: {message}")


def print_warning(message: str) -> None:
    """Print a warning message.

    Args:
        message: Warning message to display
    """
    print(f"⚠ WARNING: {message}")


def print_info(message: str) -> None:
    """Print an info message.

    Args:
        message: Info message to display
    """
    print(f"ℹ {message}")


def print_section(title: str) -> None:
    """Print a section title.

    Args:
        title: Section title to display
    """
    print(f"\n{title}:")


def print_item(label: str, value: Any, indent: int = 2) -> None:
    """Print a labeled item with value.

    Args:
        label: Item label
        value: Item value
        indent: Number of spaces to indent (default: 2)
    """
    spaces = " " * indent
    print(f"{spaces}{label}: {value}")


def print_divider() -> None:
    """Print a divider line."""
    print("-" * 80)


def print_separator() -> None:
    """Print a thin separator line."""
    print()


def format_path(path: str, max_length: int = 60) -> str:
    """Format a path for display, truncating if too long.

    Args:
        path: Path string to format
        max_length: Maximum display length (default: 60)

    Returns:
        Formatted path string
    """
    if len(path) <= max_length:
        return path
    # Show start and end of path
    truncate_point = max_length - 3  # Account for "..."
    start_len = truncate_point // 2
    end_len = truncate_point - start_len
    return f"{path[:start_len]}...{path[-end_len:]}"


def format_count(count: int, singular: str, plural: str | None = None) -> str:
    """Format a count with singular/plural noun.

    Args:
        count: Number to display
        singular: Singular form of noun
        plural: Plural form of noun (default: singular + 's')

    Returns:
        Formatted count string (e.g., "1 item", "5 items")
    """
    if plural is None:
        plural = f"{singular}s"
    noun = singular if count == 1 else plural
    return f"{count} {noun}"


def format_percentage(value: float, total: float, decimals: int = 1) -> str:
    """Format a percentage value.

    Args:
        value: Numerator value
        total: Denominator value
        decimals: Number of decimal places (default: 1)

    Returns:
        Formatted percentage string (e.g., "75.5%")
    """
    if total == 0:
        return "0.0%"
    percentage = (value / total) * 100
    return f"{percentage:.{decimals}f}%"
