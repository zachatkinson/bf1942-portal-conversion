#!/usr/bin/env python3
"""Improve asset mappings using intelligent name matching against Portal index.

Uses the descriptive names of BF1942 assets to find better Portal equivalents
by analyzing keywords, categories, and name similarity.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any


def normalize_name(name: str) -> str:
    """Normalize asset name for comparison."""
    # Remove common prefixes/suffixes
    name = re.sub(r"^(Em_|M_|BF_|XP_|CDN)", "", name)
    # Remove trailing numbers/underscores
    name = re.sub(r"[_\d]+$", "", name)
    # Lowercase
    return name.lower()


def extract_keywords(asset_name: str) -> list[str]:
    """Extract meaningful keywords from asset name."""
    # Split on underscores and camelCase
    parts = re.split(r"[_\s]+|(?<=[a-z])(?=[A-Z])", asset_name)

    # Filter out noise words
    noise = {"m1", "m2", "m3", "l1", "l2", "xp", "em", "cdn", "bf", "the", "a", "an", "of"}
    keywords = [p.lower() for p in parts if p and p.lower() not in noise and len(p) > 1]

    return keywords


def calculate_similarity(bf1942_name: str, portal_name: str) -> float:
    """Calculate similarity score between two asset names."""
    bf_keywords = set(extract_keywords(bf1942_name))
    portal_keywords = set(extract_keywords(portal_name))

    if not bf_keywords or not portal_keywords:
        return 0.0

    # Jaccard similarity
    intersection = len(bf_keywords & portal_keywords)
    union = len(bf_keywords | portal_keywords)

    return intersection / union if union > 0 else 0.0


def find_best_portal_match(
    bf1942_name: str, bf1942_category: str, portal_index: dict[str, Any]
) -> tuple[str, float, str]:
    """Find best Portal asset match for BF1942 asset.

    Returns:
        (portal_asset_name, confidence_score, reasoning)
    """

    bf_keywords = extract_keywords(bf1942_name)

    best_match = None
    best_score = 0.0
    best_reason = ""

    # Search through Portal assets by category
    portal_assets = portal_index.get("by_category", {})

    # Map BF1942 categories to Portal categories to search
    category_mapping = {
        "vehicle": ["Props", "Generic"],
        "building": ["Architecture", "Props", "Generic"],
        "prop": ["Props", "Architecture", "Nature", "Generic"],
        "weapon": ["Props", "Generic"],
        "spawner": ["Gameplay", "Props"],
        "unknown": ["Props", "Architecture", "Nature", "Generic", "Gameplay"],
    }

    search_categories = category_mapping.get(bf1942_category, ["Generic", "Props"])

    # Search relevant Portal categories
    for portal_category in search_categories:
        if portal_category not in portal_assets:
            continue

        for portal_asset in portal_assets[portal_category]:
            portal_name = portal_asset["type"]
            portal_dir = portal_asset.get("directory", "")

            # Calculate similarity
            sim_score = calculate_similarity(bf1942_name, portal_name)

            # Boost score for exact keyword matches
            portal_lower = portal_name.lower()
            for keyword in bf_keywords:
                if keyword in portal_lower:
                    sim_score += 0.2

            # Boost score for directory relevance
            if bf1942_category in portal_dir.lower():
                sim_score += 0.1

            if sim_score > best_score:
                best_score = sim_score
                best_match = portal_name
                matched_keywords = [kw for kw in bf_keywords if kw in portal_lower]
                best_reason = f"Matched keywords: {', '.join(matched_keywords) if matched_keywords else 'similarity'}"

    # If no good match found, return generic based on category
    if best_score < 0.3:
        generic_fallbacks = {
            "vehicle": ("VehicleSpawner", 0.5, "Generic vehicle spawner"),
            "building": ("Architecture_Building_Generic", 0.5, "Generic building"),
            "prop": ("Props_Generic", 0.5, "Generic prop"),
            "weapon": ("WeaponPickup", 0.5, "Generic weapon"),
            "spawner": ("VehicleSpawner", 0.5, "Generic spawner"),
            "unknown": ("Props_Generic", 0.3, "Unknown - manual review needed"),
        }
        return generic_fallbacks.get(bf1942_category, ("Props_Generic", 0.3, "No match found"))

    return (best_match, min(best_score, 0.95), best_reason)


def main() -> None:
    """Main entry point."""

    print("=" * 80)
    print("INTELLIGENT ASSET MAPPING IMPROVER")
    print("=" * 80)
    print()

    # Load Portal index
    portal_index_path = Path("asset_audit/portal_asset_index.json")
    if not portal_index_path.exists():
        print("❌ ERROR: Portal asset index not found")
        print("   Run: python3 tools/generate_portal_index.py")
        sys.exit(1)

    with open(portal_index_path) as f:
        portal_index = json.load(f)

    print("📖 Loaded Portal asset index")

    # Load current mappings
    mappings_path = Path("tools/asset_audit/bf1942_to_portal_mappings.json")
    with open(mappings_path) as f:
        mappings = json.load(f)

    print("📖 Loaded BF1942→Portal mappings")
    print()

    # Find improvable mappings
    print("🔍 Finding improvable mappings...")

    generic_mappings = {
        "TODO_MANUAL_REVIEW",
        "TreeAsset",
        "FoliageAsset",
        "NatureAsset",
        "Architecture_Generic",
        "Props_Generic",
        "Vehicle_Generic",
        "Military_Bunker",
        "Military_Tower",
        "Military_Fence",
        "Military_Crate",
        "Nature_Rock",
    }

    to_improve = []

    for section, assets in mappings.items():
        if section.startswith("_"):
            continue
        if not isinstance(assets, dict):
            continue

        for asset_name, mapping in assets.items():
            if not isinstance(mapping, dict):
                continue

            portal_eq = mapping.get("portal_equivalent", "")
            conf_score = mapping.get("confidence_score", 1.0)
            category = mapping.get("category", "unknown")

            # Improvable if generic mapping or low confidence
            if portal_eq in generic_mappings or conf_score < 0.8:
                to_improve.append(
                    {
                        "section": section,
                        "name": asset_name,
                        "current": portal_eq,
                        "confidence": conf_score,
                        "category": category,
                    }
                )

    print(f"   Found {len(to_improve)} improvable mappings")
    print()

    # Improve mappings
    print("🔧 Improving mappings using intelligent matching...")
    print()

    improved_count = 0
    unchanged_count = 0

    for item in to_improve:
        bf1942_name = item["name"]
        category = item["category"]
        current_mapping = item["current"]
        section = item["section"]

        # Find better match
        new_portal, new_confidence, reason = find_best_portal_match(
            bf1942_name, category, portal_index
        )

        # Only update if significantly better
        if new_confidence > item["confidence"] + 0.1 or (
            current_mapping in generic_mappings and new_confidence >= 0.5
        ):
            # Update mapping
            mappings[section][bf1942_name]["portal_equivalent"] = new_portal
            mappings[section][bf1942_name]["confidence_score"] = new_confidence
            mappings[section][bf1942_name]["notes"] = f"Auto-improved: {reason}"

            if new_portal != current_mapping:
                improved_count += 1
                if improved_count <= 20:  # Show first 20
                    print(f"  ✅ {bf1942_name}")
                    print(f"     {current_mapping} → {new_portal} (conf: {new_confidence:.2f})")
                    print(f"     {reason}")
                    print()
        else:
            unchanged_count += 1

    if improved_count > 20:
        print(f"  ... and {improved_count - 20} more improvements")
        print()

    # Save improved mappings
    with open(mappings_path, "w") as f:
        json.dump(mappings, f, indent=2)

    print("=" * 80)
    print("✅ MAPPING IMPROVEMENT COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  • Analyzed: {len(to_improve)} improvable mappings")
    print(f"  • Improved: {improved_count} mappings")
    print(f"  • Unchanged: {unchanged_count} mappings (no better match found)")
    print()
    print(f"💾 Saved updated mappings to: {mappings_path}")
    print()
    print("Next steps:")
    print("  1. Review improved mappings")
    print("  2. Run: python3 tools/complete_asset_analysis.py")
    print("  3. Commit changes if satisfied")
    print()


if __name__ == "__main__":
    main()
