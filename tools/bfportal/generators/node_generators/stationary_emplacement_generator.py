#!/usr/bin/env python3
"""Stationary weapon emplacement node generator for TSCN generation.

Single Responsibility: Generate stationary weapon emplacement nodes from game objects.

This generator extracts weapon emplacement objects (machine guns, TOW launchers, etc.)
from MapData and creates properly formatted Godot nodes with StationaryEmplacementSpawner instances.
"""

from ...core.interfaces import MapData
from ..components.asset_registry import AssetRegistry
from ..components.transform_formatter import TransformFormatter
from .base_generator import BaseNodeGenerator


class StationaryEmplacementGenerator(BaseNodeGenerator):
    """Generates stationary weapon emplacement nodes for Portal maps.

    Extracts weapon emplacement objects from game_objects list and creates
    StationaryEmplacementSpawner nodes with proper weapon types.

    Example Output:
        [node name="StationaryEmplacement_1" parent="Static" instance=ExtResource("5")]
        transform = Transform3D(...)
        Team = 1
        ObjId = 2001
        WeaponType = "tow_launcher"  # or "machinegun"
        # Original: antitankgunspawner (Pak40 → TOW)
    """

    def generate(
        self,
        map_data: MapData,
        asset_registry: AssetRegistry,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate stationary weapon emplacement nodes.

        Args:
            map_data: Complete map data
            asset_registry: Registry for ExtResource IDs
            transform_formatter: Formatter for Transform3D strings

        Returns:
            List of .tscn node lines for weapon emplacements
        """
        lines: list[str] = []

        # Extract weapon emplacement objects
        # Check for objects with asset_type="StationaryEmplacementSpawner"
        emplacements = [
            obj for obj in map_data.game_objects if obj.asset_type == "StationaryEmplacementSpawner"
        ]

        if not emplacements:
            return lines

        # Generate nodes for each emplacement
        for i, emplacement in enumerate(emplacements, 1):
            lines.append(
                f'[node name="StationaryEmplacement_{i}" parent="." instance=ExtResource("5")]'
            )
            lines.append(f"transform = {transform_formatter.format(emplacement.transform)}")
            lines.append(f"Team = {emplacement.team.value if emplacement.team else 0}")
            lines.append(f"ObjId = {2000 + i}")

            # Get weapon type from properties
            weapon_type = emplacement.properties.get("weapon_type", "machinegun")
            original_spawner = emplacement.properties.get("original_spawner", "unknown")

            # Set weapon type property
            lines.append(f'WeaponType = "{weapon_type}"')

            # Add comment explaining mapping
            weapon_desc = {
                "machinegun": "MG42/Browning → Modern MG",
                "tow_launcher": "Pak40/AT gun → TOW launcher",
            }.get(weapon_type, "Unknown weapon")

            lines.append(f"# Original: {original_spawner} ({weapon_desc})")
            lines.append("")

        return lines
