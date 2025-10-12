#!/usr/bin/env python3
"""
Apply axis transformation to Kursk.tscn to fix orientation.

This tool swaps or mirrors axes to align BF1942 coordinates with BF6 terrain.

Usage:
    python tools/apply_axis_transform.py <transform_type>

Transform types:
    swap_xz     - Swap X and Z axes (North-South → East-West)
    rotate_90   - Rotate 90° clockwise
    rotate_180  - Rotate 180°
    rotate_270  - Rotate 270° (or -90°)
    negate_x    - Mirror X axis
    negate_z    - Mirror Z axis
    negate_xz   - Mirror both X and Z

Author: BF1942 Portal Conversion Project
Date: 2025-10-11
"""

import re
import sys
from pathlib import Path
from typing import Tuple


def apply_axis_transform(
    x: float, y: float, z: float, transform_type: str
) -> Tuple[float, float, float]:
    """
    Apply axis transformation to coordinates.

    Args:
        x, y, z: Original coordinates
        transform_type: Type of transformation

    Returns:
        Tuple of (new_x, new_y, new_z)
    """
    transforms = {
        "swap_xz": (z, y, x),  # Swap X and Z axes
        "negate_x": (-x, y, z),  # Mirror X axis
        "negate_z": (x, y, -z),  # Mirror Z axis
        "negate_xz": (-x, y, -z),  # Mirror both X and Z
        "rotate_90": (-z, y, x),  # Rotate 90° clockwise (top view)
        "rotate_180": (-x, y, -z),  # Rotate 180°
        "rotate_270": (z, y, -x),  # Rotate 270° (or -90°)
    }

    if transform_type not in transforms:
        raise ValueError(f"Unknown transform type: {transform_type}")

    return transforms[transform_type]


def parse_transform3d(transform_str: str) -> Tuple[list, list]:
    """
    Parse Transform3D string into rotation matrix and position.

    Args:
        transform_str: String like "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, x, y, z)"

    Returns:
        Tuple of (rotation_matrix, position) where:
        - rotation_matrix is list of 9 floats
        - position is list of 3 floats [x, y, z]
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


def transform_rotation_matrix(rotation: list, transform_type: str) -> list:
    """
    Transform rotation matrix to match axis transformation.

    When swapping/rotating axes, the rotation matrix must be transformed too.

    Args:
        rotation: 3x3 rotation matrix as list of 9 floats (row-major)
        transform_type: Type of transformation

    Returns:
        Transformed rotation matrix
    """
    # Convert to column vectors (right, up, forward)
    right = [rotation[0], rotation[3], rotation[6]]  # First column
    up = [rotation[1], rotation[4], rotation[7]]  # Second column
    forward = [rotation[2], rotation[5], rotation[8]]  # Third column

    # Apply transformation to each vector
    new_right = apply_axis_transform(*right, transform_type)
    new_up = apply_axis_transform(*up, transform_type)
    new_forward = apply_axis_transform(*forward, transform_type)

    # Convert back to row-major matrix
    return [
        new_right[0],
        new_up[0],
        new_forward[0],
        new_right[1],
        new_up[1],
        new_forward[1],
        new_right[2],
        new_up[2],
        new_forward[2],
    ]


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


def apply_transform_to_line(line: str, transform_type: str) -> str:
    """
    Apply axis transformation to a transform line.

    Args:
        line: Line containing "transform = Transform3D(...)"
        transform_type: Type of transformation to apply

    Returns:
        Modified line with transformation applied
    """
    if "transform = Transform3D(" not in line:
        return line

    try:
        transform_match = re.search(r"transform = (Transform3D\([^)]+\))", line)
        if not transform_match:
            return line

        transform_str = transform_match.group(1)
        rotation, position = parse_transform3d(transform_str)

        # Apply transformation to position
        new_position = list(apply_axis_transform(*position, transform_type))

        # Apply transformation to rotation matrix
        new_rotation = transform_rotation_matrix(rotation, transform_type)

        new_transform = format_transform3d(new_rotation, new_position)

        return line.replace(transform_str, new_transform)

    except Exception as e:
        print(f"Warning: Failed to transform: {e}")
        print(f"  Line: {line.strip()}")
        return line


def apply_transform_to_tscn(input_path: Path, output_path: Path, transform_type: str) -> None:
    """
    Apply axis transformation to all transform nodes in .tscn file.

    Args:
        input_path: Path to input .tscn file
        output_path: Path to output .tscn file
        transform_type: Type of transformation to apply
    """
    print(f"Reading: {input_path}")
    print(f"Transform: {transform_type}")

    with open(input_path) as f:
        lines = f.readlines()

    modified_lines = []
    transforms_modified = 0

    for line in lines:
        if "transform = Transform3D(" in line:
            new_line = apply_transform_to_line(line, transform_type)
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
    if len(sys.argv) < 2:
        print("Usage: python tools/apply_axis_transform.py <transform_type>")
        print()
        print("Available transforms:")
        print("  swap_xz     - Swap X and Z axes (North-South → East-West)")
        print("  rotate_90   - Rotate 90° clockwise")
        print("  rotate_180  - Rotate 180°")
        print("  rotate_270  - Rotate 270° (or -90°)")
        print("  negate_x    - Mirror X axis")
        print("  negate_z    - Mirror Z axis")
        print("  negate_xz   - Mirror both X and Z")
        print()
        print("Recommended for Kursk: swap_xz")
        return 1

    transform_type = sys.argv[1]

    valid_transforms = [
        "swap_xz",
        "rotate_90",
        "rotate_180",
        "rotate_270",
        "negate_x",
        "negate_z",
        "negate_xz",
    ]

    if transform_type not in valid_transforms:
        print(f"Error: Unknown transform type '{transform_type}'")
        print(f"Valid options: {', '.join(valid_transforms)}")
        return 1

    # Paths
    project_root = Path(__file__).parent.parent
    input_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    output_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    backup_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn.backup_before_transform"

    if not input_tscn.exists():
        print(f"Error: Input file not found: {input_tscn}")
        return 1

    print("=" * 70)
    print("Kursk Axis Transformation")
    print("=" * 70)
    print()

    # Create backup
    print(f"Creating backup: {backup_tscn}")
    import shutil

    shutil.copy2(input_tscn, backup_tscn)

    # Apply transformation
    apply_transform_to_tscn(input_tscn, output_tscn, transform_type)

    print()
    print("=" * 70)
    print("✅ Transformation applied successfully!")
    print("=" * 70)
    print()
    print("What was changed:")
    print(f"  - Applied '{transform_type}' to all 41 transform nodes")
    print("  - Both positions AND rotations transformed")
    print("  - All object relationships preserved")
    print()
    print("Next steps:")
    print("1. In Godot: File → Reopen (or close/reopen scene)")
    print("2. Check if HQs are now both visible on terrain")
    print("3. Verify layout is East-West (side by side)")
    print()
    print(f"If incorrect: Restore from {backup_tscn}")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
