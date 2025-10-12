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

    def test_to_portal_preserves_coordinates(self):
        """Test coordinate conversion preserves values (both Y-up)."""
        coord_system = RefractorCoordinateSystem()
        position = Vector3(100.0, 50.0, -200.0)

        # Act
        result = coord_system.to_portal(position)

        # Assert
        assert result.x == 100.0
        assert result.y == 50.0
        assert result.z == -200.0

    def test_to_portal_rotation_preserves_angles(self):
        """Test rotation conversion preserves angles."""
        coord_system = RefractorCoordinateSystem()
        rotation = Rotation(45.0, 90.0, 180.0)

        # Act
        result = coord_system.to_portal_rotation(rotation)

        # Assert
        assert result.pitch == 45.0
        assert result.yaw == 90.0
        assert result.roll == 180.0

    def test_get_scale_factor_returns_one(self):
        """Test scale factor is 1.0 (both use meters)."""
        coord_system = RefractorCoordinateSystem()

        # Act
        result = coord_system.get_scale_factor()

        # Assert
        assert result == 1.0


class TestRefractorEngineSpawnPointIdentification:
    """Test cases for spawn point identification logic."""

    def setup_method(self):
        """Set up test engine."""
        self.engine = ConcreteRefractorEngine()

    def test_is_spawn_point_with_spawn_and_point_in_name(self):
        """Test identifying spawn points by 'spawn' and 'point' keywords."""
        # (self.engine created in setup_method)

        # Act
        result1 = self.engine._is_spawn_point("spawnpoint_axis_1", "")
        result2 = self.engine._is_spawn_point("spawn_point_allies", "")

        # Assert
        assert result1
        assert result2

    def test_is_spawn_point_with_spawnpoint_type(self):
        """Test identifying spawn points by type."""
        # (self.engine created in setup_method)

        # Act
        result1 = self.engine._is_spawn_point("some_object", "spawnpoint")
        result2 = self.engine._is_spawn_point("some_object", "objectspawner_spawnpoint")

        # Assert
        assert result1
        assert result2

    def test_is_spawn_point_with_instance_pattern(self):
        """Test identifying spawn points by instance pattern (name_groupnum_spawnnum)."""
        # (self.engine created in setup_method)

        # Act
        result1 = self.engine._is_spawn_point("openbasecammo_4_13", "")
        result2 = self.engine._is_spawn_point("spawnpoint_axis_1_1", "")
        result3 = self.engine._is_spawn_point("basecamp_3_5", "")

        # Assert
        assert result1
        assert result2
        assert result3

    def test_is_spawn_point_excludes_control_points(self):
        """Test control points are not identified as spawn points."""
        # (self.engine created in setup_method)

        # Act
        result1 = self.engine._is_spawn_point("cpoint_base_1", "")
        result2 = self.engine._is_spawn_point("controlpoint_cpoint_1", "")

        # Assert
        assert not result1
        assert not result2

    def test_is_spawn_point_rejects_non_spawn_objects(self):
        """Test non-spawn objects are rejected."""
        # (self.engine created in setup_method)

        # Act
        result1 = self.engine._is_spawn_point("building_barn_01", "")
        result2 = self.engine._is_spawn_point("vehicle_tank", "")
        result3 = self.engine._is_spawn_point("tree_pine_large", "")

        # Assert
        assert not result1
        assert not result2
        assert not result3


