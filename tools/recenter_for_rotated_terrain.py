#!/usr/bin/env python3
"""
Recalculate map centering for rotated terrain.
Adjusts all object positions to account for 90° terrain rotation.

Usage:
    python3 tools/recenter_for_rotated_terrain.py
"""

import re
from pathlib import Path


def recenter_for_rotation(tscn_path: Path) -> None:
    """Recalculate centering for 90° clockwise rotated terrain.

    When terrain is rotated 90° CW:
    - Old center: (59.0, -295.0) in X-Z
    - New center: (295.0, -59.0) in X-Z (X→Z, Z→-X)

    We need to shift all objects by the difference.
    """

    # Original mesh center (non-rotated)
    old_center_x = 59.0
    old_center_z = -295.0

    # New mesh center after 90° CW rotation (X→Z, Z→-X)
    new_center_x = -old_center_z  # 295.0
    new_center_z = -old_center_x  # -59.0

    # Calculate shift needed
    shift_x = new_center_x - old_center_x  # 295.0 - 59.0 = 236.0
    shift_z = new_center_z - old_center_z  # -59.0 - (-295.0) = 236.0

    print("🔄 Recentering for Rotated Terrain")
    print("=" * 60)
    print(f"Old terrain center (pre-rotation): ({old_center_x}, {old_center_z})")
    print(f"New terrain center (after 90° CW):  ({new_center_x}, {new_center_z})")
    print(f"Required shift: ({shift_x:+.1f}, {shift_z:+.1f})")
    print()

    # Read .tscn file
    content = tscn_path.read_text()
    lines = content.split("\n")

    # Process each line and shift transforms
    modified_lines = []
    transform_count = 0

    for line in lines:
        # Match transform lines: transform = Transform3D(...)
        # Capture the 12 numbers and extract position (last 3)
        match = re.match(
            r"^(transform = Transform3D\()([^,]+), ([^,]+), ([^,]+), "
            r"([^,]+), ([^,]+), ([^,]+), ([^,]+), ([^,]+), ([^,]+), "
            r"([^,]+), ([^,]+), ([^)]+)\)(.*)$",
            line,
        )

        if match:
            # Extract all 12 components
            prefix = match.group(1)
            r1, r2, r3 = match.group(2), match.group(3), match.group(4)
            r4, r5, r6 = match.group(5), match.group(6), match.group(7)
            r7, r8, r9 = match.group(8), match.group(9), match.group(10)
            pos_x = float(match.group(11))
            pos_y = float(match.group(12))
            pos_z = float(match.group(13))
            suffix = match.group(14)

            # Apply shift to position
            new_x = pos_x + shift_x
            new_z = pos_z + shift_z

            # Reconstruct line with shifted position
            new_line = (
                f"{prefix}{r1}, {r2}, {r3}, {r4}, {r5}, {r6}, "
                f"{r7}, {r8}, {r9}, {new_x}, {pos_y}, {new_z}){suffix}"
            )
            modified_lines.append(new_line)
            transform_count += 1
        else:
            modified_lines.append(line)

    # Write back
    new_content = "\n".join(modified_lines)
    tscn_path.write_text(new_content)

    print(f"✅ Shifted {transform_count} transforms by ({shift_x:+.1f}, {shift_z:+.1f})")
    print(f"✅ Updated: {tscn_path}")
    print()
    print("📋 Next: Reload Kursk.tscn in Godot to see recentered map")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    tscn_path = project_root / "GodotProject/levels/Kursk.tscn"

    if not tscn_path.exists():
        print(f"❌ ERROR: {tscn_path} not found!")
        return 1

    recenter_for_rotation(tscn_path)
    return 0


if __name__ == "__main__":
    exit(main())
