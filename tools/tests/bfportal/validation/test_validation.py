#!/usr/bin/env python3
"""Tests for validation logic in tools/bfportal/validation/.

Tests all validators:
- SpawnCountValidator: Validates spawn point counts match source
- CapturePointValidator: Validates capture point counts
- PositioningValidator: Validates map centering
- HeightValidator: Validates object heights match terrain
- BoundsValidator: Validates objects are within bounds
- OrientationValidator: Validates object rotations
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
from bfportal.terrain.terrain_provider import FixedHeightProvider
from bfportal.validation.map_comparator import MapComparator, MapComparison
from bfportal.validation.tscn_reader import TscnNode
from bfportal.validation.validators import (
    BoundsValidator,
    CapturePointValidator,
    HeightValidator,
    OrientationValidator,
    PositioningValidator,
    SpawnCountValidator,
    ValidationIssue,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_source_data() -> MapData:
    """Create sample source map data for testing.

    Returns:
        MapData with known counts of spawns, CPs, and objects
    """
    # Create spawn points
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
        for i in range(4)
    ]

    # Create capture points
    capture_points = [
        CapturePoint(
            name=f"CP_{i}",
            transform=Transform(position=Vector3(50.0, 0.0, i * 30.0), rotation=Rotation(0, 0, 0)),
            radius=20.0,
            control_area=[Vector3(0, 0, 0), Vector3(10, 0, 0), Vector3(10, 0, 10)],
        )
        for i in range(3)
    ]

    # Create game objects
    game_objects = [
        GameObject(
            name=f"Object_{i}",
            asset_type="Tree_Pine_Large",
            transform=Transform(
                position=Vector3(i * 5.0, 0.0, i * 5.0), rotation=Rotation(0, 0, 0)
            ),
            team=Team.NEUTRAL,
            properties={},
        )
        for i in range(10)
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
def sample_output_nodes() -> list[TscnNode]:
    """Create sample output nodes for testing.

    Returns:
        List of TscnNode objects matching sample_source_data
    """
    nodes = []

    # Add Team 1 spawn points
    for i in range(4):
        nodes.append(
            TscnNode(
                name=f"SpawnPoint_1_{i}",
                position=Vector3(i * 10.0, 1.0, 0.0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],  # Identity
                properties={"team": 1, "objid": i},
                raw_content='parent="TEAM_1_HQ"',
            )
        )

    # Add Team 2 spawn points
    for i in range(4):
        nodes.append(
            TscnNode(
                name=f"SpawnPoint_2_{i}",
                position=Vector3(i * 10.0, 1.0, 100.0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],  # Identity
                properties={"team": 2, "objid": i + 10},
                raw_content='parent="TEAM_2_HQ"',
            )
        )

    # Add capture points
    for i in range(3):
        nodes.append(
            TscnNode(
                name=f"CapturePoint_{i}",
                position=Vector3(50.0, 0.0, i * 30.0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={"objid": i + 20},
                raw_content='parent="."',
            )
        )

    # Add game objects
    for i in range(10):
        nodes.append(
            TscnNode(
                name=f"Tree_{i}",
                position=Vector3(i * 5.0, 0.0, i * 5.0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={"objid": i + 30},
                raw_content='parent="Static"',
            )
        )

    return nodes


@pytest.fixture
def sample_comparison(
    sample_source_data: MapData, sample_output_nodes: list[TscnNode]
) -> MapComparison:
    """Create a MapComparison for testing.

    Returns:
        MapComparison with matching counts
    """
    comparator = MapComparator()
    return comparator.compare(sample_source_data, sample_output_nodes)


# ============================================================================
# Test SpawnCountValidator
# ============================================================================


def test_spawn_count_validator_no_issues(sample_comparison: MapComparison):
    """Test SpawnCountValidator with matching spawn counts."""
    validator = SpawnCountValidator(sample_comparison)
    issues = validator.validate()

    assert len(issues) == 0, "Should have no issues when spawn counts match"


def test_spawn_count_validator_team1_mismatch():
    """Test SpawnCountValidator detects Team 1 spawn count mismatch."""
    comparison = MapComparison(
        source_team1_spawn_count=4,
        output_team1_spawn_count=3,  # Mismatch!
        source_team2_spawn_count=4,
        output_team2_spawn_count=4,
        source_capture_point_count=3,
        output_capture_point_count=3,
        source_object_count=10,
        output_object_count=10,
    )

    validator = SpawnCountValidator(comparison)
    issues = validator.validate()

    assert len(issues) == 1, "Should detect Team 1 spawn count mismatch"
    assert issues[0].severity == "error"
    assert issues[0].category == "missing"
    assert "Team 1" in issues[0].message
    assert issues[0].expected_value == "4"
    assert issues[0].actual_value == "3"


def test_spawn_count_validator_team2_mismatch():
    """Test SpawnCountValidator detects Team 2 spawn count mismatch."""
    comparison = MapComparison(
        source_team1_spawn_count=4,
        output_team1_spawn_count=4,
        source_team2_spawn_count=4,
        output_team2_spawn_count=5,  # Mismatch!
        source_capture_point_count=3,
        output_capture_point_count=3,
        source_object_count=10,
        output_object_count=10,
    )

    validator = SpawnCountValidator(comparison)
    issues = validator.validate()

    assert len(issues) == 1, "Should detect Team 2 spawn count mismatch"
    assert issues[0].severity == "error"
    assert "Team 2" in issues[0].message


def test_spawn_count_validator_both_teams_mismatch():
    """Test SpawnCountValidator detects both teams spawn count mismatch."""
    comparison = MapComparison(
        source_team1_spawn_count=4,
        output_team1_spawn_count=3,  # Mismatch!
        source_team2_spawn_count=4,
        output_team2_spawn_count=5,  # Mismatch!
        source_capture_point_count=3,
        output_capture_point_count=3,
        source_object_count=10,
        output_object_count=10,
    )

    validator = SpawnCountValidator(comparison)
    issues = validator.validate()

    assert len(issues) == 2, "Should detect both team spawn count mismatches"
    assert all(issue.severity == "error" for issue in issues)


# ============================================================================
# Test CapturePointValidator
# ============================================================================


def test_capture_point_validator_no_issues(sample_comparison: MapComparison):
    """Test CapturePointValidator with matching CP counts."""
    validator = CapturePointValidator(sample_comparison)
    issues = validator.validate()

    assert len(issues) == 0, "Should have no issues when CP counts match"


def test_capture_point_validator_mismatch():
    """Test CapturePointValidator detects CP count mismatch."""
    comparison = MapComparison(
        source_team1_spawn_count=4,
        output_team1_spawn_count=4,
        source_team2_spawn_count=4,
        output_team2_spawn_count=4,
        source_capture_point_count=3,
        output_capture_point_count=2,  # Mismatch!
        source_object_count=10,
        output_object_count=10,
    )

    validator = CapturePointValidator(comparison)
    issues = validator.validate()

    assert len(issues) == 1, "Should detect CP count mismatch"
    assert issues[0].severity == "error"
    assert issues[0].category == "missing"
    assert "Capture point" in issues[0].message
    assert issues[0].expected_value == "3"
    assert issues[0].actual_value == "2"


# ============================================================================
# Test PositioningValidator
# ============================================================================


def test_positioning_validator_centered():
    """Test PositioningValidator with centered map."""
    nodes = [
        TscnNode(
            name="Node1",
            position=Vector3(10.0, 0.0, 10.0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        ),
        TscnNode(
            name="Node2",
            position=Vector3(-10.0, 0.0, -10.0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        ),
    ]

    validator = PositioningValidator(nodes, tolerance=50.0)
    issues = validator.validate()

    assert len(issues) == 0, "Should have no issues when map is centered"


def test_positioning_validator_off_center():
    """Test PositioningValidator detects off-center map."""
    nodes = [
        TscnNode(
            name="Node1",
            position=Vector3(100.0, 0.0, 100.0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        ),
        TscnNode(
            name="Node2",
            position=Vector3(110.0, 0.0, 110.0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        ),
    ]

    validator = PositioningValidator(nodes, tolerance=50.0)
    issues = validator.validate()

    assert len(issues) == 1, "Should detect off-center map"
    assert issues[0].severity == "warning"
    assert issues[0].category == "positioning"
    assert "not centered" in issues[0].message


def test_positioning_validator_empty_nodes():
    """Test PositioningValidator with no nodes."""
    validator = PositioningValidator([], tolerance=50.0)
    issues = validator.validate()

    assert len(issues) == 0, "Should handle empty node list"


# ============================================================================
# Test HeightValidator
# ============================================================================


def test_height_validator_no_terrain_provider():
    """Test HeightValidator with no terrain provider."""
    nodes = [
        TscnNode(
            name="SpawnPoint_1_1",
            position=Vector3(0.0, 10.0, 0.0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        )
    ]

    validator = HeightValidator(nodes, None)
    issues = validator.validate()

    assert len(issues) == 0, "Should have no issues when no terrain provider"


def test_height_validator_correct_heights():
    """Test HeightValidator with correct spawn heights."""
    terrain = FixedHeightProvider(fixed_height=100.0)

    nodes = [
        TscnNode(
            name="SpawnPoint_1_1",
            position=Vector3(0.0, 101.0, 0.0),  # 1m above terrain (expected)
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        ),
        TscnNode(
            name="SpawnPoint_1_2",
            position=Vector3(10.0, 101.0, 10.0),  # 1m above terrain (expected)
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        ),
    ]

    validator = HeightValidator(nodes, terrain, tolerance=2.0, expected_offset=1.0)
    issues = validator.validate()

    assert len(issues) == 0, "Should have no issues when heights are correct"


def test_height_validator_incorrect_heights():
    """Test HeightValidator detects incorrect spawn heights."""
    terrain = FixedHeightProvider(fixed_height=100.0)

    nodes = [
        TscnNode(
            name="SpawnPoint_1_1",
            position=Vector3(0.0, 95.0, 0.0),  # 5m below expected (should error)
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        ),
        TscnNode(
            name="SpawnPoint_1_2",
            position=Vector3(10.0, 110.0, 10.0),  # 9m above expected (should error)
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        ),
    ]

    validator = HeightValidator(nodes, terrain, tolerance=2.0, expected_offset=1.0)
    issues = validator.validate()

    assert len(issues) == 2, "Should detect both height mismatches"
    assert all(issue.severity == "warning" for issue in issues)
    assert all(issue.category == "height" for issue in issues)


def test_height_validator_limits_reported_issues():
    """Test HeightValidator only reports first 3 height issues."""
    terrain = FixedHeightProvider(fixed_height=100.0)

    # Create 10 spawns with incorrect heights
    nodes = [
        TscnNode(
            name=f"SpawnPoint_1_{i}",
            position=Vector3(i * 10.0, 95.0, 0.0),  # All wrong
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        )
        for i in range(10)
    ]

    validator = HeightValidator(nodes, terrain, tolerance=2.0, expected_offset=1.0)
    issues = validator.validate()

    assert len(issues) == 3, "Should only report first 3 height issues"


# ============================================================================
# Test BoundsValidator
# ============================================================================


def test_bounds_validator_all_in_bounds():
    """Test BoundsValidator with all objects in bounds."""
    nodes = [
        TscnNode(
            name="Node1",
            position=Vector3(50.0, 0.0, 50.0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        ),
        TscnNode(
            name="Node2",
            position=Vector3(-50.0, 0.0, -50.0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        ),
    ]

    validator = BoundsValidator(nodes, max_distance=1000.0)
    issues = validator.validate()

    assert len(issues) == 0, "Should have no issues when all in bounds"


def test_bounds_validator_out_of_bounds():
    """Test BoundsValidator detects objects out of bounds."""
    nodes = [
        TscnNode(
            name="Node1",
            position=Vector3(50.0, 0.0, 50.0),  # In bounds
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        ),
        TscnNode(
            name="Node2",
            position=Vector3(1500.0, 0.0, 1500.0),  # Out of bounds
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        ),
    ]

    validator = BoundsValidator(nodes, max_distance=1000.0)
    issues = validator.validate()

    assert len(issues) == 1, "Should detect objects out of bounds"
    assert issues[0].severity == "warning"
    assert issues[0].category == "bounds"
    assert "outside expected bounds" in issues[0].message


# ============================================================================
# Test OrientationValidator
# ============================================================================


def test_orientation_validator_mixed_rotations():
    """Test OrientationValidator with mixed rotations."""
    nodes = [
        TscnNode(
            name="Node1",
            position=Vector3(0, 0, 0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],  # Identity
            properties={},
            raw_content="",
        ),
        TscnNode(
            name="Node2",
            position=Vector3(10, 0, 0),
            rotation_matrix=[0.7071, -0.7071, 0, 0.7071, 0.7071, 0, 0, 0, 1],  # Rotated
            properties={},
            raw_content="",
        ),
    ]

    validator = OrientationValidator(nodes)
    issues = validator.validate()

    assert len(issues) == 0, "Should have no issues with mixed rotations"


def test_orientation_validator_all_identity():
    """Test OrientationValidator detects all identity rotations."""
    # Create 15 nodes with identity rotation
    nodes = [
        TscnNode(
            name=f"Node{i}",
            position=Vector3(i * 10.0, 0, 0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],  # All identity
            properties={},
            raw_content="",
        )
        for i in range(15)
    ]

    validator = OrientationValidator(nodes)
    issues = validator.validate()

    assert len(issues) == 1, "Should detect all identity rotations"
    assert issues[0].severity == "info"
    assert issues[0].category == "rotation"
    assert "No objects have rotation" in issues[0].message


def test_orientation_validator_few_nodes_all_identity():
    """Test OrientationValidator doesn't flag small maps with identity rotations."""
    # Only 5 nodes - shouldn't trigger the warning
    nodes = [
        TscnNode(
            name=f"Node{i}",
            position=Vector3(i * 10.0, 0, 0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={},
            raw_content="",
        )
        for i in range(5)
    ]

    validator = OrientationValidator(nodes)
    issues = validator.validate()

    assert len(issues) == 0, "Should not flag small maps with identity rotations"


# ============================================================================
# Test ValidationIssue
# ============================================================================


def test_validation_issue_creation():
    """Test ValidationIssue dataclass creation."""
    issue = ValidationIssue(
        severity="error",
        category="missing",
        message="Test issue",
        object_name="TestObject",
        expected_value="5",
        actual_value="3",
    )

    assert issue.severity == "error"
    assert issue.category == "missing"
    assert issue.message == "Test issue"
    assert issue.object_name == "TestObject"
    assert issue.expected_value == "5"
    assert issue.actual_value == "3"


def test_validation_issue_minimal():
    """Test ValidationIssue with minimal fields."""
    issue = ValidationIssue(severity="warning", category="positioning", message="Test warning")

    assert issue.severity == "warning"
    assert issue.category == "positioning"
    assert issue.message == "Test warning"
    assert issue.object_name == ""
    assert issue.expected_value is None
    assert issue.actual_value is None
