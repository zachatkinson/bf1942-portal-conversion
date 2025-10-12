#!/usr/bin/env python3
"""
Compare available BF6 Portal terrains for Kursk conversion.

Based on research and SDK documentation.

Author: BF1942 Portal Conversion Project
Date: 2025-01-11
"""

terrains = {
    "MP_Abbasid": {
        "location": "Cairo, Egypt",
        "setting": "Urban/Sandy",
        "description": "Construction zones, sandy terrain",
        "rural_score": 2,
        "notes": "Urban setting, not suitable for rural Kursk",
    },
    "MP_Aftermath": {
        "location": "Brooklyn, USA",
        "setting": "Urban",
        "description": "City environment",
        "rural_score": 1,
        "notes": "Urban setting, not suitable",
    },
    "MP_Battery": {
        "location": "Gibraltar",
        "setting": "Coastal/Rocky",
        "description": "Coastal fortifications",
        "rural_score": 3,
        "notes": "Rocky coastal terrain, not farmland",
    },
    "MP_Capstone": {
        "location": "Tajikistan",
        "setting": "Mountain Valley",
        "description": "Ruined villages, trench lines, mountain valley",
        "rural_score": 8,
        "notes": "BEST OPTION: Rural villages, valleys, trenches - perfect for WW2 Kursk!",
    },
    "MP_Dumbo": {
        "location": "Brooklyn, USA",
        "setting": "Urban",
        "description": "City environment",
        "rural_score": 1,
        "notes": "Urban setting, not suitable",
    },
    "MP_FireStorm": {
        "location": "Unknown",
        "setting": "Unknown",
        "description": "Unknown",
        "rural_score": 5,
        "notes": "Need to investigate in Godot",
    },
    "MP_Limestone": {
        "location": "Gibraltar",
        "setting": "Coastal/Rocky",
        "description": "Limestone quarry/coastal",
        "rural_score": 4,
        "notes": "Rocky terrain, could work but not ideal",
    },
    "MP_Outskirts": {
        "location": "Cairo, Egypt",
        "setting": "Urban outskirts",
        "description": "Sandy construction zones with buildings",
        "rural_score": 5,
        "notes": "CURRENT CHOICE: Has buildings but somewhat open",
    },
    "MP_Tungsten": {
        "location": "Tajikistan",
        "setting": "Mountain Valley",
        "description": "Large map with ruined villages, trenches",
        "rural_score": 8,
        "notes": "BEST OPTION: Same region as Capstone, largest map",
    },
}


def main():
    print("=" * 70)
    print("BF6 Portal Terrain Comparison for Kursk")
    print("=" * 70)
    print()
    print("Sorting by rural suitability (10 = perfect rural, 1 = urban):")
    print()

    # Sort by rural_score descending
    sorted_terrains = sorted(terrains.items(), key=lambda x: x[1]["rural_score"], reverse=True)

    for name, data in sorted_terrains:
        print(f"{name} - Score: {data['rural_score']}/10")
        print(f"  Location: {data['location']}")
        print(f"  Setting: {data['setting']}")
        print(f"  Description: {data['description']}")
        print(f"  Notes: {data['notes']}")
        print()

    print("=" * 70)
    print("RECOMMENDATIONS FOR KURSK (1943 Russian farmland)")
    print("=" * 70)
    print()
    print("TOP CHOICES:")
    print()
    print("1. MP_Capstone or MP_Tungsten (Tajikistan) - Score: 8/10")
    print("   ✅ Mountain valleys (similar to Kursk geography)")
    print("   ✅ Ruined villages (authentic WW2 setting)")
    print("   ✅ Trench lines (perfect for WW2 combat)")
    print("   ✅ Tungsten is the largest map (good for 611m Kursk)")
    print()
    print("2. MP_Outskirts (Cairo) - Score: 5/10")
    print("   ⚠️  CURRENT CHOICE")
    print("   ⚠️  Has modern buildings (not authentic to 1943)")
    print("   ⚠️  Sandy/desert theme (not Russian)")
    print("   ✅ Open terrain")
    print()
    print("RECOMMENDATION:")
    print("Switch from MP_Outskirts to MP_Tungsten for authentic rural Kursk")
    print()


if __name__ == "__main__":
    main()
