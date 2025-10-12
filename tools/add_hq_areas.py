#!/usr/bin/env python3
"""
Add missing HQ area PolygonVolume nodes to Kursk.tscn.

These define the protected spawn area around each HQ.

Usage:
    python tools/add_hq_areas.py

Author: BF1942 Portal Conversion Project
Date: 2025-01-11
"""

from pathlib import Path

HQ_AREA_TEMPLATE = """
[node name="HQ_Team{team}" instance=ExtResource("2") parent="TEAM_{team}_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 5, 0)
points = PackedVector2Array(20, 20, 20, -20, -20, -20, -20, 20)
"""


def add_hq_areas(input_path: Path, output_path: Path) -> None:
    """
    Add HQ area PolygonVolume nodes after each HQ's spawn points.

    Args:
        input_path: Path to input .tscn
        output_path: Path to output .tscn
    """
    print(f"Reading: {input_path}")

    with open(input_path) as f:
        lines = f.readlines()

    modified_lines = []
    hq_areas_added = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        modified_lines.append(line)

        # After the last spawn point of TEAM_1_HQ, add HQ_Team1 area
        if 'name="SpawnPoint_1_8"' in line:
            # Skip to end of this node (find next blank line or next node)
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("[node"):
                modified_lines.append(lines[i])
                i += 1

            # Add HQ_Team1 area
            modified_lines.append(HQ_AREA_TEMPLATE.format(team=1))
            hq_areas_added += 1
            continue

        # After the last spawn point of TEAM_2_HQ, add HQ_Team2 area
        elif 'name="SpawnPoint_2_8"' in line:
            # Skip to end of this node
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("[node"):
                modified_lines.append(lines[i])
                i += 1

            # Add HQ_Team2 area
            modified_lines.append(HQ_AREA_TEMPLATE.format(team=2))
            hq_areas_added += 1
            continue

        i += 1

    # Write output
    with open(output_path, "w") as f:
        f.writelines(modified_lines)

    print(f"\nAdded {hq_areas_added} HQ area volumes")
    print(f"Output written to: {output_path}")


def main():
    """Main execution."""
    project_root = Path(__file__).parent.parent
    input_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    output_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"
    backup_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn.backup_before_hq_areas"

    if not input_tscn.exists():
        print(f"Error: Input file not found: {input_tscn}")
        return 1

    print("=" * 70)
    print("Add Missing HQ Area Volumes")
    print("=" * 70)
    print()
    print("Adding HQ_Team1 and HQ_Team2 PolygonVolume nodes...")
    print("  - Defines protected spawn area around each HQ")
    print("  - 40m x 40m square area")
    print("  - 5m above HQ position")
    print()

    # Create backup
    print(f"Creating backup: {backup_tscn}")
    import shutil

    shutil.copy2(input_tscn, backup_tscn)
    print()

    # Add HQ areas
    add_hq_areas(input_tscn, output_tscn)

    print()
    print("=" * 70)
    print("✅ HQ areas added!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. In Godot: File → Reopen")
    print("2. Expand TEAM_1_HQ in scene tree")
    print("3. Should now see 'HQ_Team1' node (PolygonVolume)")
    print("4. No more missing node warnings!")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
