#!/usr/bin/env python3
"""Vehicle spawner node generator for TSCN generation.

Single Responsibility: Generate vehicle spawner nodes from game objects.

This generator extracts vehicle spawner objects from MapData and creates
properly formatted Godot nodes with VehicleSpawner instances following
Portal SDK best practices:
- Hierarchical organization under Vehicles/Team1 and Vehicles/Team2
- Descriptive naming by vehicle type (e.g., VehicleSpawner-Abrams)
- Team assignment based on proximity to HQs
- Support for capture point spawners with DisableRespawn
"""

import math

from ...core.interfaces import MapData, Transform, Vector3
from ...mappers.vehicle_mapper import VehicleMapper
from ..components.asset_registry import AssetRegistry
from ..components.transform_formatter import TransformFormatter
from ..constants.gameplay import BF6_VEHICLE_TYPE_ENUM
from .base_generator import BaseNodeGenerator


class VehicleSpawnerGenerator(BaseNodeGenerator):
    """Generates vehicle spawner nodes for Portal maps.

    Extracts vehicle spawner objects from game_objects list and creates
    VehicleSpawner nodes with proper BF6 VehicleType enum values following
    Portal SDK organizational patterns.

    Example Output:
        [node name="Vehicles" type="Node3D" parent="."]

        [node name="Team1" type="Node3D" parent="Vehicles"]

        [node name="VehicleSpawner-Leopard" parent="Vehicles/Team1" instance=ExtResource("4")]
        transform = Transform3D(...)
        VehicleType = 1
        P_AutoSpawnEnabled = true
    """

    def __init__(self):
        """Initialize generator with vehicle mapper."""
        super().__init__()
        self.vehicle_mapper = VehicleMapper()

    def _distance_to_hq(self, pos: Vector3, hq_pos: Vector3) -> float:
        """Calculate 2D distance from spawner to HQ (ignoring Y axis).

        Args:
            pos: Spawner position
            hq_pos: HQ position

        Returns:
            2D distance in meters
        """
        dx = pos.x - hq_pos.x
        dz = pos.z - hq_pos.z
        return math.sqrt(dx * dx + dz * dz)

    def _assign_team(
        self, spawner_pos: Vector3, team1_hq_pos: Vector3, team2_hq_pos: Vector3
    ) -> int:
        """Assign spawner to team based on proximity to HQs.

        Args:
            spawner_pos: Spawner position
            team1_hq_pos: Team 1 HQ position
            team2_hq_pos: Team 2 HQ position

        Returns:
            Team number (1 or 2)
        """
        dist1 = self._distance_to_hq(spawner_pos, team1_hq_pos)
        dist2 = self._distance_to_hq(spawner_pos, team2_hq_pos)
        return 1 if dist1 < dist2 else 2

    def _get_vehicle_name(self, bf6_vehicle_type: str | None) -> str:
        """Get descriptive vehicle name for node naming.

        Args:
            bf6_vehicle_type: BF6 vehicle type (e.g., "Leopard", "UH60")

        Returns:
            Vehicle name for node (defaults to "Unknown" if not found)
        """
        return bf6_vehicle_type if bf6_vehicle_type else "Unknown"

    def generate(
        self,
        map_data: MapData,
        asset_registry: AssetRegistry,
        transform_formatter: TransformFormatter,
        min_safe_y: float = 0.0,
    ) -> list[str]:
        """Generate vehicle spawner nodes with Portal SDK hierarchy.

        Creates:
        - Vehicles container node
        - Team1 and Team2 sub-containers
        - Vehicle spawners organized by team with descriptive names

        Args:
            map_data: Complete map data with HQs and game objects
            asset_registry: Registry for ExtResource IDs
            transform_formatter: Formatter for Transform3D strings
            min_safe_y: Minimum safe Y height for spawner placement (above terrain)

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

        # Create Vehicles container node
        lines.append('[node name="Vehicles" type="Node3D" parent="."]')
        lines.append("")

        # Create Team1 and Team2 container nodes
        lines.append('[node name="Team1" type="Node3D" parent="Vehicles"]')
        lines.append("")
        lines.append('[node name="Team2" type="Node3D" parent="Vehicles"]')
        lines.append("")

        # Get HQ positions for team assignment
        team1_hq_pos = map_data.team1_hq.position
        team2_hq_pos = map_data.team2_hq.position

        # Track vehicle counts per type per team for unique naming
        vehicle_counts: dict[str, dict[int, int]] = {}  # {vehicle_name: {team: count}}

        # Generate nodes for each spawner
        for spawner in vehicle_spawners:
            # Get BF1942 vehicle type from properties or asset_type
            bf1942_vehicle = spawner.properties.get("vehicle_type", spawner.asset_type)

            # Map BF1942 vehicle type to BF6 VehicleType enum
            bf6_vehicle_type = self.vehicle_mapper.map_vehicle(bf1942_vehicle)

            # Get descriptive vehicle name
            vehicle_name = self._get_vehicle_name(bf6_vehicle_type)

            # Assign to team based on proximity to HQs
            team = self._assign_team(spawner.transform.position, team1_hq_pos, team2_hq_pos)

            # Track count for unique naming
            if vehicle_name not in vehicle_counts:
                vehicle_counts[vehicle_name] = {1: 0, 2: 0}
            vehicle_counts[vehicle_name][team] += 1
            count = vehicle_counts[vehicle_name][team]

            # Create unique node name (append number if multiple of same type)
            if count > 1:
                node_name = f"VehicleSpawner-{vehicle_name}{count}"
            else:
                node_name = f"VehicleSpawner-{vehicle_name}"

            # Determine parent path
            parent_path = f"Vehicles/Team{team}"

            # Generate node
            lines.append(
                f'[node name="{node_name}" parent="{parent_path}" instance=ExtResource("4")]'
            )

            # Ensure spawner is above terrain for snapping
            spawner_transform = spawner.transform
            if spawner_transform.position.y < min_safe_y:
                # Clamp Y to minimum safe height
                safe_pos = Vector3(
                    spawner_transform.position.x,
                    min_safe_y,
                    spawner_transform.position.z,
                )
                spawner_transform = Transform(
                    safe_pos, spawner_transform.rotation, spawner_transform.scale
                )

            lines.append(f"transform = {transform_formatter.format(spawner_transform)}")

            # Enable auto-spawning so vehicles appear without TypeScript code
            lines.append("P_AutoSpawnEnabled = true")

            # Set VehicleType enum index
            if bf6_vehicle_type and bf6_vehicle_type in BF6_VEHICLE_TYPE_ENUM:
                enum_index = BF6_VEHICLE_TYPE_ENUM[bf6_vehicle_type]
                lines.append(f"VehicleType = {enum_index}")
            else:
                # Unmapped vehicle - default to Abrams
                lines.append("VehicleType = 0")

            lines.append("")

        return lines
