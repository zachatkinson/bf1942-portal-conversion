#!/usr/bin/env python3
"""Generic prop snapper for rocks, crates, barrels, and misc objects.

Handles all non-gameplay, non-vegetation objects.
"""

from .base_snapper import IObjectSnapper, ITerrainProvider, SnapResult


class PropSnapper(IObjectSnapper):
    """Snaps generic props (rocks, crates, barrels, etc.) to terrain.

    Height Rules:
    - Most props sit directly on terrain (offset: 0m)
    - Some props (like water bodies, decals) may need custom handling

    Single Responsibility: Only handles prop/decoration snapping.
    """

    # Prop patterns that should NOT be snapped (stay at their current height)
    SKIP_PATTERNS = [
        "decal_puddle",  # Water decals stay at waterLevel
        "lake_",  # Water bodies
        "water_",  # Water effects
    ]

    def __init__(self, terrain: ITerrainProvider):
        """Initialize prop snapper.

        Args:
            terrain: Terrain provider for height queries
        """
        super().__init__(terrain)

    def can_snap(self, node_name: str, asset_type: str | None = None) -> bool:
        """Check if this is a generic prop.

        This is a catch-all snapper - it handles everything that other
        snappers don't handle.

        Args:
            node_name: Node name from .tscn
            asset_type: Optional asset type

        Returns:
            True for most objects (this is the default snapper)
        """
        # Skip special objects that shouldn't be terrain-snapped
        name_lower = node_name.lower()
        asset_lower = asset_type.lower() if asset_type else ""

        for pattern in self.SKIP_PATTERNS:
            if pattern in name_lower or pattern in asset_lower:
                return False

        # This is a catch-all snapper - handles everything else
        return True

    # Patterns for large objects that need multi-point sampling
    LARGE_OBJECT_PATTERNS = [
        "building",
        "bunker",
        "hangar",
        "barracks",
        "house",
        "warehouse",
        "factory",
    ]

    def _is_large_object(self, node_name: str) -> bool:
        """Check if object is large and needs multi-point sampling.

        Args:
            node_name: Node name

        Returns:
            True if this is a large building/structure
        """
        name_lower = node_name.lower()
        return any(pattern in name_lower for pattern in self.LARGE_OBJECT_PATTERNS)

    def _sample_terrain_multipoint(self, x: float, z: float, sample_radius: float = 10.0) -> float:
        """Sample terrain at multiple points and return minimum height.

        This prevents large buildings from sinking into terrain on slopes.

        Args:
            x: Center X position
            z: Center Z position
            sample_radius: Radius to sample around center (default: 10m)

        Returns:
            Minimum terrain height from all sample points
        """
        # Sample 5 points: center + 4 corners of a square
        sample_points = [
            (x, z),  # Center
            (x - sample_radius, z - sample_radius),  # SW corner
            (x + sample_radius, z - sample_radius),  # SE corner
            (x + sample_radius, z + sample_radius),  # NE corner
            (x - sample_radius, z + sample_radius),  # NW corner
        ]

        heights = []
        for sx, sz in sample_points:
            try:
                h = self.terrain.get_height_at(sx, sz)
                heights.append(h)
            except Exception:
                # Skip points that fail (out of bounds)
                continue

        if not heights:
            # All samples failed - fall back to center point
            return self.terrain.get_height_at(x, z)

        # Return minimum height (prevents sinking)
        return min(heights)

    def calculate_snapped_height(
        self, x: float, z: float, current_y: float, node_name: str
    ) -> SnapResult:
        """Calculate appropriate height for prop.

        For large objects (buildings), samples multiple terrain points
        to find the lowest ground height, preventing sinking on slopes.

        Args:
            x: Object X position
            z: Object Z position
            current_y: Current Y position
            node_name: Node name for logging

        Returns:
            SnapResult with snapped height
        """
        # Check if this is a special object that should keep its height
        name_lower = node_name.lower()
        for pattern in self.SKIP_PATTERNS:
            if pattern in name_lower:
                return SnapResult(
                    original_y=current_y,
                    snapped_y=current_y,
                    was_adjusted=False,
                    reason=f"Skipped ({pattern} pattern)",
                )

        try:
            # ALL objects benefit from multi-point sampling on uneven terrain
            # Adjust sample radius based on object size
            if self._is_large_object(node_name):
                # Large buildings: sample 10m radius
                terrain_height = self._sample_terrain_multipoint(x, z, sample_radius=10.0)
                # Add small upward offset for large buildings to prevent edge clipping
                terrain_height += 0.2
                reason = "Large object (10m radius sampled)"
            else:
                # Small props/crates: sample 2m radius (prevents sinking on slopes)
                terrain_height = self._sample_terrain_multipoint(x, z, sample_radius=2.0)
                reason = "Prop (2m radius sampled)"

            snapped_y = terrain_height

            # Check if adjustment is significant (>0.1m)
            was_adjusted = abs(snapped_y - current_y) > 0.1

            return SnapResult(
                original_y=current_y,
                snapped_y=snapped_y,
                was_adjusted=was_adjusted,
                reason=reason,
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
            "Props"
        """
        return "Props"
