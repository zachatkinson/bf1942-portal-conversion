#!/usr/bin/env python3
"""
Apply coordinate offset correction to generated Kursk.tscn

This tool centers the BF1942 coordinates around (0, 0, 0) to align with
the BF6 terrain coordinate system.

Usage:
    python tools/apply_coordinate_offset.py

Author: BF1942 Portal Conversion Project
Date: 2025-10-11
"""

import re
from pathlib import Path


def parse_transform3d(transform_str: str) -> tuple[list, list]:
    """
    Parse Transform3D string into rotation matrix and position.

    Args:
        transform_str: String like "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, x, y, z)"

    Returns:
        Tuple of (rotation_matrix, position) where:
        - rotation_matrix is list of 9 floats
        - position is list of 3 floats [x, y, z]
    """
    # Extract numbers from Transform3D(...) - handle scientific notation
    match = re.search(r"Transform3D\(([^)]+)\)", transform_str)
    if not match:
        raise ValueError(f"Invalid Transform3D format: {transform_str}")

    # Split by comma and convert to floats (handles scientific notation like 4.8e-05)
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
        rotation: List of 9 floats (3x3 rotation matrix in row-major order)
        position: List of 3 floats [x, y, z]

    Returns:
        Formatted Transform3D string
    """
    values = rotation + position
    values_str = ", ".join(f"{v:.6g}" for v in values)
    return f"Transform3D({values_str})"


def apply_offset_to_transform(transform_line: str, offset: tuple[float, float, float]) -> str:
    """
    Apply coordinate offset to a transform line.

    Args:
        transform_line: Line containing "transform = Transform3D(...)"
        offset: Tuple of (x_offset, y_offset, z_offset) to ADD to position

    Returns:
        Modified line with offset applied
    """
    if "transform = Transform3D(" not in transform_line:
        return transform_line

    try:
        # Find the Transform3D part
        transform_match = re.search(r"transform = (Transform3D\([^\)]+\))", transform_line)
        if not transform_match:
            return transform_line

        transform_str = transform_match.group(1)
        rotation, position = parse_transform3d(transform_str)

        # Apply offset
        new_position = [position[0] + offset[0], position[1] + offset[1], position[2] + offset[2]]

        new_transform = format_transform3d(rotation, new_position)

        # Replace in original line
        new_line = transform_line.replace(transform_str, new_transform)

        return new_line

    except Exception as e:
        print(f"Warning: Failed to parse transform: {e}")
        print(f"  Line: {transform_line.strip()}")
        return transform_line


def calculate_kursk_offset() -> tuple[float, float, float]:
    """
    Calculate the offset needed to center Kursk coordinates.

    Based on analysis:
    - X range: 437.315 to 639.658 → center = 538.49
    - Z range: 238.39 to 849.956 → center = 544.17
    - Y: keep original (terrain height)

    Returns:
        Tuple of (x_offset, y_offset, z_offset)
    """
    x_center = (437.315 + 639.658) / 2  # 538.4865
    z_center = (238.39 + 849.956) / 2  # 544.173

    # Negative because we're subtracting to move to origin
    return (-x_center, 0.0, -z_center)


def apply_offset_to_tscn(
    input_path: Path, output_path: Path, offset: tuple[float, float, float]
) -> None:
    """
    Apply coordinate offset to all transform nodes in .tscn file.

    Args:
        input_path: Path to input .tscn file
        output_path: Path to output .tscn file
        offset: Coordinate offset to apply (x, y, z)
    """
    print(f"Reading: {input_path}")
    print(f"Offset: ({offset[0]:.2f}, {offset[1]:.2f}, {offset[2]:.2f})")

    with open(input_path) as f:
        lines = f.readlines()

    modified_lines = []
    transforms_modified = 0

    for line in lines:
        if "transform = Transform3D(" in line:
            new_line = apply_offset_to_transform(line, offset)
            if new_line != line:
                transforms_modified += 1
            modified_lines.append(new_line)
        else:
            modified_lines.append(line)

    with open(output_path, "w") as f:
        f.writelines(modified_lines)

    print(f"Modified {transforms_modified} transform nodes")
    print(f"Output written to: {output_path}")


def main():
    """Main execution."""
    # Paths
    project_root = Path(__file__).parent.parent
    input_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    output_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    backup_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn.backup"

    if not input_tscn.exists():
        print(f"Error: Input file not found: {input_tscn}")
        return 1

    # Calculate offset
    offset = calculate_kursk_offset()

    print("=" * 60)
    print("Kursk Coordinate Offset Correction")
    print("=" * 60)
    print()
    print("This tool centers BF1942 Kursk coordinates around (0,0,0)")
    print("to align with the BF6 MP_Outskirts terrain.")
    print()
    print(f"Calculated offset: ({offset[0]:.2f}, {offset[1]:.2f}, {offset[2]:.2f})")
    print()

    # Create backup
    if output_tscn.exists():
        print(f"Creating backup: {backup_tscn}")
        import shutil

        shutil.copy2(output_tscn, backup_tscn)

    # Apply offset
    apply_offset_to_tscn(input_tscn, output_tscn, offset)

    print()
    print("=" * 60)
    print("✅ Offset applied successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Open Godot")
    print("2. Reload Kursk.tscn (File → Reopen)")
    print("3. Check if objects are now aligned with terrain")
    print()
    print(f"If you need to revert: Copy {backup_tscn} back to {output_tscn}")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
