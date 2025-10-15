#!/usr/bin/env python3
"""Vehicle spawner node generator for TSCN generation.

Single Responsibility: Generate vehicle spawner nodes from game objects.

This generator extracts vehicle spawner objects from MapData and creates
properly formatted Godot nodes with VehicleSpawner instances.
"""

from ...core.interfaces import MapData
from ...mappers.vehicle_mapper import VehicleMapper
from ..components.asset_registry import AssetRegistry
from ..components.transform_formatter import TransformFormatter
from ..constants.gameplay import BF6_VEHICLE_TYPE_ENUM
from .base_generator import BaseNodeGenerator


class VehicleSpawnerGenerator(BaseNodeGenerator):
    """Generates vehicle spawner nodes for Portal maps.

    Extracts vehicle spawner objects from game_objects list and creates
    VehicleSpawner nodes with proper BF6 VehicleType enum values.

    Example Output:
        [node name="VehicleSpawner_1" parent="." instance=ExtResource("4")]
        transform = Transform3D(...)
        Team = 1
        ObjId = 1001
        VehicleType = 1  # Leopard (enum index)
    """

    def __init__(self):
        """Initialize generator with vehicle mapper."""
        super().__init__()
        self.vehicle_mapper = VehicleMapper()

    def generate(
        self,
        map_data: MapData,
        asset_registry: AssetRegistry,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate vehicle spawner nodes.

        Args:
            map_data: Complete map data
            asset_registry: Registry for ExtResource IDs
            transform_formatter: Formatter for Transform3D strings

        Returns:
            List of .tscn node lines for vehicle spawners
        """
        lines: list[str] = []

        # Extract vehicle spawner objects
        # Check for objects with vehicle_type property (set by RefractorEngine)
        vehicle_spawners = [
            obj
            for obj in map_data.game_objects
            if "vehicle_type" in obj.properties or "spawner" in obj.asset_type.lower()
        ]

        if not vehicle_spawners:
            return lines

        # Generate nodes for each spawner
        for i, spawner in enumerate(vehicle_spawners, 1):
            lines.append(f'[node name="VehicleSpawner_{i}" parent="." instance=ExtResource("4")]')
            lines.append(f"transform = {transform_formatter.format(spawner.transform)}")
            lines.append(f"Team = {spawner.team.value if spawner.team else 0}")
            lines.append(f"ObjId = {1000 + i}")

            # Get BF1942 vehicle type from properties or asset_type
            bf1942_vehicle = spawner.properties.get("vehicle_type", spawner.asset_type)

            # Map BF1942 vehicle type to BF6 VehicleType enum
            bf6_vehicle_type = self.vehicle_mapper.map_vehicle(bf1942_vehicle)

            if bf6_vehicle_type and bf6_vehicle_type in BF6_VEHICLE_TYPE_ENUM:
                # Set VehicleType enum index
                enum_index = BF6_VEHICLE_TYPE_ENUM[bf6_vehicle_type]
                lines.append(f"VehicleType = {enum_index}")

                # Add comment for clarity
                mapping_info = self.vehicle_mapper.get_mapping_info(bf1942_vehicle)
                if mapping_info:
                    lines.append(
                        f"# {bf1942_vehicle} → {bf6_vehicle_type} ({mapping_info.category})"
                    )
            else:
                # Unmapped vehicle - default to Abrams with warning comment
                lines.append("VehicleType = 0  # Default: Abrams")
                lines.append(f"# ⚠️ UNMAPPED: {bf1942_vehicle} (needs manual review)")

            lines.append("")

        return lines
