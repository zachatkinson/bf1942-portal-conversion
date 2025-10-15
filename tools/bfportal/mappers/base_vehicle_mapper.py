#!/usr/bin/env python3
"""Base vehicle mapper interface for all Battlefield game conversions.

Single Responsibility: Define the interface that all vehicle mappers must implement.

This ensures consistency across all eras (WW2, Vietnam, Modern, Future) and allows
generators to work with any mapper without knowing implementation details.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-15
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol


@dataclass
class VehicleMapping:
    """Represents a mapping from source game vehicle to BF6 VehicleType.

    Attributes:
        source_name: Original vehicle identifier from source game
        bf6_vehicle_type: BF6 Portal VehicleType enum value
        era: Historical/gameplay era (WW2, Vietnam, Modern, Future)
        category: Vehicle category (Tank, Fighter, APC, etc.)
        faction: Faction alignment (Axis, Allied, NATO, non-NATO, etc.)
        notes: Additional mapping notes and rationale
    """

    source_name: str
    bf6_vehicle_type: str
    era: str
    category: str
    faction: str = ""
    notes: str = ""


class IVehicleMapper(Protocol):
    """Protocol defining the interface for all vehicle mappers.

    All vehicle mappers (BF1942, Vietnam, BF2, BF2142, etc.) must implement
    this interface to ensure compatibility with generators and validators.

    Example Usage:
        def generate_spawner(vehicle_name: str, mapper: IVehicleMapper):
            bf6_type = mapper.map_vehicle(vehicle_name)
            if bf6_type:
                # Generate spawner node...
    """

    def map_vehicle(self, source_vehicle_name: str) -> str | None:
        """Map source game vehicle name to BF6 VehicleType enum value.

        Args:
            source_vehicle_name: Vehicle identifier from source game
                (e.g., "Sherman", "T34", "UH1", "M1A2")

        Returns:
            BF6 VehicleType enum value (e.g., "Abrams", "Leopard", "UH60"),
            or None if unmapped

        Examples:
            >>> mapper.map_vehicle("Sherman")
            'Abrams'
            >>> mapper.map_vehicle("PanzerIV")
            'Leopard'
            >>> mapper.map_vehicle("UnknownVehicle")
            None
        """
        ...

    def get_mapping_info(self, source_vehicle_name: str) -> VehicleMapping | None:
        """Get complete mapping information for a source vehicle.

        Args:
            source_vehicle_name: Vehicle identifier from source game

        Returns:
            VehicleMapping object with full details (era, category, notes),
            or None if unmapped

        Examples:
            >>> info = mapper.get_mapping_info("Sherman")
            >>> info.era
            'WW2'
            >>> info.category
            'Tank'
            >>> info.faction
            'Allied'
        """
        ...

    def get_all_mappings(self) -> dict[str, VehicleMapping]:
        """Get all vehicle mappings for this mapper.

        Returns:
            Dictionary mapping source vehicle names to VehicleMapping objects

        Examples:
            >>> mappings = mapper.get_all_mappings()
            >>> len(mappings)
            81  # BF1942 mapper has 81 vehicles
            >>> "Sherman" in mappings
            True
        """
        ...


class BaseVehicleMapper(ABC):
    """Abstract base class for vehicle mappers with common functionality.

    Provides shared implementation for common operations like case-insensitive
    matching and fallback logic. Subclasses only need to implement _build_mappings().

    Example Subclass:
        class BF1942VehicleMapper(BaseVehicleMapper):
            def get_game_name(self) -> str:
                return "BF1942"

            def get_era(self) -> str:
                return "WW2"

            def _build_mappings(self) -> dict[str, VehicleMapping]:
                mappings = {}
                mappings["Sherman"] = VehicleMapping(...)
                return mappings
    """

    def __init__(self):
        """Initialize mapper and build mapping table."""
        self._mappings = self._build_mappings()

    @abstractmethod
    def get_game_name(self) -> str:
        """Return the source game name (e.g., 'BF1942', 'BFVietnam', 'BF2')."""

    @abstractmethod
    def get_era(self) -> str:
        """Return the gameplay era (e.g., 'WW2', 'Vietnam', 'Modern', 'Future')."""

    @abstractmethod
    def _build_mappings(self) -> dict[str, VehicleMapping]:
        """Build the complete vehicle mapping table for this game.

        Subclasses implement this to define their specific vehicle mappings.

        Returns:
            Dictionary mapping source vehicle names to VehicleMapping objects
        """

    def map_vehicle(self, source_vehicle_name: str) -> str | None:
        """Map source vehicle name to BF6 VehicleType enum value.

        Implements IVehicleMapper interface with case-insensitive fallback.

        Args:
            source_vehicle_name: Vehicle identifier from source game

        Returns:
            BF6 VehicleType enum value, or None if unmapped
        """
        # Try exact match first
        if source_vehicle_name in self._mappings:
            return self._mappings[source_vehicle_name].bf6_vehicle_type

        # Try case-insensitive partial match
        name_lower = source_vehicle_name.lower()
        for key, mapping in self._mappings.items():
            if key.lower() in name_lower or name_lower in key.lower():
                return mapping.bf6_vehicle_type

        return None

    def get_mapping_info(self, source_vehicle_name: str) -> VehicleMapping | None:
        """Get complete mapping information for a source vehicle.

        Implements IVehicleMapper interface.

        Args:
            source_vehicle_name: Vehicle identifier from source game

        Returns:
            VehicleMapping object with full details, or None if unmapped
        """
        if source_vehicle_name in self._mappings:
            return self._mappings[source_vehicle_name]

        # Try case-insensitive partial match
        name_lower = source_vehicle_name.lower()
        for key, mapping in self._mappings.items():
            if key.lower() in name_lower or name_lower in key.lower():
                return mapping

        return None

    def get_all_mappings(self) -> dict[str, VehicleMapping]:
        """Get all vehicle mappings for this mapper.

        Implements IVehicleMapper interface.

        Returns:
            Dictionary of all source vehicle to BF6 mappings
        """
        return self._mappings.copy()

    def get_supported_vehicles(self) -> list[str]:
        """Get list of all supported source vehicle names.

        Returns:
            Sorted list of source vehicle identifiers
        """
        return sorted(self._mappings.keys())

    def get_bf6_vehicle_types(self) -> list[str]:
        """Get list of all BF6 VehicleType enum values used in mappings.

        Returns:
            Sorted list of unique BF6 VehicleType values
        """
        types = {mapping.bf6_vehicle_type for mapping in self._mappings.values()}
        return sorted(types)

    def get_mappings_by_category(self, category: str) -> dict[str, VehicleMapping]:
        """Get all mappings for a specific category.

        Args:
            category: Vehicle category (e.g., "Tank", "Fighter", "APC")

        Returns:
            Dictionary of mappings matching the category
        """
        return {
            name: mapping
            for name, mapping in self._mappings.items()
            if mapping.category.lower() == category.lower()
        }

    def get_mappings_by_faction(self, faction: str) -> dict[str, VehicleMapping]:
        """Get all mappings for a specific faction.

        Args:
            faction: Faction identifier (e.g., "Axis", "Allied", "NATO", "non-NATO")

        Returns:
            Dictionary of mappings matching the faction
        """
        return {
            name: mapping
            for name, mapping in self._mappings.items()
            if mapping.faction.lower() == faction.lower()
        }

    def get_mappings_by_bf6_type(self, bf6_type: str) -> dict[str, VehicleMapping]:
        """Get all source vehicles that map to a specific BF6 VehicleType.

        Useful for understanding which source vehicles share the same BF6 representation.

        Args:
            bf6_type: BF6 VehicleType enum value (e.g., "Abrams", "Leopard")

        Returns:
            Dictionary of mappings that use this BF6 VehicleType

        Examples:
            >>> mapper.get_mappings_by_bf6_type("Abrams")
            {
                "Sherman": VehicleMapping(...),
                "M4Sherman": VehicleMapping(...),
                "T34": VehicleMapping(...)
            }
        """
        return {
            name: mapping
            for name, mapping in self._mappings.items()
            if mapping.bf6_vehicle_type == bf6_type
        }

    def validate_mappings(self, valid_bf6_types: set[str]) -> list[str]:
        """Validate that all mappings use valid BF6 VehicleType enum values.

        Args:
            valid_bf6_types: Set of valid BF6 VehicleType values
                (typically from BF6_VEHICLE_TYPE_ENUM)

        Returns:
            List of error messages for invalid mappings (empty if all valid)

        Examples:
            >>> from tools.bfportal.generators.constants.gameplay import BF6_VEHICLE_TYPE_ENUM
            >>> errors = mapper.validate_mappings(set(BF6_VEHICLE_TYPE_ENUM.keys()))
            >>> if errors:
            ...     print("Invalid mappings found:", errors)
        """
        errors = []

        for source_name, mapping in self._mappings.items():
            if mapping.bf6_vehicle_type not in valid_bf6_types:
                errors.append(
                    f"{source_name} maps to invalid BF6 type '{mapping.bf6_vehicle_type}' "
                    f"(valid types: {sorted(valid_bf6_types)})"
                )

        return errors

    def get_unmapped_vehicles(self, vehicle_list: list[str]) -> list[str]:
        """Find vehicles in list that have no mapping.

        Useful for auditing new maps or game expansions.

        Args:
            vehicle_list: List of vehicle names to check

        Returns:
            List of vehicle names that lack mappings

        Examples:
            >>> found_vehicles = ["Sherman", "PanzerIV", "NewTankType"]
            >>> mapper.get_unmapped_vehicles(found_vehicles)
            ['NewTankType']
        """
        unmapped = []

        for vehicle in vehicle_list:
            if self.map_vehicle(vehicle) is None:
                unmapped.append(vehicle)

        return unmapped

    def __repr__(self) -> str:
        """String representation of mapper."""
        return (
            f"{self.__class__.__name__}("
            f"game={self.get_game_name()}, "
            f"era={self.get_era()}, "
            f"vehicles={len(self._mappings)})"
        )
