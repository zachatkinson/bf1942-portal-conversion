#!/usr/bin/env python3
"""Gameplay object snapper.

Handles HQs, spawn points, and capture points.
These objects have specific gameplay requirements for height placement.
"""

from .base_snapper import IObjectSnapper, ITerrainProvider, SnapResult


class GameplaySnapper(IObjectSnapper):
    """Snaps gameplay objects (HQs, spawns, capture points) to terrain.

    Height Rules:
    - HQs: At terrain surface (offset: 0m)
    - Spawn points: 1m above terrain (clearance for player spawn)
    - Capture points: At terrain surface (offset: 0m)

    Single Responsibility: Only handles gameplay object snapping.
    """

    def __init__(self, terrain: ITerrainProvider):
        """Initialize gameplay snapper.

        Args:
            terrain: Terrain provider for height queries
        """
        super().__init__(terrain)

    def can_snap(self, node_name: str, asset_type: str | None = None) -> bool:
        """Check if this is a gameplay object.

        Args:
            node_name: Node name from .tscn
            asset_type: Optional asset type (unused for gameplay objects)

        Returns:
            True if this is a gameplay object (HQ, spawn, capture point)
        """
        # HQ nodes
        if "TEAM_" in node_name and "_HQ" in node_name:
            return True

        # Spawn points (both HQ spawns and capture point spawns)
        if "SpawnPoint" in node_name or "Spawn_" in node_name:
            return True

        # Capture points
        return "CapturePoint" in node_name

    def calculate_snapped_height(
        self, x: float, z: float, current_y: float, node_name: str
    ) -> SnapResult:
        """Calculate appropriate height for gameplay object.

        Args:
            x: Object X position
            z: Object Z position
            current_y: Current Y position
            node_name: Node name for determining offset

        Returns:
            SnapResult with snapped height
        """
        try:
            terrain_height = self.terrain.get_height_at(x, z)

            # Determine offset based on object type
            if "SpawnPoint" in node_name or "Spawn_" in node_name:
                # Spawns need 1m clearance for player spawn
                offset = 1.0
                reason = "Spawn point (1m clearance)"
            else:
                # HQs and capture points sit on terrain
                offset = 0.0
                reason = "Gameplay object (at terrain)"

            snapped_y = terrain_height + offset

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
            "Gameplay"
        """
        return "Gameplay"
