#!/usr/bin/env python3
"""Capture point node generator for .tscn generation.

Single Responsibility: Generate CapturePoint nodes with spawn assignments.
Follows SOLID principles and DRY patterns.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-12
"""

from ...core.interfaces import CapturePoint, MapData
from ..components.asset_registry import AssetRegistry
from ..components.transform_formatter import TransformFormatter
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
        [node name="CapturePoint_1" parent="." instance=ExtResource("3")]
        transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 0, 200)
        Team = 0
        ObjId = 101
        InfantrySpawnPoints_Team1 = [NodePath("CP1_Spawn_1_1"), ...]
        InfantrySpawnPoints_Team2 = [NodePath("CP1_Spawn_2_1"), ...]

        [node name="CaptureZone_1" type="Area3D" parent="CapturePoint_1"]
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
            lines.extend(
                self._generate_single_capture_point(i, cp, asset_registry, transform_formatter)
            )

        return lines

    def _generate_single_capture_point(
        self,
        index: int,
        cp: CapturePoint,
        asset_registry: AssetRegistry,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate a single capture point with all children.

        Args:
            index: Capture point index (1-based)
            cp: Capture point data
            asset_registry: Registry for ExtResource lookups
            transform_formatter: Formatter for Transform3D strings

        Returns:
            List of .tscn lines for this capture point
        """
        lines = []

        # Get spawn lists (post_init ensures these are never None)
        team1_spawns = cp.team1_spawns if cp.team1_spawns is not None else []
        team2_spawns = cp.team2_spawns if cp.team2_spawns is not None else []

        # Generate main capture point node
        lines.extend(
            self._generate_capture_point_node(
                index, cp, team1_spawns, team2_spawns, transform_formatter
            )
        )

        # Generate capture zone
        lines.extend(self._generate_capture_zone(index, cp.radius))

        # Generate spawn points for both teams
        lines.extend(self._generate_spawn_points(index, 1, team1_spawns, cp, transform_formatter))
        lines.extend(self._generate_spawn_points(index, 2, team2_spawns, cp, transform_formatter))

        return lines

    def _generate_capture_point_node(
        self,
        index: int,
        cp: CapturePoint,
        team1_spawns: list,
        team2_spawns: list,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate main CapturePoint node definition.

        Args:
            index: Capture point index
            cp: Capture point data
            team1_spawns: Team 1 spawn points
            team2_spawns: Team 2 spawn points
            transform_formatter: Transform formatter

        Returns:
            List of .tscn lines for capture point node
        """
        lines = []

        # Build spawn path arrays
        team1_spawn_paths = [
            f'NodePath("CP{index}_Spawn_1_{j + 1}")' for j in range(len(team1_spawns))
        ]
        team2_spawn_paths = [
            f'NodePath("CP{index}_Spawn_2_{j + 1}")' for j in range(len(team2_spawns))
        ]

        team1_spawns_str = ", ".join(team1_spawn_paths) if team1_spawn_paths else ""
        team2_spawns_str = ", ".join(team2_spawn_paths) if team2_spawn_paths else ""

        # Capture point node
        lines.append(f'[node name="CapturePoint_{index}" parent="." instance=ExtResource("3")]')
        lines.append(f"transform = {transform_formatter.format(cp.transform)}")
        lines.append(f'Label = "{cp.label}"')  # Display label (A, B, C, etc.)
        lines.append("Team = 0")  # Neutral by default
        lines.append(f"ObjId = {100 + index}")  # ObjId range: 100-999 for gameplay objects

        # Add spawn arrays if capture point has spawns
        if team1_spawn_paths:
            lines.append(f"InfantrySpawnPoints_Team1 = [{team1_spawns_str}]")
        if team2_spawn_paths:
            lines.append(f"InfantrySpawnPoints_Team2 = [{team2_spawns_str}]")

        lines.append("")

        return lines

    def _generate_capture_zone(self, index: int, radius: float) -> list[str]:
        """Generate capture zone Area3D node.

        Args:
            index: Capture point index
            radius: Capture radius from BF1942 data

        Returns:
            List of .tscn lines for capture zone
        """
        lines = []

        lines.append(
            f'[node name="CaptureZone_{index}" type="Area3D" parent="CapturePoint_{index}"]'
        )
        lines.append(f"height = {CAPTURE_ZONE_HEIGHT_M}")

        # Create square capture zone using BF1942 radius
        # PackedVector2Array: (x, z) coordinates for 2D polygon
        lines.append(
            f"points = PackedVector2Array(-{radius}, -{radius}, "
            f"{radius}, -{radius}, "
            f"{radius}, {radius}, "
            f"-{radius}, {radius})"
        )
        lines.append("")

        return lines

    def _generate_spawn_points(
        self,
        cp_index: int,
        team: int,
        spawns: list,
        cp: CapturePoint,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate spawn point nodes for a team.

        Args:
            cp_index: Capture point index
            team: Team number (1 or 2)
            spawns: List of spawn points
            cp: Parent capture point (for relative transforms)
            transform_formatter: Transform formatter

        Returns:
            List of .tscn lines for spawn points
        """
        lines = []

        for j, spawn in enumerate(spawns, 1):
            lines.append(
                f'[node name="CP{cp_index}_Spawn_{team}_{j}" '
                f'parent="CapturePoint_{cp_index}" instance=ExtResource("2")]'
            )

            # Calculate relative transform (spawn position relative to capture point)
            rel_transform = transform_formatter.make_relative(spawn.transform, cp.transform)
            lines.append(f"transform = {transform_formatter.format(rel_transform)}")
            lines.append("")

        return lines
