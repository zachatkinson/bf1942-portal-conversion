#!/usr/bin/env python3
"""HQ node generator for .tscn files.

Generates Team HQ nodes with spawn points and safety zones.
Single Responsibility: HQ and spawn point node generation only.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-12
"""

from ...core.interfaces import MapData
from ..components.asset_registry import AssetRegistry
from ..components.transform_formatter import TransformFormatter
from ..constants.gameplay import HQ_PROTECTION_HEIGHT_M, HQ_PROTECTION_RADIUS_M
from .base_generator import BaseNodeGenerator


class HQGenerator(BaseNodeGenerator):
    """Generates HQ nodes with spawn points for both teams.

    This generator creates:
    - TEAM_1_HQ and TEAM_2_HQ nodes with HQ_PlayerSpawner instances
    - HQ safety zones (50m radius Area3D polygons)
    - Spawn point nodes as children of HQs (with relative transforms)

    Requirements per BF6 Portal spec:
    - Minimum 4 spawn points per team
    - HQ nodes reference spawn points via node paths
    - Spawn points use relative transforms (relative to HQ position)
    - HQ safety zones use 50m radius (matching BF1942 standard)

    Example Output:
        [node name="TEAM_1_HQ" parent="." instance=ExtResource("1")]
        transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 0, 200)
        Team = 1
        AltTeam = 0
        ObjId = 1
        HQArea = NodePath("HQ_Team1")
        InfantrySpawns = [NodePath("SpawnPoint_1_1"), NodePath("SpawnPoint_1_2"), ...]

        [node name="HQ_Team1" type="Area3D" parent="TEAM_1_HQ"]
        height = 50.0
        points = PackedVector2Array(-50, -50, 50, -50, 50, 50, -50, 50)

        [node name="SpawnPoint_1_1" parent="TEAM_1_HQ" instance=ExtResource("2")]
        transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 0, 5)
    """

    def generate(
        self,
        map_data: MapData,
        asset_registry: AssetRegistry,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate HQ nodes with spawn points for both teams.

        Args:
            map_data: Complete map data with HQ and spawn data
            asset_registry: Registry for ExtResource ID lookup
            transform_formatter: Formatter for Transform3D strings

        Returns:
            List of formatted .tscn lines for both team HQs

        Note:
            Assumes asset_registry already has HQ_PlayerSpawner (ID "1")
            and SpawnPoint (ID "2") registered. These are standard Portal
            gameplay assets registered during initialization.
        """
        lines = []

        # Generate Team 1 HQ
        lines.extend(
            self._generate_team_hq(
                team_num=1,
                hq_transform=map_data.team1_hq,
                spawn_points=map_data.team1_spawns,
                asset_registry=asset_registry,
                transform_formatter=transform_formatter,
            )
        )

        # Generate Team 2 HQ
        lines.extend(
            self._generate_team_hq(
                team_num=2,
                hq_transform=map_data.team2_hq,
                spawn_points=map_data.team2_spawns,
                asset_registry=asset_registry,
                transform_formatter=transform_formatter,
            )
        )

        return lines

    def _generate_team_hq(
        self,
        team_num: int,
        hq_transform,
        spawn_points: list,
        asset_registry: AssetRegistry,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate HQ node for a single team.

        Args:
            team_num: Team number (1 or 2)
            hq_transform: Transform for HQ position
            spawn_points: List of SpawnPoint objects for this team
            asset_registry: Registry for ExtResource ID lookup
            transform_formatter: Formatter for Transform3D strings

        Returns:
            List of formatted .tscn lines for this team's HQ
        """
        lines = []

        # Build spawn path array
        spawn_paths = [
            f'NodePath("SpawnPoint_{team_num}_{i + 1}")' for i in range(len(spawn_points))
        ]
        spawn_paths_str = ", ".join(spawn_paths)

        # HQ node header
        lines.append(
            f'[node name="TEAM_{team_num}_HQ" parent="." '
            f'node_paths=PackedStringArray("HQArea", "InfantrySpawns") '
            f'instance=ExtResource("1")]'
        )
        lines.append(f"transform = {transform_formatter.format(hq_transform)}")
        lines.append(f"Team = {team_num}")
        lines.append("AltTeam = 0")  # Alternative team (usually 0)
        lines.append(f"ObjId = {team_num}")  # ObjId 1 for Team1, 2 for Team2
        lines.append(f'HQArea = NodePath("HQ_Team{team_num}")')
        lines.append(f"InfantrySpawns = [{spawn_paths_str}]")
        lines.append("")

        # HQ safety zone (50m radius Area3D polygon)
        lines.extend(self._generate_hq_safety_zone(team_num))

        # Spawn points (as children of HQ, with relative transforms)
        lines.extend(
            self._generate_spawn_points(
                team_num=team_num,
                hq_transform=hq_transform,
                spawn_points=spawn_points,
                transform_formatter=transform_formatter,
            )
        )

        return lines

    def _generate_hq_safety_zone(self, team_num: int) -> list[str]:
        """Generate HQ safety zone (Area3D polygon).

        Args:
            team_num: Team number (1 or 2)

        Returns:
            List of .tscn lines for safety zone
        """
        lines = []
        radius = HQ_PROTECTION_RADIUS_M

        lines.append(f'[node name="HQ_Team{team_num}" type="Area3D" parent="TEAM_{team_num}_HQ"]')
        lines.append(f"height = {HQ_PROTECTION_HEIGHT_M}")

        # Square polygon with 50m radius (100m x 100m square)
        lines.append(
            f"points = PackedVector2Array(-{radius}, -{radius}, {radius}, -{radius}, {radius}, {radius}, -{radius}, {radius})"
        )
        lines.append("")

        return lines

    def _generate_spawn_points(
        self,
        team_num: int,
        hq_transform,
        spawn_points: list,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate spawn point nodes for a team.

        Args:
            team_num: Team number (1 or 2)
            hq_transform: HQ transform (for calculating relative transforms)
            spawn_points: List of SpawnPoint objects
            transform_formatter: Formatter for Transform3D strings

        Returns:
            List of .tscn lines for all spawn points
        """
        lines = []

        for i, spawn in enumerate(spawn_points, 1):
            # Convert to relative transform (relative to HQ position)
            rel_transform = transform_formatter.make_relative(spawn.transform, hq_transform)

            lines.append(
                f'[node name="SpawnPoint_{team_num}_{i}" '
                f'parent="TEAM_{team_num}_HQ" instance=ExtResource("2")]'
            )
            lines.append(f"transform = {transform_formatter.format(rel_transform)}")
            lines.append("")

        return lines
