#!/usr/bin/env python3
"""Unit tests for RefractorEngine base class."""

import sys
from pathlib import Path

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bfportal.core.interfaces import (
    CapturePoint,
    GameObject,
    Rotation,
    SpawnPoint,
    Team,
    Transform,
    Vector3,
)
from bfportal.engines.refractor.refractor_base import RefractorCoordinateSystem, RefractorEngine


class ConcreteRefractorEngine(RefractorEngine):
    """Concrete implementation of RefractorEngine for testing."""

    def get_game_name(self) -> str:
        """Return test game name."""
        return "TestGame"

    def get_engine_version(self) -> str:
        """Return test engine version."""
        return "Refractor 1.0"

    def get_game_mode_default(self) -> str:
        """Return test default game mode."""
        return "Conquest"


class TestRefractorCoordinateSystem:
    """Test cases for RefractorCoordinateSystem."""

    def test_to_portal_negates_z_axis(self):
        """Test coordinate conversion negates Z-axis (BF1942 +Z=north, Portal -Z=north)."""
        # Arrange
        coord_system = RefractorCoordinateSystem()
        position = Vector3(100.0, 50.0, 200.0)  # BF1942: +Z is north

        # Act
        result = coord_system.to_portal(position)

        # Assert - X and Y preserved, Z negated
        assert result.x == 100.0
        assert result.y == 50.0
        assert result.z == -200.0  # Portal: -Z is north (negated)

    def test_to_portal_rotation_adds_180_to_yaw(self):
        """Test rotation conversion adds 180° to yaw (compensates for Z-axis flip)."""
        # Arrange
        coord_system = RefractorCoordinateSystem()
        rotation = Rotation(45.0, 90.0, 180.0)

        # Act
        result = coord_system.to_portal_rotation(rotation)

        # Assert - Pitch and roll preserved, yaw += 180° (normalized)
        assert result.pitch == 45.0
        assert result.yaw == -90.0  # 90 + 180 = 270, normalized to -90
        assert result.roll == 180.0

    def test_to_portal_rotation_normalizes_yaw_to_negative_180_to_180(self):
        """Test rotation normalization keeps yaw within [-180, 180] range."""
        # Arrange
        coord_system = RefractorCoordinateSystem()

        # Act & Assert - Test boundary cases
        # yaw=0 + 180 = 180 (stays at 180)
        result1 = coord_system.to_portal_rotation(Rotation(0, 0, 0))
        assert result1.yaw == 180.0

        # yaw=1 + 180 = 181, normalized to -179
        result2 = coord_system.to_portal_rotation(Rotation(0, 1, 0))
        assert result2.yaw == pytest.approx(-179.0)

        # yaw=-180 + 180 = 0
        result3 = coord_system.to_portal_rotation(Rotation(0, -180, 0))
        assert result3.yaw == 0.0

        # yaw=-90 + 180 = 90
        result4 = coord_system.to_portal_rotation(Rotation(0, -90, 0))
        assert result4.yaw == 90.0

    def test_to_portal_rotation_preserves_pitch_and_roll(self):
        """Test rotation conversion preserves pitch and roll (only modifies yaw)."""
        # Arrange
        coord_system = RefractorCoordinateSystem()
        rotation = Rotation(-30.0, 45.0, 75.0)

        # Act
        result = coord_system.to_portal_rotation(rotation)

        # Assert - Pitch and roll unchanged
        assert result.pitch == -30.0
        assert result.roll == 75.0
        # Yaw modified: 45 + 180 = 225, normalized to -135
        assert result.yaw == pytest.approx(-135.0)

    def test_get_scale_factor_returns_one(self):
        """Test scale factor is 1.0 (both use meters)."""
        # Arrange
        coord_system = RefractorCoordinateSystem()

        # Act
        result = coord_system.get_scale_factor()

        # Assert
        assert result == 1.0


