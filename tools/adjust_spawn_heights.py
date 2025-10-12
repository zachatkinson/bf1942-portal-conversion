#!/usr/bin/env python3
"""
Adjust Y-coordinate for spawn points only.

This tool adjusts spawn point heights while keeping their circular pattern.

Usage:
    python tools/adjust_spawn_heights.py <height_offset>

Example:
    python tools/adjust_spawn_heights.py -5  # Lower spawn points by 5m

Author: BF1942 Portal Conversion Project
Date: 2025-10-11
"""

import re
import sys
from pathlib import Path
from typing import Tuple


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


def adjust_spawn_heights(input_path: Path, output_path: Path, height_offset: float) -> None:
    """
    Adjust Y-coordinate for all spawn points.

    Args:
        input_path: Path to input .tscn
        output_path: Path to output .tscn
        height_offset: Height offset to add
    """
    print(f"Reading: {input_path}")
    print(f"Spawn point height offset: {height_offset:+.2f}m")

    with open(input_path) as f:
        lines = f.readlines()

    modified_lines = []
    in_spawn_point = False
    spawn_points_modified = 0

    for line in lines:
        # Track if we're in a spawn point node
        if '[node name="SpawnPoint_' in line and 'parent="TEAM_' in line:
            in_spawn_point = True

        # Reset when we leave spawn point section
        elif "[node name=" in line and "SpawnPoint" not in line:
            in_spawn_point = False

        # Adjust spawn point transform
        if in_spawn_point and "transform = Transform3D(" in line:
            try:
                rotation, position = parse_transform3d(line)

                # Adjust Y coordinate
                new_position = [position[0], position[1] + height_offset, position[2]]

                new_transform = format_transform3d(rotation, new_position)
                new_line = f"transform = {new_transform}\n"
                modified_lines.append(new_line)
                spawn_points_modified += 1
                continue

            except Exception as e:
                print(f"Warning: Failed to adjust spawn point: {e}")

        modified_lines.append(line)

    with open(output_path, "w") as f:
        f.writelines(modified_lines)

    print(f"\nModified {spawn_points_modified} spawn point heights")
    print(f"Output written to: {output_path}")


def main():
    """Main execution."""
    if len(sys.argv) < 2:
        print("Usage: python tools/adjust_spawn_heights.py <height_offset>")
        print()
        print("Examples:")
        print("  python tools/adjust_spawn_heights.py -5    # Lower by 5m")
        print("  python tools/adjust_spawn_heights.py -10   # Lower by 10m")
        print("  python tools/adjust_spawn_heights.py 2     # Raise by 2m")
        print()
        print("Current situation:")
        print("  Spawn points at Y=0 (relative to HQ)")
        print("  HQs at Y=92-93")
        print("  Actual spawn height: ~92-93m")
        print()
        print("If spawn points are floating:")
        print("  Try: -5 to -10 meters")
        return 1

    try:
        height_offset = float(sys.argv[1])
    except ValueError:
        print(f"Error: Invalid number '{sys.argv[1]}'")
        return 1

    project_root = Path(__file__).parent.parent
    input_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    output_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    backup_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn.backup_spawn_height"

    if not input_tscn.exists():
        print(f"Error: Input file not found: {input_tscn}")
        return 1

    print("=" * 70)
    print("Adjust Spawn Point Heights")
    print("=" * 70)
    print()

    # Create backup
    print(f"Creating backup: {backup_tscn}")
    import shutil

    shutil.copy2(input_tscn, backup_tscn)
    print()

    # Adjust heights
    adjust_spawn_heights(input_tscn, output_tscn, height_offset)

    print()
    print("=" * 70)
    print("✅ Spawn point heights adjusted!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. In Godot: File → Reopen")
    print("2. Select a spawn point and press F")
    print("3. Check if it's on the ground")
    print()
    print("If still wrong:")
    print(f"  - Restore: cp {backup_tscn.name} Kursk.tscn")
    print(f"  - Try different offset (current: {height_offset:+.1f}m)")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
