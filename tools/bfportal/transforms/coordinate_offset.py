#!/usr/bin/env python3
"""Coordinate offset calculator for map re-centering."""

from typing import List

from ..core.interfaces import ICoordinateOffset, GameObject, Transform, Vector3


class CoordinateOffset(ICoordinateOffset):
    """Calculates and applies coordinate offsets to re-center maps.

    Used when converting BF1942 maps to Portal base maps, or when switching
    between different Portal base terrains.
    """

    def calculate_centroid(self, objects: List[GameObject]) -> Vector3:
        """Calculate the centroid (center of mass) of all objects.

        Args:
            objects: List of game objects

        Returns:
            Centroid position

        Note:
            Only uses X and Z coordinates. Y (height) is handled separately.
        """
        if not objects:
            return Vector3(0, 0, 0)

        total_x = 0.0
        total_z = 0.0
        count = 0

        for obj in objects:
            total_x += obj.transform.position.x
            total_z += obj.transform.position.z
            count += 1

        avg_x = total_x / count
        avg_z = total_z / count

        # Y coordinate is average for reference, but not used for offset
        total_y = sum(obj.transform.position.y for obj in objects)
        avg_y = total_y / count

        return Vector3(avg_x, avg_y, avg_z)

    def calculate_offset(self, source_center: Vector3, target_center: Vector3) -> Vector3:
        """Calculate offset vector between two map centers.

        Args:
            source_center: Center of source map
            target_center: Center of target Portal base map

        Returns:
            Offset vector to apply to all objects
        """
        return Vector3(
            target_center.x - source_center.x,
            0,  # Don't offset Y, handle via terrain adjustment
            target_center.z - source_center.z
        )

    def apply_offset(self, transform: Transform, offset: Vector3) -> Transform:
        """Apply offset to a transform.

        Args:
            transform: Original transform
            offset: Offset vector

        Returns:
            New transform with offset applied (original unchanged)
        """
        new_position = Vector3(
            transform.position.x + offset.x,
            transform.position.y + offset.y,  # Usually 0
            transform.position.z + offset.z
        )

        # Return new transform, preserving rotation and scale
        return Transform(
            position=new_position,
            rotation=transform.rotation,
            scale=transform.scale
        )

    def apply_scale(self, transform: Transform, scale_factor: float) -> Transform:
        """Apply scale factor to a transform (for large→small map conversions).

        Args:
            transform: Original transform
            scale_factor: Scale multiplier (e.g., 0.5 to shrink 50%)

        Returns:
            Scaled transform
        """
        new_position = Vector3(
            transform.position.x * scale_factor,
            transform.position.y,  # Don't scale height
            transform.position.z * scale_factor
        )

        return Transform(
            position=new_position,
            rotation=transform.rotation,
            scale=transform.scale
        )
