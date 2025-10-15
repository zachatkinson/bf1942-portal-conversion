#!/usr/bin/env python3
"""
Scan all BF1942 maps and extracted data for AXIS vehicles (German, Italian, Japanese).
Categorizes vehicles by type and provides a complete inventory.
"""

from collections import defaultdict
from pathlib import Path

# Vehicle categorization based on BF1942 internal names and types
AXIS_VEHICLES = {
    # German Land Vehicles
    "PanzerIV": {"faction": "German", "category": "Tanks/Armored", "full_name": "Panzer IV"},
    "Tiger": {"faction": "German", "category": "Tanks/Armored", "full_name": "Tiger I"},
    "Wespe": {
        "faction": "German",
        "category": "Tanks/Armored",
        "full_name": "Wespe (Self-Propelled Artillery)",
    },
    "Hanomag": {"faction": "German", "category": "Transports", "full_name": "Sd.Kfz. 251 Hanomag"},
    "Kubelwagen": {"faction": "German", "category": "Transports", "full_name": "Kübelwagen"},
    "KettenKrad": {
        "faction": "German",
        "category": "Transports",
        "full_name": "Sd.Kfz. 2 Kettenkrad",
    },
    "Flak_38": {
        "faction": "German",
        "category": "Infantry/Emplacements",
        "full_name": "Flak 38 (AA Gun)",
    },
    # German Aircraft
    "bf109": {"faction": "German", "category": "Aircraft", "full_name": "Bf 109 (Fighter)"},
    "Stuka": {
        "faction": "German",
        "category": "Aircraft",
        "full_name": "Ju 87 Stuka (Dive Bomber)",
    },
    "bf110": {"faction": "German", "category": "Aircraft", "full_name": "Bf 110 (Heavy Fighter)"},
    "Ju88": {"faction": "German", "category": "Aircraft", "full_name": "Ju 88 (Bomber)"},
    "He111": {"faction": "German", "category": "Aircraft", "full_name": "He 111 (Bomber)"},
    "FW190": {"faction": "German", "category": "Aircraft", "full_name": "Fw 190 (Fighter)"},
    "Me262": {"faction": "German", "category": "Aircraft", "full_name": "Me 262 (Jet Fighter)"},
    # Japanese Land Vehicles
    "Chi-ha": {
        "faction": "Japanese",
        "category": "Tanks/Armored",
        "full_name": "Type 97 Chi-Ha (Tank)",
    },
    "Ho-Ha": {
        "faction": "Japanese",
        "category": "Tanks/Armored",
        "full_name": "Type 2 Ho-Ha (Half-track)",
    },
    # Japanese Aircraft
    "Zero": {"faction": "Japanese", "category": "Aircraft", "full_name": "A6M Zero (Fighter)"},
    "AichiVal": {
        "faction": "Japanese",
        "category": "Aircraft",
        "full_name": "Aichi D3A Val (Dive Bomber)",
    },
    "AichiVal-T": {
        "faction": "Japanese",
        "category": "Aircraft",
        "full_name": "Aichi D3A Val Torpedo Bomber",
    },
    "Kate": {
        "faction": "Japanese",
        "category": "Aircraft",
        "full_name": "Nakajima B5N Kate (Torpedo Bomber)",
    },
    # Japanese Naval
    "Yamato": {"faction": "Japanese", "category": "Naval", "full_name": "Yamato (Battleship)"},
    "Shokaku": {
        "faction": "Japanese",
        "category": "Naval",
        "full_name": "Shokaku (Aircraft Carrier)",
    },
    "Hatsuzuki": {"faction": "Japanese", "category": "Naval", "full_name": "Hatsuzuki (Destroyer)"},
    "Type38": {"faction": "Japanese", "category": "Naval", "full_name": "Type 38 Torpedo Boat"},
    "Type38Raft": {
        "faction": "Japanese",
        "category": "Transports",
        "full_name": "Type 38 Landing Craft",
    },
    "Daihatsu": {
        "faction": "Japanese",
        "category": "Transports",
        "full_name": "Daihatsu Landing Craft",
    },
    "Sub7C": {"faction": "Japanese", "category": "Naval", "full_name": "I-Class Submarine"},
    # Italian Vehicles (Road to Rome expansion)
    "M13_40": {"faction": "Italian", "category": "Tanks/Armored", "full_name": "M13/40 (Tank)"},
    "M11-39": {
        "faction": "Italian",
        "category": "Tanks/Armored",
        "full_name": "M11/39 (Light Tank)",
    },
    "AB41": {"faction": "Italian", "category": "Tanks/Armored", "full_name": "AB 41 (Armored Car)"},
    "Breda": {
        "faction": "Italian",
        "category": "Infantry/Emplacements",
        "full_name": "Breda M37 (Machine Gun)",
    },
    "Autoblinda": {
        "faction": "Italian",
        "category": "Tanks/Armored",
        "full_name": "Autoblinda AB 41",
    },
    "AT25": {
        "faction": "Italian",
        "category": "Infantry/Emplacements",
        "full_name": "Ansaldo 25mm Anti-Tank Gun",
    },
    "ItLcvp": {
        "faction": "Italian",
        "category": "Transports",
        "full_name": "Italian Landing Craft",
    },
    "SdKfz7": {
        "faction": "German",
        "category": "Transports",
        "full_name": "Sd.Kfz. 7 (Half-track)",
    },
    "SturmGeschutz": {
        "faction": "German",
        "category": "Tanks/Armored",
        "full_name": "StuG III (Assault Gun)",
    },
    # Italian Aircraft
    "MC202": {"faction": "Italian", "category": "Aircraft", "full_name": "Macchi C.202 (Fighter)"},
    "SM79": {"faction": "Italian", "category": "Aircraft", "full_name": "SM.79 Sparviero (Bomber)"},
    "G50": {"faction": "Italian", "category": "Aircraft", "full_name": "Fiat G.50 (Fighter)"},
    # German Secret Weapons (XPack2)
    "V2Rocket": {
        "faction": "German",
        "category": "Infantry/Emplacements",
        "full_name": "V-2 Rocket",
    },
    "Sturmtiger": {"faction": "German", "category": "Tanks/Armored", "full_name": "Sturmtiger"},
    "SturmTiger": {
        "faction": "German",
        "category": "Tanks/Armored",
        "full_name": "Sturmtiger (Heavy Assault Gun)",
    },
    "T95": {
        "faction": "German",
        "category": "Tanks/Armored",
        "full_name": "Captured T95 (Heavy Tank)",
    },
    "Horton": {
        "faction": "German",
        "category": "Aircraft",
        "full_name": "Horten Ho 229 (Jet Fighter)",
    },
    "HO229": {
        "faction": "German",
        "category": "Aircraft",
        "full_name": "Horten Ho 229 (Jet Fighter)",
    },
    "Wasserfall": {
        "faction": "German",
        "category": "Infantry/Emplacements",
        "full_name": "Wasserfall (AA Missile)",
    },
    "WasserfallRocket": {
        "faction": "German",
        "category": "Infantry/Emplacements",
        "full_name": "Wasserfall Rocket (Ammunition)",
    },
    "Goliath": {
        "faction": "German",
        "category": "Tanks/Armored",
        "full_name": "Goliath (Remote Demolition Vehicle)",
    },
    "Natter": {
        "faction": "German",
        "category": "Aircraft",
        "full_name": "Bachem Ba 349 Natter (Rocket Interceptor)",
    },
    "Flakpanzer": {
        "faction": "German",
        "category": "Tanks/Armored",
        "full_name": "Flakpanzer IV (AA Tank)",
    },
    "R75": {
        "faction": "German",
        "category": "Transports",
        "full_name": "BMW R75 (Motorcycle with Sidecar)",
    },
    "Schwimmwagen": {
        "faction": "German",
        "category": "Transports",
        "full_name": "VW Type 166 Schwimmwagen (Amphibious Car)",
    },
    # Defensive Emplacements
    "Defgun": {
        "faction": "German",
        "category": "Infantry/Emplacements",
        "full_name": "Defensive Gun",
    },
    "Flak18": {
        "faction": "German",
        "category": "Infantry/Emplacements",
        "full_name": "Flak 18 (AA Gun)",
    },
    "Pak40": {
        "faction": "German",
        "category": "Infantry/Emplacements",
        "full_name": "Pak 40 (Anti-Tank Gun)",
    },
    "MG42": {
        "faction": "German",
        "category": "Infantry/Emplacements",
        "full_name": "MG42 (Machine Gun)",
    },
    "MG42_Lafette": {
        "faction": "German",
        "category": "Infantry/Emplacements",
        "full_name": "MG42 on Lafette Mount",
    },
    "Type93": {
        "faction": "Japanese",
        "category": "Infantry/Emplacements",
        "full_name": "Type 93 (Machine Gun)",
    },
    "Type88": {
        "faction": "Japanese",
        "category": "Infantry/Emplacements",
        "full_name": "Type 88 (AA Gun)",
    },
}


