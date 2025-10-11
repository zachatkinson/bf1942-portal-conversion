"""Orientation detection tools for map conversion.

Detects and matches map orientations between source maps and Portal terrains.
"""

from .interfaces import IOrientationDetector, Orientation
from .map_orientation_detector import MapOrientationDetector
from .terrain_orientation_detector import TerrainOrientationDetector
from .orientation_matcher import OrientationMatcher

__all__ = [
    'IOrientationDetector',
    'Orientation',
    'MapOrientationDetector',
    'TerrainOrientationDetector',
    'OrientationMatcher'
]
