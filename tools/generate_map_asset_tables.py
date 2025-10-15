#!/usr/bin/env python3
"""Generate asset tables for each map from asset_types.json."""

import json
from collections import defaultdict
from pathlib import Path

from bfportal.generators.constants.paths import get_asset_types_path, get_project_root


def parse_assets(
    asset_types_path: Path,
) -> tuple[
    defaultdict[str, defaultdict[str, list[str]]],
    defaultdict[str, list[str]],
    dict[str, str],
]:
    """Parse asset_types.json and organize by map."""
    with open(asset_types_path) as f:
        data = json.load(f)

    # Map technical names to display names
    map_names = {
        "MP_Tungsten": "Mirak Valley",
        "MP_FireStorm": "Operation Firestorm",
        "MP_Abbasid": "Siege of Cairo",
        "MP_Aftermath": "Empire State",
        "MP_Battery": "Iberian Offensive",
        "MP_Capstone": "Liberation Peak",
        "MP_Dumbo": "Manhattan Bridge",
        "MP_Limestone": "Saint's Quarter",
        "MP_Outskirts": "New Sobek City",
    }

    # Organize assets by map and category
    map_assets: defaultdict[str, defaultdict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    global_assets: defaultdict[str, list[str]] = defaultdict(list)

    for asset in data["AssetTypes"]:
        asset_type = asset["type"]
        directory = asset.get("directory", "Unknown")
        level_restrictions = asset.get("levelRestrictions", [])

        # Categorize by directory
        if "Nature" in directory:
            category = "Nature"
        elif "Architecture" in directory or "Buildings" in directory:
            category = "Architecture"
        elif "Props" in directory:
            category = "Props"
        elif "LightFixtures" in directory:
            category = "Lighting"
        elif directory.startswith("Gameplay"):
            category = "Gameplay"
        else:
            category = "Other"

        # Organize by map restrictions
        if not level_restrictions:
            # Global asset available on all maps
            global_assets[category].append(asset_type)
        else:
            for map_code in level_restrictions:
                map_assets[map_code][category].append(asset_type)

    return map_assets, global_assets, map_names


def generate_table_html(
    map_code: str,
    map_name: str,
    map_assets: defaultdict[str, defaultdict[str, list[str]]],
    global_assets: defaultdict[str, list[str]],
) -> str:
    """Generate HTML table for a single map."""
    # Combine map-specific and global assets
    all_categories = defaultdict(list)

    # Add map-specific assets
    for category, assets in map_assets[map_code].items():
        all_categories[category].extend(assets)

    # Add global assets
    for category, assets in global_assets.items():
        all_categories[category].extend(assets)

    # Sort categories
    category_order = ["Architecture", "Nature", "Props", "Lighting", "Gameplay", "Other"]
    sorted_categories = [
        (cat, all_categories[cat]) for cat in category_order if cat in all_categories
    ]

    # Generate table rows
    rows = []
    for category, assets in sorted_categories:
        count = len(assets)
        examples = ", ".join(sorted(assets)[:3])  # Show first 3 examples
        if len(assets) > 3:
            examples += f", ... (+{len(assets) - 3} more)"

        rows.append(f"""
                                <tr class="border-b border-bf-dark-border/30 dark:border-bf-dark-border/30 border-bf-light-border/50">
                                    <td class="px-3 py-2">{category}</td>
                                    <td class="px-3 py-2">{count}</td>
                                    <td class="px-3 py-2 text-xs">{examples}</td>
                                </tr>""")

    return "\n".join(rows)


def main():
    """Generate asset tables for all maps."""
    project_root = get_project_root()
    asset_types_path = get_asset_types_path()

    map_assets, global_assets, map_names = parse_assets(asset_types_path)

    print("Asset Analysis Complete!")
    print("=" * 60)

    for map_code in sorted(map_names.keys()):
        map_name = map_names[map_code]
        print(f"\n{map_name} ({map_code}):")

        # Count assets
        map_specific = sum(len(assets) for assets in map_assets[map_code].values())
        global_count = sum(len(assets) for assets in global_assets.values())
        total = map_specific + global_count

        print(f"  Map-specific: {map_specific}")
        print(f"  Global: {global_count}")
        print(f"  Total: {total}")

        # Show breakdown by category
        for category in ["Architecture", "Nature", "Props", "Lighting", "Gameplay"]:
            specific = len(map_assets[map_code].get(category, []))
            shared = len(global_assets.get(category, []))
            if specific > 0 or shared > 0:
                print(
                    f"    {category}: {specific + shared} ({specific} specific + {shared} global)"
                )

    print(f"\n{'=' * 60}")
    print("\nGenerating HTML tables...")

    # Generate HTML output file
    output_path = project_root / "tools" / "map_asset_tables.html"
    with open(output_path, "w") as f:
        for map_code in sorted(map_names.keys()):
            map_name = map_names[map_code]
            table_html = generate_table_html(map_code, map_name, map_assets, global_assets)

            f.write(f"\n<!-- {map_name} ({map_code}) -->\n")
            f.write(table_html)
            f.write("\n")

    print(f"✅ HTML tables written to: {output_path}")
    print("\nCopy these tables into sdk_reference/index.html")


if __name__ == "__main__":
    main()
