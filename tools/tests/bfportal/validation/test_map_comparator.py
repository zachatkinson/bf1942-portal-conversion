#!/usr/bin/env python3
"""Tests for map_comparator module.

Tests MapComparator and MapComparison classes with 100% coverage.
"""

import pytest
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
from bfportal.validation.map_comparator import MapComparator, MapComparison
from bfportal.validation.tscn_reader import TscnNode

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_map_data() -> MapData:
    """Create sample MapData for testing.

    Returns:
        MapData with known counts for testing
    """
    # Arrange
    team1_spawns = [
        SpawnPoint(
            name=f"Spawn_T1_{i}",
            transform=Transform(position=Vector3(i * 10.0, 0.0, 0.0), rotation=Rotation(0, 0, 0)),
            team=Team.TEAM_1,
        )
        for i in range(4)
    ]

    team2_spawns = [
        SpawnPoint(
            name=f"Spawn_T2_{i}",
            transform=Transform(position=Vector3(i * 10.0, 0.0, 100.0), rotation=Rotation(0, 0, 0)),
            team=Team.TEAM_2,
        )
        for i in range(5)
    ]

    capture_points = [
        CapturePoint(
            name=f"CP_{i}",
            transform=Transform(position=Vector3(50.0, 0.0, i * 30.0), rotation=Rotation(0, 0, 0)),
            radius=20.0,
            control_area=[Vector3(0, 0, 0), Vector3(10, 0, 0), Vector3(10, 0, 10)],
        )
        for i in range(3)
    ]

    game_objects = [
        GameObject(
            name=f"Object_{i}",
            asset_type="Tree_Pine_Large",
            transform=Transform(
                position=Vector3(i * 5.0, 2.0, i * 5.0), rotation=Rotation(0, 45, 0)
            ),
            team=Team.NEUTRAL,
            properties={},
        )
        for i in range(7)
    ]

    return MapData(
        map_name="TestMap",
        game_mode="Conquest",
        team1_hq=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
        team2_hq=Transform(position=Vector3(0, 0, 100), rotation=Rotation(0, 0, 0)),
        team1_spawns=team1_spawns,
        team2_spawns=team2_spawns,
        capture_points=capture_points,
        game_objects=game_objects,
        bounds=MapBounds(
            min_point=Vector3(-100, 0, -100),
            max_point=Vector3(100, 50, 100),
            combat_area_polygon=[
                Vector3(-100, 0, -100),
                Vector3(100, 0, -100),
                Vector3(100, 0, 100),
                Vector3(-100, 0, 100),
            ],
            height=50.0,
        ),
        metadata={},
    )