class TestRefractorEngineSpawnPointIdentification:
    """Test cases for spawn point identification logic."""

    def test_is_spawn_point_with_spawn_and_point_in_name(self):
        """Test identifying spawn points by 'spawn' and 'point' keywords."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        result1 = engine._is_spawn_point("spawnpoint_axis_1", "")
        result2 = engine._is_spawn_point("spawn_point_allies", "")

        # Assert
        assert result1
        assert result2

    def test_is_spawn_point_with_spawnpoint_type(self):
        """Test identifying spawn points by type."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        result1 = engine._is_spawn_point("some_object", "spawnpoint")
        # Note: "objectspawner_spawnpoint" is not "spawnpoint", so it won't match
        # unless it's in spawn_template_types

        # Assert
        assert result1

    def test_is_spawn_point_with_template_based_detection(self):
        """Test identifying spawn points using template-based detection."""
        # Arrange
        engine = ConcreteRefractorEngine()
        # Simulate loading spawn templates (normally done in parse_map)
        engine.spawn_template_types.add("openbasecammo")
        engine.spawn_template_types.add("al_5")
        engine.spawn_template_types.add("ax_6")

        # Act - Test template instances (type=template_name)
        result1 = engine._is_spawn_point("openbasecammo_4_13", "openbasecammo")
        result2 = engine._is_spawn_point("al_5_instance", "al_5")
        result3 = engine._is_spawn_point("ax_6_instance", "ax_6")
        # Test fallback to pattern matching for "spawn" + "point" in name
        result4 = engine._is_spawn_point("spawnpoint_axis_1_1", "")

        # Assert
        assert result1  # Matches loaded template
        assert result2  # Matches loaded template (bot spawn)
        assert result3  # Matches loaded template (bot spawn)
        assert result4  # Matches fallback pattern

    def test_is_spawn_point_excludes_control_points(self):
        """Test control points are not identified as spawn points."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        result1 = engine._is_spawn_point("cpoint_base_1", "")
        result2 = engine._is_spawn_point("controlpoint_cpoint_1", "")

        # Assert
        assert not result1
        assert not result2

    def test_is_spawn_point_rejects_non_spawn_objects(self):
        """Test non-spawn objects are rejected."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        result1 = engine._is_spawn_point("building_barn_01", "")
        result2 = engine._is_spawn_point("vehicle_tank", "")
        result3 = engine._is_spawn_point("tree_pine_large", "")

        # Assert
        assert not result1
        assert not result2
        assert not result3


class TestRefractorEngineOwnershipClassification:
    """Test cases for spawn ownership classification."""

    def test_classify_spawn_ownership_team1_axis(self):
        """Test classifying team1 spawns by 'axis' keyword."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        result = engine._classify_spawn_ownership("spawnpoint_axis_1")

        # Assert
        assert result == "team1"

    def test_classify_spawn_ownership_team1_index(self):
        """Test classifying team1 spawns by _1_ index pattern."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        result1 = engine._classify_spawn_ownership("spawn_1_1")
        result2 = engine._classify_spawn_ownership("basecamp_1_5")

        # Assert
        assert result1 == "team1"
        assert result2 == "team1"

    def test_classify_spawn_ownership_team2_allies(self):
        """Test classifying team2 spawns by 'allies' keyword."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        result = engine._classify_spawn_ownership("spawnpoint_allies_1")

        # Assert
        assert result == "team2"

    def test_classify_spawn_ownership_team2_index(self):
        """Test classifying team2 spawns by _2_ index pattern."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        result1 = engine._classify_spawn_ownership("spawn_2_1")
        result2 = engine._classify_spawn_ownership("basecamp_2_3")

        # Assert
        assert result1 == "team2"
        assert result2 == "team2"

    def test_classify_spawn_ownership_neutral(self):
        """Test classifying neutral spawns."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        result1 = engine._classify_spawn_ownership("spawn_3_1")
        result2 = engine._classify_spawn_ownership("spawn_4_2")
        result3 = engine._classify_spawn_ownership("openbasecamp_5_1")

        # Assert
        assert result1 == "neutral"
        assert result2 == "neutral"
        assert result3 == "neutral"


class TestRefractorEngineTeamFiltering:
    """Test cases for team-based spawn filtering logic."""

    def test_should_include_spawn_for_team1(self):
        """Test including team1 spawns for team1 request."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        result1 = engine._should_include_spawn_for_team("team1", Team.TEAM_1)
        result2 = engine._should_include_spawn_for_team("team2", Team.TEAM_1)
        result3 = engine._should_include_spawn_for_team("neutral", Team.TEAM_1)

        # Assert
        assert result1 is True
        assert result2 is False
        assert result3 is False

    def test_should_include_spawn_for_team2(self):
        """Test including team2 spawns for team2 request."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        result1 = engine._should_include_spawn_for_team("team2", Team.TEAM_2)
        result2 = engine._should_include_spawn_for_team("team1", Team.TEAM_2)
        result3 = engine._should_include_spawn_for_team("neutral", Team.TEAM_2)

        # Assert
        assert result1 is True
        assert result2 is False
        assert result3 is False

    def test_should_exclude_neutral_spawns_from_hq(self):
        """Test neutral spawns are excluded from team HQs."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        result1 = engine._should_include_spawn_for_team("neutral", Team.TEAM_1)
        result2 = engine._should_include_spawn_for_team("neutral", Team.TEAM_2)

        # Assert
        assert result1 is False
        assert result2 is False


