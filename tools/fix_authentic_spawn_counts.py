#!/usr/bin/env python3
"""
Fix infantry spawn point counts to match authentic BF1942 Kursk.

BF1942 Kursk Conquest mode has:
- Axis HQ: 5 spawn points
- Allies HQ: 4 spawn points

We currently have 8 per HQ, which is inauthentic.

Usage:
    python tools/fix_authentic_spawn_counts.py

Author: BF1942 Portal Conversion Project
Date: 2025-01-11
"""

from pathlib import Path


def fix_spawn_counts(input_path: Path, output_path: Path) -> None:
    """
    Remove extra spawn points to match BF1942 authentic counts.

    Team 1 (Axis): Keep SpawnPoint_1_1 through SpawnPoint_1_5 (remove 6-8)
    Team 2 (Allies): Keep SpawnPoint_2_1 through SpawnPoint_2_4 (remove 5-8)

    Args:
        input_path: Path to input .tscn
        output_path: Path to output .tscn
    """
    print(f"Reading: {input_path}")

    with open(input_path) as f:
        lines = f.readlines()

    modified_lines = []
    skip_until_next_node = False
    spawns_removed = 0

    # Track which spawns to remove
    remove_spawns = {
        "SpawnPoint_1_6",
        "SpawnPoint_1_7",
        "SpawnPoint_1_8",  # Axis: remove 6-8
        "SpawnPoint_2_5",
        "SpawnPoint_2_6",
        "SpawnPoint_2_7",
        "SpawnPoint_2_8",  # Allies: remove 5-8
    }

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is a spawn point to remove
        should_remove = False
        for spawn_name in remove_spawns:
            if f'name="{spawn_name}"' in line:
                should_remove = True
                skip_until_next_node = True
                spawns_removed += 1
                break

        if should_remove:
            i += 1
            continue

        # If we're skipping, check if we hit the next node
        if skip_until_next_node:
            if line.startswith("[node name=") or line.startswith("[ext_resource"):
                skip_until_next_node = False
            else:
                i += 1
                continue

        modified_lines.append(line)
        i += 1

    # Now update the InfantrySpawns array references in each HQ
    final_lines = []
    for line in modified_lines:
        if "InfantrySpawns = [NodePath" in line and "TEAM_1_HQ" in "".join(
            modified_lines[max(0, modified_lines.index(line) - 10) : modified_lines.index(line)]
        ):
            # Team 1 should only have spawn points 1-5
            line = 'InfantrySpawns = [NodePath("SpawnPoint_1_1"), NodePath("SpawnPoint_1_2"), NodePath("SpawnPoint_1_3"), NodePath("SpawnPoint_1_4"), NodePath("SpawnPoint_1_5")]\n'
        elif "InfantrySpawns = [NodePath" in line and "TEAM_2_HQ" in "".join(
            modified_lines[max(0, modified_lines.index(line) - 10) : modified_lines.index(line)]
        ):
            # Team 2 should only have spawn points 1-4
            line = 'InfantrySpawns = [NodePath("SpawnPoint_2_1"), NodePath("SpawnPoint_2_2"), NodePath("SpawnPoint_2_3"), NodePath("SpawnPoint_2_4")]\n'

        final_lines.append(line)

    # Write output
    with open(output_path, "w") as f:
        f.writelines(final_lines)

    print(f"\nRemoved {spawns_removed} extra spawn points")
    print("Team 1 (Axis): Now has 5 spawn points (authentic)")
    print("Team 2 (Allies): Now has 4 spawn points (authentic)")
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
    print("Fix Authentic Spawn Point Counts")
    print("=" * 70)
    print()
    print("Current Status:")
    print("  - Team 1 (Axis): 8 spawn points")
    print("  - Team 2 (Allies): 8 spawn points")
    print()
    print("BF1942 Authentic Counts:")
    print("  - Team 1 (Axis): 5 spawn points")
    print("  - Team 2 (Allies): 4 spawn points")
    print()
    print("Action: Removing extra spawn points to match BF1942")
    print()

    # Create backup
    print(f"Creating backup: {backup_tscn}")
    import shutil

    shutil.copy2(input_tscn, backup_tscn)
    print()

    # Fix spawn counts
    fix_spawn_counts(input_tscn, output_tscn)

    print()
    print("=" * 70)
    print("Spawn Points Fixed!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. In Godot: File → Reopen")
    print("2. Verify spawn point counts in scene tree:")
    print("   - TEAM_1_HQ: SpawnPoint_1_1 through SpawnPoint_1_5 (5 total)")
    print("   - TEAM_2_HQ: SpawnPoint_2_1 through SpawnPoint_2_4 (4 total)")
    print()
    print("Authenticity Status:")
    print("  Infantry spawns: Now match BF1942 exactly")
    print("  Vehicle spawners: Already authentic (18 total, including airfields)")
    print("  Capture points: Already authentic (2 neutral)")
    print("  HQ positions: Already authentic (transformed N-S to E-W)")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
