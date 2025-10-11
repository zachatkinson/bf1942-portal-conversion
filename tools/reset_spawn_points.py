#!/usr/bin/env python3
"""
Reset spawn points to proper relative positions around parent HQs.

Creates spawn points in a 10-meter radius circle around the HQ.

Usage:
    python tools/reset_spawn_points.py

Author: BF1942 Portal Conversion Project
Date: 2025-10-11
"""

import re
import math
from pathlib import Path
from typing import Tuple


def format_transform3d(rotation: list, position: list) -> str:
    """Format rotation matrix and position into Transform3D string."""
    values = rotation + position
    values_str = ", ".join(f"{v:.6g}" for v in values)
    return f"Transform3D({values_str})"


def generate_spawn_point_transform(index: int, total: int, radius: float = 10.0) -> str:
    """
    Generate transform for spawn point in a circle.

    Args:
        index: Spawn point index (0-based)
        total: Total number of spawn points
        radius: Radius of spawn circle in meters

    Returns:
        Transform3D string
    """
    # Calculate angle for this spawn point
    angle = (index / total) * 2 * math.pi

    # Position in circle
    x = radius * math.sin(angle)
    z = radius * math.cos(angle)
    y = 0  # Same height as parent

    # Rotation matrix (facing outward from center)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    # Rotation matrix for facing direction
    rotation = [
        cos_a, 0, sin_a,
        0, 1, 0,
        -sin_a, 0, cos_a
    ]

    return format_transform3d(rotation, [x, y, z])


def reset_spawn_points(input_path: Path, output_path: Path) -> None:
    """
    Reset spawn point positions to proper relative coords.

    Args:
        input_path: Path to input .tscn
        output_path: Path to output .tscn
    """
    print(f"Reading: {input_path}")

    with open(input_path, 'r') as f:
        lines = f.readlines()

    modified_lines = []
    current_parent = None
    spawn_point_index = 0
    spawn_points_fixed = 0

    for line in lines:
        # Track which HQ we're inside
        if '[node name="SpawnPoint_' in line:
            if 'parent="TEAM_1_HQ"' in line:
                current_parent = "TEAM_1_HQ"
                # Extract spawn point number
                match = re.search(r'SpawnPoint_1_(\d+)', line)
                if match:
                    spawn_point_index = int(match.group(1)) - 1  # Convert to 0-based
            elif 'parent="TEAM_2_HQ"' in line:
                current_parent = "TEAM_2_HQ"
                match = re.search(r'SpawnPoint_2_(\d+)', line)
                if match:
                    spawn_point_index = int(match.group(1)) - 1

        # Replace spawn point transform
        if current_parent and "transform = Transform3D(" in line:
            new_transform = generate_spawn_point_transform(spawn_point_index, total=8, radius=10.0)
            new_line = f"transform = {new_transform}\n"
            modified_lines.append(new_line)
            spawn_points_fixed += 1
            current_parent = None  # Reset after fixing
            continue

        # Reset parent tracking when leaving spawn point section
        if '[node name=' in line and 'SpawnPoint' not in line:
            current_parent = None

        modified_lines.append(line)

    # Write output
    with open(output_path, 'w') as f:
        f.writelines(modified_lines)

    print(f"\nReset {spawn_points_fixed} spawn point positions")
    print(f"Spawn points now in 10m radius circle around each HQ")
    print(f"Output written to: {output_path}")


def main():
    """Main execution."""
    project_root = Path(__file__).parent.parent
    input_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    output_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    backup_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn.backup_before_spawn_reset"

    if not input_tscn.exists():
        print(f"Error: Input file not found: {input_tscn}")
        return 1

    print("=" * 70)
    print("Reset Spawn Point Positions")
    print("=" * 70)
    print()
    print("Generating new spawn point positions...")
    print("  - 8 spawn points per HQ")
    print("  - 10 meter radius circle")
    print("  - Relative to parent HQ")
    print()

    # Create backup
    print(f"Creating backup: {backup_tscn}")
    import shutil
    shutil.copy2(input_tscn, backup_tscn)
    print()

    # Reset spawn points
    reset_spawn_points(input_tscn, output_tscn)

    print()
    print("=" * 70)
    print("✅ Spawn points reset!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. In Godot: File → Reopen")
    print("2. Expand TEAM_1_HQ in scene tree")
    print("3. Select SpawnPoint_1_1 and press F")
    print("4. Should see spawn points in a circle around HQ")
    print()
    print("Spawn point layout:")
    print("         SP_1")
    print("    SP_8     SP_2")
    print("  SP_7   HQ   SP_3")
    print("    SP_6     SP_4")
    print("         SP_5")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
