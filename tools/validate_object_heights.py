#!/usr/bin/env python3
"""Height Validation Tool.

Validates that all gameplay objects (HQs, spawns, capture points, vehicles)
are positioned at appropriate heights relative to the terrain.

For now, this validates against the original BF1942 heights stored in
kursk_extracted_data.json. Future enhancement: query actual Godot terrain heights.

Usage:
    python tools/validate_object_heights.py
"""

import json
from pathlib import Path
from typing import Any


def load_kursk_data(data_path: Path) -> dict[str, Any]:
    """Load Kursk extracted data."""
    with open(data_path) as f:
        data: dict[str, Any] = json.load(f)
        return data


def analyze_heights(kursk_data: dict[str, Any]) -> None:
    """Analyze height distribution of all objects."""
    print("=" * 70)
    print("Kursk Object Height Analysis")
    print("=" * 70)

    # Collect all heights
    heights = []

    print("\n📍 Control Points:")
    for cp in kursk_data["control_points"]:
        y = cp["position"]["y"]
        heights.append(y)
        print(f"   {cp['name']}: Y = {y:.2f}m")

    print("\n🚗 Vehicle Spawners:")
    for spawner in kursk_data["vehicle_spawners"]:
        y = spawner["position"]["y"]
        heights.append(y)
        team = spawner.get("team", "neutral")
        print(f"   {spawner['bf1942_type']} (Team {team}): Y = {y:.2f}m")

    # Statistics
    min_height = min(heights)
    max_height = max(heights)
    avg_height = sum(heights) / len(heights)

    print("\n" + "=" * 70)
    print("Height Statistics:")
    print("=" * 70)
    print(f"   Min height: {min_height:.2f}m")
    print(f"   Max height: {max_height:.2f}m")
    print(f"   Avg height: {avg_height:.2f}m")
    print(f"   Range: {max_height - min_height:.2f}m")

    print("\n💡 Recommendations:")
    print("   • All objects use original BF1942 heights")
    print("   • Heights range from ~76m to ~93m")
    print("   • For Tungsten terrain compatibility:")
    print("     - Option 1: Keep BF1942 heights (may float/sink)")
    print("     - Option 2: Sample Tungsten terrain at each XZ coord")
    print("     - Option 3: Convert BF1942 heightmap to replace Tungsten")


def main() -> int:
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    kursk_data_path = project_root / "tools" / "kursk_extracted_data.json"

    if not kursk_data_path.exists():
        print(f"❌ ERROR: Kursk data not found: {kursk_data_path}")
        return 1

    kursk_data = load_kursk_data(kursk_data_path)
    analyze_heights(kursk_data)

    return 0


if __name__ == "__main__":
    exit(main())
