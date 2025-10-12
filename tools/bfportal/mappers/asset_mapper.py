#!/usr/bin/env python3
"""Asset mapper implementation using the BF1942 → Portal lookup table."""

import json
from pathlib import Path

from ..core.exceptions import MappingError
from ..core.interfaces import IAssetMapper, MapContext, PortalAsset


class AssetMapper(IAssetMapper):
    """Maps BF1942 assets to Portal equivalents using JSON lookup table.

    This implementation uses the 733-asset mapping table generated in Phase 1.
    """

    def __init__(self, portal_assets_path: Path):
        """Initialize mapper.

        Args:
            portal_assets_path: Path to Portal SDK asset_types.json
        """
        self.mappings: dict[str, dict] = {}
        self.portal_assets: dict[str, PortalAsset] = {}

        # Load Portal asset catalog
        with open(portal_assets_path) as f:
            portal_data = json.load(f)

        for asset in portal_data.get("AssetTypes", []):
            self.portal_assets[asset["type"]] = PortalAsset(
                type=asset["type"],
                directory=asset.get("directory", ""),
                level_restrictions=asset.get("levelRestrictions", []),
                properties=asset.get("properties", []),
            )

    def load_mappings(self, mappings_file: Path) -> None:
        """Load BF1942 → Portal mappings from JSON file.

        Args:
            mappings_file: Path to bf1942_to_portal_mappings.json

        Raises:
            FileNotFoundError: If mappings file not found
            ValueError: If mappings file is invalid
        """
        if not mappings_file.exists():
            raise FileNotFoundError(f"Mappings file not found: {mappings_file}")

        with open(mappings_file) as f:
            data = json.load(f)

        # Flatten category-based structure into single lookup dict
        for category_key in data:
            if category_key == "_metadata":
                continue

            category = data[category_key]
            if not isinstance(category, dict):
                continue

            for asset_type, asset_info in category.items():
                if not isinstance(asset_info, dict):
                    continue

                portal_eq = asset_info.get("portal_equivalent")
                if portal_eq and portal_eq != "TODO":
                    self.mappings[asset_type] = {
                        "portal_type": portal_eq,
                        "category": asset_info.get("category", "unknown"),
                        "confidence": asset_info.get("confidence_score", 1.0),
                        "notes": asset_info.get("notes", ""),
                        "fallbacks": asset_info.get("fallbacks", {}),  # Map-specific fallbacks
                    }

        print(f"✅ Loaded {len(self.mappings)} asset mappings from {mappings_file.name}")

    def map_asset(self, source_asset: str, context: MapContext) -> PortalAsset | None:
        """Map BF1942 asset to Portal equivalent.

        Args:
            source_asset: BF1942 asset type name
            context: Context for mapping decisions

        Returns:
            PortalAsset if mapping found and compatible, None otherwise

        Raises:
            MappingError: If mapping exists but Portal asset is restricted
        """
        # Check if we have a mapping
        if source_asset not in self.mappings:
            # Check if this is a terrain element that should be skipped
            if self._is_terrain_element(source_asset):
                return None  # Skip terrain elements

            # Asset not in mappings file - try best-guess fallback
            return self._find_best_guess_fallback(source_asset, context.target_base_map)

        mapping = self.mappings[source_asset]
        portal_type = mapping["portal_type"]

        # Check if Portal asset exists
        if portal_type not in self.portal_assets:
            # Mapped asset doesn't exist - try fallback instead
            print(
                f"  ⚠️  Mapped asset '{portal_type}' not in catalog, trying fallback for {source_asset}"
            )
            alternative = self._find_alternative(
                source_asset, mapping["category"], context.target_base_map
            )
            if alternative:
                return alternative

            # No category alternative found, try best-guess
            best_guess = self._find_best_guess_fallback(source_asset, context.target_base_map)
            if best_guess:
                return best_guess

            # No fallback found at all
            raise MappingError(
                f"Mapped Portal asset '{portal_type}' not found in Portal catalog. "
                f"BF1942 asset: {source_asset}"
            )

        portal_asset = self.portal_assets[portal_type]

        # Check level restrictions
        if portal_asset.level_restrictions:
            if context.target_base_map not in portal_asset.level_restrictions:
                # Asset is restricted and not available on this map

                # Step 1: Check for map-specific fallback
                fallbacks = mapping.get("fallbacks", {})
                if context.target_base_map in fallbacks:
                    fallback_type = fallbacks[context.target_base_map]
                    if fallback_type in self.portal_assets:
                        fallback_asset = self.portal_assets[fallback_type]
                        # Verify fallback is available on target map
                        if (
                            not fallback_asset.level_restrictions
                            or context.target_base_map in fallback_asset.level_restrictions
                        ):
                            print(
                                f"  🔄 Using map-specific fallback: {fallback_type} "
                                f"for {source_asset} on {context.target_base_map}"
                            )
                            return fallback_asset

                # Step 2: Try to find an alternative (unrestricted or available on target map)
                alternative = self._find_alternative(
                    source_asset, mapping["category"], context.target_base_map
                )

                if alternative:
                    return alternative
                else:
                    raise MappingError(
                        f"Portal asset '{portal_type}' is restricted to "
                        f"{portal_asset.level_restrictions} and not available on "
                        f"'{context.target_base_map}'. No fallback or alternative found. "
                        f"BF1942 asset: {source_asset}"
                    )

        return portal_asset

    def _find_alternative(
        self, source_asset: str, category: str, target_map: str
    ) -> PortalAsset | None:
        """Find an alternative Portal asset in the same category.

        Looks for assets that are either unrestricted OR available on the target map.
        Prioritizes assets with similar type keywords (e.g., tree->tree, rock->rock).

        Args:
            source_asset: Original BF1942 asset
            category: Asset category (vehicle, building, prop, etc.)
            target_map: Target map name (e.g., 'MP_Tungsten')

        Returns:
            PortalAsset if found, None otherwise
        """
        # Determine asset type keywords from source asset name
        source_lower = source_asset.lower()
        type_keywords = []
        if any(kw in source_lower for kw in ["tree", "pine", "spruce", "oak", "birch", "palm"]):
            type_keywords = ["tree", "pine", "spruce", "oak", "birch", "palm", "cedar"]
        elif any(kw in source_lower for kw in ["rock", "stone", "boulder"]):
            type_keywords = ["rock", "stone", "boulder", "cliff"]
        elif any(kw in source_lower for kw in ["fence", "wall"]):
            type_keywords = ["fence", "wall", "barrier"]

        # Look for other mappings in the same category
        category_mappings = []
        for bf_asset, mapping in self.mappings.items():
            if mapping["category"] != category or bf_asset == source_asset:
                continue

            portal_type = mapping["portal_type"]
            if portal_type not in self.portal_assets:
                continue

            portal_asset = self.portal_assets[portal_type]

            # Check if asset is available (unrestricted or on target map)
            available = (
                not portal_asset.level_restrictions or target_map in portal_asset.level_restrictions
            )

            if available:
                category_mappings.append((bf_asset, mapping, portal_asset))

        # Sort by: 1) matching type keywords, 2) confidence score
        def sort_key(item):
            bf_asset, mapping, portal_asset = item
            portal_type = mapping["portal_type"].lower()

            # Check if portal asset matches any type keywords
            type_match = any(kw in portal_type for kw in type_keywords) if type_keywords else False

            # Return tuple: (type_match as int, confidence)
            # This prioritizes type matches first, then confidence within each group
            return (int(type_match), mapping["confidence"])

        category_mappings.sort(key=sort_key, reverse=True)

        # Return first available asset (already filtered for availability)
        if category_mappings:
            bf_asset, mapping, portal_asset = category_mappings[0]

            # If we have type keywords, only return if first asset matches them
            # Otherwise fall through to catalog search
            if type_keywords:
                portal_type_lower = portal_asset.type.lower()
                if not any(kw in portal_type_lower for kw in type_keywords):
                    # First result doesn't match type - don't settle for wrong type
                    # Fall through to catalog search instead
                    pass
                else:
                    # Matches type keywords!
                    if not portal_asset.level_restrictions:
                        print(
                            f"  ℹ️  Using unrestricted alternative: {portal_asset.type} "
                            f"for {source_asset}"
                        )
                    else:
                        print(
                            f"  ℹ️  Using map-compatible alternative: {portal_asset.type} "
                            f"for {source_asset} on {target_map}"
                        )
                    return portal_asset
            else:
                # No type keywords - return best match by category
                if not portal_asset.level_restrictions:
                    print(
                        f"  ℹ️  Using unrestricted alternative: {portal_asset.type} "
                        f"for {source_asset}"
                    )
                else:
                    print(
                        f"  ℹ️  Using map-compatible alternative: {portal_asset.type} "
                        f"for {source_asset} on {target_map}"
                    )
                return portal_asset

        # Step 2: If no mapped alternatives found, search entire Portal catalog for type matches
        if type_keywords:
            # Search all Portal assets for matching type keywords available on target map
            for portal_type, portal_asset in self.portal_assets.items():
                portal_type_lower = portal_type.lower()

                # Check if this Portal asset matches type keywords
                if any(kw in portal_type_lower for kw in type_keywords):
                    # Check if unrestricted
                    if not portal_asset.level_restrictions:
                        print(f"  ℹ️  Using catalog alternative: {portal_type} for {source_asset}")
                        return portal_asset

                    # Check if available on target map
                    if target_map in portal_asset.level_restrictions:
                        print(
                            f"  ℹ️  Using catalog alternative: {portal_type} "
                            f"for {source_asset} on {target_map}"
                        )
                        return portal_asset

        return None

    def get_mapping_info(self, source_asset: str) -> dict | None:
        """Get detailed mapping information for an asset.

        Args:
            source_asset: BF1942 asset type

        Returns:
            Mapping info dict or None if not found
        """
        return self.mappings.get(source_asset)

    def get_stats(self) -> dict:
        """Get mapping statistics.

        Returns:
            Statistics dictionary
        """
        total = len(self.mappings)
        categories: dict[str, int] = {}

        for asset, mapping in self.mappings.items():
            category = mapping["category"]
            categories[category] = categories.get(category, 0) + 1

        return {
            "total_mappings": total,
            "by_category": categories,
            "portal_assets_available": len(self.portal_assets),
        }

    def _is_terrain_element(self, source_asset: str) -> bool:
        """Check if asset is a terrain element that should be skipped.

        Terrain elements include water bodies, terrain objects, and other
        environmental features that are part of the terrain system rather
        than placeable props.

        Args:
            source_asset: BF1942 asset name

        Returns:
            True if asset is a terrain element, False otherwise
        """
        source_lower = source_asset.lower()

        # Water bodies - Portal has limited water support
        if any(kw in source_lower for kw in ["lake", "river", "ocean", "sea", "pond"]):
            print(
                f"  ℹ️  Skipping terrain element: {source_asset} "
                f"(water bodies not supported in Portal SDK)"
            )
            return True

        # Terrain objects
        if "terrain" in source_lower and "object" in source_lower:
            print(
                f"  ℹ️  Skipping terrain element: {source_asset} "
                f"(terrain reference, not a placeable object)"
            )
            return True

        return False

    def _find_best_guess_fallback(self, source_asset: str, target_map: str) -> PortalAsset | None:
        """Find best-guess fallback for asset not in mappings file.

        Uses name-based heuristics to guess asset type and find Portal equivalent.

        Args:
            source_asset: BF1942 asset name not in mappings
            target_map: Target map name

        Returns:
            PortalAsset if reasonable guess found, None otherwise
        """
        source_lower = source_asset.lower()

        # Define type keywords with category hints
        type_categories = [
            (
                ["tree", "pine", "spruce", "oak", "birch", "palm", "cedar"],
                ["tree", "pine", "spruce", "oak", "birch", "palm", "cedar"],
            ),
            (
                ["barn", "house", "building", "warehouse", "mill", "lumbermill"],
                ["barn", "house", "building", "warehouse", "shed", "hut"],
            ),
            (["sandbag", "sand"], ["sandbag", "sand", "bag"]),
            (["cart", "wagon"], ["cart", "wagon", "wheelbarrow"]),
            (["camo", "netting", "net"], ["camo", "netting", "tarp", "canopy"]),
        ]

        # Find matching type
        for source_keywords, portal_keywords in type_categories:
            if any(kw in source_lower for kw in source_keywords):
                # Search Portal catalog for matching assets
                for portal_type, portal_asset in self.portal_assets.items():
                    portal_type_lower = portal_type.lower()

                    if any(kw in portal_type_lower for kw in portal_keywords):
                        # Check if unrestricted
                        if not portal_asset.level_restrictions:
                            print(
                                f"  ℹ️  Using best-guess fallback: {portal_type} "
                                f"for unmapped {source_asset}"
                            )
                            return portal_asset

                        # Check if available on target map
                        if target_map in portal_asset.level_restrictions:
                            print(
                                f"  ℹ️  Using best-guess fallback: {portal_type} "
                                f"for unmapped {source_asset} on {target_map}"
                            )
                            return portal_asset

        # No reasonable guess found
        return None
