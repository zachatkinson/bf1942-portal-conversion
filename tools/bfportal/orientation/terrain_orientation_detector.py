#!/usr/bin/env python3
"""Terrain orientation detector for Portal terrains.

Single Responsibility: Only detects orientation of Portal terrain heightmaps.
"""

from pathlib import Path

from ..terrain.terrain_provider import ITerrainProvider
from .interfaces import IOrientationDetector, Orientation, OrientationAnalysis


class TerrainOrientationDetector(IOrientationDetector):
    """Detects orientation of Portal terrain by analyzing heightmap variation.

    Single Responsibility: Only analyzes terrain heightmap to determine orientation.
    Dependency Inversion: Depends on ITerrainProvider abstraction.
    """

    def __init__(
        self,
        terrain_provider: ITerrainProvider | None = None,
        heightmap_path: Path | None = None,
        terrain_size: tuple[float, float] = (2048.0, 2048.0),
        threshold: float = 1.2,
    ):
        """Initialize detector.

        Args:
            terrain_provider: Optional terrain provider for height sampling
            heightmap_path: Optional path to heightmap (for future enhancement)
            terrain_size: Terrain size in meters (width_x, depth_z)
            threshold: Ratio threshold to determine orientation (default 1.2)
        """
        self.terrain_provider = terrain_provider
        self.heightmap_path = heightmap_path
        self.terrain_size = terrain_size
        self.threshold = threshold

    def detect_orientation(self) -> OrientationAnalysis:
        """Detect terrain orientation.

        For most Portal terrains, we analyze based on known terrain dimensions.
        Future enhancement: Sample heightmap for actual variation analysis.

        Returns:
            OrientationAnalysis with detected orientation
        """
        width_x, depth_z = self.terrain_size

        # Avoid division by zero
        if width_x == 0 or depth_z == 0:
            return OrientationAnalysis(
                orientation=Orientation.SQUARE,
                width_x=width_x,
                depth_z=depth_z,
                ratio=1.0,
                confidence="low",
            )

        # Calculate ratio (always >= 1.0)
        if width_x > depth_z:
            ratio = width_x / depth_z
            orientation = Orientation.EAST_WEST if ratio >= self.threshold else Orientation.SQUARE
        else:
            ratio = depth_z / width_x
            orientation = Orientation.NORTH_SOUTH if ratio >= self.threshold else Orientation.SQUARE

        # Most Portal terrains are square (2048x2048), so if ratio is close to 1.0,
        # we have low confidence in detecting orientation
        if abs(ratio - 1.0) < 0.1:
            confidence = "low"
            orientation = Orientation.SQUARE
        elif ratio >= 1.5:
            confidence = "high"
        elif ratio >= self.threshold:
            confidence = "medium"
        else:
            confidence = "low"

        return OrientationAnalysis(
            orientation=orientation,
            width_x=width_x,
            depth_z=depth_z,
            ratio=ratio,
            confidence=confidence,
        )

    def get_bounds(self) -> tuple[float, float, float, float]:
        """Get terrain bounding box.

        Assumes terrain is centered at origin.

        Returns:
            Tuple of (min_x, max_x, min_z, max_z)
        """
        width_x, depth_z = self.terrain_size

        half_width = width_x / 2
        half_depth = depth_z / 2

        return (-half_width, half_width, -half_depth, half_depth)

    def analyze_heightmap_variation(self) -> OrientationAnalysis:
        """Future enhancement: Analyze actual heightmap pixel variation.

        This would sample the heightmap along X and Z axes to determine
        which direction has more terrain features, providing better
        orientation detection for non-square terrains.

        Returns:
            OrientationAnalysis based on heightmap variation
        """
        # TODO: Implement heightmap analysis
        # - Sample heightmap at regular intervals along X axis
        # - Sample heightmap at regular intervals along Z axis
        # - Calculate variance in each direction
        # - Direction with higher variance is primary orientation

        # For now, fall back to size-based detection
        return self.detect_orientation()
