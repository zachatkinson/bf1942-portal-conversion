#!/usr/bin/env python3
"""Capture point node generator for .tscn generation.

Single Responsibility: Generate CapturePoint nodes with spawn assignments.
Follows SOLID principles and DRY patterns.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-12
"""

from ...core.interfaces import MapData
from ..components.asset_registry import AssetRegistry
from ..components.transform_formatter import TransformFormatter
from ..constants.extresource_ids import EXT_RESOURCE_POLYGON_VOLUME
from ..constants.gameplay import CAPTURE_ZONE_HEIGHT_M
from .base_generator import BaseNodeGenerator


class CapturePointGenerator(BaseNodeGenerator):
    """Generates CapturePoint nodes with neutral spawns for both teams.

    This generator creates Conquest-style capture points with:
    - Main CapturePoint node (neutral by default)
    - Capture zone based on BF1942 radius
    - Team 1 spawn points (when captured by Team 1)
    - Team 2 spawn points (when captured by Team 2)
    - Proper node hierarchy and transforms

    Example Output:
        [node name="CapturePoint_1" parent="." node_paths=PackedStringArray("CaptureArea", "InfantrySpawnPoints_Team1", "InfantrySpawnPoints_Team2") instance=ExtResource("3")]
        transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 0, 200)
        Team = 0
        ObjId = 101
        CaptureArea = NodePath("CaptureZone_1")
        InfantrySpawnPoints_Team1 = [NodePath("CP1_Spawn_1_1"), ...]
        InfantrySpawnPoints_Team2 = [NodePath("CP1_Spawn_2_1"), ...]

        [node name="CaptureZone_1" parent="CapturePoint_1" instance=ExtResource("10")]
        height = 50.0
        points = PackedVector2Array(-25, -25, 25, -25, 25, 25, -25, 25)

        [node name="CP1_Spawn_1_1" parent="CapturePoint_1" instance=ExtResource("2")]
        transform = Transform3D(...)
    """

    def generate(
        self,
        map_data: MapData,
        asset_registry: AssetRegistry,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate capture point nodes with spawn points.

        Args:
            map_data: Map data containing capture points
            asset_registry: Registry for ExtResource lookups
            transform_formatter: Formatter for Transform3D strings

        Returns:
            List of .tscn lines for all capture points

        Note:
            - ExtResource("3") is CapturePoint.tscn
            - ExtResource("2") is SpawnPoint.tscn
            - ObjId starts at 101 for capture points (100-999 range)
        """
        lines: list[str] = []

        if not map_data.capture_points:
            return lines

        for i, cp in enumerate(map_data.capture_points, 1):
            # __post_init__ ensures these are never None, but need explicit check for mypy
            team1_spawns = cp.team1_spawns if cp.team1_spawns is not None else []
            team2_spawns = cp.team2_spawns if cp.team2_spawns is not None else []

            # Build spawn arrays
            team1_spawn_paths = [
                f'NodePath("CP{i}_Spawn_1_{j + 1}")' for j in range(len(team1_spawns))
            ]
            team2_spawn_paths = [
                f'NodePath("CP{i}_Spawn_2_{j + 1}")' for j in range(len(team2_spawns))
            ]

            team1_spawns_str = ", ".join(team1_spawn_paths) if team1_spawn_paths else ""
            team2_spawns_str = ", ".join(team2_spawn_paths) if team2_spawn_paths else ""

            # Build node_paths array for Portal SDK compatibility
            node_paths = ["CaptureArea"]
            if team1_spawn_paths:
                node_paths.append("InfantrySpawnPoints_Team1")
            if team2_spawn_paths:
                node_paths.append("InfantrySpawnPoints_Team2")
            node_paths_str = ", ".join([f'"{path}"' for path in node_paths])

            lines.append(
                f'[node name="CapturePoint_{i}" parent="." node_paths=PackedStringArray({node_paths_str}) instance=ExtResource("3")]'
            )
            lines.append(f"transform = {transform_formatter.format(cp.transform)}")
            lines.append("Team = 0")  # Neutral
            lines.append(f"ObjId = {100 + i}")
            lines.append(f'CaptureArea = NodePath("CaptureZone_{i}")')

            # Add spawn arrays if capture point has spawns
            if team1_spawn_paths:
                lines.append(f"InfantrySpawnPoints_Team1 = [{team1_spawns_str}]")
            if team2_spawn_paths:
                lines.append(f"InfantrySpawnPoints_Team2 = [{team2_spawns_str}]")

            lines.append("")

            # Add capture zone using BF1942 radius (use PolygonVolume instance for Portal SDK compatibility)
            radius = cp.radius
            lines.append(
                f'[node name="CaptureZone_{i}" parent="CapturePoint_{i}" instance=ExtResource("{EXT_RESOURCE_POLYGON_VOLUME}")]'
            )
            lines.append(f"height = {CAPTURE_ZONE_HEIGHT_M}")
            # Create square capture zone with BF1942 radius
            lines.append(
                f"points = PackedVector2Array(-{radius}, -{radius}, {radius}, -{radius}, {radius}, {radius}, -{radius}, {radius})"
            )
            lines.append("")

            # Generate spawn point nodes as children of the capture point
            for j, spawn in enumerate(team1_spawns, 1):
                lines.append(
                    f'[node name="CP{i}_Spawn_1_{j}" parent="CapturePoint_{i}" instance=ExtResource("2")]'
                )
                rel_transform = transform_formatter.make_relative(spawn.transform, cp.transform)
                lines.append(f"transform = {transform_formatter.format(rel_transform)}")
                lines.append("")

            for j, spawn in enumerate(team2_spawns, 1):
                lines.append(
                    f'[node name="CP{i}_Spawn_2_{j}" parent="CapturePoint_{i}" instance=ExtResource("2")]'
                )
                rel_transform = transform_formatter.make_relative(spawn.transform, cp.transform)
                lines.append(f"transform = {transform_formatter.format(rel_transform)}")
                lines.append("")

        return lines
