#!/usr/bin/env python3
"""Tests for MapOrientationDetector class.

Comprehensive test coverage for orientation detection from map data.
"""

import sys
from pathlib import Path

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

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
from bfportal.orientation.interfaces import Orientation
from bfportal.orientation.map_orientation_detector import MapOrientationDetector

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def empty_map_data():
    """Create map data with no objects."""
    # Arrange
    return MapData(
        map_name="EmptyMap",
        game_mode="Conquest",
        team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
        team2_hq=Transform(Vector3(100, 0, 0), Rotation(0, 0, 0)),
        team1_spawns=[],
        team2_spawns=[],
        capture_points=[],
        game_objects=[],
        bounds=MapBounds(
            Vector3(-500, 0, -500), Vector3(500, 100, 500), [], 100.0
        ),
        metadata={},
    )


@pytest.fixture
def square_map_data():
    """Create map data with square layout (1000x1000)."""
    # Arrange
    return MapData(
        map_name="SquareMap",
        game_mode="Conquest",
        team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
        team2_hq=Transform(Vector3(1000, 0, 1000), Rotation(0, 0, 0)),
        team1_spawns=[
            SpawnPoint(
                "Spawn1",
                Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
                Team.TEAM_1,
            ),
            SpawnPoint(
                "Spawn2",
                Transform(Vector3(1000, 0, 0), Rotation(0, 0, 0)),
                Team.TEAM_1,
            ),
        ],
        team2_spawns=[
            SpawnPoint(
                "Spawn3",
                Transform(Vector3(0, 0, 1000), Rotation(0, 0, 0)),
                Team.TEAM_2,
            ),
            SpawnPoint(
                "Spawn4",
                Transform(Vector3(1000, 0, 1000), Rotation(0, 0, 0)),
                Team.TEAM_2,
            ),
        ],
        capture_points=[],
        game_objects=[],
        bounds=MapBounds(
            Vector3(-500, 0, -500), Vector3(1500, 100, 1500), [], 100.0
        ),
        metadata={},
    )


@pytest.fixture
def north_south_map_data():
    """Create map data with north-south orientation (1000x2000)."""
    # Arrange
    return MapData(
        map_name="NorthSouthMap",
        game_mode="Conquest",
        team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
        team2_hq=Transform(Vector3(0, 0, 2000), Rotation(0, 0, 0)),
        team1_spawns=[
            SpawnPoint(
                "Spawn1",
                Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
                Team.TEAM_1,
            ),
            SpawnPoint(
                "Spawn2",
                Transform(Vector3(1000, 0, 0), Rotation(0, 0, 0)),
                Team.TEAM_1,
            ),
        ],
        team2_spawns=[
            SpawnPoint(
                "Spawn3",
                Transform(Vector3(0, 0, 2000), Rotation(0, 0, 0)),
                Team.TEAM_2,
            ),
            SpawnPoint(
                "Spawn4",
                Transform(Vector3(1000, 0, 2000), Rotation(0, 0, 0)),
                Team.TEAM_2,
            ),
        ],
        capture_points=[
            CapturePoint(
                "CP_Mid",
                Transform(Vector3(500, 0, 1000), Rotation(0, 0, 0)),
                50.0,
                [],
            )
        ],
        game_objects=[],
        bounds=MapBounds(
            Vector3(-500, 0, -500), Vector3(1500, 100, 2500), [], 100.0
        ),
        metadata={},
    )


@pytest.fixture
def east_west_map_data():
    """Create map data with east-west orientation (3000x1500)."""
    # Arrange
    return MapData(
        map_name="EastWestMap",
        game_mode="Conquest",
        team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
        team2_hq=Transform(Vector3(3000, 0, 0), Rotation(0, 0, 0)),
        team1_spawns=[
            SpawnPoint(
                "Spawn1",
                Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
                Team.TEAM_1,
            ),
            SpawnPoint(
                "Spawn2",
                Transform(Vector3(0, 0, 1500), Rotation(0, 0, 0)),
                Team.TEAM_1,
            ),
        ],
        team2_spawns=[
            SpawnPoint(
                "Spawn3",
                Transform(Vector3(3000, 0, 0), Rotation(0, 0, 0)),
                Team.TEAM_2,
            ),
            SpawnPoint(
                "Spawn4",
                Transform(Vector3(3000, 0, 1500), Rotation(0, 0, 0)),
                Team.TEAM_2,
            ),
        ],
        capture_points=[],
        game_objects=[
            GameObject(
                "Building1",
                "MP_Building",
                Transform(Vector3(1500, 0, 750), Rotation(0, 0, 0)),
                Team.NEUTRAL,
                {},
            )
        ],
        bounds=MapBounds(
            Vector3(-500, 0, -500), Vector3(3500, 100, 2000), [], 100.0
        ),
        metadata={},
    )


