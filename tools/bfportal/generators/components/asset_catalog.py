#!/usr/bin/env python3
"""Asset catalog for querying Portal asset metadata.

Single Responsibility: Load and query Portal asset information.
"""

import json
from pathlib import Path

from ..constants.paths import get_asset_types_path, get_godot_project_dir


class AssetCatalog:
    """Provides access to Portal asset metadata.

    This class loads asset_types.json once and provides efficient
    lookups for asset properties like directory paths and level restrictions.
    """

    def __init__(self, catalog_path: Path | None = None):
        """Initialize catalog.

        Args:
            catalog_path: Path to asset_types.json (defaults to SDK location)
        """
        self.catalog: dict[str, dict] = {}
        self._load_catalog(catalog_path)

    def _load_catalog(self, catalog_path: Path | None) -> None:
        """Load Portal asset catalog from asset_types.json.

        Args:
            catalog_path: Path to catalog, or None to use default location
        """
        if catalog_path is None:
            # Default: FbExportData/asset_types.json from project root
            catalog_path = get_asset_types_path()

        if not catalog_path.exists():
            print(f"⚠️  Warning: asset_types.json not found at {catalog_path}")
            return

        try:
            with open(catalog_path) as f:
                data = json.load(f)
                for asset in data.get("AssetTypes", []):
                    asset_type = asset.get("type")
                    if asset_type:
                        self.catalog[asset_type] = {
                            "directory": asset.get("directory", ""),
                            "level_restrictions": asset.get("levelRestrictions", []),
                        }
        except Exception as e:
            print(f"⚠️  Warning: Failed to load asset catalog: {e}")

    def get_directory(self, asset_type: str) -> str | None:
        """Get directory path for an asset type.

        Args:
            asset_type: Asset type name (e.g., "Birch_01_L")

        Returns:
            Directory path (e.g., "Nature") or None if not found
        """
        if asset_type in self.catalog:
            directory: str = self.catalog[asset_type]["directory"]
            return directory
        return None

    def get_level_restrictions(self, asset_type: str) -> list[str]:
        """Get level restrictions for an asset type.

        Args:
            asset_type: Asset type name

        Returns:
            List of allowed map names, or empty list if unrestricted
        """
        if asset_type in self.catalog:
            restrictions: list[str] = self.catalog[asset_type]["level_restrictions"]
            return restrictions
        return []

    def is_available_on_terrain(self, asset_type: str, terrain: str) -> bool:
        """Check if asset is available on a specific terrain.

        Args:
            asset_type: Asset type name
            terrain: Terrain name (e.g., "MP_Tungsten")

        Returns:
            True if asset has no restrictions OR terrain is in allowed list
        """
        restrictions = self.get_level_restrictions(asset_type)
        return not restrictions or terrain in restrictions

    def get_scene_path(self, asset_type: str, base_terrain: str) -> str | None:
        """Get Godot scene path for an asset type.

        Args:
            asset_type: Asset type name (e.g., "Birch_01_L")
            base_terrain: Base terrain name (e.g., "MP_Tungsten")

        Returns:
            Scene path (e.g., "res://objects/.../Birch_01_L.tscn") or None

        Note:
            Portal SDK structure varies by terrain. This method tries
            multiple path patterns to find the correct location.
        """
        directory = self.get_directory(asset_type)
        if not directory:
            return None

        # Portal SDK structure:
        # - Map-specific: res://objects/<Region>/<Terrain>/directory/asset.tscn
        # - Shared: res://objects/Shared/directory/asset.tscn
        # - Generic: res://objects/<Region>/<Terrain>/Generic/directory/asset.tscn

        # Map terrain to region (auto-discovered from filesystem)
        terrain_regions = {
            "MP_Tungsten": "Tajikistan",
            "MP_Dumbo": "Tajikistan",
            "MP_Capstone": "Tajikistan",
            "MP_FireStorm": "Turkmenistan",
            "MP_Outskirts": "Cairo",
            "MP_Battery": "Brooklyn",
            "MP_Aftermath": "Brooklyn",
            "MP_Limestone": "Gibraltar",
            "MP_Abbasid": "Cairo",  # Guess based on Middle East theme
        }

        region = terrain_regions.get(base_terrain)

        # Build path list dynamically based on region
        paths_to_try = []

        if region:
            # Try region-specific paths first
            paths_to_try.extend(
                [
                    f"res://objects/{region}/{base_terrain}/Generic/{directory}/{asset_type}.tscn",
                    f"res://objects/{region}/{base_terrain}/Generic/Common/{directory}/{asset_type}.tscn",
                    f"res://objects/{region}/{base_terrain}/{directory}/{asset_type}.tscn",
                ]
            )

        # Then try shared/global paths (work for all terrains)
        paths_to_try.extend(
            [
                f"res://objects/Shared/Generic/{directory}/{asset_type}.tscn",
                f"res://objects/Shared/Generic/Common/{directory}/{asset_type}.tscn",
                f"res://objects/Shared/{directory}/{asset_type}.tscn",
                f"res://objects/Global/{directory}/{asset_type}.tscn",
            ]
        )

        # Check which path actually exists on disk
        godot_project = get_godot_project_dir()
        for res_path in paths_to_try:
            fs_path = godot_project / res_path.replace("res://", "")
            if fs_path.exists():
                return res_path

        # If none exist, return first option (will error in Godot but structure is correct)
        return paths_to_try[0]

    def find_assets_by_keyword(
        self, keyword: str, terrain: str | None = None, limit: int = 10
    ) -> list[str]:
        """Find assets matching a keyword.

        Args:
            keyword: Keyword to search for (case-insensitive)
            terrain: Optional terrain filter
            limit: Maximum number of results

        Returns:
            List of matching asset type names
        """
        keyword_lower = keyword.lower()
        matches = []

        for asset_type in self.catalog:
            if keyword_lower in asset_type.lower() and (
                terrain is None or self.is_available_on_terrain(asset_type, terrain)
            ):
                matches.append(asset_type)
                if len(matches) >= limit:
                    break

        return matches

    def get_stats(self) -> dict:
        """Get catalog statistics.

        Returns:
            Dict with total assets count and other metadata
        """
        return {
            "total_assets": len(self.catalog),
            "restricted_assets": sum(
                1 for asset in self.catalog.values() if asset["level_restrictions"]
            ),
        }
