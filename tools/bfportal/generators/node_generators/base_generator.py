#!/usr/bin/env python3
"""Base node generator interface for TSCN generation.

This module defines the abstract base class that all node generators must implement.
Following the Open/Closed Principle: new node generators can be added without
modifying existing code.

Single Responsibility: Defines the contract for node generation.
"""

from abc import ABC, abstractmethod

from ...core.interfaces import MapData
from ..components.asset_registry import AssetRegistry
from ..components.transform_formatter import TransformFormatter


class BaseNodeGenerator(ABC):
    """Abstract base class for all node generators.

    All node generators must implement this interface to ensure consistency
    and enable dependency injection. This follows SOLID principles:

    - Single Responsibility: Each generator handles one type of node
    - Open/Closed: Can add new generators without modifying existing code
    - Liskov Substitution: All generators are interchangeable via this interface
    - Dependency Inversion: Generators depend on abstractions (this interface)

    Design Pattern: Strategy Pattern
    - Each generator is a concrete strategy for generating specific node types
    - The TscnGenerator acts as the context that uses these strategies
    - Strategies share common dependencies (AssetRegistry, TransformFormatter)

    Example Usage:
        >>> registry = AssetRegistry()
        >>> formatter = TransformFormatter()
        >>> generator = HQNodeGenerator()
        >>> lines = generator.generate(map_data, registry, formatter)
        >>> # Returns formatted .tscn node lines
    """

    @abstractmethod
    def generate(
        self,
        map_data: MapData,
        asset_registry: AssetRegistry,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate .tscn node lines for this generator's responsibility.

        Args:
            map_data: Complete map data containing all game objects
            asset_registry: Registry for managing ExtResource IDs
            transform_formatter: Formatter for Transform3D strings

        Returns:
            List of formatted .tscn node definition lines

        Note:
            Implementations must:
            1. Extract relevant data from map_data
            2. Register any needed assets with asset_registry
            3. Format transforms using transform_formatter
            4. Return valid Godot .tscn node syntax

        Example Return Value:
            [
                '[node name="TEAM_1_HQ" parent="." instance=ExtResource("1")]',
                'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 0, 200)',
                'Team = 1',
                'ObjId = 1',
                ''
            ]
        """
