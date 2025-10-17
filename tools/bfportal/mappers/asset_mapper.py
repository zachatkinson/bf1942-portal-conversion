#!/usr/bin/env python3
"""Asset mapper implementation using the BF1942 → Portal lookup table."""

import json
from pathlib import Path

from ..core.exceptions import MappingError
from ..core.interfaces import IAssetMapper, MapContext, PortalAsset
from ..generators.constants.paths import get_project_root


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
        self.fallback_keywords: list[dict] = []

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

        # Load keyword fallback config for best-guess asset matching
        keywords_path = (
            get_project_root() / "tools" / "asset_audit" / "asset_fallback_keywords.json"
        )
        if keywords_path.exists():
            with open(keywords_path) as f:
                data = json.load(f)
                self.fallback_keywords = data.get("type_categories", [])

    def load_mappings(self, mappings_file: Path) -> None:
        """Load BF1942 → Portal mappings from JSON file.

        Supports both nested (category-based) and flat (top-level) asset structures.

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

        # Flatten category-based structure and top-level assets into single lookup dict
        for key in data:
            if key == "_metadata":
                continue

            value = data[key]
            if not isinstance(value, dict):
                continue

            # Check if this is an asset (has bf1942_type) or a category (contains assets)
            if "bf1942_type" in value:
                # This is a TOP-LEVEL ASSET (e.g., Afri_bush1_M1)
                asset_type = key
                asset_info = value
                portal_eq = asset_info.get("portal_equivalent")
                if portal_eq and portal_eq != "TODO":
                    alternatives = asset_info.get("alternatives", [])
                    fallbacks = asset_info.get("fallbacks", {})

                    self.mappings[asset_type] = {
                        "portal_type": portal_eq,
                        "alternatives": alternatives,
                        "category": asset_info.get("category", "unknown"),
                        "confidence": asset_info.get("confidence_score", 1.0),
                        "notes": asset_info.get("notes", ""),
                        "fallbacks": fallbacks,
                    }
            else:
                # This is a CATEGORY containing nested assets (e.g., "vehicles", "props")
                category = value
                for asset_type, asset_info in category.items():
                    if not isinstance(asset_info, dict):
                        continue

                    portal_eq = asset_info.get("portal_equivalent")
                    if portal_eq and portal_eq != "TODO":
                        alternatives = asset_info.get("alternatives", [])
                        fallbacks = asset_info.get("fallbacks", {})

                        self.mappings[asset_type] = {
                            "portal_type": portal_eq,
                            "alternatives": alternatives,
                            "category": asset_info.get("category", "unknown"),
                            "confidence": asset_info.get("confidence_score", 1.0),
                            "notes": asset_info.get("notes", ""),
                            "fallbacks": fallbacks,
                        }

        print(f"✅ Loaded {len(self.mappings)} asset mappings from {mappings_file.name}")

    def map_asset(self, source_asset: str, context: MapContext) -> PortalAsset | None:
        """Map BF1942 asset to Portal equivalent using preferred + alternatives cascade.

        New Logic (preferred + alternatives):
        1. Try preferred asset (portal_equivalent)
        2. If unavailable, try explicit alternatives[] in order
        3. If none work, try legacy fallbacks{} system
        4. If still none, try category search
        5. If all fail, try best-guess

        Args:
            source_asset: BF1942 asset type name
            context: Context for mapping decisions

        Returns:
            PortalAsset if mapping found and compatible, None otherwise

        Raises:
            MappingError: If mapping exists but no compatible asset found
        """
        # Normalize asset name: Try exact match first, then lowercase
        # BF1942 has inconsistent casing (artilleryspawner vs ArtillerySpawner)
        asset_key = source_asset
        if source_asset not in self.mappings:
            # Try case-insensitive lookup
            source_lower = source_asset.lower()
            for key in self.mappings:
                if key.lower() == source_lower:
                    asset_key = key
                    break

        # Check if we have a mapping (do this BEFORE terrain element check)
        # This allows us to map water bodies like lakes to crater decals
        if asset_key not in self.mappings:
            # Check if this is a terrain element that should be skipped
            if self._is_terrain_element(source_asset):
                return None  # Skip unmapped terrain elements

            # Asset not in mappings file - try best-guess fallback
            return self._find_best_guess_fallback(source_asset, context.target_base_map)

        mapping = self.mappings[asset_key]
        target_map = context.target_base_map

        # Build cascade of assets to try (preferred → alternatives → fallbacks)
        assets_to_try = []

        # 1. Preferred asset (primary mapping)
        preferred = mapping["portal_type"]
        assets_to_try.append(("preferred", preferred))

        # 2. Explicit alternatives (new format)
        for alt in mapping.get("alternatives", []):
            assets_to_try.append(("alternative", alt))

        # 3. Map-specific fallback (legacy format)
        fallbacks = mapping.get("fallbacks", {})
        if target_map in fallbacks:
            fallback = fallbacks[target_map]
            if fallback not in [preferred] + mapping.get("alternatives", []):
                assets_to_try.append(("fallback", fallback))

        # Try each asset in cascade order
        for asset_type_label, portal_type in assets_to_try:
            # Check if asset exists in catalog
            if portal_type not in self.portal_assets:
                continue

            portal_asset = self.portal_assets[portal_type]

            # Check if available on target map
            if self._is_asset_available_on_map(portal_asset, target_map):
                # Found a match!
                if asset_type_label != "preferred":
                    print(
                        f"  🔄 Using {asset_type_label}: {portal_type} "
                        f"for {source_asset} on {target_map}"
                    )
                return portal_asset

        # No explicit mapping worked - try category search as last resort
        alternative = self._find_alternative(source_asset, mapping["category"], target_map)
        if alternative:
            return alternative

        # Still nothing - try best-guess
        best_guess = self._find_best_guess_fallback(source_asset, target_map)
        if best_guess:
            return best_guess

        # Complete failure - no compatible asset found
        raise MappingError(
            f"No compatible Portal asset found for '{source_asset}' on '{target_map}'. "
            f"Tried: {', '.join([t for _, t in assets_to_try])}. "
            f"Check asset availability and add alternatives to mappings file."
        )

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
        # Get type keywords from config
        _source_keywords, portal_keywords = self._get_type_keywords(source_asset)

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
            if self._is_asset_available_on_map(portal_asset, target_map):
                category_mappings.append((bf_asset, mapping, portal_asset))

        # Sort by: 1) matching type keywords, 2) confidence score
        def sort_key(item):
            bf_asset, mapping, portal_asset = item
            portal_type = mapping["portal_type"].lower()

            # Check if portal asset matches any type keywords
            type_match = (
                any(kw in portal_type for kw in portal_keywords) if portal_keywords else False
            )

            # Return tuple: (type_match as int, confidence)
            # This prioritizes type matches first, then confidence within each group
            return (int(type_match), mapping["confidence"])

        category_mappings.sort(key=sort_key, reverse=True)

        # Return first available asset (already filtered for availability)
        if category_mappings:
            bf_asset, mapping, portal_asset = category_mappings[0]

            # If we have type keywords, only return if first asset matches them
            # Otherwise fall through to catalog search
            if portal_keywords:
                portal_type_lower = portal_asset.type.lower()
                if not any(kw in portal_type_lower for kw in portal_keywords):
                    # First result doesn't match type - don't settle for wrong type
                    # Fall through to catalog search instead
                    pass
                else:
                    # Matches type keywords!
                    self._print_alternative_message(portal_asset, source_asset, target_map)
                    return portal_asset
            else:
                # No type keywords - return best match by category
                self._print_alternative_message(portal_asset, source_asset, target_map)
                return portal_asset

        # Step 2: If no mapped alternatives found, search entire Portal catalog for type matches
        if portal_keywords:
            # Search all Portal assets for matching type keywords available on target map
            for portal_type, portal_asset in self.portal_assets.items():
                portal_type_lower = portal_type.lower()

                # Check if this Portal asset matches type keywords
                if any(
                    kw in portal_type_lower for kw in portal_keywords
                ) and self._is_asset_available_on_map(portal_asset, target_map):
                    print(f"  ℹ️  Using catalog alternative: {portal_type} for {source_asset}")
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

        for _asset, mapping in self.mappings.items():
            category = mapping["category"]
            categories[category] = categories.get(category, 0) + 1

        return {
            "total_mappings": total,
            "by_category": categories,
            "portal_assets_available": len(self.portal_assets),
        }

    def _is_asset_available_on_map(self, portal_asset: PortalAsset, target_map: str) -> bool:
        """Check if Portal asset is available on target map.

        Args:
            portal_asset: Portal asset to check
            target_map: Target map name (e.g., 'MP_Tungsten')

        Returns:
            True if asset is unrestricted OR available on target map

        Note:
            DRY helper - eliminates repeated availability checking logic.
        """
        return not portal_asset.level_restrictions or target_map in portal_asset.level_restrictions

    def _get_type_keywords(self, source_asset: str) -> tuple[list[str], list[str]]:
        """Get source and Portal keywords for asset type matching.

        Uses the loaded fallback_keywords config to determine what type of
        asset this is based on its name, then returns appropriate keywords
        for searching Portal assets.

        Args:
            source_asset: BF1942 asset name

        Returns:
            Tuple of (source_keywords, portal_keywords). Both lists are empty
            if no matching category found.

        Note:
            DRY helper - eliminates keyword logic duplication between
            _find_alternative() and _find_best_guess_fallback().
        """
        source_lower = source_asset.lower()

        # Search loaded config for matching category
        for category in self.fallback_keywords:
            source_kw = category.get("source_keywords", [])
            if any(kw in source_lower for kw in source_kw):
                portal_kw = category.get("portal_keywords", [])
                return (source_kw, portal_kw)

        # No matching category
        return ([], [])

    def _print_alternative_message(
        self, portal_asset: PortalAsset, source_asset: str, target_map: str
    ) -> None:
        """Print message about using alternative asset.

        Args:
            portal_asset: The alternative Portal asset being used
            source_asset: Original BF1942 asset name
            target_map: Target map name

        Note:
            DRY helper - eliminates repeated print logic.
        """
        if not portal_asset.level_restrictions:
            print(f"  ℹ️  Using unrestricted alternative: {portal_asset.type} for {source_asset}")
        else:
            print(
                f"  ℹ️  Using map-compatible alternative: {portal_asset.type} "
                f"for {source_asset} on {target_map}"
            )

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

        Uses name-based heuristics from config to guess asset type and find
        Portal equivalent.

        Args:
            source_asset: BF1942 asset name not in mappings
            target_map: Target map name

        Returns:
            PortalAsset if reasonable guess found, None otherwise
        """
        # Get type keywords from config
        _source_keywords, portal_keywords = self._get_type_keywords(source_asset)

        # If we matched a category, search Portal catalog
        if portal_keywords:
            for portal_type, portal_asset in self.portal_assets.items():
                portal_type_lower = portal_type.lower()

                if any(
                    kw in portal_type_lower for kw in portal_keywords
                ) and self._is_asset_available_on_map(portal_asset, target_map):
                    print(
                        f"  ℹ️  Using best-guess fallback: {portal_type} for unmapped {source_asset}"
                    )
                    return portal_asset

        # No reasonable guess found
        return None
