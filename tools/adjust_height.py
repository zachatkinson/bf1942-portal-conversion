#!/usr/bin/env python3
"""
Adjust Y-axis (height) for all objects in Kursk.tscn.

This tool adds a uniform height offset to align objects with the terrain.

Usage:
    python tools/adjust_height.py <height_offset>

Example:
    python tools/adjust_height.py 15  # Add 15 meters to all heights

Author: BF1942 Portal Conversion Project
Date: 2025-10-11
"""

import re
import sys
from pathlib import Path


def parse_transform3d(transform_str: str) -> tuple[list, list]:
    """
    Parse Transform3D string into rotation matrix and position.

    Args:
        transform_str: String like "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, x, y, z)"

    Returns:
        Tuple of (rotation_matrix, position)
    """
    match = re.search(r"Transform3D\(([^)]+)\)", transform_str)
    if not match:
        raise ValueError(f"Invalid Transform3D format: {transform_str}")

    values = [float(x.strip()) for x in match.group(1).split(",")]

    if len(values) != 12:
        raise ValueError(f"Expected 12 values in Transform3D, got {len(values)}")

    rotation_matrix = values[:9]
    position = values[9:]

    return rotation_matrix, position


def format_transform3d(rotation: list, position: list) -> str:
    """
    Format rotation matrix and position back into Transform3D string.

    Args:
        rotation: List of 9 floats (3x3 rotation matrix)
        position: List of 3 floats [x, y, z]

    Returns:
        Formatted Transform3D string
    """
    values = rotation + position
    values_str = ", ".join(f"{v:.6g}" for v in values)
    return f"Transform3D({values_str})"


def adjust_height_in_line(line: str, height_offset: float) -> str:
    """
    Add height offset to Y-coordinate in transform line.

    Args:
        line: Line containing "transform = Transform3D(...)"
        height_offset: Value to add to Y coordinate

    Returns:
        Modified line with adjusted height
    """
    if "transform = Transform3D(" not in line:
        return line

    try:
        transform_match = re.search(r"transform = (Transform3D\([^)]+\))", line)
        if not transform_match:
            return line

        transform_str = transform_match.group(1)
        rotation, position = parse_transform3d(transform_str)

        # Adjust Y coordinate (index 1)
        new_position = [position[0], position[1] + height_offset, position[2]]

        new_transform = format_transform3d(rotation, new_position)

        return line.replace(transform_str, new_transform)

    except Exception as e:
        print(f"Warning: Failed to adjust height: {e}")
        print(f"  Line: {line.strip()}")
        return line


def adjust_heights_in_tscn(input_path: Path, output_path: Path, height_offset: float) -> None:
    """
    Apply height offset to all transform nodes in .tscn file.

    Args:
        input_path: Path to input .tscn file
        output_path: Path to output .tscn file
        height_offset: Height offset to add
    """
    print(f"Reading: {input_path}")
    print(f"Height offset: +{height_offset:.2f}m")

    with open(input_path) as f:
        lines = f.readlines()

    modified_lines = []
    transforms_modified = 0
    example_before = None
    example_after = None

    for line in lines:
        if "transform = Transform3D(" in line:
            if example_before is None:
                example_before = line.strip()
            new_line = adjust_height_in_line(line, height_offset)
            if new_line != line:
                transforms_modified += 1
                if example_after is None:
                    example_after = new_line.strip()
            modified_lines.append(new_line)
        else:
            modified_lines.append(line)

    with open(output_path, "w") as f:
        f.writelines(modified_lines)

    print(f"Modified {transforms_modified} transform nodes")
    print()
    print("Example change:")
    print(f"  Before: {example_before}")
    print(f"  After:  {example_after}")
    print()
    print(f"Output written to: {output_path}")


def main():
    """Main execution."""
    if len(sys.argv) < 2:
        print("Usage: python tools/adjust_height.py <height_offset>")
        print()
        print("Examples:")
        print("  python tools/adjust_height.py 15    # Raise all objects by 15m")
        print("  python tools/adjust_height.py -5    # Lower all objects by 5m")
        print()
        print("Current situation:")
        print("  Kursk objects: Y = 77-85 (BF1942 terrain heights)")
        print("  MP_Outskirts:  Y = 92-95 (BF6 terrain heights)")
        print("  Suggested offset: +15 to +18 meters")
        return 1

    try:
        height_offset = float(sys.argv[1])
    except ValueError:
        print(f"Error: Invalid number '{sys.argv[1]}'")
        return 1

    # Paths
    project_root = Path(__file__).parent.parent
    input_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    output_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    backup_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn.backup_before_height"

    if not input_tscn.exists():
        print(f"Error: Input file not found: {input_tscn}")
        return 1

    print("=" * 70)
    print("Kursk Height Adjustment")
    print("=" * 70)
    print()

    # Create backup
    print(f"Creating backup: {backup_tscn}")
    import shutil

    shutil.copy2(input_tscn, backup_tscn)
    print()

    # Apply height adjustment
    adjust_heights_in_tscn(input_tscn, output_tscn, height_offset)

    print()
    print("=" * 70)
    print("✅ Height adjustment applied successfully!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. In Godot: File → Reopen (or close/reopen scene)")
    print("2. Select TEAM_1_HQ and press F to focus on it")
    print("3. Check if object is now on the terrain surface")
    print()
    print("If height is still wrong:")
    print(f"  - Restore from: {backup_tscn}")
    print(f"  - Try different offset (current: {height_offset:+.1f}m)")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
