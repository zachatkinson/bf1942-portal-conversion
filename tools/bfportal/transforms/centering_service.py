#!/usr/bin/env python3
"""Universal centering service for Portal map conversion.

Single Responsibility: Calculate centering offsets for terrain, assets, and combat areas.
Open/Closed: Easy to extend with new centering strategies.
Dependency Inversion: Depends on abstract terrain interface, not concrete implementations.

This module provides a unified approach to centering all map elements at world origin (0, 0),
ensuring consistent positioning across all Portal terrains.
"""

from dataclasses import dataclass

from ..core.interfaces import Vector3


@dataclass
class CenteringOffsets:
    """Offsets needed to center various map elements at world origin.

    Attributes:
        terrain_offset: XYZ offset to apply to terrain node
        asset_target_center: Target center point for asset positioning
        combat_area_center: Center point for combat area boundary
    """

    terrain_offset: Vector3  # Offset to apply to terrain transform
    asset_target_center: Vector3  # Where to position assets (usually 0,0,0)
    combat_area_center: Vector3  # Where to position combat area (usually 0,0,0)


class CenteringService:
    """Service for calculating universal centering offsets.

    This service implements the "center everything at world origin" strategy,
    which works consistently across all Portal terrains without hardcoded constants.
    """

    def calculate_universal_centering(
        self,
        terrain_mesh_center_x: float,
        terrain_mesh_center_z: float,
        terrain_y_baseline: float,
    ) -> CenteringOffsets:
        """Calculate offsets to center all map elements at world origin.

        Strategy:
        1. Terrain: Offset by (-mesh_center_x, -y_baseline, -mesh_center_z)
           → Terrain's geometric center lands at world origin (0, 0)
        2. Assets: Position relative to (0, 0, 0)
           → Assets align with centered terrain
        3. CombatArea: Position at (0, 0, 0)
           → Combat boundary centered with terrain and assets

        Args:
            terrain_mesh_center_x: X coordinate of terrain mesh center
            terrain_mesh_center_z: Z coordinate of terrain mesh center
            terrain_y_baseline: Y baseline offset for terrain height normalization

        Returns:
            CenteringOffsets with terrain offset and target centers

        Example:
            >>> service = CenteringService()
            >>> offsets = service.calculate_universal_centering(
            ...     terrain_mesh_center_x=59.0,
            ...     terrain_mesh_center_z=-295.0,
            ...     terrain_y_baseline=64.8
            ... )
            >>> print(offsets.terrain_offset)
            Vector3(x=-59.0, y=-64.8, z=295.0)
            >>> print(offsets.asset_target_center)
            Vector3(x=0.0, y=0.0, z=0.0)
        """
        # Terrain offset: Negative mesh center to place center at origin
        # Y offset brings terrain's lowest point to Y=0 (Portal ground plane)
        terrain_offset = Vector3(
            x=-terrain_mesh_center_x,
            y=-terrain_y_baseline,  # Subtract baseline to normalize lowest point to Y=0
            z=-terrain_mesh_center_z,
        )

        # Asset target: World origin since terrain is centered there
        asset_target_center = Vector3(x=0.0, y=0.0, z=0.0)

        # Combat area: Also at world origin to match terrain and assets
        combat_area_center = Vector3(x=0.0, y=0.0, z=0.0)

        return CenteringOffsets(
            terrain_offset=terrain_offset,
            asset_target_center=asset_target_center,
            combat_area_center=combat_area_center,
        )

    def get_asset_target_center(self) -> Vector3:
        """Get target center for asset positioning.

        Returns world origin (0, 0, 0) since all elements are centered there.

        Returns:
            Vector3 at world origin
        """
        return Vector3(x=0.0, y=0.0, z=0.0)

    def get_combat_area_center(self) -> Vector3:
        """Get center point for combat area boundary.

        Returns world origin (0, 0, 0) since all elements are centered there.

        Returns:
            Vector3 at world origin
        """
        return Vector3(x=0.0, y=0.0, z=0.0)

    def calculate_rotated_centering(
        self,
        terrain_mesh_center_x: float,
        terrain_mesh_center_z: float,
        terrain_y_baseline: float,
        rotation_degrees: float,
    ) -> CenteringOffsets:
        """Calculate offsets for rotated terrain centering.

        When terrain rotates 90° CW around Y-axis, the mesh center coordinates
        also rotate. This method applies the rotation transformation to the
        centering offsets to ensure the rotated terrain centers at world origin.

        Strategy:
        1. Apply Y-axis rotation to mesh center coordinates
        2. Negate rotated coordinates for centering offset
        3. Maintain world origin targets for assets and combat area

        Args:
            terrain_mesh_center_x: Original X coordinate of terrain mesh center
            terrain_mesh_center_z: Original Z coordinate of terrain mesh center
            terrain_y_baseline: Y baseline offset for terrain height normalization
            rotation_degrees: Rotation angle in degrees (typically 90 or -90)

        Returns:
            CenteringOffsets with rotated terrain offset and target centers

        Example:
            >>> service = CenteringService()
            >>> # Original mesh center: (59, -295)
            >>> offsets = service.calculate_rotated_centering(
            ...     terrain_mesh_center_x=59.0,
            ...     terrain_mesh_center_z=-295.0,
            ...     terrain_y_baseline=64.8,
            ...     rotation_degrees=90
            ... )
            >>> # After 90° CW rotation: X'=Z, Z'=-X
            >>> # New center: (295, -59) → offset: (-295, 59)
            >>> print(offsets.terrain_offset)
            Vector3(x=295.0, y=-64.8, z=59.0)
        """
        import math

        # Convert rotation to radians
        rotation_rad = math.radians(rotation_degrees)
        cos_r = math.cos(rotation_rad)
        sin_r = math.sin(rotation_rad)

        # Apply Y-axis rotation to mesh center coordinates
        # Rotation matrix for Y-axis: [cos, 0, sin; 0, 1, 0; -sin, 0, cos]
        # New X = cos(θ) * old_x + sin(θ) * old_z
        # New Z = -sin(θ) * old_x + cos(θ) * old_z
        rotated_center_x = cos_r * terrain_mesh_center_x + sin_r * terrain_mesh_center_z
        rotated_center_z = -sin_r * terrain_mesh_center_x + cos_r * terrain_mesh_center_z

        # Negate rotated coordinates to center at origin
        # Y offset brings terrain's lowest point to Y=0 (Portal ground plane)
        terrain_offset = Vector3(
            x=-rotated_center_x,
            y=-terrain_y_baseline,  # Subtract baseline to normalize lowest point to Y=0
            z=-rotated_center_z,
        )

        # Assets and combat area still target world origin
        asset_target_center = Vector3(x=0.0, y=0.0, z=0.0)
        combat_area_center = Vector3(x=0.0, y=0.0, z=0.0)

        return CenteringOffsets(
            terrain_offset=terrain_offset,
            asset_target_center=asset_target_center,
            combat_area_center=combat_area_center,
        )
