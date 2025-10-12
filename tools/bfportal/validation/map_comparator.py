#!/usr/bin/env python3
"""Map comparator for validation.

Single Responsibility: Only compares source map data vs output .tscn data.
"""

from dataclasses import dataclass
from typing import List, Tuple

from ..core.interfaces import MapData, Vector3
from .tscn_reader import TscnNode


@dataclass
class MapComparison:
    """Result of comparing source and output maps."""

    source_team1_spawn_count: int
    output_team1_spawn_count: int
    source_team2_spawn_count: int
    output_team2_spawn_count: int
    source_capture_point_count: int
    output_capture_point_count: int
    source_object_count: int
    output_object_count: int

    def has_spawn_mismatch(self) -> bool:
        """Check if spawn counts match."""
        return (
            self.source_team1_spawn_count != self.output_team1_spawn_count
            or self.source_team2_spawn_count != self.output_team2_spawn_count
        )

    def has_capture_point_mismatch(self) -> bool:
        """Check if capture point counts match."""
        return self.source_capture_point_count != self.output_capture_point_count

    def has_object_mismatch(self) -> bool:
        """Check if object counts match."""
        return self.source_object_count != self.output_object_count


class MapComparator:
    """Compares source map data with output .tscn nodes.

    Single Responsibility: Only responsible for comparing two data sets
    and producing comparison results. Does not validate or read files.
    """

    def compare(self, source_data: MapData, output_nodes: List[TscnNode]) -> MapComparison:
        """Compare source map data with output nodes.

        Args:
            source_data: Parsed source map data
            output_nodes: Parsed .tscn nodes

        Returns:
            MapComparison with counts
        """
        # Count output spawns
        output_team1_spawns = self._count_team_spawns(output_nodes, 1)
        output_team2_spawns = self._count_team_spawns(output_nodes, 2)

        # Count output capture points (exclude static props)
        output_capture_points = self._count_capture_points(output_nodes)

        # Count output objects (everything with a transform)
        output_object_count = len(output_nodes)

        return MapComparison(
            source_team1_spawn_count=len(source_data.team1_spawns),
            output_team1_spawn_count=output_team1_spawns,
            source_team2_spawn_count=len(source_data.team2_spawns),
            output_team2_spawn_count=output_team2_spawns,
            source_capture_point_count=len(source_data.capture_points),
            output_capture_point_count=output_capture_points,
            source_object_count=len(source_data.game_objects),
            output_object_count=output_object_count,
        )

    def _count_team_spawns(self, nodes: List[TscnNode], team: int) -> int:
        """Count spawn points for a specific team.

        Single Responsibility: Only counts spawns for one team.

        Args:
            nodes: List of nodes
            team: Team number (1 or 2)

        Returns:
            Count of spawns
        """
        return sum(1 for node in nodes if f"SpawnPoint_{team}_" in node.name)

    def _count_capture_points(self, nodes: List[TscnNode]) -> int:
        """Count capture points (excluding static props).

        Single Responsibility: Only counts capture points.

        Args:
            nodes: List of nodes

        Returns:
            Count of capture points
        """
        return sum(
            1
            for node in nodes
            if node.name.startswith("CapturePoint_") and 'parent="Static"' not in node.raw_content
        )

    def calculate_position_centroid(self, nodes: List[TscnNode]) -> Vector3:
        """Calculate centroid of node positions.

        Args:
            nodes: List of nodes

        Returns:
            Centroid position
        """
        if not nodes:
            return Vector3(0, 0, 0)

        total_x = sum(node.position.x for node in nodes)
        total_y = sum(node.position.y for node in nodes)
        total_z = sum(node.position.z for node in nodes)
        count = len(nodes)

        return Vector3(total_x / count, total_y / count, total_z / count)

    def calculate_bounds(self, nodes: List[TscnNode]) -> Tuple[Vector3, Vector3]:
        """Calculate bounding box of nodes.

        Args:
            nodes: List of nodes

        Returns:
            Tuple of (min_point, max_point)
        """
        if not nodes:
            return (Vector3(0, 0, 0), Vector3(0, 0, 0))

        positions = [node.position for node in nodes]

        min_point = Vector3(
            min(p.x for p in positions), min(p.y for p in positions), min(p.z for p in positions)
        )

        max_point = Vector3(
            max(p.x for p in positions), max(p.y for p in positions), max(p.z for p in positions)
        )

        return (min_point, max_point)
