#!/usr/bin/env python3
"""Remove engine-specific technical objects from catalog and mappings.

Only keeps visual and gameplay assets that need Portal equivalents.
Removes camera components, seat objects, cockpit internals, etc.
"""

import json
from pathlib import Path


def is_technical_object(asset_name: str) -> bool:
    """Determine if asset is an engine-specific technical object."""

    name_lower = asset_name.lower()

    # Technical object patterns (engine internals, not visual assets)
    technical_patterns = [
        "camera",
        "cockpit",
        "seat",
        "entry",
        "bodyinfo",
        "wheelinfo",
        "steeringinfo",
        "engineinfo",
        "passenge rinfo",
        "gunnerinfo",
        "driverinfo",
        "pilotinfo",
        "pco",  # Player camera object
        "gun_rotate",
        "gun_base",
        "gunbarrel",
        "gunrotate",
        "_info",
        "footrest",
        "leftfoot",
        "rightfoot",
        "weaponbase",
        "floater",
        "propeller",
        "rotaryplane",
        "flap",
        "carriage",
        "horn",
        "wheel",  # Individual wheel components
        "steer",
        "suspension",
        "springobject",
    ]

    # Check if it's a technical object
    for pattern in technical_patterns:
        if pattern in name_lower:
            return True

    # Also remove generic numbered objects
    if asset_name.isdigit() or asset_name in ["1", "2", "3"]:
        return True

    return False


def is_gameplay_system_object(asset_name: str) -> bool:
    """Determine if asset is a gameplay system object (keep these)."""

    name_lower = asset_name.lower()

    # Gameplay objects to KEEP (even if they match some technical patterns)
    gameplay_patterns = [
        "spawner",
        "spawn",
        "controlpoint",
        "capturepoint",
        "aispawn",
        "objective",
        "trigger",
    ]

    for pattern in gameplay_patterns:
        if pattern in name_lower:
            return True

    return False


def main() -> None:
    """Main entry point."""

    print("=" * 80)
    print("TECHNICAL OBJECT CLEANUP")
    print("=" * 80)
    print()

    # Load catalog
    catalog_path = Path("tools/asset_audit/bf1942_asset_catalog.json")
    with open(catalog_path) as f:
        catalog = json.load(f)

    print(f"📖 Current catalog: {len(catalog)} assets")

    # Load mappings
    mappings_path = Path("tools/asset_audit/bf1942_to_portal_mappings.json")
    with open(mappings_path) as f:
        mappings = json.load(f)

    total_mappings = sum(
        len(assets)
        for section, assets in mappings.items()
        if isinstance(assets, dict) and not section.startswith("_")
    )

    print(f"📖 Current mappings: {total_mappings} entries")
    print()

    # Identify technical objects to remove
    print("🔍 Identifying technical objects...")

    to_remove_from_catalog = []
    to_remove_from_mappings = []

    for asset_name in catalog.keys():
        # Keep if it's a gameplay object
        if is_gameplay_system_object(asset_name):
            continue

        # Remove if it's technical
        if is_technical_object(asset_name):
            to_remove_from_catalog.append(asset_name)

    print(f"   Found {len(to_remove_from_catalog)} technical objects in catalog")

    # Also find in mappings
    for section, assets in mappings.items():
        if section.startswith("_"):
            continue
        if not isinstance(assets, dict):
            continue

        for asset_name in list(assets.keys()):
            # Keep gameplay objects
            if is_gameplay_system_object(asset_name):
                continue

            # Remove if technical
            if is_technical_object(asset_name):
                to_remove_from_mappings.append((section, asset_name))

    print(f"   Found {len(to_remove_from_mappings)} technical objects in mappings")
    print()

    # Show samples
    print("Sample technical objects to remove (first 20):")
    for asset in sorted(to_remove_from_catalog)[:20]:
        print(f"  • {asset}")
    if len(to_remove_from_catalog) > 20:
        print(f"  ... and {len(to_remove_from_catalog) - 20} more")

    print()

    # Confirm with user
    response = input("Remove these technical objects? (y/N): ")
    if response.lower() != "y":
        print("Cancelled.")
        return

    print()
    print("🗑️  Removing technical objects...")

    # Remove from catalog
    for asset_name in to_remove_from_catalog:
        del catalog[asset_name]

    # Remove from mappings
    for section, asset_name in to_remove_from_mappings:
        del mappings[section][asset_name]

    # Save cleaned files
    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2)

    with open(mappings_path, "w") as f:
        json.dump(mappings, f, indent=2)

    # Calculate final counts
    new_catalog_size = len(catalog)
    new_mappings_size = sum(
        len(assets)
        for section, assets in mappings.items()
        if isinstance(assets, dict) and not section.startswith("_")
    )

    print()
    print("=" * 80)
    print("✅ CLEANUP COMPLETE")
    print("=" * 80)
    print()
    print(f"Catalog: {len(to_remove_from_catalog)} removed, {new_catalog_size} remaining")
    print(f"Mappings: {len(to_remove_from_mappings)} removed, {new_mappings_size} remaining")
    print()
    print("Cleaned files contain only visual and gameplay assets.")
    print()


if __name__ == "__main__":
    main()
