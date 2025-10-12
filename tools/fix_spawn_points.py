#!/usr/bin/env python3
"""
Fix spawn point positions to be relative to their parent HQs.

Currently spawn points have absolute world coordinates, but they should
have positions relative to their parent HQ node.

Usage:
    python tools/fix_spawn_points.py

Author: BF1942 Portal Conversion Project
Date: 2025-10-11
"""

import re
from pathlib import Path
from typing import Dict, Tuple


def parse_transform3d(transform_str: str) -> Tuple[list, list]:
    """Parse Transform3D into rotation matrix and position."""
    match = re.search(r"Transform3D\(([^)]+)\)", transform_str)
    if not match:
        raise ValueError("Invalid Transform3D format")

    values = [float(x.strip()) for x in match.group(1).split(",")]
    if len(values) != 12:
        raise ValueError(f"Expected 12 values, got {len(values)}")

    return values[:9], values[9:]


def format_transform3d(rotation: list, position: list) -> str:
    """Format rotation matrix and position into Transform3D string."""
    values = rotation + position
    values_str = ", ".join(f"{v:.6g}" for v in values)
    return f"Transform3D({values_str})"


def extract_hq_positions(lines: list) -> Dict[str, Tuple[float, float, float]]:
    """
    Extract HQ positions from .tscn file.

    Returns:
        Dict mapping HQ names to (x, y, z) positions
    """
    hq_positions = {}
    current_hq = None

    for line in lines:
        # Find HQ node definition
        if 'name="TEAM_1_HQ"' in line:
            current_hq = "TEAM_1_HQ"
        elif 'name="TEAM_2_HQ"' in line:
            current_hq = "TEAM_2_HQ"

        # Get transform for current HQ
        if current_hq and "transform = Transform3D(" in line:
            match = re.search(r"Transform3D\(([^)]+)\)", line)
            if match:
                values = [float(x.strip()) for x in match.group(1).split(",")]
                position = tuple(values[9:12])
                hq_positions[current_hq] = position
                current_hq = None

    return hq_positions


def make_position_relative(
    child_pos: Tuple[float, float, float], parent_pos: Tuple[float, float, float]
) -> Tuple[float, float, float]:
    """
    Convert absolute child position to relative position.

    Args:
        child_pos: Absolute world position
        parent_pos: Parent HQ absolute position

    Returns:
        Relative position (child - parent)
    """
    return (
        child_pos[0] - parent_pos[0],
        child_pos[1] - parent_pos[1],
        child_pos[2] - parent_pos[2],
    )


def fix_spawn_points(input_path: Path, output_path: Path) -> None:
    """
    Fix spawn point positions to be relative to parent HQs.

    Args:
        input_path: Path to input .tscn
        output_path: Path to output .tscn
    """
    print(f"Reading: {input_path}")

    with open(input_path) as f:
        lines = f.readlines()

    # Extract HQ positions
    hq_positions = extract_hq_positions(lines)

    print("\nFound HQ positions:")
    for hq_name, pos in hq_positions.items():
        print(f"  {hq_name}: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

    # Process lines
    modified_lines = []
    current_parent = None
    spawn_points_fixed = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # Track which HQ we're inside
        if 'parent="TEAM_1_HQ"' in line and "SpawnPoint" in line:
            current_parent = "TEAM_1_HQ"
        elif 'parent="TEAM_2_HQ"' in line and "SpawnPoint" in line:
            current_parent = "TEAM_2_HQ"
        elif "[node name=" in line and 'parent="."' in line:
            # Back to root level
            current_parent = None

        # Fix spawn point transform
        if current_parent and "transform = Transform3D(" in line:
            try:
                rotation, position = parse_transform3d(line)
                parent_pos = hq_positions[current_parent]

                # Convert to relative position
                relative_pos = make_position_relative(tuple(position), parent_pos)

                # Create new transform
                new_transform = format_transform3d(rotation, list(relative_pos))
                new_line = re.sub(
                    r"transform = Transform3D\([^)]+\)", f"transform = {new_transform}", line
                )

                modified_lines.append(new_line)
                spawn_points_fixed += 1
                i += 1
                continue

            except Exception as e:
                print(f"Warning: Failed to fix spawn point: {e}")

        modified_lines.append(line)
        i += 1

    # Write output
    with open(output_path, "w") as f:
        f.writelines(modified_lines)

    print(f"\nFixed {spawn_points_fixed} spawn point positions")
    print(f"Output written to: {output_path}")


def main():
    """Main execution."""
    project_root = Path(__file__).parent.parent
    input_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    output_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    backup_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn.backup_before_spawn_fix"

    if not input_tscn.exists():
        print(f"Error: Input file not found: {input_tscn}")
        return 1

    print("=" * 70)
    print("Fix Spawn Point Positions")
    print("=" * 70)
    print()
    print("Converting spawn points from absolute to relative positioning...")
    print()

    # Create backup
    print(f"Creating backup: {backup_tscn}")
    import shutil

    shutil.copy2(input_tscn, backup_tscn)
    print()

    # Fix spawn points
    fix_spawn_points(input_tscn, output_tscn)

    print()
    print("=" * 70)
    print("✅ Spawn points fixed!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. In Godot: File → Reopen")
    print("2. Expand TEAM_1_HQ in scene tree")
    print("3. Select SpawnPoint_1_1 and press F")
    print("4. Should be close to the HQ (not far away)")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
