#!/usr/bin/env python3
"""
Remove capture points that are at HQ locations.

BF1942 bases should NOT have capture points in BF6 - they're HQs.
Only neutral capturable points should remain.

Usage:
    python tools/remove_base_capture_points.py

Author: BF1942 Portal Conversion Project
Date: 2025-01-11
"""

from pathlib import Path


def remove_base_capture_points(input_path: Path, output_path: Path) -> None:
    """
    Remove CapturePoint_1 and CapturePoint_2 (base capture points).
    Keep only CapturePoint_3 and CapturePoint_4 (neutral points).

    Args:
        input_path: Path to input .tscn
        output_path: Path to output .tscn
    """
    print(f"Reading: {input_path}")

    with open(input_path, 'r') as f:
        lines = f.readlines()

    modified_lines = []
    skip_until_next_node = False
    points_removed = 0

    for line in lines:
        # Start skipping when we hit CapturePoint_1 or CapturePoint_2
        if '[node name="CapturePoint_1"' in line or '[node name="CapturePoint_2"' in line:
            skip_until_next_node = True
            points_removed += 1
            continue

        # Stop skipping when we hit the next node
        if skip_until_next_node and line.startswith('[node name='):
            skip_until_next_node = False

        # Skip lines while we're in a capture point node to remove
        if skip_until_next_node:
            continue

        modified_lines.append(line)

    # Write output
    with open(output_path, 'w') as f:
        f.writelines(modified_lines)

    print(f"\nRemoved {points_removed} base capture points")
    print(f"Remaining: CapturePoint_3 (Lumber Mill) and CapturePoint_4 (Central Ammo)")
    print(f"Output written to: {output_path}")


def main():
    """Main execution."""
    project_root = Path(__file__).parent.parent
    input_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    output_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    backup_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn.backup_before_cp_removal"

    if not input_tscn.exists():
        print(f"Error: Input file not found: {input_tscn}")
        return 1

    print("=" * 70)
    print("Remove Base Capture Points")
    print("=" * 70)
    print()
    print("Issue: CapturePoint_1 and _2 are at HQ locations")
    print("  - CapturePoint_1 at TEAM_1_HQ position (Axis base)")
    print("  - CapturePoint_2 at TEAM_2_HQ position (Allies base)")
    print()
    print("Fix: Remove these base capture points")
    print("  - Keep CapturePoint_3 (Lumber Mill - neutral)")
    print("  - Keep CapturePoint_4 (Central Ammo - neutral)")
    print()
    print("Result: 2 capturable points (matches BF1942 Kursk)")
    print()

    # Create backup
    print(f"Creating backup: {backup_tscn}")
    import shutil
    shutil.copy2(input_tscn, backup_tscn)
    print()

    # Remove base capture points
    remove_base_capture_points(input_tscn, output_tscn)

    print()
    print("=" * 70)
    print("✅ Base capture points removed!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. In Godot: File → Reopen")
    print("2. Scene tree should show:")
    print("   - TEAM_1_HQ (no capture point)")
    print("   - TEAM_2_HQ (no capture point)")
    print("   - CapturePoint_3 (neutral - between bases)")
    print("   - CapturePoint_4 (neutral - between bases)")
    print()
    print("Verify in 3D viewport:")
    print("  - No capture points inside HQ safety zones")
    print("  - 2 neutral capture points in middle of map")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
