#!/usr/bin/env python3
"""
Test different axis orientations for Kursk map.

This creates test versions with different axis transformations to find
the correct orientation.

Usage:
    python tools/test_orientation.py
"""

import re
from pathlib import Path


def apply_axis_transform(
    x: float, y: float, z: float, transform_type: str
) -> tuple[float, float, float]:
    """
    Apply different axis transformations.

    Args:
        x, y, z: Original coordinates
        transform_type: Type of transformation

    Returns:
        Tuple of (new_x, new_y, new_z)
    """
    transforms = {
        "original": (x, y, z),
        "swap_xz": (z, y, x),  # Swap X and Z axes
        "negate_x": (-x, y, z),  # Mirror X axis
        "negate_z": (x, y, -z),  # Mirror Z axis
        "negate_xz": (-x, y, -z),  # Mirror both X and Z
        "rotate_90": (-z, y, x),  # Rotate 90° clockwise (top view)
        "rotate_180": (-x, y, -z),  # Rotate 180°
        "rotate_270": (z, y, -x),  # Rotate 270° (or -90°)
    }

    return transforms.get(transform_type, (x, y, z))


def parse_transform3d(transform_str: str) -> tuple[float, float, float] | None:
    """Parse Transform3D to extract position."""
    match = re.search(r"Transform3D\(([^)]+)\)", transform_str)
    if not match:
        return None

    values = [float(x.strip()) for x in match.group(1).split(",")]
    if len(values) != 12:
        return None

    return values[9], values[10], values[11]  # x, y, z position


def main():
    """Generate orientation test report."""
    project_root = Path(__file__).parent.parent
    kursk_tscn = project_root / "GodotProject" / "levels" / "Kursk.tscn"

    print("=" * 70)
    print("Kursk Orientation Test")
    print("=" * 70)
    print()

    # Read current HQ positions
    with open(kursk_tscn) as f:
        content = f.read()

    # Extract TEAM_1_HQ and TEAM_2_HQ transforms
    team1_match = re.search(
        r'\[node name="TEAM_1_HQ".*?\ntransform = (Transform3D\([^)]+\))', content, re.DOTALL
    )
    team2_match = re.search(
        r'\[node name="TEAM_2_HQ".*?\ntransform = (Transform3D\([^)]+\))', content, re.DOTALL
    )

    if not team1_match or not team2_match:
        print("Error: Could not find team HQs")
        return 1

    team1_pos = parse_transform3d(team1_match.group(1))
    team2_pos = parse_transform3d(team2_match.group(1))

    if not team1_pos or not team2_pos:
        print("Error: Could not parse HQ transforms")
        return 1

    print("Current HQ Positions (After Offset):")
    print(f"  TEAM_1_HQ (Axis):   ({team1_pos[0]:7.2f}, {team1_pos[1]:7.2f}, {team1_pos[2]:7.2f})")
    print(f"  TEAM_2_HQ (Allies): ({team2_pos[0]:7.2f}, {team2_pos[1]:7.2f}, {team2_pos[2]:7.2f})")
    print()

    print("=" * 70)
    print("Test Different Orientations:")
    print("=" * 70)
    print()

    transforms = [
        "original",
        "swap_xz",
        "negate_x",
        "negate_z",
        "negate_xz",
        "rotate_90",
        "rotate_180",
        "rotate_270",
    ]

    for transform in transforms:
        new_t1 = apply_axis_transform(*team1_pos, transform)
        new_t2 = apply_axis_transform(*team2_pos, transform)

        # Calculate separation vector
        dx = new_t2[0] - new_t1[0]
        dz = new_t2[2] - new_t1[2]

        # Determine cardinal direction
        if abs(dx) > abs(dz):
            direction = "East-West" if dx > 0 else "West-East"
            primary_axis = "X"
        else:
            direction = "North-South" if dz > 0 else "South-North"
            primary_axis = "Z"

        print(f"{transform:12s}:")
        print(f"  TEAM_1: ({new_t1[0]:7.2f}, {new_t1[1]:7.2f}, {new_t1[2]:7.2f})")
        print(f"  TEAM_2: ({new_t2[0]:7.2f}, {new_t2[1]:7.2f}, {new_t2[2]:7.2f})")
        print(f"  Layout: {direction} (primary: {primary_axis}-axis)")
        print(f"  Delta:  ΔX={dx:7.2f}, ΔZ={dz:7.2f}")
        print()

    print("=" * 70)
    print("BF1942 Original Layout:")
    print("=" * 70)
    print()
    print("From Kursk analysis:")
    print("  Axis Base:   X=437, Z=238   (lower Z = traditionally SOUTH)")
    print("  Allies Base: X=568, Z=850   (higher Z = traditionally NORTH)")
    print("  Layout: North-South along Z-axis")
    print("  Map is ~611m long (Z-axis), ~202m wide (X-axis)")
    print()

    print("=" * 70)
    print("Expected MP_Outskirts Layout:")
    print("=" * 70)
    print()
    print("From MP_Outskirts.tscn:")
    print("  TEAM_1_HQ: (-99.79, 92.41, -124.59)")
    print("  TEAM_2_HQ: ( 12.82, 94.93, -130.54)")
    print("  Layout: East-West along X-axis (ΔX=112.6, ΔZ=-5.95)")
    print("  Teams separated primarily along X-axis")
    print()

    print("=" * 70)
    print("Diagnosis:")
    print("=" * 70)
    print()
    print("If Kursk is currently:")
    print("  - 'original' or 'negate_xz': Layout is North-South (Z-axis)")
    print("    → Need to rotate 90° to match MP_Outskirts (East-West / X-axis)")
    print()
    print("  - 'rotate_90' or 'rotate_270': Layout is East-West (X-axis)")
    print("    → Orientation matches MP_Outskirts!")
    print()
    print("If teams are on wrong sides:")
    print("  - Try 'rotate_180' or mirror operations")
    print()

    print("Next steps:")
    print("1. In Godot, check which direction the map is laid out")
    print("2. Identify if teams are on correct sides")
    print("3. Run: python tools/apply_axis_transform.py <transform_type>")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
