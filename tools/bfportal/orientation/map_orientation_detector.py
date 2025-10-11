#!/usr/bin/env python3
"""Map orientation detector for source maps.

Single Responsibility: Only detects orientation of source map data.
"""

from typing import List, Tuple

from ..core.interfaces import MapData, Vector3
from .interfaces import IOrientationDetector, Orientation, OrientationAnalysis


class MapOrientationDetector(IOrientationDetector):
    """Detects orientation of source map by analyzing object distribution.

    Single Responsibility: Only analyzes map object positions to determine orientation.
    Open/Closed: Can be extended for different analysis strategies without modification.
    """

    def __init__(self, map_data: MapData, threshold: float = 1.2):
        """Initialize detector.

        Args:
            map_data: Parsed map data with objects
            threshold: Ratio threshold to determine orientation (default 1.2)
                      If width/depth > threshold, considered oriented along that axis
        """
        self.map_data = map_data
        self.threshold = threshold

    def detect_orientation(self) -> OrientationAnalysis:
        """Detect map orientation by analyzing object distribution.

        Returns:
            OrientationAnalysis with detected orientation
        """
        # Get all object positions
        positions = self._collect_positions()

        if not positions:
            # No objects - assume square
            return OrientationAnalysis(
                orientation=Orientation.SQUARE,
                width_x=0,
                depth_z=0,
                ratio=1.0,
                confidence='low'
            )

        # Calculate bounds
        min_x, max_x, min_z, max_z = self.get_bounds()

        width_x = max_x - min_x
        depth_z = max_z - min_z

        # Avoid division by zero
        if width_x == 0 or depth_z == 0:
            return OrientationAnalysis(
                orientation=Orientation.SQUARE,
                width_x=width_x,
                depth_z=depth_z,
                ratio=1.0,
                confidence='low'
            )

        # Calculate ratio (always >= 1.0)
        if width_x > depth_z:
            ratio = width_x / depth_z
            orientation = Orientation.EAST_WEST if ratio >= self.threshold else Orientation.SQUARE
        else:
            ratio = depth_z / width_x
            orientation = Orientation.NORTH_SOUTH if ratio >= self.threshold else Orientation.SQUARE

        # Determine confidence based on ratio
        if ratio >= 1.5:
            confidence = 'high'
        elif ratio >= self.threshold:
            confidence = 'medium'
        else:
            confidence = 'low'

        return OrientationAnalysis(
            orientation=orientation,
            width_x=width_x,
            depth_z=depth_z,
            ratio=ratio,
            confidence=confidence
        )

    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get bounding box of all map objects.

        Returns:
            Tuple of (min_x, max_x, min_z, max_z)
        """
        positions = self._collect_positions()

        if not positions:
            return (0, 0, 0, 0)

        min_x = min(p.x for p in positions)
        max_x = max(p.x for p in positions)
        min_z = min(p.z for p in positions)
        max_z = max(p.z for p in positions)

        return (min_x, max_x, min_z, max_z)

    def _collect_positions(self) -> List[Vector3]:
        """Collect all object positions from map data.

        Single Responsibility: Only collects positions.

        Returns:
            List of Vector3 positions
        """
        positions = []

        # Spawns
        for spawn in self.map_data.team1_spawns:
            positions.append(spawn.transform.position)
        for spawn in self.map_data.team2_spawns:
            positions.append(spawn.transform.position)

        # Capture points
        for cp in self.map_data.capture_points:
            positions.append(cp.transform.position)

        # Game objects
        for obj in self.map_data.game_objects:
            positions.append(obj.transform.position)

        return positions
