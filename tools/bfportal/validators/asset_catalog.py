#!/usr/bin/env python3
"""Shared asset catalog loader for Portal asset validation.

Single Responsibility: Load and provide access to Portal asset catalog.
DRY Principle: Eliminates duplicate catalog loading across validators.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-17
"""

import json
from pathlib import Path
from typing import Any, cast

from ..generators.constants.paths import get_asset_types_path


class AssetCatalog:
    """Portal asset catalog loader and query interface.

    This class provides the Single Source of Truth for Portal asset data,
    eliminating duplicate loading logic across validation tools.

    Example:
        >>> catalog = AssetCatalog()
        >>> if catalog.has_level_restrictions("MP_Tungsten_Bunker"):
        ...     allowed = catalog.get_level_restrictions("MP_Tungsten_Bunker")
        ...     print(f"Only allowed on: {allowed}")
    """

    def __init__(self, catalog_path: Path | None = None):
        """Initialize asset catalog.

        Args:
            catalog_path: Optional path to asset_types.json (default: auto-detect)
        """
        self.catalog_path = catalog_path or get_asset_types_path()
        self._catalog: dict[str, dict[str, Any]] = {}
        self._load_catalog()

    def _load_catalog(self) -> None:
        """Load asset catalog from JSON file.

        Raises:
            FileNotFoundError: If catalog file doesn't exist
            json.JSONDecodeError: If catalog file is invalid JSON
        """
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Asset catalog not found: {self.catalog_path}")

        with open(self.catalog_path, encoding="utf-8") as f:
            data = json.load(f)

        # Build indexed catalog for fast lookup
        for asset in data.get("AssetTypes", []):
            asset_type = asset.get("type")
            if asset_type:
                self._catalog[asset_type] = {
                    "directory": asset.get("directory", ""),
                    "level_restrictions": asset.get("levelRestrictions", []),
                    "constants": asset.get("constants", []),
                    "properties": asset.get("properties", []),
                }

    def get_asset(self, asset_type: str) -> dict[str, Any] | None:
        """Get asset data by type.

        Args:
            asset_type: Asset type name (e.g., "MP_Tungsten_Bunker")

        Returns:
            Asset data dictionary or None if not found
        """
        return self._catalog.get(asset_type)

    def has_asset(self, asset_type: str) -> bool:
        """Check if asset exists in catalog.

        Args:
            asset_type: Asset type name

        Returns:
            True if asset exists in catalog
        """
        return asset_type in self._catalog

    def get_level_restrictions(self, asset_type: str) -> list[str]:
        """Get level restrictions for an asset.

        Args:
            asset_type: Asset type name

        Returns:
            List of allowed map names, or empty list if no restrictions
        """
        asset = self.get_asset(asset_type)
        if asset:
            return cast(list[str], asset.get("level_restrictions", []))
        return []

    def has_level_restrictions(self, asset_type: str) -> bool:
        """Check if asset has level restrictions.

        Args:
            asset_type: Asset type name

        Returns:
            True if asset has level restrictions
        """
        restrictions = self.get_level_restrictions(asset_type)
        return len(restrictions) > 0

    def is_allowed_on_map(self, asset_type: str, map_name: str) -> bool:
        """Check if asset is allowed on a specific map.

        Args:
            asset_type: Asset type name
            map_name: Portal map name (e.g., "MP_Tungsten")

        Returns:
            True if asset is allowed on map (no restrictions or map in allowed list)
        """
        restrictions = self.get_level_restrictions(asset_type)
        # No restrictions = allowed everywhere
        if not restrictions:
            return True
        # Has restrictions = only allowed on specified maps
        return map_name in restrictions

    def get_asset_count(self) -> int:
        """Get total number of assets in catalog.

        Returns:
            Number of assets
        """
        return len(self._catalog)

    def get_all_asset_types(self) -> list[str]:
        """Get list of all asset types in catalog.

        Returns:
            List of asset type names
        """
        return list(self._catalog.keys())
