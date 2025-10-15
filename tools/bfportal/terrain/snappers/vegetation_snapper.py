#!/usr/bin/env python3
"""Vegetation snapper for trees, plants, and natural objects.

Handles all vegetation types with appropriate ground contact.
"""

from .base_snapper import IObjectSnapper, ITerrainProvider, SnapResult


class VegetationSnapper(IObjectSnapper):
    """Snaps vegetation objects (trees, plants, bushes) to terrain.

    Height Rules:
    - All vegetation sits directly on terrain (offset: 0m)
    - Roots/base should touch ground naturally

    Single Responsibility: Only handles vegetation snapping.
    """

    # Common vegetation asset name patterns
    VEGETATION_PATTERNS = [
        "tree",
        "birch",
        "oak",
        "pine",
        "spruce",
        "bush",
        "shrub",
        "plant",
        "grass",
        "fern",
        "flower",
        "weed",
        "palm",
        "cactus",
    ]

    def __init__(self, terrain: ITerrainProvider):
        """Initialize vegetation snapper.

        Args:
            terrain: Terrain provider for height queries
        """
        super().__init__(terrain)

    def can_snap(self, node_name: str, asset_type: str | None = None) -> bool:
        """Check if this is a vegetation object.

        Args:
            node_name: Node name from .tscn
            asset_type: Optional asset type for pattern matching

        Returns:
            True if this is vegetation
        """
        # Check node name and asset type against vegetation patterns
        name_lower = node_name.lower()
        asset_lower = asset_type.lower() if asset_type else ""

        for pattern in self.VEGETATION_PATTERNS:
            if pattern in name_lower or pattern in asset_lower:
                return True

        return False

    def _sample_terrain_multipoint(self, x: float, z: float, sample_radius: float = 1.5) -> float:
        """Sample terrain at tree base to prevent sinking on slopes.

        Args:
            x: Center X position
            z: Center Z position
            sample_radius: Radius around tree trunk (default: 1.5m)

        Returns:
            Minimum terrain height from sample points
        """
        # Sample 5 points: center + 4 cardinal directions around trunk
        sample_points = [
            (x, z),  # Center (trunk)
            (x - sample_radius, z),  # West
            (x + sample_radius, z),  # East
            (x, z - sample_radius),  # South
            (x, z + sample_radius),  # North
        ]

        heights = []
        for sx, sz in sample_points:
            try:
                h = self.terrain.get_height_at(sx, sz)
                heights.append(h)
            except Exception:
                continue

        if not heights:
            return self.terrain.get_height_at(x, z)

        # Return minimum height (prevents sinking)
        return min(heights)

    def calculate_snapped_height(
        self, x: float, z: float, current_y: float, node_name: str
    ) -> SnapResult:
        """Calculate appropriate height for vegetation.

        Uses multi-point sampling around the tree trunk to prevent
        sinking into slopes.

        Args:
            x: Object X position
            z: Object Z position
            current_y: Current Y position
            node_name: Node name for logging

        Returns:
            SnapResult with snapped height
        """
        try:
            # Multi-point sample around tree base (prevents sinking on slopes)
            terrain_height = self._sample_terrain_multipoint(x, z, sample_radius=1.5)

            # Vegetation sits directly on terrain
            snapped_y = terrain_height

            # Check if adjustment is significant (>0.1m)
            was_adjusted = abs(snapped_y - current_y) > 0.1

            return SnapResult(
                original_y=current_y,
                snapped_y=snapped_y,
                was_adjusted=was_adjusted,
                reason="Vegetation (1.5m radius sampled)",
            )

        except Exception as e:
            # Out of bounds or query failed - keep original
            return SnapResult(
                original_y=current_y,
                snapped_y=current_y,
                was_adjusted=False,
                reason=f"Query failed: {e}",
            )

    def get_category_name(self) -> str:
        """Get category name for logging.

        Returns:
            "Vegetation"
        """
        return "Vegetation"
