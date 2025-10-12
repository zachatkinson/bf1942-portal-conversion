#!/usr/bin/env python3
"""BF1942 to Portal Asset Mapping Tool.

Interactive tool to assist with mapping 733 BF1942 assets to Portal equivalents.
Uses fuzzy matching to suggest Portal assets based on BF1942 asset names.

Usage:
    python3 tools/create_asset_mappings.py [--auto-suggest]

Options:
    --auto-suggest    Automatically fill in best-guess mappings (requires manual review)
"""

import json
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Tuple


class AssetMapper:
    """Maps BF1942 assets to Portal equivalents."""

    def __init__(self, bf1942_template_path: Path, portal_assets_path: Path):
        self.bf1942_template_path = bf1942_template_path
        self.portal_assets_path = portal_assets_path

        # Load BF1942 template
        with open(bf1942_template_path) as f:
            self.bf1942_data = json.load(f)

        # Load Portal assets
        with open(portal_assets_path) as f:
            portal_data = json.load(f)
            self.portal_assets = portal_data.get("AssetTypes", [])

        # Build Portal asset lookup by type and keywords
        self.portal_by_type = {a["type"]: a for a in self.portal_assets}
        self.portal_unrestricted = [
            a for a in self.portal_assets if not a.get("levelRestrictions", [])
        ]

        # Category keyword mappings
        self.category_keywords = {
            "vehicle": [
                "tank",
                "jeep",
                "boat",
                "plane",
                "aircraft",
                "car",
                "truck",
                "apc",
                "helicopter",
            ],
            "weapon": ["gun", "rifle", "pistol", "mg", "cannon"],
            "building": [
                "house",
                "bunker",
                "tower",
                "building",
                "barracks",
                "factory",
                "structure",
            ],
            "prop": ["barrel", "crate", "fence", "debris", "sandbag", "box"],
            "spawner": ["spawner", "spawn", "controlpoint", "capturepoint", "hq"],
        }

    def similarity_score(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def find_best_matches(
        self, bf1942_asset: str, category: str, top_n: int = 5
    ) -> List[Tuple[str, float, Dict]]:
        """Find best Portal asset matches for a BF1942 asset."""
        scores = []

        # Get keywords for this category
        keywords = self.category_keywords.get(category, [])

        for portal_asset in self.portal_assets:
            portal_type = portal_asset["type"]

            # Calculate base similarity
            base_score = self.similarity_score(bf1942_asset, portal_type)

            # Bonus if keywords match
            keyword_bonus = 0.0
            bf_lower = bf1942_asset.lower()
            portal_lower = portal_type.lower()

            for keyword in keywords:
                if keyword in bf_lower and keyword in portal_lower:
                    keyword_bonus += 0.2

            # Penalty for level restrictions (prefer unrestricted assets)
            restriction_penalty = 0.0
            restrictions = portal_asset.get("levelRestrictions", [])
            if restrictions:
                restriction_penalty = 0.1  # Slight penalty for restricted assets

            final_score = base_score + keyword_bonus - restriction_penalty

            scores.append((portal_type, final_score, portal_asset))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:top_n]

    def auto_suggest_mappings(self) -> Dict:
        """Automatically suggest mappings for all assets."""
        print("=" * 70)
        print("Auto-Suggesting Asset Mappings")
        print("=" * 70)
        print("This will suggest best-guess mappings. Manual review is REQUIRED!")
        print()

        mappings_made = 0
        total_assets = 0

        for category_key in [
            "vehicles",
            "spawners",
            "buildings",
            "props",
            "weapons",
            "static_objects",
            "unknown",
        ]:
            category = self.bf1942_data.get(category_key, {})
            if not isinstance(category, dict):
                continue

            print(f"\n📦 Processing {category_key}...")

            for asset_type, asset_info in category.items():
                if not isinstance(asset_info, dict):
                    continue

                total_assets += 1

                # Skip if already mapped
                if asset_info.get("portal_equivalent") != "TODO":
                    continue

                # Find best match
                bf_category = asset_info.get("category", "unknown")
                matches = self.find_best_matches(asset_type, bf_category, top_n=1)

                if matches:
                    best_match, score, portal_asset = matches[0]

                    # Only auto-map if confidence is high enough
                    if score > 0.3:  # Threshold for auto-suggestion
                        asset_info["portal_equivalent"] = best_match
                        asset_info["auto_suggested"] = True
                        asset_info["confidence_score"] = round(score, 3)
                        asset_info["notes"] = "⚠️ AUTO-SUGGESTED - REQUIRES MANUAL REVIEW"

                        restrictions = portal_asset.get("levelRestrictions", [])
                        if restrictions:
                            asset_info["notes"] += f" | Restricted to {len(restrictions)} maps"

                        mappings_made += 1
                        print(f"  ✓ {asset_type:40s} → {best_match} (confidence: {score:.2f})")
                    else:
                        print(f"  ⚠️  {asset_type:40s} → No confident match (best: {score:.2f})")

        print("\n" + "=" * 70)
        print(f"Auto-suggested {mappings_made} of {total_assets} assets")
        print("=" * 70)
        print("\n⚠️  IMPORTANT: Manual review required for all suggestions!")
        print("Review each 'auto_suggested' entry and:")
        print("  1. Verify the Portal asset is appropriate")
        print("  2. Check level restrictions")
        print("  3. Remove 'auto_suggested' flag when confirmed")
        print("  4. Update 'notes' with your validation")

        return self.bf1942_data

    def generate_mapping_report(self) -> None:
        """Generate a report on current mapping status."""
        print("\n" + "=" * 70)
        print("Asset Mapping Status Report")
        print("=" * 70)

        total_assets = 0
        mapped_assets = 0
        auto_suggested = 0

        for category_key in [
            "vehicles",
            "spawners",
            "buildings",
            "props",
            "weapons",
            "static_objects",
            "unknown",
        ]:
            category = self.bf1942_data.get(category_key, {})
            if not isinstance(category, dict):
                continue

            cat_total = 0
            cat_mapped = 0
            cat_auto = 0

            for asset_type, asset_info in category.items():
                if not isinstance(asset_info, dict):
                    continue

                cat_total += 1
                total_assets += 1

                portal_eq = asset_info.get("portal_equivalent", "TODO")
                if portal_eq != "TODO":
                    cat_mapped += 1
                    mapped_assets += 1

                    if asset_info.get("auto_suggested", False):
                        cat_auto += 1
                        auto_suggested += 1

            if cat_total > 0:
                percent = (cat_mapped / cat_total) * 100
                print(f"\n{category_key:20s}")
                print(
                    f"  Total: {cat_total:4d} | Mapped: {cat_mapped:4d} ({percent:5.1f}%) | Auto: {cat_auto:4d}"
                )

        print("\n" + "=" * 70)
        print(
            f"Overall: {mapped_assets}/{total_assets} mapped ({(mapped_assets / total_assets) * 100:.1f}%)"
        )
        print(f"Auto-suggested (needs review): {auto_suggested}")
        print("=" * 70)

    def save_mappings(self, output_path: Path) -> None:
        """Save mappings to file."""
        with open(output_path, "w") as f:
            json.dump(self.bf1942_data, f, indent=2)
        print(f"\n✅ Saved mappings to: {output_path}")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent

    bf1942_template = (
        project_root / "tools" / "asset_audit" / "bf1942_to_portal_mappings_template.json"
    )
    portal_assets = project_root / "FbExportData" / "asset_types.json"
    output_path = project_root / "tools" / "asset_audit" / "bf1942_to_portal_mappings.json"

    if not bf1942_template.exists():
        print(f"❌ ERROR: BF1942 template not found: {bf1942_template}")
        return 1

    if not portal_assets.exists():
        print(f"❌ ERROR: Portal assets not found: {portal_assets}")
        return 1

    mapper = AssetMapper(bf1942_template, portal_assets)

    # Check if auto-suggest flag is set
    auto_suggest = "--auto-suggest" in sys.argv

    if auto_suggest:
        print("🤖 Auto-suggest mode enabled")
        mapper.auto_suggest_mappings()
        mapper.generate_mapping_report()
        mapper.save_mappings(output_path)

        print("\n💡 Next steps:")
        print(f"  1. Review {output_path}")
        print("  2. Manually verify all 'auto_suggested' entries")
        print("  3. Fix any incorrect mappings")
        print("  4. Remove 'auto_suggested' flags after verification")
        print("  5. Rename to bf1942_to_portal.json when complete")
    else:
        print("📊 Report mode (use --auto-suggest to generate mappings)")
        mapper.generate_mapping_report()

    return 0


if __name__ == "__main__":
    exit(main())
