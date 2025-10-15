#!/usr/bin/env python3
"""Asset randomizer for visual variety in converted maps.

Single Responsibility: Asset variety selection with terrain filtering.

This component provides randomized asset selection for repeated objects
(trees, rocks, shrubs, crates, houses) while respecting Portal's
level restrictions to ensure all variants are available on the target terrain.
"""

import json
import random
from pathlib import Path

from ..constants.paths import get_mappings_file
from .asset_catalog import AssetCatalog

# Category keywords (DRY: Single Source of Truth for asset categorization)
CATEGORY_KEYWORDS = {
    "trees": [
        "tree",
        "birch",
        "pine",
        "oak",
        "spruce",
        "poplar",
        "juniper",
        "hawthorn",
        "walnut",
        "fig",
    ],
    "rocks": ["rock", "boulder", "stone"],
    "shrubs": ["bush", "shrub", "hedge", "undergrowth"],
    "buildings": ["house", "building", "barn", "mill", "hangar", "bunker"],
    "props": ["crate", "barrel", "box", "container"],
}


class AssetRandomizer:
    """Randomizes asset selection for visual variety.

    Uses variety pools from mappings file and filters by terrain availability.
    Supports trees, rocks, shrubs, crates, houses, and any other repeated objects.
    """

    def __init__(
        self,
        asset_catalog: AssetCatalog,
        target_terrain: str,
        mappings_file: Path | None = None,
        seed: int = 42,
    ):
        """Initialize randomizer.

        Args:
            asset_catalog: AssetCatalog for terrain filtering
            target_terrain: Target terrain name (e.g., "MP_Tungsten")
            mappings_file: Path to mappings file with variety pools
            seed: Random seed for reproducibility
        """
        self.asset_catalog = asset_catalog
        self.target_terrain = target_terrain
        self.variety_pools: dict[str, list[str]] = {}
        self.randomize_flags: dict[str, bool] = {}
        self._random = random.Random(seed)

        self._load_variety_pools(mappings_file)

    def _load_variety_pools(self, mappings_file: Path | None) -> None:
        """Load variety pools from mappings file.

        Args:
            mappings_file: Path to bf1942_to_portal_mappings.json
        """
        if mappings_file is None:
            # Default location
            mappings_file = get_mappings_file()

        if not mappings_file.exists():
            print(f"⚠️  Warning: Mappings file not found at {mappings_file}")
            print("   Asset randomization will be disabled")
            return

        try:
            with open(mappings_file) as f:
                data = json.load(f)

            # Extract variety pools from static_objects section
            for asset_type, mapping in data.get("static_objects", {}).items():
                if "variety_pool" in mapping:
                    pool = mapping["variety_pool"]
                    # Filter pool by terrain availability
                    filtered_pool = [
                        variant
                        for variant in pool
                        if self.asset_catalog.is_available_on_terrain(variant, self.target_terrain)
                    ]

                    if filtered_pool:
                        self.variety_pools[asset_type] = filtered_pool
                        self.randomize_flags[asset_type] = mapping.get("randomize", True)

            if self.variety_pools:
                print(
                    f"   🎲 Loaded {len(self.variety_pools)} variety pools "
                    f"for asset randomization on {self.target_terrain}"
                )

        except Exception as e:
            print(f"⚠️  Warning: Failed to load variety pools: {e}")

    def should_randomize(self, asset_type: str) -> bool:
        """Check if an asset type should be randomized.

        Args:
            asset_type: Asset type name

        Returns:
            True if asset has variety pool and randomization is enabled
        """
        return (
            asset_type in self.variety_pools
            and self.randomize_flags.get(asset_type, True)
            and len(self.variety_pools[asset_type]) > 1
        )

    def get_random_variant(self, asset_type: str) -> str:
        """Get a random variant for an asset type.

        Args:
            asset_type: Asset type name

        Returns:
            Random variant from variety pool, or original asset_type if no pool

        Note:
            Uses seeded random for reproducibility across runs.
        """
        if not self.should_randomize(asset_type):
            return asset_type

        pool = self.variety_pools[asset_type]
        return self._random.choice(pool)

    def get_variety_pool(self, asset_type: str) -> list[str]:
        """Get the full variety pool for an asset type.

        Args:
            asset_type: Asset type name

        Returns:
            List of variants (filtered by terrain), or [asset_type] if no pool
        """
        return self.variety_pools.get(asset_type, [asset_type])

    def get_stats(self) -> dict:
        """Get randomizer statistics.

        Returns:
            Dict with variety pool counts and metadata
        """
        total_variants = sum(len(pool) for pool in self.variety_pools.values())
        active_pools = sum(1 for at in self.variety_pools if self.should_randomize(at))

        return {
            "variety_pools": len(self.variety_pools),
            "active_pools": active_pools,
            "total_variants": total_variants,
            "target_terrain": self.target_terrain,
        }

    def categorize_variety_pools(self) -> dict[str, list[str]]:
        """Categorize variety pools by asset type.

        Returns:
            Dict mapping categories to asset types with variety pools

        Categories: trees, rocks, shrubs, buildings, props

        Note:
            Uses CATEGORY_KEYWORDS constant for DRY principle.
        """
        categories: dict[str, list[str]] = {
            "trees": [],
            "rocks": [],
            "shrubs": [],
            "buildings": [],
            "props": [],
            "other": [],
        }

        for asset_type in self.variety_pools:
            lower = asset_type.lower()
            categorized = False

            # Check each category using centralized keywords (DRY)
            for category, keywords in CATEGORY_KEYWORDS.items():
                if any(kw in lower for kw in keywords):
                    categories[category].append(asset_type)
                    categorized = True
                    break

            # Fallback for uncategorized assets
            if not categorized:
                categories["other"].append(asset_type)

        return categories
