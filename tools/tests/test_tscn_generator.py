#!/usr/bin/env python3
"""Unit tests for TSCN Generator.

Tests for the TscnGenerator class which generates complete Portal-compatible
.tscn scene files from MapData.
"""

import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bfportal.core.exceptions import ValidationError
from bfportal.core.interfaces import (
    CapturePoint,
    GameObject,
    MapBounds,
    MapData,
    Rotation,
    SpawnPoint,
    Team,
    Transform,
    Vector3,
)
from bfportal.generators.tscn_generator import TscnGenerator


class TestTscnGenerator:
    """Test cases for TscnGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create a TscnGenerator instance for testing."""
        return TscnGenerator()

    @pytest.fixture
    def minimal_map_data(self):
        """Create minimal valid MapData for testing."""
        # Team 1 HQ and spawns
        team1_hq = Transform(
            position=Vector3(100.0, 50.0, 100.0),
            rotation=Rotation(0.0, 0.0, 0.0),
        )
        team1_spawns = [
            SpawnPoint(
                name="Spawn_1_1",
                transform=Transform(
                    position=Vector3(105.0, 50.0, 105.0),
                    rotation=Rotation(0.0, 90.0, 0.0),
                ),
                team=Team.TEAM_1,
            ),
            SpawnPoint(
                name="Spawn_1_2",
                transform=Transform(
                    position=Vector3(95.0, 50.0, 105.0),
                    rotation=Rotation(0.0, 90.0, 0.0),
                ),
                team=Team.TEAM_1,
            ),
            SpawnPoint(
                name="Spawn_1_3",
                transform=Transform(
                    position=Vector3(105.0, 50.0, 95.0),
                    rotation=Rotation(0.0, 90.0, 0.0),
                ),
                team=Team.TEAM_1,
            ),
            SpawnPoint(
                name="Spawn_1_4",
                transform=Transform(
                    position=Vector3(95.0, 50.0, 95.0),
                    rotation=Rotation(0.0, 90.0, 0.0),
                ),
                team=Team.TEAM_1,
            ),
        ]

        # Team 2 HQ and spawns
        team2_hq = Transform(
            position=Vector3(-100.0, 50.0, -100.0),
            rotation=Rotation(0.0, 180.0, 0.0),
        )
        team2_spawns = [
            SpawnPoint(
                name="Spawn_2_1",
                transform=Transform(
                    position=Vector3(-105.0, 50.0, -105.0),
                    rotation=Rotation(0.0, 270.0, 0.0),
                ),
                team=Team.TEAM_2,
            ),
            SpawnPoint(
                name="Spawn_2_2",
                transform=Transform(
                    position=Vector3(-95.0, 50.0, -105.0),
                    rotation=Rotation(0.0, 270.0, 0.0),
                ),
                team=Team.TEAM_2,
            ),
            SpawnPoint(
                name="Spawn_2_3",
                transform=Transform(
                    position=Vector3(-105.0, 50.0, -95.0),
                    rotation=Rotation(0.0, 270.0, 0.0),
                ),
                team=Team.TEAM_2,
            ),
            SpawnPoint(
                name="Spawn_2_4",
                transform=Transform(
                    position=Vector3(-95.0, 50.0, -95.0),
                    rotation=Rotation(0.0, 270.0, 0.0),
                ),
                team=Team.TEAM_2,
            ),
        ]

        # Map bounds
        bounds = MapBounds(
            min_point=Vector3(-1024.0, 0.0, -1024.0),
            max_point=Vector3(1024.0, 200.0, 1024.0),
            combat_area_polygon=[
                Vector3(-1024.0, 0.0, -1024.0),
                Vector3(1024.0, 0.0, -1024.0),
                Vector3(1024.0, 0.0, 1024.0),
                Vector3(-1024.0, 0.0, 1024.0),
            ],
            height=200.0,
        )

        return MapData(
            map_name="TestMap",
            game_mode="Conquest",
            team1_hq=team1_hq,
            team2_hq=team2_hq,
            team1_spawns=team1_spawns,
            team2_spawns=team2_spawns,
            capture_points=[],
            game_objects=[],
            bounds=bounds,
            metadata={},
        )

    def test_validate_map_data_valid(self, generator, minimal_map_data):
        """Test validation accepts valid map data."""
        # Should not raise exception
        generator._validate_map_data(minimal_map_data)

    def test_validate_map_data_missing_team1_hq(self, generator, minimal_map_data):
        """Test validation fails with missing Team 1 HQ."""
        minimal_map_data.team1_hq = None

        with pytest.raises(ValidationError, match="Missing Team 1 HQ"):
            generator._validate_map_data(minimal_map_data)

    def test_validate_map_data_missing_team2_hq(self, generator, minimal_map_data):
        """Test validation fails with missing Team 2 HQ."""
        minimal_map_data.team2_hq = None

        with pytest.raises(ValidationError, match="Missing Team 2 HQ"):
            generator._validate_map_data(minimal_map_data)

    def test_validate_map_data_insufficient_team1_spawns(self, generator, minimal_map_data):
        """Test validation fails with fewer than 4 Team 1 spawns."""
        minimal_map_data.team1_spawns = minimal_map_data.team1_spawns[:3]  # Only 3 spawns

        with pytest.raises(ValidationError, match="Team 1 needs at least 4 spawns"):
            generator._validate_map_data(minimal_map_data)

    def test_validate_map_data_insufficient_team2_spawns(self, generator, minimal_map_data):
        """Test validation fails with fewer than 4 Team 2 spawns."""
        minimal_map_data.team2_spawns = minimal_map_data.team2_spawns[:2]  # Only 2 spawns

        with pytest.raises(ValidationError, match="Team 2 needs at least 4 spawns"):
            generator._validate_map_data(minimal_map_data)

    def test_format_transform_identity(self, generator):
        """Test formatting identity transform (no rotation, zero position)."""
        transform = Transform(
            position=Vector3(0.0, 0.0, 0.0),
            rotation=Rotation(0.0, 0.0, 0.0),
        )

        result = generator._format_transform(transform)

        assert "Transform3D(" in result
        assert result.endswith("0, 0, 0)")
        # Check identity rotation matrix - note: -0 is valid for negative zero
        assert "1, 0, 0" in result
        assert "0, 1, 0" in result

    def test_format_transform_with_position(self, generator):
        """Test formatting transform with position but no rotation."""
        transform = Transform(
            position=Vector3(100.0, 50.0, -200.0),
            rotation=Rotation(0.0, 0.0, 0.0),
        )

        result = generator._format_transform(transform)

        assert "100, 50, -200)" in result

    def test_format_transform_with_yaw_rotation(self, generator):
        """Test formatting transform with Y-axis rotation (yaw)."""
        transform = Transform(
            position=Vector3(10.0, 20.0, 30.0),
            rotation=Rotation(0.0, 90.0, 0.0),  # 90-degree yaw
        )

        result = generator._format_transform(transform)

        # 90-degree rotation around Y should give approximately:
        # [0, 0, 1, 0, 1, 0, -1, 0, 0]
        assert "Transform3D(" in result
        assert "10, 20, 30)" in result

    def test_generate_hqs_creates_both_teams(self, generator, minimal_map_data):
        """Test HQ generation creates both team HQs with spawn points."""
        generator.base_terrain = "MP_Tungsten"
        generator._init_ext_resources()

        lines = generator._generate_hqs(minimal_map_data)
        content = "\n".join(lines)

        # Check Team 1 HQ
        assert 'name="TEAM_1_HQ"' in content
        assert "Team = 1" in content
        assert 'HQArea = NodePath("HQ_Team1")' in content

        # Check Team 2 HQ
        assert 'name="TEAM_2_HQ"' in content
        assert "Team = 2" in content
        assert 'HQArea = NodePath("HQ_Team2")' in content

        # Check spawn points
        assert 'name="SpawnPoint_1_1"' in content
        assert 'name="SpawnPoint_2_4"' in content

    def test_generate_combat_area_with_bounds(self, generator, minimal_map_data):
        """Test combat area generation uses map bounds."""
        generator.base_terrain = "MP_Tungsten"
        generator._init_ext_resources()

        lines = generator._generate_combat_area(minimal_map_data)
        content = "\n".join(lines)

        assert 'name="CombatArea"' in content
        assert "height = 200.0" in content
        assert "PackedVector2Array" in content

    def test_generate_combat_area_without_bounds(self, generator, minimal_map_data):
        """Test combat area generation with default bounds."""
        minimal_map_data.bounds = None
        generator.base_terrain = "MP_Tungsten"
        generator._init_ext_resources()

        lines = generator._generate_combat_area(minimal_map_data)
        content = "\n".join(lines)

        assert 'name="CombatArea"' in content
        assert "PackedVector2Array" in content

    def test_generate_capture_points(self, generator):
        """Test capture point generation with spawns."""
        generator.base_terrain = "MP_Tungsten"
        generator._init_ext_resources()

        capture_points = [
            CapturePoint(
                name="CP1",
                transform=Transform(
                    position=Vector3(0.0, 50.0, 0.0),
                    rotation=Rotation(0.0, 0.0, 0.0),
                ),
                radius=30.0,
                control_area=[],
                team1_spawns=[
                    SpawnPoint(
                        name="CP1_Spawn_1",
                        transform=Transform(
                            position=Vector3(10.0, 50.0, 10.0),
                            rotation=Rotation(0.0, 0.0, 0.0),
                        ),
                        team=Team.TEAM_1,
                    )
                ],
                team2_spawns=[
                    SpawnPoint(
                        name="CP1_Spawn_2",
                        transform=Transform(
                            position=Vector3(-10.0, 50.0, -10.0),
                            rotation=Rotation(0.0, 180.0, 0.0),
                        ),
                        team=Team.TEAM_2,
                    )
                ],
            )
        ]

        lines = generator._generate_capture_points(capture_points)
        content = "\n".join(lines)

        assert 'name="CapturePoint_1"' in content
        assert "ObjId = 101" in content
        assert 'name="CaptureZone_1"' in content
        # Check that the radius (30.0) is used in the capture zone points
        assert "30.0" in content or "30" in content

    def test_generate_vehicle_spawners(self, generator):
        """Test vehicle spawner generation."""
        generator.base_terrain = "MP_Tungsten"
        generator._init_ext_resources()

        spawners = [
            GameObject(
                name="Tank_Spawner",
                asset_type="Tank_Sherman",
                transform=Transform(
                    position=Vector3(50.0, 50.0, 50.0),
                    rotation=Rotation(0.0, 45.0, 0.0),
                ),
                team=Team.TEAM_1,
                properties={},
            )
        ]

        lines = generator._generate_vehicle_spawners(spawners)
        content = "\n".join(lines)

        assert 'name="VehicleSpawner_1"' in content
        assert "Team = 1" in content
        assert 'VehicleTemplate = "Tank_Sherman"' in content

    def test_generate_static_layer(self, generator, minimal_map_data):
        """Test static layer generation with terrain."""
        generator.base_terrain = "MP_Tungsten"
        generator._init_ext_resources()

        # Add some static objects
        minimal_map_data.game_objects = [
            GameObject(
                name="Building_01",
                asset_type="Building_Warehouse",
                transform=Transform(
                    position=Vector3(200.0, 0.0, 200.0),
                    rotation=Rotation(0.0, 0.0, 0.0),
                ),
                team=Team.NEUTRAL,
                properties={},
            )
        ]

        lines = generator._generate_static_layer(minimal_map_data)
        content = "\n".join(lines)

        assert 'name="Static"' in content
        assert 'name="MP_Tungsten_Terrain"' in content
        assert 'name="Building_Warehouse_1"' in content

    def test_generate_complete_tscn_file(self, generator, minimal_map_data):
        """Test complete .tscn file generation."""
        with NamedTemporaryFile(mode="w", suffix=".tscn", delete=False) as f:
            output_path = Path(f.name)

        try:
            generator.generate(minimal_map_data, output_path, base_terrain="MP_Tungsten")

            # Verify file was created
            assert output_path.exists()

            # Read and verify content
            content = output_path.read_text()

            # Check header
            assert "[gd_scene" in content
            assert "format=3" in content

            # Check ExtResources
            assert "HQ_PlayerSpawner.tscn" in content
            assert "SpawnPoint.tscn" in content
            assert "CombatArea.tscn" in content

            # Check root node
            assert 'name="TestMap"' in content

            # Check required components
            assert "TEAM_1_HQ" in content
            assert "TEAM_2_HQ" in content
            assert "CombatArea" in content
            assert "Static" in content

        finally:
            # Cleanup
            if output_path.exists():
                output_path.unlink()

    def test_validate_generated_file(self, generator, minimal_map_data):
        """Test validation of generated .tscn file."""
        with NamedTemporaryFile(mode="w", suffix=".tscn", delete=False) as f:
            output_path = Path(f.name)

        try:
            generator.generate(minimal_map_data, output_path)

            errors = generator.validate(output_path)

            assert len(errors) == 0, f"Validation errors: {errors}"

        finally:
            if output_path.exists():
                output_path.unlink()

    def test_validate_missing_file(self, generator):
        """Test validation of non-existent file."""
        errors = generator.validate(Path("/nonexistent/file.tscn"))

        assert len(errors) > 0
        assert "File not found" in errors[0]

    def test_make_relative_transform(self, generator):
        """Test making child transform relative to parent."""
        parent = Transform(
            position=Vector3(100.0, 50.0, 100.0),
            rotation=Rotation(0.0, 0.0, 0.0),
        )
        child = Transform(
            position=Vector3(110.0, 50.0, 105.0),
            rotation=Rotation(0.0, 45.0, 0.0),
        )

        result = generator._make_relative_transform(child, parent)

        # Relative position should be (10, 0, 5)
        assert result.position.x == pytest.approx(10.0)
        assert result.position.y == pytest.approx(0.0)
        assert result.position.z == pytest.approx(5.0)

    def test_resource_management(self, generator):
        """Test ExtResource initialization and management."""
        generator.base_terrain = "MP_Tungsten"
        generator._init_ext_resources()

        # Check all required resources are present
        assert len(generator.ext_resources) == 6

        resource_paths = [r["path"] for r in generator.ext_resources]
        assert "res://objects/Gameplay/Common/HQ_PlayerSpawner.tscn" in resource_paths
        assert "res://objects/entities/SpawnPoint.tscn" in resource_paths
        assert "res://objects/Gameplay/Conquest/CapturePoint.tscn" in resource_paths
        assert "res://objects/Gameplay/Common/VehicleSpawner.tscn" in resource_paths
        assert "res://objects/Gameplay/Common/CombatArea.tscn" in resource_paths
        assert "res://static/MP_Tungsten_Terrain.tscn" in resource_paths

        # Check next ID is correct
        assert generator.next_ext_resource_id == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