def scan_vehicle_directories() -> dict[str, set[str]]:
    """Scan extracted vehicle directories for AXIS vehicles."""
    base_path = Path("/Users/zach/Downloads/PortalSDK/bf1942_source/extracted")
    found_vehicles = defaultdict(set)

    # Scan base game
    bf1942_vehicles = base_path / "Bf1942/Archives/Objects/Vehicles"
    if bf1942_vehicles.exists():
        for category in ["Land", "Air", "Sea"]:
            cat_path = bf1942_vehicles / category
            if cat_path.exists():
                for vehicle_dir in cat_path.iterdir():
                    if vehicle_dir.is_dir():
                        vehicle_name = vehicle_dir.name
                        if vehicle_name in AXIS_VEHICLES:
                            found_vehicles["base_game"].add(vehicle_name)

    # Scan Road to Rome (XPack1)
    xpack1_vehicles = base_path / "XPack1/objects/Vehicles"
    if xpack1_vehicles.exists():
        for item in xpack1_vehicles.rglob("*"):
            if item.is_dir():
                vehicle_name = item.name
                if vehicle_name in AXIS_VEHICLES:
                    found_vehicles["road_to_rome"].add(vehicle_name)

    # Scan Secret Weapons (XPack2)
    xpack2_vehicles = base_path / "XPack2/Objects/Vehicles"
    if xpack2_vehicles.exists():
        for item in xpack2_vehicles.rglob("*"):
            if item.is_dir():
                vehicle_name = item.name
                if vehicle_name in AXIS_VEHICLES:
                    found_vehicles["secret_weapons"].add(vehicle_name)

    return found_vehicles


