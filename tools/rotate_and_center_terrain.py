#!/usr/bin/env python3
"""
Rotate terrain 90° clockwise and center it for portrait mode.
DOES NOT touch any assets - they stay exactly where they are.

This script rotates the MP_Tungsten terrain 90° CW around the Y-axis,
keeping the Y elevation unchanged (only affects X and Z axes).

Usage:
    python3 tools/rotate_and_center_terrain.py [--backup]

Options:
    --backup    Create a .tscn.backup file before modifying
"""

import argparse
import shutil
from pathlib import Path


def rotate_and_center_terrain(tscn_path: Path, create_backup: bool = False) -> bool:
    """Rotate terrain 90° CW and reposition for portrait centering.

    The rotation is performed around the Y-axis, which means:
    - Right vector (1,0,0) → (0,0,-1)  [X→Z, Z→-X]
    - Up vector (0,1,0) → (0,1,0)      [Y unchanged - elevation preserved]
    - Forward vector (0,0,1) → (1,0,0) [Z→X]
    - Position Y component stays constant (-64.7589)

    Args:
        tscn_path: Path to the .tscn file to modify
        create_backup: If True, creates a .tscn.backup file before modifying

    Returns:
        True if successful, False if terrain transform not found
    """

    # Create backup if requested
    if create_backup:
        backup_path = tscn_path.with_suffix(".tscn.backup")
        shutil.copy2(tscn_path, backup_path)
        print(f"✅ Backed up to: {backup_path}")

    # Read file
    content = tscn_path.read_text()

    # Find the terrain transform line
    # Current: transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, -64.7589, 0)
    # This is: right(1,0,0), up(0,1,0), forward(0,0,1), pos(0,-64.7589,0)

    # After 90° CW rotation around Y-axis:
    # Rotation matrix: [0, 0, 1; 0, 1, 0; -1, 0, 0]
    # New transform: right(0,0,-1), up(0,1,0), forward(1,0,0)
    # Position (0, -64.7589, 0) keeps Y offset but centers X and Z

    old_transform = "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, -64.7589, 0)"

    # Rotate 90° CW + center for portrait
    new_transform = "transform = Transform3D(0, 0, 1, 0, 1, 0, -1, 0, 0, 0, -64.7589, 0)"

    if old_transform not in content:
        print("❌ ERROR: Could not find expected terrain transform!")
        print("   Looking for:", old_transform)
        return False

    # Replace
    new_content = content.replace(old_transform, new_transform)
    tscn_path.write_text(new_content)

    print(f"✅ Rotated terrain 90° clockwise in: {tscn_path}")
    print("\n🔄 Rotation Details:")
    print("   Before: Identity matrix (no rotation)")
    print("   After:  90° clockwise around Y-axis")
    print("   Y elevation: -64.7589 (unchanged)")
    print(f"\n   Old: {old_transform}")
    print(f"   New: {new_transform}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Rotate MP_Tungsten terrain 90° clockwise for portrait mode"
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create a .tscn.backup file before modifying"
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    tscn_path = project_root / "GodotProject/levels/Kursk.tscn"

    if not tscn_path.exists():
        print(f"❌ ERROR: {tscn_path} not found!")
        return 1

    print("🧪 Rotating terrain 90° and centering for portrait mode")
    print("=" * 60)

    if rotate_and_center_terrain(tscn_path, create_backup=args.backup):
        print("\n📋 Next Steps:")
        print("   1. Reload Kursk.tscn in Godot")
        print("   2. Check if terrain rotated correctly")
        print("   3. Export and test in Portal web builder")
        if args.backup:
            backup_path = tscn_path.with_suffix(".tscn.backup")
            print(f"\n   To restore: mv {backup_path} {tscn_path}")
        print("\n" + "=" * 60)
        print("✅ Rotation complete!")
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