class TestRefractorEngineOwnershipClassification:
    """Test cases for spawn ownership classification."""

    def setup_method(self):
        """Set up test engine."""
        self.engine = ConcreteRefractorEngine()

    def test_classify_spawn_ownership_team1_axis(self):
        """Test classifying team1 spawns by 'axis' keyword."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
        result = self.engine._classify_spawn_ownership("spawnpoint_axis_1")

        # Assert
        assert result == "team1"

    def test_classify_spawn_ownership_team1_index(self):
        """Test classifying team1 spawns by _1_ index pattern."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
        result1 = self.engine._classify_spawn_ownership("spawn_1_1")
        result2 = self.engine._classify_spawn_ownership("basecamp_1_5")

        # Assert
        assert result1 == "team1"
        assert result2 == "team1"

    def test_classify_spawn_ownership_team2_allies(self):
        """Test classifying team2 spawns by 'allies' keyword."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
        result = self.engine._classify_spawn_ownership("spawnpoint_allies_1")

        # Assert
        assert result == "team2"

    def test_classify_spawn_ownership_team2_index(self):
        """Test classifying team2 spawns by _2_ index pattern."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
        result1 = self.engine._classify_spawn_ownership("spawn_2_1")
        result2 = self.engine._classify_spawn_ownership("basecamp_2_3")

        # Assert
        assert result1 == "team2"
        assert result2 == "team2"

    def test_classify_spawn_ownership_neutral(self):
        """Test classifying neutral spawns."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
        result1 = self.engine._classify_spawn_ownership("spawn_3_1")
        result2 = self.engine._classify_spawn_ownership("spawn_4_2")
        result3 = self.engine._classify_spawn_ownership("openbasecamp_5_1")

        # Assert
        assert result1 == "neutral"
        assert result2 == "neutral"
        assert result3 == "neutral"


class TestRefractorEngineTeamFiltering:
    """Test cases for team-based spawn filtering logic."""

    def setup_method(self):
        """Set up test engine."""
        self.engine = ConcreteRefractorEngine()

    def test_should_include_spawn_for_team1(self):
        """Test including team1 spawns for team1 request."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
        result1 = self.engine._should_include_spawn_for_team("team1", Team.TEAM_1)
        result2 = self.engine._should_include_spawn_for_team("team2", Team.TEAM_1)
        result3 = self.engine._should_include_spawn_for_team("neutral", Team.TEAM_1)

        # Assert
        assert result1 is True
        assert result2 is False
        assert result3 is False

    def test_should_include_spawn_for_team2(self):
        """Test including team2 spawns for team2 request."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
        result1 = self.engine._should_include_spawn_for_team("team2", Team.TEAM_2)
        result2 = self.engine._should_include_spawn_for_team("team1", Team.TEAM_2)
        result3 = self.engine._should_include_spawn_for_team("neutral", Team.TEAM_2)

        # Assert
        assert result1 is True
        assert result2 is False
        assert result3 is False

    def test_should_exclude_neutral_spawns_from_hq(self):
        """Test neutral spawns are excluded from team HQs."""
        # Arrange
        # (self.engine created in setup_method)

        # Neutral spawns belong to capture points, not HQs

        # Act
        result1 = self.engine._should_include_spawn_for_team("neutral", Team.TEAM_1)
        result2 = self.engine._should_include_spawn_for_team("neutral", Team.TEAM_2)

        # Assert
        assert result1 is False
        assert result2 is False


class TestRefractorEngineCoordinateConversion:
    """Test cases for coordinate system conversion."""

    def setup_method(self):
        """Set up test engine."""
        self.engine = ConcreteRefractorEngine()

    def test_get_coordinate_system_returns_refractor_system(self):
        """Test getting coordinate system returns RefractorCoordinateSystem."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
        result = self.engine.get_coordinate_system()

        # Assert
        assert isinstance(result, RefractorCoordinateSystem)

    def test_coordinate_system_converts_position(self):
        """Test coordinate system can convert positions."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
        coord_system = self.engine.get_coordinate_system()
        position = Vector3(500.0, 100.0, -300.0)

        result = coord_system.to_portal(position)

        # Both use Y-up, so conversion preserves values

        # Assert
        assert result.x == 500.0
        assert result.y == 100.0
        assert result.z == -300.0


class TestRefractorEngineBoundsCalculation:
    """Test cases for map bounds calculation."""

    def setup_method(self):
        """Set up test engine."""
        self.engine = ConcreteRefractorEngine()

    def test_calculate_bounds_with_spawns(self):
        """Test bounds calculation from spawn points."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
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

        bounds = self.engine._calculate_bounds(spawns, [], [])

        # Check bounds include all spawns with padding

        # Assert
        assert bounds.min_point.x < 0
        assert bounds.max_point.x > 100
        assert bounds.min_point.z < 0
        assert bounds.max_point.z > 200

    def test_calculate_bounds_with_capture_points(self):
        """Test bounds calculation includes capture points."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
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

        bounds = self.engine._calculate_bounds([], capture_points, [])

        # Check bounds include capture points with padding

        # Assert
        assert bounds.min_point.x < -500
        assert bounds.max_point.x > 500
        assert bounds.min_point.z < -500
        assert bounds.max_point.z > 500

    def test_calculate_bounds_with_game_objects(self):
        """Test bounds calculation includes game objects."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
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

        bounds = self.engine._calculate_bounds([], [], objects)

        # Check bounds include objects with padding

        # Assert
        assert bounds.min_point.x < 0
        assert bounds.max_point.x > 1000
        assert bounds.min_point.z < 0
        assert bounds.max_point.z > 1000

    def test_calculate_bounds_adds_vertical_buffer(self):
        """Test bounds calculation adds vertical buffer for height."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
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

        bounds = self.engine._calculate_bounds(spawns, [], [])

        # Height should be max_y - min_y + 100m buffer
        expected_height = 100 - 0 + 100

        # Assert
        assert bounds.height == expected_height

    def test_calculate_bounds_with_empty_lists_returns_defaults(self):
        """Test bounds calculation with no objects returns default bounds."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
        bounds = self.engine._calculate_bounds([], [], [])

        # Default bounds

        # Assert
        assert bounds.min_point.x == -1000
        assert bounds.max_point.x == 1000
        assert bounds.min_point.z == -1000
        assert bounds.max_point.z == 1000
        assert bounds.height == 200

    def test_calculate_bounds_adds_10_percent_padding(self):
        """Test bounds calculation adds 10% padding."""
        # Arrange
        # (self.engine created in setup_method)

        # Act
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

        bounds = self.engine._calculate_bounds(spawns, [], [])

        # Width/depth = 1000, padding = 10% = 100
        # min should be -100, max should be 1100

        # Assert
        assert bounds.min_point.x == pytest.approx(-100.0)
        assert bounds.max_point.x == pytest.approx(1100.0)
        assert bounds.min_point.z == pytest.approx(-100.0)
        assert bounds.max_point.z == pytest.approx(1100.0)