@pytest.fixture
def sample_tscn_nodes() -> list[TscnNode]:
    """Create sample TscnNode list for testing.

    Returns:
        List of TscnNode objects with known positions
    """
    # Arrange
    nodes = []

    # Team 1 spawns
    for i in range(4):
        nodes.append(
            TscnNode(
                name=f"SpawnPoint_1_{i}",
                position=Vector3(i * 10.0, 1.0, 0.0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={"team": 1},
                raw_content='parent="TEAM_1_HQ"',
            )
        )

    # Team 2 spawns
    for i in range(5):
        nodes.append(
            TscnNode(
                name=f"SpawnPoint_2_{i}",
                position=Vector3(i * 10.0, 1.0, 100.0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={"team": 2},
                raw_content='parent="TEAM_2_HQ"',
            )
        )

    # Capture points
    for i in range(3):
        nodes.append(
            TscnNode(
                name=f"CapturePoint_{i}",
                position=Vector3(50.0, 0.0, i * 30.0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content='parent="."',
            )
        )

    # Game objects
    for i in range(7):
        nodes.append(
            TscnNode(
                name=f"Tree_{i}",
                position=Vector3(i * 5.0, 2.0, i * 5.0),
                rotation_matrix=[0.707, -0.707, 0, 0.707, 0.707, 0, 0, 0, 1],
                properties={},
                raw_content='parent="Static"',
            )
        )

    return nodes


# ============================================================================
# Test MapComparison
# ============================================================================


class TestMapComparisonHasSpawnMismatch:
    """Test MapComparison.has_spawn_mismatch()."""

    def test_has_spawn_mismatch_returns_false_when_both_teams_match(self) -> None:
        """Test has_spawn_mismatch returns False when both teams match."""
        # Arrange
        comparison = MapComparison(
            source_team1_spawn_count=4,
            output_team1_spawn_count=4,
            source_team2_spawn_count=5,
            output_team2_spawn_count=5,
            source_capture_point_count=3,
            output_capture_point_count=3,
            source_object_count=7,
            output_object_count=7,
        )

        # Act
        result = comparison.has_spawn_mismatch()

        # Assert
        assert result is False

    def test_has_spawn_mismatch_returns_true_when_team1_differs(self) -> None:
        """Test has_spawn_mismatch returns True when Team 1 count differs."""
        # Arrange
        comparison = MapComparison(
            source_team1_spawn_count=4,
            output_team1_spawn_count=3,
            source_team2_spawn_count=5,
            output_team2_spawn_count=5,
            source_capture_point_count=3,
            output_capture_point_count=3,
            source_object_count=7,
            output_object_count=7,
        )

        # Act
        result = comparison.has_spawn_mismatch()

        # Assert
        assert result is True

    def test_has_spawn_mismatch_returns_true_when_team2_differs(self) -> None:
        """Test has_spawn_mismatch returns True when Team 2 count differs."""
        # Arrange
        comparison = MapComparison(
            source_team1_spawn_count=4,
            output_team1_spawn_count=4,
            source_team2_spawn_count=5,
            output_team2_spawn_count=6,
            source_capture_point_count=3,
            output_capture_point_count=3,
            source_object_count=7,
            output_object_count=7,
        )

        # Act
        result = comparison.has_spawn_mismatch()

        # Assert
        assert result is True

    def test_has_spawn_mismatch_returns_true_when_both_teams_differ(self) -> None:
        """Test has_spawn_mismatch returns True when both teams differ."""
        # Arrange
        comparison = MapComparison(
            source_team1_spawn_count=4,
            output_team1_spawn_count=3,
            source_team2_spawn_count=5,
            output_team2_spawn_count=6,
            source_capture_point_count=3,
            output_capture_point_count=3,
            source_object_count=7,
            output_object_count=7,
        )

        # Act
        result = comparison.has_spawn_mismatch()

        # Assert
        assert result is True


class TestMapComparisonHasCapturePointMismatch:
    """Test MapComparison.has_capture_point_mismatch()."""

    def test_has_capture_point_mismatch_returns_false_when_counts_match(self) -> None:
        """Test has_capture_point_mismatch returns False when counts match."""
        # Arrange
        comparison = MapComparison(
            source_team1_spawn_count=4,
            output_team1_spawn_count=4,
            source_team2_spawn_count=5,
            output_team2_spawn_count=5,
            source_capture_point_count=3,
            output_capture_point_count=3,
            source_object_count=7,
            output_object_count=7,
        )

        # Act
        result = comparison.has_capture_point_mismatch()

        # Assert
        assert result is False

    def test_has_capture_point_mismatch_returns_true_when_counts_differ(self) -> None:
        """Test has_capture_point_mismatch returns True when counts differ."""
        # Arrange
        comparison = MapComparison(
            source_team1_spawn_count=4,
            output_team1_spawn_count=4,
            source_team2_spawn_count=5,
            output_team2_spawn_count=5,
            source_capture_point_count=3,
            output_capture_point_count=2,
            source_object_count=7,
            output_object_count=7,
        )

        # Act
        result = comparison.has_capture_point_mismatch()

        # Assert
        assert result is True


class TestMapComparisonHasObjectMismatch:
    """Test MapComparison.has_object_mismatch()."""

    def test_has_object_mismatch_returns_false_when_counts_match(self) -> None:
        """Test has_object_mismatch returns False when counts match."""
        # Arrange
        comparison = MapComparison(
            source_team1_spawn_count=4,
            output_team1_spawn_count=4,
            source_team2_spawn_count=5,
            output_team2_spawn_count=5,
            source_capture_point_count=3,
            output_capture_point_count=3,
            source_object_count=7,
            output_object_count=7,
        )

        # Act
        result = comparison.has_object_mismatch()

        # Assert
        assert result is False

    def test_has_object_mismatch_returns_true_when_counts_differ(self) -> None:
        """Test has_object_mismatch returns True when counts differ."""
        # Arrange
        comparison = MapComparison(
            source_team1_spawn_count=4,
            output_team1_spawn_count=4,
            source_team2_spawn_count=5,
            output_team2_spawn_count=5,
            source_capture_point_count=3,
            output_capture_point_count=3,
            source_object_count=7,
            output_object_count=10,
        )

        # Act
        result = comparison.has_object_mismatch()

        # Assert
        assert result is True


# ============================================================================
# Test MapComparator.compare()
# ============================================================================


class TestMapComparatorCompare:
    """Test MapComparator.compare()."""

    def test_compare_returns_correct_counts_when_matching(
        self, sample_map_data: MapData, sample_tscn_nodes: list[TscnNode]
    ) -> None:
        """Test compare returns correct counts when source and output match."""
        # Arrange
        comparator = MapComparator()

        # Act
        comparison = comparator.compare(sample_map_data, sample_tscn_nodes)

        # Assert
        assert comparison.source_team1_spawn_count == 4
        assert comparison.output_team1_spawn_count == 4
        assert comparison.source_team2_spawn_count == 5
        assert comparison.output_team2_spawn_count == 5
        assert comparison.source_capture_point_count == 3
        assert comparison.output_capture_point_count == 3
        assert comparison.source_object_count == 7
        assert comparison.output_object_count == len(sample_tscn_nodes)

    def test_compare_counts_all_nodes_as_output_objects(self) -> None:
        """Test compare counts all nodes as output objects."""
        # Arrange
        comparator = MapComparator()
        map_data = MapData(
            map_name="Test",
            game_mode="Conquest",
            team1_hq=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
            team2_hq=Transform(position=Vector3(0, 0, 100), rotation=Rotation(0, 0, 0)),
            team1_spawns=[],
            team2_spawns=[],
            capture_points=[],
            game_objects=[],
            bounds=MapBounds(
                min_point=Vector3(0, 0, 0),
                max_point=Vector3(100, 50, 100),
                combat_area_polygon=[],
                height=50.0,
            ),
            metadata={},
        )
        nodes = [
            TscnNode(
                name="Node1",
                position=Vector3(0, 0, 0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
            TscnNode(
                name="Node2",
                position=Vector3(10, 0, 0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
        ]

        # Act
        comparison = comparator.compare(map_data, nodes)

        # Assert
        assert comparison.output_object_count == 2


# ============================================================================
# Test MapComparator._count_team_spawns()
# ============================================================================


class TestMapComparatorCountTeamSpawns:
    """Test MapComparator._count_team_spawns()."""

    def test_count_team_spawns_counts_team1_spawns_correctly(self) -> None:
        """Test _count_team_spawns counts Team 1 spawns correctly."""
        # Arrange
        comparator = MapComparator()
        nodes = [
            TscnNode(
                name="SpawnPoint_1_0",
                position=Vector3(0, 0, 0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
            TscnNode(
                name="SpawnPoint_1_1",
                position=Vector3(10, 0, 0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
            TscnNode(
                name="SpawnPoint_2_0",
                position=Vector3(0, 0, 100),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
        ]

        # Act
        count = comparator._count_team_spawns(nodes, 1)

        # Assert
        assert count == 2

    def test_count_team_spawns_counts_team2_spawns_correctly(self) -> None:
        """Test _count_team_spawns counts Team 2 spawns correctly."""
        # Arrange
        comparator = MapComparator()
        nodes = [
            TscnNode(
                name="SpawnPoint_1_0",
                position=Vector3(0, 0, 0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
            TscnNode(
                name="SpawnPoint_2_0",
                position=Vector3(0, 0, 100),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
            TscnNode(
                name="SpawnPoint_2_1",
                position=Vector3(10, 0, 100),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
        ]

        # Act
        count = comparator._count_team_spawns(nodes, 2)

        # Assert
        assert count == 2

    def test_count_team_spawns_returns_zero_when_no_spawns(self) -> None:
        """Test _count_team_spawns returns zero when no spawns exist."""
        # Arrange
        comparator = MapComparator()
        nodes = [
            TscnNode(
                name="SomeOtherNode",
                position=Vector3(0, 0, 0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
        ]

        # Act
        count = comparator._count_team_spawns(nodes, 1)

        # Assert
        assert count == 0


# ============================================================================
# Test MapComparator._count_capture_points()
# ============================================================================


class TestMapComparatorCountCapturePoints:
    """Test MapComparator._count_capture_points()."""

    def test_count_capture_points_counts_non_static_cps_correctly(self) -> None:
        """Test _count_capture_points counts non-static CPs correctly."""
        # Arrange
        comparator = MapComparator()
        nodes = [
            TscnNode(
                name="CapturePoint_0",
                position=Vector3(0, 0, 0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content='parent="."',
            ),
            TscnNode(
                name="CapturePoint_1",
                position=Vector3(10, 0, 0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content='parent="."',
            ),
        ]

        # Act
        count = comparator._count_capture_points(nodes)

        # Assert
        assert count == 2

    def test_count_capture_points_excludes_static_cps(self) -> None:
        """Test _count_capture_points excludes CPs in Static parent."""
        # Arrange
        comparator = MapComparator()
        nodes = [
            TscnNode(
                name="CapturePoint_0",
                position=Vector3(0, 0, 0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content='parent="."',
            ),
            TscnNode(
                name="CapturePoint_1",
                position=Vector3(10, 0, 0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content='parent="Static"',
            ),
        ]

        # Act
        count = comparator._count_capture_points(nodes)

        # Assert
        assert count == 1

    def test_count_capture_points_returns_zero_when_no_cps(self) -> None:
        """Test _count_capture_points returns zero when no CPs exist."""
        # Arrange
        comparator = MapComparator()
        nodes = [
            TscnNode(
                name="SomeOtherNode",
                position=Vector3(0, 0, 0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
        ]

        # Act
        count = comparator._count_capture_points(nodes)

        # Assert
        assert count == 0


# ============================================================================
# Test MapComparator.calculate_position_centroid()
# ============================================================================


class TestMapComparatorCalculatePositionCentroid:
    """Test MapComparator.calculate_position_centroid()."""

    def test_calculate_position_centroid_returns_zero_vector_when_empty(self) -> None:
        """Test calculate_position_centroid returns zero vector when empty."""
        # Arrange
        comparator = MapComparator()
        nodes: list[TscnNode] = []

        # Act
        centroid = comparator.calculate_position_centroid(nodes)

        # Assert
        assert centroid.x == 0
        assert centroid.y == 0
        assert centroid.z == 0

    def test_calculate_position_centroid_calculates_average_position(self) -> None:
        """Test calculate_position_centroid calculates average position."""
        # Arrange
        comparator = MapComparator()
        nodes = [
            TscnNode(
                name="Node1",
                position=Vector3(0, 0, 0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
            TscnNode(
                name="Node2",
                position=Vector3(10, 20, 30),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
            TscnNode(
                name="Node3",
                position=Vector3(20, 40, 60),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
        ]

        # Act
        centroid = comparator.calculate_position_centroid(nodes)

        # Assert
        assert centroid.x == 10.0
        assert centroid.y == 20.0
        assert centroid.z == 30.0

    def test_calculate_position_centroid_handles_negative_coordinates(self) -> None:
        """Test calculate_position_centroid handles negative coordinates."""
        # Arrange
        comparator = MapComparator()
        nodes = [
            TscnNode(
                name="Node1",
                position=Vector3(-10, -20, -30),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
            TscnNode(
                name="Node2",
                position=Vector3(10, 20, 30),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
        ]

        # Act
        centroid = comparator.calculate_position_centroid(nodes)

        # Assert
        assert centroid.x == 0.0
        assert centroid.y == 0.0
        assert centroid.z == 0.0


# ============================================================================
# Test MapComparator.calculate_bounds()
# ============================================================================


class TestMapComparatorCalculateBounds:
    """Test MapComparator.calculate_bounds()."""

    def test_calculate_bounds_returns_zero_vectors_when_empty(self) -> None:
        """Test calculate_bounds returns zero vectors when empty."""
        # Arrange
        comparator = MapComparator()
        nodes: list[TscnNode] = []

        # Act
        min_point, max_point = comparator.calculate_bounds(nodes)

        # Assert
        assert min_point.x == 0
        assert min_point.y == 0
        assert min_point.z == 0
        assert max_point.x == 0
        assert max_point.y == 0
        assert max_point.z == 0

    def test_calculate_bounds_calculates_min_and_max_correctly(self) -> None:
        """Test calculate_bounds calculates min and max correctly."""
        # Arrange
        comparator = MapComparator()
        nodes = [
            TscnNode(
                name="Node1",
                position=Vector3(0, 0, 0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
            TscnNode(
                name="Node2",
                position=Vector3(100, 50, 200),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
            TscnNode(
                name="Node3",
                position=Vector3(-50, 25, 150),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
        ]

        # Act
        min_point, max_point = comparator.calculate_bounds(nodes)

        # Assert
        assert min_point.x == -50
        assert min_point.y == 0
        assert min_point.z == 0
        assert max_point.x == 100
        assert max_point.y == 50
        assert max_point.z == 200

    def test_calculate_bounds_handles_single_node(self) -> None:
        """Test calculate_bounds handles single node."""
        # Arrange
        comparator = MapComparator()
        nodes = [
            TscnNode(
                name="Node1",
                position=Vector3(42, 13, 99),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
        ]

        # Act
        min_point, max_point = comparator.calculate_bounds(nodes)

        # Assert
        assert min_point.x == 42
        assert min_point.y == 13
        assert min_point.z == 99
        assert max_point.x == 42
        assert max_point.y == 13
        assert max_point.z == 99

    def test_calculate_bounds_handles_negative_coordinates(self) -> None:
        """Test calculate_bounds handles negative coordinates."""
        # Arrange
        comparator = MapComparator()
        nodes = [
            TscnNode(
                name="Node1",
                position=Vector3(-100, -50, -200),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
            TscnNode(
                name="Node2",
                position=Vector3(-10, -5, -20),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            ),
        ]

        # Act
        min_point, max_point = comparator.calculate_bounds(nodes)

        # Assert
        assert min_point.x == -100
        assert min_point.y == -50
        assert min_point.z == -200
        assert max_point.x == -10
        assert max_point.y == -5
        assert max_point.z == -20