class TestRefractorEngineCoordinateConversion:
    """Test cases for coordinate system conversion."""

    def test_get_coordinate_system_returns_refractor_system(self):
        """Test getting coordinate system returns RefractorCoordinateSystem."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        result = engine.get_coordinate_system()

        # Assert
        assert isinstance(result, RefractorCoordinateSystem)

    def test_coordinate_system_converts_position(self):
        """Test coordinate system can convert positions with Z-axis negation."""
        # Arrange
        engine = ConcreteRefractorEngine()
        coord_system = engine.get_coordinate_system()
        position = Vector3(500.0, 100.0, -300.0)  # BF1942: -Z is south

        # Act
        result = coord_system.to_portal(position)

        # Assert - X and Y preserved, Z negated
        assert result.x == 500.0
        assert result.y == 100.0
        assert result.z == 300.0  # Portal: +Z is south (negated)


class TestRefractorEngineBoundsCalculation:
    """Test cases for map bounds calculation."""

    def test_calculate_bounds_with_spawns(self):
        """Test bounds calculation from spawn points."""
        # Arrange
        engine = ConcreteRefractorEngine()
        spawns = [
            SpawnPoint(
                name="spawn1",
                transform=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
                team=Team.TEAM_1,
            ),
            SpawnPoint(
                name="spawn2",
                transform=Transform(position=Vector3(100, 50, 200), rotation=Rotation(0, 0, 0)),
                team=Team.TEAM_1,
            ),
        ]

        # Act
        bounds = engine._calculate_bounds(spawns, [], [])

        # Assert
        assert bounds.min_point.x < 0
        assert bounds.max_point.x > 100
        assert bounds.min_point.z < 0
        assert bounds.max_point.z > 200

    def test_calculate_bounds_with_capture_points(self):
        """Test bounds calculation includes capture points."""
        # Arrange
        engine = ConcreteRefractorEngine()
        capture_points = [
            CapturePoint(
                name="cp1",
                transform=Transform(position=Vector3(-500, 10, -500), rotation=Rotation(0, 0, 0)),
                radius=50.0,
                control_area=[],
            ),
            CapturePoint(
                name="cp2",
                transform=Transform(position=Vector3(500, 10, 500), rotation=Rotation(0, 0, 0)),
                radius=50.0,
                control_area=[],
            ),
        ]

        # Act
        bounds = engine._calculate_bounds([], capture_points, [])

        # Assert
        assert bounds.min_point.x < -500
        assert bounds.max_point.x > 500
        assert bounds.min_point.z < -500
        assert bounds.max_point.z > 500

    def test_calculate_bounds_with_game_objects(self):
        """Test bounds calculation includes game objects."""
        # Arrange
        engine = ConcreteRefractorEngine()
        objects = [
            GameObject(
                name="obj1",
                asset_type="Building",
                transform=Transform(position=Vector3(0, 20, 0), rotation=Rotation(0, 0, 0)),
                team=Team.NEUTRAL,
                properties={},
            ),
            GameObject(
                name="obj2",
                asset_type="Building",
                transform=Transform(position=Vector3(1000, 20, 1000), rotation=Rotation(0, 0, 0)),
                team=Team.NEUTRAL,
                properties={},
            ),
        ]

        # Act
        bounds = engine._calculate_bounds([], [], objects)

        # Assert
        assert bounds.min_point.x < 0
        assert bounds.max_point.x > 1000
        assert bounds.min_point.z < 0
        assert bounds.max_point.z > 1000

    def test_calculate_bounds_adds_vertical_buffer(self):
        """Test bounds calculation adds vertical buffer for height."""
        # Arrange
        engine = ConcreteRefractorEngine()
        spawns = [
            SpawnPoint(
                name="spawn1",
                transform=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
                team=Team.TEAM_1,
            ),
            SpawnPoint(
                name="spawn2",
                transform=Transform(position=Vector3(0, 100, 0), rotation=Rotation(0, 0, 0)),
                team=Team.TEAM_1,
            ),
        ]
        expected_height = 100 - 0 + 100

        # Act
        bounds = engine._calculate_bounds(spawns, [], [])

        # Assert
        assert bounds.height == expected_height

    def test_calculate_bounds_with_empty_lists_returns_defaults(self):
        """Test bounds calculation with no objects returns default bounds."""
        # Arrange
        engine = ConcreteRefractorEngine()

        # Act
        bounds = engine._calculate_bounds([], [], [])

        # Assert
        assert bounds.min_point.x == -1000
        assert bounds.max_point.x == 1000
        assert bounds.min_point.z == -1000
        assert bounds.max_point.z == 1000
        assert bounds.height == 200

    def test_calculate_bounds_adds_10_percent_padding(self):
        """Test bounds calculation adds 10% padding."""
        # Arrange
        engine = ConcreteRefractorEngine()
        spawns = [
            SpawnPoint(
                name="spawn1",
                transform=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
                team=Team.TEAM_1,
            ),
            SpawnPoint(
                name="spawn2",
                transform=Transform(position=Vector3(1000, 0, 1000), rotation=Rotation(0, 0, 0)),
                team=Team.TEAM_1,
            ),
        ]

        # Act
        bounds = engine._calculate_bounds(spawns, [], [])

        # Assert
        assert bounds.min_point.x == pytest.approx(-100.0)
        assert bounds.max_point.x == pytest.approx(1100.0)
        assert bounds.min_point.z == pytest.approx(-100.0)
        assert bounds.max_point.z == pytest.approx(1100.0)