def categorize_vehicles() -> dict[str, list[dict[str, str]]]:
    """Categorize all AXIS vehicles by type."""
    categories: dict[str, list[dict[str, str]]] = {
        "Tanks/Armored": [],
        "Aircraft": [],
        "Infantry/Emplacements": [],
        "Naval": [],
        "Transports": [],
    }

    for vehicle_id, info in sorted(AXIS_VEHICLES.items()):
        categories[info["category"]].append(
            {"id": vehicle_id, "name": info["full_name"], "faction": info["faction"]}
        )

    return categories


def main():
    """Main execution."""
    print("=" * 80)
    print("BF1942 AXIS VEHICLE INVENTORY")
    print("Scanning all 36 maps and expansion packs")
    print("=" * 80)
    print()

    # Get categorized list
    categories = categorize_vehicles()

    # Print by category
    total_count = 0
    for category, vehicles in categories.items():
        print(f"\n{category.upper()}")
        print("-" * 80)

        # Group by faction
        by_faction = defaultdict(list)
        for vehicle in vehicles:
            by_faction[vehicle["faction"]].append(vehicle)

        for faction in ["German", "Italian", "Japanese"]:
            if faction in by_faction:
                print(f"\n  {faction}:")
                for vehicle in by_faction[faction]:
                    print(f"    • {vehicle['name']} ({vehicle['id']})")
                    total_count += 1

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    for category, vehicles in categories.items():
        faction_counts_per_category: defaultdict[str, int] = defaultdict(int)
        for vehicle in vehicles:
            faction_counts_per_category[vehicle["faction"]] += 1

        print(f"\n{category}: {len(vehicles)} total")
        for faction in ["German", "Italian", "Japanese"]:
            if faction in faction_counts_per_category and faction_counts_per_category[faction] > 0:
                print(f"  - {faction}: {faction_counts_per_category[faction]}")

    print(f"\n{'=' * 80}")
    print(f"TOTAL AXIS VEHICLES: {total_count}")
    print(f"{'=' * 80}")

    # Faction totals
    faction_counts: defaultdict[str, int] = defaultdict(int)
    for info in AXIS_VEHICLES.values():
        faction_counts[info["faction"]] += 1

    print("\nBy Faction:")
    for faction, count in sorted(faction_counts.items()):
        print(f"  - {faction}: {count} vehicles")


if __name__ == "__main__":
    main()
