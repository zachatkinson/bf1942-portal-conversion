#!/usr/bin/env python3
"""
Rotate all objects 90° clockwise while keeping terrain in original orientation.

This is the correct approach - rotate assets to match terrain, not terrain to match assets.

Usage:
    python3 tools/rotate_objects_90.py
"""

import re
from pathlib import Path


def rotate_objects_90_cw(tscn_path: Path) -> None:
    """Rotate all objects 90° clockwise around Y-axis.

    Rotation transformation (90° CW around Y):
    - Position: (x, y, z) → (z, y, -x)
    - Rotation matrix: Multiply existing rotation by 90° CW Y rotation

    90° CW Y rotation matrix:
    [ 0  0  1 ]
    [ 0  1  0 ]
    [-1  0  0 ]
    """

    print("🔄 Rotating Objects 90° Clockwise")
    print("=" * 60)
    print("Strategy: Keep terrain stationary, rotate all objects")
    print()

    # Read .tscn file
    content = tscn_path.read_text()
    lines = content.split("\n")

    # Track which node we're in
    in_static_section = False
    in_terrain_node = False
    skip_next_transform = False

    modified_lines = []
    rotated_count = 0
    skipped_count = 0

    for _i, line in enumerate(lines):
        # Detect Static section
        if '[node name="Static"' in line:
            in_static_section = True
            modified_lines.append(line)
            continue

        # Detect terrain node (skip its transform)
        if in_static_section and '[node name="MP_Tungsten_Terrain"' in line:
            in_terrain_node = True
            skip_next_transform = True
            modified_lines.append(line)
            continue

        # Check if we're leaving terrain node
        if in_terrain_node and line.startswith("[node name=") and "MP_Tungsten_Terrain" not in line:
            in_terrain_node = False

        # Check if we're leaving Static section
        if (
            in_static_section
            and line.startswith("[node name=")
            and 'parent="Static"' not in line
            and not in_terrain_node
        ):
            in_static_section = False

        # Match transform lines
        match = re.match(
            r"^(transform = Transform3D\()([^,]+), ([^,]+), ([^,]+), "
            r"([^,]+), ([^,]+), ([^,]+), ([^,]+), ([^,]+), ([^,]+), "
            r"([^,]+), ([^,]+), ([^)]+)\)(.*)$",
            line,
        )

        if match:
            # Skip terrain transform (restore to identity)
            if skip_next_transform:
                # Restore terrain to non-rotated state
                prefix = match.group(1)
                pos_x = float(match.group(11))
                pos_y = float(match.group(12))
                pos_z = float(match.group(13))
                suffix = match.group(14)

                # Identity rotation
                new_line = f"{prefix}1, 0, 0, 0, 1, 0, 0, 0, 1, {pos_x}, {pos_y}, {pos_z}){suffix}"
                modified_lines.append(new_line)
                skip_next_transform = False
                skipped_count += 1
                continue

            # Extract transform components
            prefix = match.group(1)
            r1, r2, r3 = float(match.group(2)), float(match.group(3)), float(match.group(4))
            r4, r5, r6 = float(match.group(5)), float(match.group(6)), float(match.group(7))
            r7, r8, r9 = float(match.group(8)), float(match.group(9)), float(match.group(10))
            pos_x = float(match.group(11))
            pos_y = float(match.group(12))
            pos_z = float(match.group(13))
            suffix = match.group(14)

            # Rotate position: (x, y, z) → (z, y, -x)
            new_pos_x = pos_z
            new_pos_y = pos_y
            new_pos_z = -pos_x

            # Rotate the rotation matrix by 90° CW around Y
            # New matrix = Rot_Y(90°) * Old matrix
            # Rot_Y(90°) = [0 0 1; 0 1 0; -1 0 0]
            new_r1 = r7
            new_r2 = r8
            new_r3 = r9

            new_r4 = r4
            new_r5 = r5
            new_r6 = r6

            new_r7 = -r1
            new_r8 = -r2
            new_r9 = -r3

            # Reconstruct line
            new_line = (
                f"{prefix}{new_r1}, {new_r2}, {new_r3}, "
                f"{new_r4}, {new_r5}, {new_r6}, "
                f"{new_r7}, {new_r8}, {new_r9}, "
                f"{new_pos_x}, {new_pos_y}, {new_pos_z}){suffix}"
            )
            modified_lines.append(new_line)
            rotated_count += 1
        else:
            modified_lines.append(line)

    # Write back
    new_content = "\n".join(modified_lines)
    tscn_path.write_text(new_content)

    print(f"✅ Rotated {rotated_count} object transforms 90° CW")
    print(f"✅ Restored {skipped_count} terrain transform to identity")
    print(f"✅ Updated: {tscn_path}")
    print()
    print("📋 Next: Reload Kursk.tscn in Godot")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    tscn_path = project_root / "GodotProject/levels/Kursk.tscn"

    if not tscn_path.exists():
        print(f"❌ ERROR: {tscn_path} not found!")
        return 1

    # Backup first
    backup_path = tscn_path.with_suffix(".tscn.pre_rotation")
    import shutil

    shutil.copy2(tscn_path, backup_path)
    print(f"✅ Backed up to: {backup_path}\n")

    rotate_objects_90_cw(tscn_path)
    return 0


if __name__ == "__main__":
    exit(main())
