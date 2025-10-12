#!/usr/bin/env python3
"""Production TSCN Generator - Creates complete Portal-compatible .tscn files.

This generator creates full Godot 4 scene files with all Portal requirements:
- ExtResource references
- HQ nodes with spawn assignments
- Combat area with polygon boundaries
- Capture points (if applicable)
- Vehicle spawners
- Proper node hierarchy
- Resource management

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-11
"""

import math
from pathlib import Path
from typing import Dict, List

from ..core.exceptions import ValidationError
from ..core.interfaces import (
    CapturePoint,
    GameObject,
    ISceneGenerator,
    MapData,
    Transform,
    Vector3,
)


class TscnGenerator(ISceneGenerator):
    """Production-quality .tscn scene generator.

    Generates complete Godot 4 scenes with all Portal-required components.
    """

    def __init__(self):
        """Initialize generator."""
        self.ext_resources: List[Dict] = []
        self.next_ext_resource_id = 1
        self.base_terrain: str = ""

    def generate(
        self, map_data: MapData, output_path: Path, base_terrain: str = "MP_Tungsten"
    ) -> None:
        """Generate .tscn file from map data.

        Args:
            map_data: Parsed and transformed map data
            output_path: Output .tscn file path
            base_terrain: Portal base terrain name (e.g., "MP_Tungsten")

        Raises:
            ValidationError: If map data is invalid
        """
        self.base_terrain = base_terrain
        # Validate map data
        self._validate_map_data(map_data)

        # Initialize ext_resources
        self._init_ext_resources()

        # Build scene content
        lines = []

        # Header
        load_steps = len(self.ext_resources) + 1
        lines.append(f"[gd_scene load_steps={load_steps} format=3]")
        lines.append("")

        # ExtResources
        for resource in self.ext_resources:
            lines.append(
                f'[ext_resource type="{resource["type"]}" '
                f'path="{resource["path"]}" id="{resource["id"]}"]'
            )
        lines.append("")

        # Root node
        lines.append(f'[node name="{map_data.map_name}" type="Node3D"]')
        lines.append("")

        # Team HQs and spawns
        lines.extend(self._generate_hqs(map_data))

        # Capture points
        if map_data.capture_points:
            lines.extend(self._generate_capture_points(map_data.capture_points))

        # Vehicle spawners (from game_objects)
        vehicle_spawners = [
            obj
            for obj in map_data.game_objects
            if "vehicle" in obj.asset_type.lower() or "spawner" in obj.asset_type.lower()
        ]
        if vehicle_spawners:
            lines.extend(self._generate_vehicle_spawners(vehicle_spawners))

        # Combat area
        lines.extend(self._generate_combat_area(map_data))

        # Static layer (terrain + other objects)
        lines.extend(self._generate_static_layer(map_data))

        # Write file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write("\n".join(lines))

    def _validate_map_data(self, map_data: MapData) -> None:
        """Validate map data has required components.

        Args:
            map_data: Map data to validate

        Raises:
            ValidationError: If required components missing
        """
        # Check for HQs (stored as transforms in MapData)
        if not map_data.team1_hq:
            raise ValidationError("Missing Team 1 HQ")
        if not map_data.team2_hq:
            raise ValidationError("Missing Team 2 HQ")

        # Check for spawns
        if len(map_data.team1_spawns) < 4:
            raise ValidationError(
                f"Team 1 needs at least 4 spawns, got {len(map_data.team1_spawns)}"
            )
        if len(map_data.team2_spawns) < 4:
            raise ValidationError(
                f"Team 2 needs at least 4 spawns, got {len(map_data.team2_spawns)}"
            )

    def _init_ext_resources(self) -> None:
        """Initialize ExtResource list with Portal SDK paths."""
        self.ext_resources = [
            {
                "id": "1",
                "type": "PackedScene",
                "path": "res://objects/Gameplay/Common/HQ_PlayerSpawner.tscn",
            },
            {"id": "2", "type": "PackedScene", "path": "res://objects/entities/SpawnPoint.tscn"},
            {
                "id": "3",
                "type": "PackedScene",
                "path": "res://objects/Gameplay/Conquest/CapturePoint.tscn",
            },
            {
                "id": "4",
                "type": "PackedScene",
                "path": "res://objects/Gameplay/Common/VehicleSpawner.tscn",
            },
            {
                "id": "5",
                "type": "PackedScene",
                "path": "res://objects/Gameplay/Common/CombatArea.tscn",
            },
            {
                "id": "6",
                "type": "PackedScene",
                "path": f"res://static/{self.base_terrain}_Terrain.tscn",
            },
        ]
        self.next_ext_resource_id = 7

    def _format_transform(self, transform: Transform) -> str:
        """Format Transform to Transform3D string.

        Args:
            transform: Transform to format

        Returns:
            Transform3D string
        """
        # Convert rotation (pitch, yaw, roll) to rotation matrix
        # Using ZYX Euler angles
        pitch = math.radians(transform.rotation.pitch)
        yaw = math.radians(transform.rotation.yaw)
        roll = math.radians(transform.rotation.roll)

        # Rotation matrix from Euler angles
        cos_p, sin_p = math.cos(pitch), math.sin(pitch)
        cos_y, sin_y = math.cos(yaw), math.sin(yaw)
        cos_r, sin_r = math.cos(roll), math.sin(roll)

        # Combined rotation matrix (ZYX order)
        m00 = cos_y * cos_p
        m01 = cos_y * sin_p * sin_r - sin_y * cos_r
        m02 = cos_y * sin_p * cos_r + sin_y * sin_r

        m10 = sin_y * cos_p
        m11 = sin_y * sin_p * sin_r + cos_y * cos_r
        m12 = sin_y * sin_p * cos_r - cos_y * sin_r

        m20 = -sin_p
        m21 = cos_p * sin_r
        m22 = cos_p * cos_r

        return (
            f"Transform3D({m00:.6g}, {m01:.6g}, {m02:.6g}, "
            f"{m10:.6g}, {m11:.6g}, {m12:.6g}, "
            f"{m20:.6g}, {m21:.6g}, {m22:.6g}, "
            f"{transform.position.x:.6g}, {transform.position.y:.6g}, {transform.position.z:.6g})"
        )

    def _generate_hqs(self, map_data: MapData) -> List[str]:
        """Generate HQ nodes with spawn points.

        Args:
            map_data: Map data

        Returns:
            List of .tscn lines
        """
        lines = []

        # Team 1 HQ
        team1_hq_transform = map_data.team1_hq
        team1_spawns = map_data.team1_spawns

        # Build spawn paths array
        spawn_paths = [f'NodePath("SpawnPoint_1_{i + 1}")' for i in range(len(team1_spawns))]
        spawn_paths_str = ", ".join(spawn_paths)

        lines.append(
            '[node name="TEAM_1_HQ" parent="." node_paths=PackedStringArray("HQArea", "InfantrySpawns") instance=ExtResource("1")]'
        )
        lines.append(f"transform = {self._format_transform(team1_hq_transform)}")
        lines.append("Team = 1")
        lines.append("AltTeam = 0")
        lines.append("ObjId = 1")
        lines.append('HQArea = NodePath("HQ_Team1")')
        lines.append(f"InfantrySpawns = [{spawn_paths_str}]")
        lines.append("")

        # Team 1 HQ Area (safety zone) - 50m radius matching BF1942
        lines.append('[node name="HQ_Team1" type="Area3D" parent="TEAM_1_HQ"]')
        lines.append("height = 50.0")
        # Create a 50m radius square around HQ
        lines.append("points = PackedVector2Array(-50, -50, 50, -50, 50, 50, -50, 50)")
        lines.append("")

        # Team 1 spawns (relative to HQ)
        for i, spawn in enumerate(team1_spawns, 1):
            lines.append(
                f'[node name="SpawnPoint_1_{i}" parent="TEAM_1_HQ" instance=ExtResource("2")]'
            )
            # Use spawn's actual transform (relative to HQ)
            rel_transform = self._make_relative_transform(spawn.transform, team1_hq_transform)
            lines.append(f"transform = {self._format_transform(rel_transform)}")
            lines.append("")

        # Team 2 HQ
        team2_hq_transform = map_data.team2_hq
        team2_spawns = map_data.team2_spawns

        spawn_paths = [f'NodePath("SpawnPoint_2_{i + 1}")' for i in range(len(team2_spawns))]
        spawn_paths_str = ", ".join(spawn_paths)

        lines.append(
            '[node name="TEAM_2_HQ" parent="." node_paths=PackedStringArray("HQArea", "InfantrySpawns") instance=ExtResource("1")]'
        )
        lines.append(f"transform = {self._format_transform(team2_hq_transform)}")
        lines.append("Team = 2")
        lines.append("AltTeam = 0")
        lines.append("ObjId = 2")
        lines.append('HQArea = NodePath("HQ_Team2")')
        lines.append(f"InfantrySpawns = [{spawn_paths_str}]")
        lines.append("")

        # Team 2 HQ Area (safety zone) - 50m radius matching BF1942
        lines.append('[node name="HQ_Team2" type="Area3D" parent="TEAM_2_HQ"]')
        lines.append("height = 50.0")
        # Create a 50m radius square around HQ
        lines.append("points = PackedVector2Array(-50, -50, 50, -50, 50, 50, -50, 50)")
        lines.append("")

        # Team 2 spawns
        for i, spawn in enumerate(team2_spawns, 1):
            lines.append(
                f'[node name="SpawnPoint_2_{i}" parent="TEAM_2_HQ" instance=ExtResource("2")]'
            )
            rel_transform = self._make_relative_transform(spawn.transform, team2_hq_transform)
            lines.append(f"transform = {self._format_transform(rel_transform)}")
            lines.append("")

        return lines

    def _make_relative_transform(self, child: Transform, parent: Transform) -> Transform:
        """Make child transform relative to parent.

        Args:
            child: Child's world transform
            parent: Parent's world transform

        Returns:
            Relative transform
        """
        # Simple approach: subtract parent position
        rel_pos = Vector3(
            child.position.x - parent.position.x,
            child.position.y - parent.position.y,
            child.position.z - parent.position.z,
        )

        # Keep rotation as-is for now (proper solution would account for parent rotation)
        return Transform(rel_pos, child.rotation, child.scale)

    def _generate_capture_points(self, capture_points: List[CapturePoint]) -> List[str]:
        """Generate capture point nodes with spawn points.

        Args:
            capture_points: List of capture points

        Returns:
            List of .tscn lines
        """
        lines = []

        for i, cp in enumerate(capture_points, 1):
            # Build spawn arrays
            team1_spawn_paths = [
                f'NodePath("CP{i}_Spawn_1_{j + 1}")' for j in range(len(cp.team1_spawns))
            ]
            team2_spawn_paths = [
                f'NodePath("CP{i}_Spawn_2_{j + 1}")' for j in range(len(cp.team2_spawns))
            ]

            team1_spawns_str = ", ".join(team1_spawn_paths) if team1_spawn_paths else ""
            team2_spawns_str = ", ".join(team2_spawn_paths) if team2_spawn_paths else ""

            lines.append(f'[node name="CapturePoint_{i}" parent="." instance=ExtResource("3")]')
            lines.append(f"transform = {self._format_transform(cp.transform)}")
            lines.append("Team = 0")  # Neutral
            lines.append(f"ObjId = {100 + i}")

            # Add spawn arrays if capture point has spawns
            if team1_spawn_paths:
                lines.append(f"InfantrySpawnPoints_Team1 = [{team1_spawns_str}]")
            if team2_spawn_paths:
                lines.append(f"InfantrySpawnPoints_Team2 = [{team2_spawns_str}]")

            lines.append("")

            # Add capture zone using BF1942 radius
            radius = cp.radius
            lines.append(f'[node name="CaptureZone_{i}" type="Area3D" parent="CapturePoint_{i}"]')
            lines.append("height = 50.0")
            # Create square capture zone with BF1942 radius
            lines.append(
                f"points = PackedVector2Array(-{radius}, -{radius}, {radius}, -{radius}, {radius}, {radius}, -{radius}, {radius})"
            )
            lines.append("")

            # Generate spawn point nodes as children of the capture point
            for j, spawn in enumerate(cp.team1_spawns, 1):
                lines.append(
                    f'[node name="CP{i}_Spawn_1_{j}" parent="CapturePoint_{i}" instance=ExtResource("2")]'
                )
                rel_transform = self._make_relative_transform(spawn.transform, cp.transform)
                lines.append(f"transform = {self._format_transform(rel_transform)}")
                lines.append("")

            for j, spawn in enumerate(cp.team2_spawns, 1):
                lines.append(
                    f'[node name="CP{i}_Spawn_2_{j}" parent="CapturePoint_{i}" instance=ExtResource("2")]'
                )
                rel_transform = self._make_relative_transform(spawn.transform, cp.transform)
                lines.append(f"transform = {self._format_transform(rel_transform)}")
                lines.append("")

        return lines

    def _generate_vehicle_spawners(self, spawners: List[GameObject]) -> List[str]:
        """Generate vehicle spawner nodes.

        Args:
            spawners: List of vehicle spawner objects

        Returns:
            List of .tscn lines
        """
        lines = []

        for i, spawner in enumerate(spawners, 1):
            lines.append(f'[node name="VehicleSpawner_{i}" parent="." instance=ExtResource("4")]')
            lines.append(f"transform = {self._format_transform(spawner.transform)}")
            lines.append(f"Team = {spawner.team.value if spawner.team else 0}")
            lines.append(f"ObjId = {1000 + i}")

            # Vehicle template (use Portal asset name)
            vehicle_template = spawner.asset_type
            lines.append(f'VehicleTemplate = "{vehicle_template}"')
            lines.append("")

        return lines

    def _generate_combat_area(self, map_data: MapData) -> List[str]:
        """Generate combat area with polygon boundary.

        Args:
            map_data: Map data with bounds

        Returns:
            List of .tscn lines
        """
        lines = []

        if not map_data.bounds:
            # Create default bounds
            print("⚠️  Warning: No bounds provided, using default 2048x2048")
            min_x, max_x = -1024, 1024
            min_z, max_z = -1024, 1024
            center_x, center_z = 0, 0
            center_y = 80.0
        else:
            min_x = map_data.bounds.min_point.x
            max_x = map_data.bounds.max_point.x
            min_z = map_data.bounds.min_point.z
            max_z = map_data.bounds.max_point.z
            center_x = (min_x + max_x) / 2
            center_z = (min_z + max_z) / 2
            center_y = (map_data.bounds.min_point.y + map_data.bounds.max_point.y) / 2

        # Calculate relative coordinates for polygon
        half_width = (max_x - min_x) / 2
        half_depth = (max_z - min_z) / 2

        lines.append(
            '[node name="CombatArea" parent="." node_paths=PackedStringArray("CombatVolume") instance=ExtResource("5")]'
        )
        lines.append(
            f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {center_x}, {center_y}, {center_z})"
        )
        lines.append('CombatVolume = NodePath("CollisionPolygon3D")')
        lines.append("")

        lines.append('[node name="CollisionPolygon3D" type="Area3D" parent="CombatArea"]')
        lines.append("height = 200.0")

        # Create rectangular boundary (relative to CombatArea center)
        lines.append(
            f"points = PackedVector2Array({-half_width}, {-half_depth}, "
            f"{half_width}, {-half_depth}, "
            f"{half_width}, {half_depth}, "
            f"{-half_width}, {half_depth})"
        )
        lines.append("")

        return lines

    def _generate_static_layer(self, map_data: MapData) -> List[str]:
        """Generate static layer with terrain and objects.

        Args:
            map_data: Map data

        Returns:
            List of .tscn lines
        """
        lines = []

        lines.append('[node name="Static" type="Node3D" parent="."]')
        lines.append("")

        # Terrain with rotation (if needed)
        terrain_rotation = map_data.metadata.get("terrain_rotation", 0)

        if terrain_rotation != 0:
            # Apply Y-axis rotation to terrain
            rotation_rad = math.radians(terrain_rotation)
            cos_r = math.cos(rotation_rad)
            sin_r = math.sin(rotation_rad)

            # Rotation matrix for Y-axis rotation
            # [cos, 0, sin]
            # [0,   1, 0  ]
            # [-sin, 0, cos]
            terrain_transform = (
                f"Transform3D({cos_r:.6g}, 0, {sin_r:.6g}, "
                f"0, 1, 0, "
                f"{-sin_r:.6g}, 0, {cos_r:.6g}, "
                f"0, 0, 0)"
            )

            lines.append(
                f'[node name="{self.base_terrain}_Terrain" parent="Static" instance=ExtResource("6")]'
            )
            lines.append(f"transform = {terrain_transform}")
        else:
            lines.append(
                f'[node name="{self.base_terrain}_Terrain" parent="Static" instance=ExtResource("6")]'
            )

        lines.append("")

        # Other static objects (exclude gameplay elements that are handled separately)
        static_objects = [
            obj
            for obj in map_data.game_objects
            if "vehicle" not in obj.asset_type.lower()
            and "spawner" not in obj.asset_type.lower()
            and "spawnpoint" not in obj.asset_type.lower()
            and "spawn" not in obj.asset_type.lower()
            and "controlpoint" not in obj.asset_type.lower()
            and "capturepoint" not in obj.asset_type.lower()
            and "cpoint" not in obj.asset_type.lower()
        ]

        for i, obj in enumerate(static_objects, 1):
            lines.append(f'[node name="{obj.asset_type}_{i}" type="Node3D" parent="Static"]')
            lines.append(f"transform = {self._format_transform(obj.transform)}")
            lines.append("")

        return lines

    def validate(self, tscn_path: Path) -> List[str]:
        """Validate generated .tscn file.

        Args:
            tscn_path: Path to .tscn file

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not tscn_path.exists():
            errors.append(f"File not found: {tscn_path}")
            return errors

        # Basic validation - check for required nodes
        with open(tscn_path) as f:
            content = f.read()

        if "TEAM_1_HQ" not in content:
            errors.append("Missing TEAM_1_HQ node")
        if "TEAM_2_HQ" not in content:
            errors.append("Missing TEAM_2_HQ node")
        if "CombatArea" not in content:
            errors.append("Missing CombatArea node")

        return errors
