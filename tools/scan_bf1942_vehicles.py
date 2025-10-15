#!/usr/bin/env python3
"""
Scan BF1942 base game maps and extract all vehicles from ObjectSpawnTemplates.con files.

This script analyzes the ObjectSpawnTemplates.con files in each map's Conquest directory
and extracts all unique vehicle object templates.
"""

import json
import re
from pathlib import Path

# Base game maps to scan (Battle_of_Britain through Gazala alphabetically)
BASE_GAME_MAPS = [
    "Battle_of_Britain",
    "Battle_of_the_Bulge",
    "Battleaxe",
    "Berlin",
    "Bocage",
    "Coral_sea",
    "El_Alamein",
    "Gazala",
    "GuadalCanal",
    "Invasion_of_the_Philippines",
    "Iwo_Jima",
    "Kharkov",
    "Kursk",
    "Liberation_of_Caen",
    "Market_Garden",
    "Midway",
    "Omaha_Beach",
    "Stalingrad",
    "Tobruk",
    "Wake",
]


def extract_vehicles_from_file(file_path: Path) -> set[str]:
    """
    Extract all vehicle object templates from an ObjectSpawnTemplates.con file.

    Args:
        file_path: Path to ObjectSpawnTemplates.con

    Returns:
        Set of unique vehicle template names
    """
    vehicles: set[str] = set()

    if not file_path.exists():
        return vehicles

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return vehicles

    # Look for ObjectTemplate.create lines
    # Format: ObjectTemplate.create ObjectSpawner VehicleName
    pattern = r"ObjectTemplate\.create\s+ObjectSpawner\s+(\S+)"

    for match in re.finditer(pattern, content):
        vehicle_name = match.group(1)
        vehicles.add(vehicle_name)

    return vehicles


def scan_all_maps(base_path: Path) -> dict[str, list[str]]:
    """
    Scan all base game maps and extract vehicles.

    Args:
        base_path: Base directory containing BF1942 extracted levels

    Returns:
        Dictionary mapping map names to lists of vehicles
    """
    results: dict[str, list[str]] = {}

    for map_name in BASE_GAME_MAPS:
        map_dir = base_path / map_name
        conquest_file = map_dir / "Conquest" / "ObjectSpawnTemplates.con"

        if not conquest_file.exists():
            print(f"⚠️  {map_name}: No ObjectSpawnTemplates.con found")
            results[map_name] = []
            continue

        vehicles = extract_vehicles_from_file(conquest_file)
        results[map_name] = sorted(vehicles)

        print(f"✓ {map_name}: Found {len(vehicles)} vehicles")

    return results


def print_results(results: dict[str, list[str]]) -> None:
    """Print scan results in a readable format."""
    print("\n" + "=" * 80)
    print("BF1942 BASE GAME VEHICLE SCAN RESULTS")
    print("=" * 80 + "\n")

    # Collect all unique vehicles across all maps
    all_vehicles = set()
    for vehicles in results.values():
        all_vehicles.update(vehicles)

    print(f"Total maps scanned: {len(results)}")
    print(f"Total unique vehicles: {len(all_vehicles)}\n")

    # Print per-map results
    for map_name, vehicles in results.items():
        print(f"\n{map_name} ({len(vehicles)} vehicles):")
        print("-" * 80)
        if vehicles:
            for vehicle in vehicles:
                print(f"  • {vehicle}")
        else:
            print("  (No vehicles found)")

    # Print all unique vehicles
    print("\n" + "=" * 80)
    print(f"ALL UNIQUE VEHICLES ({len(all_vehicles)} total):")
    print("=" * 80)
    for vehicle in sorted(all_vehicles):
        print(f"  • {vehicle}")
    print()


def save_json(results: dict[str, list[str]], output_path: Path) -> None:
    """Save results to JSON file."""
    output_data = {
        "scan_type": "BF1942 Base Game Vehicles",
        "maps_scanned": len(results),
        "total_unique_vehicles": len({v for vehicles in results.values() for v in vehicles}),
        "maps": results,
    }

    output_path.write_text(json.dumps(output_data, indent=2))
    print(f"✓ Results saved to: {output_path}")


def main():
    """Main entry point."""
    # Determine base path
    base_path = Path(
        "/Users/zach/Downloads/PortalSDK/bf1942_source/extracted/Bf1942/Archives/bf1942/Levels"
    )

    if not base_path.exists():
        print(f"❌ Error: BF1942 levels directory not found at {base_path}")
        return 1

    print(f"Scanning BF1942 maps in: {base_path}\n")

    # Scan all maps
    results = scan_all_maps(base_path)

    # Print results
    print_results(results)

    # Save to JSON
    output_path = Path(__file__).parent / "bf1942_vehicle_scan_results.json"
    save_json(results, output_path)

    return 0


if __name__ == "__main__":
    exit(main())