# ============================================================================
# Test MapOrientationDetector.__init__
# ============================================================================


class TestMapOrientationDetectorInit:
    """Tests for MapOrientationDetector initialization."""

    def test_init_with_default_threshold_creates_detector(self, square_map_data):
        """Test initialization with default threshold."""
        # Arrange & Act
        detector = MapOrientationDetector(square_map_data)

        # Assert
        assert detector.map_data == square_map_data
        assert detector.threshold == 1.2

    def test_init_with_custom_threshold_stores_threshold(self, square_map_data):
        """Test initialization with custom threshold."""
        # Arrange
        custom_threshold = 1.5

        # Act
        detector = MapOrientationDetector(square_map_data, threshold=custom_threshold)

        # Assert
        assert detector.threshold == 1.5
        assert detector.map_data == square_map_data


# ============================================================================
# Test MapOrientationDetector.detect_orientation
# ============================================================================


class TestMapOrientationDetectorDetectOrientation:
    """Tests for orientation detection."""

    def test_detect_orientation_empty_map_returns_square_low_confidence(
        self, empty_map_data
    ):
        """Test detecting orientation with no objects returns square."""
        # Arrange
        detector = MapOrientationDetector(empty_map_data)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert result.width_x == 0
        assert result.depth_z == 0
        assert result.ratio == 1.0
        assert result.confidence == "low"

    def test_detect_orientation_square_map_returns_square(self, square_map_data):
        """Test detecting orientation with square map layout."""
        # Arrange
        detector = MapOrientationDetector(square_map_data)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert result.width_x == 1000.0
        assert result.depth_z == 1000.0
        assert result.ratio == 1.0
        assert result.confidence == "low"

    def test_detect_orientation_north_south_returns_north_south(
        self, north_south_map_data
    ):
        """Test detecting north-south orientation."""
        # Arrange
        detector = MapOrientationDetector(north_south_map_data)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.NORTH_SOUTH
        assert result.width_x == 1000.0
        assert result.depth_z == 2000.0
        assert result.ratio == 2.0
        assert result.confidence == "high"

    def test_detect_orientation_east_west_returns_east_west(self, east_west_map_data):
        """Test detecting east-west orientation."""
        # Arrange
        detector = MapOrientationDetector(east_west_map_data)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.EAST_WEST
        assert result.width_x == 3000.0
        assert result.depth_z == 1500.0
        assert result.ratio == 2.0
        assert result.confidence == "high"

    def test_detect_orientation_zero_width_returns_square_low_confidence(self):
        """Test detecting orientation when width is zero."""
        # Arrange
        map_data = MapData(
            map_name="ZeroWidthMap",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
            team2_hq=Transform(Vector3(0, 0, 100), Rotation(0, 0, 0)),
            team1_spawns=[
                SpawnPoint(
                    "Spawn1",
                    Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
                SpawnPoint(
                    "Spawn2",
                    Transform(Vector3(0, 0, 100), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
            ],
            team2_spawns=[],
            capture_points=[],
            game_objects=[],
            bounds=MapBounds(Vector3(0, 0, 0), Vector3(0, 100, 100), [], 100.0),
            metadata={},
        )
        detector = MapOrientationDetector(map_data)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert result.width_x == 0.0
        assert result.depth_z == 100.0
        assert result.ratio == 1.0
        assert result.confidence == "low"

    def test_detect_orientation_zero_depth_returns_square_low_confidence(self):
        """Test detecting orientation when depth is zero."""
        # Arrange
        map_data = MapData(
            map_name="ZeroDepthMap",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
            team2_hq=Transform(Vector3(100, 0, 0), Rotation(0, 0, 0)),
            team1_spawns=[
                SpawnPoint(
                    "Spawn1",
                    Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
                SpawnPoint(
                    "Spawn2",
                    Transform(Vector3(100, 0, 0), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
            ],
            team2_spawns=[],
            capture_points=[],
            game_objects=[],
            bounds=MapBounds(Vector3(0, 0, 0), Vector3(100, 100, 0), [], 100.0),
            metadata={},
        )
        detector = MapOrientationDetector(map_data)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert result.width_x == 100.0
        assert result.depth_z == 0.0
        assert result.ratio == 1.0
        assert result.confidence == "low"

    def test_detect_orientation_ratio_at_threshold_returns_medium_confidence(self):
        """Test detecting orientation with ratio exactly at threshold."""
        # Arrange
        map_data = MapData(
            map_name="ThresholdMap",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
            team2_hq=Transform(Vector3(1200, 0, 0), Rotation(0, 0, 0)),
            team1_spawns=[
                SpawnPoint(
                    "Spawn1",
                    Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
                SpawnPoint(
                    "Spawn2",
                    Transform(Vector3(1200, 0, 1000), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
            ],
            team2_spawns=[],
            capture_points=[],
            game_objects=[],
            bounds=MapBounds(
                Vector3(0, 0, 0), Vector3(1200, 100, 1000), [], 100.0
            ),
            metadata={},
        )
        detector = MapOrientationDetector(map_data, threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.EAST_WEST
        assert result.ratio == 1.2
        assert result.confidence == "medium"

    def test_detect_orientation_ratio_above_1_5_returns_high_confidence(self):
        """Test detecting orientation with ratio above 1.5."""
        # Arrange
        map_data = MapData(
            map_name="HighRatioMap",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
            team2_hq=Transform(Vector3(0, 0, 1600), Rotation(0, 0, 0)),
            team1_spawns=[
                SpawnPoint(
                    "Spawn1",
                    Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
                SpawnPoint(
                    "Spawn2",
                    Transform(Vector3(1000, 0, 1600), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
            ],
            team2_spawns=[],
            capture_points=[],
            game_objects=[],
            bounds=MapBounds(
                Vector3(0, 0, 0), Vector3(1000, 100, 1600), [], 100.0
            ),
            metadata={},
        )
        detector = MapOrientationDetector(map_data, threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.NORTH_SOUTH
        assert result.ratio == 1.6
        assert result.confidence == "high"

    def test_detect_orientation_ratio_below_threshold_returns_square(self):
        """Test detecting orientation with ratio below threshold."""
        # Arrange
        map_data = MapData(
            map_name="BelowThresholdMap",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
            team2_hq=Transform(Vector3(1100, 0, 1000), Rotation(0, 0, 0)),
            team1_spawns=[
                SpawnPoint(
                    "Spawn1",
                    Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
                SpawnPoint(
                    "Spawn2",
                    Transform(Vector3(1100, 0, 1000), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
            ],
            team2_spawns=[],
            capture_points=[],
            game_objects=[],
            bounds=MapBounds(
                Vector3(0, 0, 0), Vector3(1100, 100, 1000), [], 100.0
            ),
            metadata={},
        )
        detector = MapOrientationDetector(map_data, threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert result.ratio == 1.1
        assert result.confidence == "low"


# ============================================================================
# Test MapOrientationDetector.get_bounds
# ============================================================================


class TestMapOrientationDetectorGetBounds:
    """Tests for getting bounding box."""

    def test_get_bounds_empty_map_returns_zeros(self, empty_map_data):
        """Test getting bounds with no objects."""
        # Arrange
        detector = MapOrientationDetector(empty_map_data)

        # Act
        min_x, max_x, min_z, max_z = detector.get_bounds()

        # Assert
        assert min_x == 0
        assert max_x == 0
        assert min_z == 0
        assert max_z == 0

    def test_get_bounds_square_map_returns_correct_bounds(self, square_map_data):
        """Test getting bounds from square map."""
        # Arrange
        detector = MapOrientationDetector(square_map_data)

        # Act
        min_x, max_x, min_z, max_z = detector.get_bounds()

        # Assert
        assert min_x == 0.0
        assert max_x == 1000.0
        assert min_z == 0.0
        assert max_z == 1000.0

    def test_get_bounds_north_south_map_returns_correct_bounds(
        self, north_south_map_data
    ):
        """Test getting bounds from north-south map."""
        # Arrange
        detector = MapOrientationDetector(north_south_map_data)

        # Act
        min_x, max_x, min_z, max_z = detector.get_bounds()

        # Assert
        assert min_x == 0.0
        assert max_x == 1000.0
        assert min_z == 0.0
        assert max_z == 2000.0

    def test_get_bounds_east_west_map_returns_correct_bounds(self, east_west_map_data):
        """Test getting bounds from east-west map."""
        # Arrange
        detector = MapOrientationDetector(east_west_map_data)

        # Act
        min_x, max_x, min_z, max_z = detector.get_bounds()

        # Assert
        assert min_x == 0.0
        assert max_x == 3000.0
        assert min_z == 0.0
        assert max_z == 1500.0

    def test_get_bounds_negative_coordinates_returns_correct_bounds(self):
        """Test getting bounds with negative coordinates."""
        # Arrange
        map_data = MapData(
            map_name="NegativeMap",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(-500, 0, -500), Rotation(0, 0, 0)),
            team2_hq=Transform(Vector3(500, 0, 500), Rotation(0, 0, 0)),
            team1_spawns=[
                SpawnPoint(
                    "Spawn1",
                    Transform(Vector3(-500, 0, -500), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
                SpawnPoint(
                    "Spawn2",
                    Transform(Vector3(500, 0, 500), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
            ],
            team2_spawns=[],
            capture_points=[],
            game_objects=[],
            bounds=MapBounds(
                Vector3(-500, 0, -500), Vector3(500, 100, 500), [], 100.0
            ),
            metadata={},
        )
        detector = MapOrientationDetector(map_data)

        # Act
        min_x, max_x, min_z, max_z = detector.get_bounds()

        # Assert
        assert min_x == -500.0
        assert max_x == 500.0
        assert min_z == -500.0
        assert max_z == 500.0


# ============================================================================
# Test MapOrientationDetector._collect_positions
# ============================================================================


class TestMapOrientationDetectorCollectPositions:
    """Tests for collecting object positions."""

    def test_collect_positions_empty_map_returns_empty_list(self, empty_map_data):
        """Test collecting positions from empty map."""
        # Arrange
        detector = MapOrientationDetector(empty_map_data)

        # Act
        positions = detector._collect_positions()

        # Assert
        assert len(positions) == 0
        assert positions == []

    def test_collect_positions_includes_team1_spawns(self):
        """Test collecting positions includes team 1 spawns."""
        # Arrange
        map_data = MapData(
            map_name="TestMap",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
            team2_hq=Transform(Vector3(100, 0, 0), Rotation(0, 0, 0)),
            team1_spawns=[
                SpawnPoint(
                    "Spawn1",
                    Transform(Vector3(10, 0, 20), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
                SpawnPoint(
                    "Spawn2",
                    Transform(Vector3(30, 0, 40), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
            ],
            team2_spawns=[],
            capture_points=[],
            game_objects=[],
            bounds=MapBounds(Vector3(0, 0, 0), Vector3(100, 100, 100), [], 100.0),
            metadata={},
        )
        detector = MapOrientationDetector(map_data)

        # Act
        positions = detector._collect_positions()

        # Assert
        assert len(positions) == 2
        assert Vector3(10, 0, 20) in positions
        assert Vector3(30, 0, 40) in positions

    def test_collect_positions_includes_team2_spawns(self):
        """Test collecting positions includes team 2 spawns."""
        # Arrange
        map_data = MapData(
            map_name="TestMap",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
            team2_hq=Transform(Vector3(100, 0, 0), Rotation(0, 0, 0)),
            team1_spawns=[],
            team2_spawns=[
                SpawnPoint(
                    "Spawn3",
                    Transform(Vector3(50, 0, 60), Rotation(0, 0, 0)),
                    Team.TEAM_2,
                ),
                SpawnPoint(
                    "Spawn4",
                    Transform(Vector3(70, 0, 80), Rotation(0, 0, 0)),
                    Team.TEAM_2,
                ),
            ],
            capture_points=[],
            game_objects=[],
            bounds=MapBounds(Vector3(0, 0, 0), Vector3(100, 100, 100), [], 100.0),
            metadata={},
        )
        detector = MapOrientationDetector(map_data)

        # Act
        positions = detector._collect_positions()

        # Assert
        assert len(positions) == 2
        assert Vector3(50, 0, 60) in positions
        assert Vector3(70, 0, 80) in positions

    def test_collect_positions_includes_capture_points(self):
        """Test collecting positions includes capture points."""
        # Arrange
        map_data = MapData(
            map_name="TestMap",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
            team2_hq=Transform(Vector3(100, 0, 0), Rotation(0, 0, 0)),
            team1_spawns=[],
            team2_spawns=[],
            capture_points=[
                CapturePoint(
                    "CP1",
                    Transform(Vector3(25, 0, 25), Rotation(0, 0, 0)),
                    50.0,
                    [],
                ),
                CapturePoint(
                    "CP2",
                    Transform(Vector3(75, 0, 75), Rotation(0, 0, 0)),
                    50.0,
                    [],
                ),
            ],
            game_objects=[],
            bounds=MapBounds(Vector3(0, 0, 0), Vector3(100, 100, 100), [], 100.0),
            metadata={},
        )
        detector = MapOrientationDetector(map_data)

        # Act
        positions = detector._collect_positions()

        # Assert
        assert len(positions) == 2
        assert Vector3(25, 0, 25) in positions
        assert Vector3(75, 0, 75) in positions

    def test_collect_positions_includes_game_objects(self):
        """Test collecting positions includes game objects."""
        # Arrange
        map_data = MapData(
            map_name="TestMap",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
            team2_hq=Transform(Vector3(100, 0, 0), Rotation(0, 0, 0)),
            team1_spawns=[],
            team2_spawns=[],
            capture_points=[],
            game_objects=[
                GameObject(
                    "Building1",
                    "MP_Building",
                    Transform(Vector3(15, 0, 35), Rotation(0, 0, 0)),
                    Team.NEUTRAL,
                    {},
                ),
                GameObject(
                    "Tank1",
                    "MP_Tank",
                    Transform(Vector3(65, 0, 85), Rotation(0, 0, 0)),
                    Team.NEUTRAL,
                    {},
                ),
            ],
            bounds=MapBounds(Vector3(0, 0, 0), Vector3(100, 100, 100), [], 100.0),
            metadata={},
        )
        detector = MapOrientationDetector(map_data)

        # Act
        positions = detector._collect_positions()

        # Assert
        assert len(positions) == 2
        assert Vector3(15, 0, 35) in positions
        assert Vector3(65, 0, 85) in positions

    def test_collect_positions_includes_all_object_types(self):
        """Test collecting positions includes all object types."""
        # Arrange
        map_data = MapData(
            map_name="TestMap",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
            team2_hq=Transform(Vector3(100, 0, 0), Rotation(0, 0, 0)),
            team1_spawns=[
                SpawnPoint(
                    "Spawn1",
                    Transform(Vector3(10, 0, 10), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                )
            ],
            team2_spawns=[
                SpawnPoint(
                    "Spawn2",
                    Transform(Vector3(90, 0, 90), Rotation(0, 0, 0)),
                    Team.TEAM_2,
                )
            ],
            capture_points=[
                CapturePoint(
                    "CP1",
                    Transform(Vector3(50, 0, 50), Rotation(0, 0, 0)),
                    50.0,
                    [],
                )
            ],
            game_objects=[
                GameObject(
                    "Building1",
                    "MP_Building",
                    Transform(Vector3(30, 0, 70), Rotation(0, 0, 0)),
                    Team.NEUTRAL,
                    {},
                )
            ],
            bounds=MapBounds(Vector3(0, 0, 0), Vector3(100, 100, 100), [], 100.0),
            metadata={},
        )
        detector = MapOrientationDetector(map_data)

        # Act
        positions = detector._collect_positions()

        # Assert
        assert len(positions) == 4
        assert Vector3(10, 0, 10) in positions
        assert Vector3(90, 0, 90) in positions
        assert Vector3(50, 0, 50) in positions
        assert Vector3(30, 0, 70) in positions


# ============================================================================
# Integration Tests
# ============================================================================


class TestMapOrientationDetectorIntegration:
    """Integration tests for complete orientation detection workflows."""

    def test_full_workflow_complex_north_south_map(self):
        """Test complete workflow with complex north-south map."""
        # Arrange
        map_data = MapData(
            map_name="ComplexNS",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
            team2_hq=Transform(Vector3(0, 0, 3000), Rotation(0, 0, 0)),
            team1_spawns=[
                SpawnPoint(
                    "Spawn1",
                    Transform(Vector3(-500, 0, 0), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
                SpawnPoint(
                    "Spawn2",
                    Transform(Vector3(500, 0, 0), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
            ],
            team2_spawns=[
                SpawnPoint(
                    "Spawn3",
                    Transform(Vector3(-500, 0, 3000), Rotation(0, 0, 0)),
                    Team.TEAM_2,
                ),
                SpawnPoint(
                    "Spawn4",
                    Transform(Vector3(500, 0, 3000), Rotation(0, 0, 0)),
                    Team.TEAM_2,
                ),
            ],
            capture_points=[
                CapturePoint(
                    "CP1",
                    Transform(Vector3(0, 0, 1000), Rotation(0, 0, 0)),
                    50.0,
                    [],
                ),
                CapturePoint(
                    "CP2",
                    Transform(Vector3(0, 0, 2000), Rotation(0, 0, 0)),
                    50.0,
                    [],
                ),
            ],
            game_objects=[
                GameObject(
                    "Building1",
                    "MP_Building",
                    Transform(Vector3(200, 0, 1500), Rotation(0, 0, 0)),
                    Team.NEUTRAL,
                    {},
                ),
                GameObject(
                    "Building2",
                    "MP_Building",
                    Transform(Vector3(-200, 0, 1500), Rotation(0, 0, 0)),
                    Team.NEUTRAL,
                    {},
                ),
            ],
            bounds=MapBounds(
                Vector3(-1000, 0, -500), Vector3(1000, 100, 3500), [], 100.0
            ),
            metadata={},
        )
        detector = MapOrientationDetector(map_data, threshold=1.2)

        # Act
        analysis = detector.detect_orientation()
        bounds = detector.get_bounds()

        # Assert
        assert analysis.orientation == Orientation.NORTH_SOUTH
        assert analysis.width_x == 1000.0
        assert analysis.depth_z == 3000.0
        assert analysis.ratio == 3.0
        assert analysis.confidence == "high"
        assert bounds == (-500.0, 500.0, 0.0, 3000.0)

    def test_full_workflow_complex_east_west_map(self):
        """Test complete workflow with complex east-west map."""
        # Arrange
        map_data = MapData(
            map_name="ComplexEW",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),
            team2_hq=Transform(Vector3(4000, 0, 0), Rotation(0, 0, 0)),
            team1_spawns=[
                SpawnPoint(
                    "Spawn1",
                    Transform(Vector3(0, 0, -300), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
                SpawnPoint(
                    "Spawn2",
                    Transform(Vector3(0, 0, 300), Rotation(0, 0, 0)),
                    Team.TEAM_1,
                ),
            ],
            team2_spawns=[
                SpawnPoint(
                    "Spawn3",
                    Transform(Vector3(4000, 0, -300), Rotation(0, 0, 0)),
                    Team.TEAM_2,
                ),
                SpawnPoint(
                    "Spawn4",
                    Transform(Vector3(4000, 0, 300), Rotation(0, 0, 0)),
                    Team.TEAM_2,
                ),
            ],
            capture_points=[
                CapturePoint(
                    "CP1",
                    Transform(Vector3(2000, 0, 0), Rotation(0, 0, 0)),
                    50.0,
                    [],
                )
            ],
            game_objects=[
                GameObject(
                    "Building1",
                    "MP_Building",
                    Transform(Vector3(1000, 0, 100), Rotation(0, 0, 0)),
                    Team.NEUTRAL,
                    {},
                ),
                GameObject(
                    "Building2",
                    "MP_Building",
                    Transform(Vector3(3000, 0, -100), Rotation(0, 0, 0)),
                    Team.NEUTRAL,
                    {},
                ),
            ],
            bounds=MapBounds(
                Vector3(-500, 0, -1000), Vector3(4500, 100, 1000), [], 100.0
            ),
            metadata={},
        )
        detector = MapOrientationDetector(map_data, threshold=1.2)

        # Act
        analysis = detector.detect_orientation()
        bounds = detector.get_bounds()

        # Assert
        assert analysis.orientation == Orientation.EAST_WEST
        assert analysis.width_x == 4000.0
        assert analysis.depth_z == 600.0
        assert pytest.approx(analysis.ratio, rel=0.01) == 6.67
        assert analysis.confidence == "high"
        assert bounds == (0.0, 4000.0, -300.0, 300.0)
