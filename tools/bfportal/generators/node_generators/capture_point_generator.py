#!/usr/bin/env python3
"""Capture point node generator for .tscn generation.

Single Responsibility: Generate CapturePoint nodes with spawn assignments.
Follows SOLID principles and DRY patterns.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-12
"""

from ...core.interfaces import MapData, Transform, Vector3
from ..components.asset_registry import AssetRegistry
from ..components.transform_formatter import TransformFormatter
from ..constants.extresource_ids import (
    EXT_RESOURCE_CAPTURE_POINT,
    EXT_RESOURCE_POLYGON_VOLUME,
    EXT_RESOURCE_SPAWN_POINT,
)
from ..constants.gameplay import CAPTURE_ZONE_HEIGHT_M, OBJID_CAPTURE_POINTS_START
from .base_generator import BaseNodeGenerator


class CapturePointGenerator(BaseNodeGenerator):
    """Generates CapturePoint nodes with neutral spawns for both teams.

    This generator creates Conquest-style capture points with:
    - Main CapturePoint node (neutral by default)
    - Capture zone based on BF1942 radius
    - Team 1 spawn points (when captured by Team 1)
    - Team 2 spawn points (when captured by Team 2)
    - Proper node hierarchy and transforms
    - Terrain snapping support (min_safe_y parameter)

    Example Output:
        [node name="CapturePointA" parent="." node_paths=PackedStringArray("CaptureArea", "InfantrySpawnPoints_Team1", "InfantrySpawnPoints_Team2") instance=ExtResource("3")]
        transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 0, 200)
        ObjId = 101
        CaptureArea = NodePath("CapturePointArea")
        InfantrySpawnPoints_Team1 = [NodePath("CPA_Spawn_1_1"), ...]
        InfantrySpawnPoints_Team2 = [NodePath("CPA_Spawn_2_1"), ...]

        [node name="CapturePointArea" parent="CapturePointA" instance=ExtResource("10")]
        height = 50.0
        points = PackedVector2Array(-25, -25, 25, -25, 25, 25, -25, 25)

        [node name="CPA_Spawn_1_1" parent="CapturePointA" instance=ExtResource("2")]
        transform = Transform3D(...)
    """

    def generate(
        self,
        map_data: MapData,
        asset_registry: AssetRegistry,
        transform_formatter: TransformFormatter,
        min_safe_y: float = 0.0,
    ) -> list[str]:
        """Generate capture point nodes with spawn points.

        Args:
            map_data: Map data containing capture points
            asset_registry: Registry for ExtResource lookups
            transform_formatter: Formatter for Transform3D strings
            min_safe_y: Minimum safe Y position (above terrain) for snapping

        Returns:
            List of .tscn lines for all capture points

        Note:
            - Uses constants for ExtResource IDs (EXT_RESOURCE_CAPTURE_POINT, etc.)
            - ObjId starts at OBJID_CAPTURE_POINTS_START (101)
            - Ensures capture points are above terrain for proper snapping
        """
        lines: list[str] = []

        if not map_data.capture_points:
            return lines

        for i, cp in enumerate(map_data.capture_points, 1):
            # __post_init__ ensures these are never None, but need explicit check for mypy
            team1_spawns = cp.team1_spawns if cp.team1_spawns is not None else []
            team2_spawns = cp.team2_spawns if cp.team2_spawns is not None else []

            # Use letter-based naming (A, B, C, etc.) to match Portal SDK convention
            label = cp.label  # "A", "B", "C", etc.

            # Build spawn arrays
            team1_spawn_paths = [
                f'NodePath("CP{label}_Spawn_1_{j + 1}")' for j in range(len(team1_spawns))
            ]
            team2_spawn_paths = [
                f'NodePath("CP{label}_Spawn_2_{j + 1}")' for j in range(len(team2_spawns))
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

            # Main CapturePoint node
            lines.append(
                f'[node name="CapturePoint{label}" parent="." node_paths=PackedStringArray({node_paths_str}) instance=ExtResource("{EXT_RESOURCE_CAPTURE_POINT}")]'
            )
            # Ensure capture point is above terrain for snapping
            safe_cp_transform = self._ensure_safe_height(cp.transform, min_safe_y)
            lines.append(f"transform = {transform_formatter.format(safe_cp_transform)}")
            lines.append(f"ObjId = {OBJID_CAPTURE_POINTS_START + i}")
            lines.append("OutlineAbove16Points = true")
            lines.append("TacticalAdvicePriorityLevel_Team1 = 1")
            lines.append("TacticalAdvicePriorityLevel_Team2 = 1")
            lines.append('CaptureArea = NodePath("CapturePointArea")')

            # Add spawn arrays if capture point has spawns
            if team1_spawn_paths:
                lines.append(f"InfantrySpawnPoints_Team1 = [{team1_spawns_str}]")
            if team2_spawn_paths:
                lines.append(f"InfantrySpawnPoints_Team2 = [{team2_spawns_str}]")

            lines.append("")

            # Add capture zone using BF1942 radius (use PolygonVolume instance for Portal SDK compatibility)
            radius = cp.radius
            lines.append(
                f'[node name="CapturePointArea" parent="CapturePoint{label}" instance=ExtResource("{EXT_RESOURCE_POLYGON_VOLUME}")]'
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
                    f'[node name="CP{label}_Spawn_1_{j}" parent="CapturePoint{label}" instance=ExtResource("{EXT_RESOURCE_SPAWN_POINT}")]'
                )
                rel_transform = transform_formatter.make_relative(
                    spawn.transform, safe_cp_transform
                )
                lines.append(f"transform = {transform_formatter.format(rel_transform)}")
                lines.append("")

            for j, spawn in enumerate(team2_spawns, 1):
                lines.append(
                    f'[node name="CP{label}_Spawn_2_{j}" parent="CapturePoint{label}" instance=ExtResource("{EXT_RESOURCE_SPAWN_POINT}")]'
                )
                rel_transform = transform_formatter.make_relative(
                    spawn.transform, safe_cp_transform
                )
                lines.append(f"transform = {transform_formatter.format(rel_transform)}")
                lines.append("")

        return lines

    def _ensure_safe_height(self, transform: Transform, min_safe_y: float) -> Transform:
        """Ensure transform Y position is above minimum safe height.

        This prevents objects from being placed underground where terrain snapping
        cannot work (raycast finds no collision below them).

        Args:
            transform: Original transform
            min_safe_y: Minimum safe Y position (above terrain)

        Returns:
            Transform with Y position clamped to min_safe_y if needed
        """
        if transform.position.y < min_safe_y:
            # Clamp Y to minimum safe height
            safe_pos = Vector3(
                transform.position.x,
                min_safe_y,
                transform.position.z,
            )
            return Transform(safe_pos, transform.rotation, transform.scale)
        return transform
