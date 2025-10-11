#!/usr/bin/env python3
"""Interfaces for orientation detection.

Defines abstractions for detecting map and terrain orientations.
Interface Segregation Principle: Each interface defines minimal contract.
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Tuple


class Orientation(Enum):
    """Map orientation enum."""
    NORTH_SOUTH = "north_south"  # Map extends more along Z axis (north-south)
    EAST_WEST = "east_west"      # Map extends more along X axis (east-west)
    SQUARE = "square"             # Roughly equal in both dimensions


@dataclass
class OrientationAnalysis:
    """Result of orientation analysis."""
    orientation: Orientation
    width_x: float  # Extent along X axis
    depth_z: float  # Extent along Z axis
    ratio: float    # ratio of larger dimension to smaller (>= 1.0)
    confidence: str  # 'high', 'medium', 'low'


class IOrientationDetector(ABC):
    """Interface for orientation detection.

    Single Responsibility: Only detects orientation of one type of data.
    Interface Segregation: Minimal contract - just detection.
    """

    @abstractmethod
    def detect_orientation(self) -> OrientationAnalysis:
        """Detect orientation.

        Returns:
            OrientationAnalysis with detected orientation and metrics
        """
        pass

    @abstractmethod
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get bounding box.

        Returns:
            Tuple of (min_x, max_x, min_z, max_z)
        """
        pass
