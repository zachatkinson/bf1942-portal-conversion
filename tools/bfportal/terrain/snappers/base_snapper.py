#!/usr/bin/env python3
"""Base interface for terrain snapping.

Single Responsibility: Define contract for all snappers.
Open/Closed Principle: Extensible via inheritance, closed for modification.
Liskov Substitution: All snappers can be used interchangeably.
Interface Segregation: Simple, focused interface.
Dependency Inversion: Depends on abstractions (ITerrainProvider).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol


@dataclass
class SnapResult:
    """Result of a snapping operation.

    Attributes:
        original_y: Original Y coordinate
        snapped_y: New Y coordinate after snapping
        was_adjusted: True if Y was changed
        reason: Human-readable reason for adjustment (or why not)
    """

    original_y: float
    snapped_y: float
    was_adjusted: bool
    reason: str


class ITerrainProvider(Protocol):
    """Protocol for terrain height queries.

    Note: This duplicates the interface in core/interfaces.py but avoids
    circular imports. Both should stay in sync.
    """

    def get_height_at(self, x: float, z: float) -> float:
        """Get terrain height at (x, z) position.

        Args:
            x: X coordinate
            z: Z coordinate

        Returns:
            Height at position

        Raises:
            Exception: If position is out of bounds
        """
        ...


class IObjectSnapper(ABC):
    """Abstract base class for object snapping strategies.

    Each snapper handles a specific category of objects (gameplay, vegetation, etc.)
    and knows how to calculate appropriate heights for those objects.

    Single Responsibility: Each subclass handles one object category.
    Open/Closed: New snappers can be added without modifying existing ones.
    """

    def __init__(self, terrain: ITerrainProvider):
        """Initialize snapper.

        Args:
            terrain: Terrain provider for height queries
        """
        self.terrain = terrain

    @abstractmethod
    def can_snap(self, node_name: str, asset_type: str | None = None) -> bool:
        """Check if this snapper handles the given object.

        Args:
            node_name: Node name from .tscn (e.g., "TEAM_1_HQ", "Birch_01_L_1")
            asset_type: Optional asset type (e.g., "Birch_01_L")

        Returns:
            True if this snapper should handle this object
        """

    @abstractmethod
    def calculate_snapped_height(
        self, x: float, z: float, current_y: float, node_name: str
    ) -> SnapResult:
        """Calculate snapped height for an object.

        Args:
            x: Object X position
            z: Object Z position
            current_y: Current Y position
            node_name: Node name for context

        Returns:
            SnapResult with new height and adjustment details
        """

    @abstractmethod
    def get_category_name(self) -> str:
        """Get human-readable category name for logging.

        Returns:
            Category name (e.g., "Gameplay", "Vegetation")
        """
