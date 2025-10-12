"""Orientation detection tools for map conversion.

Detects and matches map orientations between source maps and Portal terrains.
"""

from .interfaces import IOrientationDetector, Orientation
from .map_orientation_detector import MapOrientationDetector
from .orientation_matcher import OrientationMatcher
from .terrain_orientation_detector import TerrainOrientationDetector

__all__ = [
    "IOrientationDetector",
    "Orientation",
    "MapOrientationDetector",
    "TerrainOrientationDetector",
    "OrientationMatcher",
]
