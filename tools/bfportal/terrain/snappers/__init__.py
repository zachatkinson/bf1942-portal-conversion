"""Terrain snapping modules for different asset categories.

This package provides specialized snappers for different object types,
following Single Responsibility Principle.
"""

from .base_snapper import IObjectSnapper, SnapResult
from .gameplay_snapper import GameplaySnapper
from .prop_snapper import PropSnapper
from .snap_validator import SnapValidator
from .vegetation_snapper import VegetationSnapper

__all__ = [
    "IObjectSnapper",
    "SnapResult",
    "GameplaySnapper",
    "VegetationSnapper",
    "PropSnapper",
    "SnapValidator",
]
