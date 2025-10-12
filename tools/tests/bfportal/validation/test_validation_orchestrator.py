#!/usr/bin/env python3
"""Tests for ValidationOrchestrator."""

from pathlib import Path
from unittest.mock import patch

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
from bfportal.validation.tscn_reader import TscnNode
from bfportal.validation.validation_orchestrator import ValidationOrchestrator


@pytest.fixture
def sample_map_data() -> MapData:
    """Create sample map data for testing.

    Returns:
        MapData with spawns, CPs, and objects
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
        for i in range(4)
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
        metadata={"source_path": "/path/to/source"},
    )


@pytest.fixture
def sample_tscn_nodes() -> list[TscnNode]:
    """Create sample .tscn nodes matching sample_map_data.

    Returns:
        List of TscnNode objects
    """
    # Arrange
    nodes = []

    # Add Team 1 spawn points
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

    # Add Team 2 spawn points
    for i in range(4):
        nodes.append(
            TscnNode(
                name=f"SpawnPoint_2_{i}",
                position=Vector3(i * 10.0, 1.0, 100.0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={"team": 2},
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
                properties={},
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
                properties={},
                raw_content='parent="Static"',
            )
        )

    return nodes


class TestValidationOrchestratorInit:
    """Tests for ValidationOrchestrator.__init__()."""

    def test_initializes_successfully_with_terrain_provider(
        self, sample_map_data: MapData, tmp_path: Path
    ):
        """Test successful initialization with terrain provider."""
        # Arrange
        output_path = tmp_path / "test.tscn"
        terrain = FixedHeightProvider(fixed_height=100.0)

        # Act
        orchestrator = ValidationOrchestrator(
            source_data=sample_map_data,
            output_tscn_path=output_path,
            terrain_provider=terrain,
            terrain_size=2048.0,
        )

        # Assert
        assert orchestrator.source_data == sample_map_data
        assert orchestrator.output_tscn_path == output_path
        assert orchestrator.terrain_provider == terrain
        assert orchestrator.terrain_size == 2048.0
        assert orchestrator.issues == []

    def test_initializes_successfully_without_terrain_provider(
        self, sample_map_data: MapData, tmp_path: Path
    ):
        """Test successful initialization without terrain provider."""
        # Arrange
        output_path = tmp_path / "test.tscn"

        # Act
        orchestrator = ValidationOrchestrator(
            source_data=sample_map_data, output_tscn_path=output_path
        )

        # Assert
        assert orchestrator.terrain_provider is None
        assert orchestrator.terrain_size == 2048.0


class TestValidateMethod:
    """Tests for ValidationOrchestrator.validate() method."""

    def test_validate_returns_success_with_no_issues(
        self, sample_map_data: MapData, sample_tscn_nodes: list[TscnNode], tmp_path: Path
    ):
        """Test validate returns success when no issues found."""
        # Arrange
        output_path = tmp_path / "test.tscn"
        orchestrator = ValidationOrchestrator(
            source_data=sample_map_data, output_tscn_path=output_path
        )

        with patch.object(orchestrator.tscn_reader, "parse", return_value=sample_tscn_nodes):
            # Act
            is_valid, issues = orchestrator.validate()

        # Assert
        assert is_valid is True
        # May have info issues (like all identity rotations) but no errors/warnings
        error_count = sum(1 for i in issues if i.severity in ["error", "warning"])
        assert error_count == 0

    def test_validate_returns_failure_with_errors(self, sample_map_data: MapData, tmp_path: Path):
        """Test validate returns failure when errors found."""
        # Arrange
        output_path = tmp_path / "test.tscn"
        orchestrator = ValidationOrchestrator(
            source_data=sample_map_data, output_tscn_path=output_path
        )

        # Create mismatched nodes (missing Team 1 spawns)
        nodes = [
            TscnNode(
                name=f"SpawnPoint_2_{i}",
                position=Vector3(i * 10.0, 1.0, 100.0),
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={"team": 2},
                raw_content='parent="TEAM_2_HQ"',
            )
            for i in range(4)
        ]

        with patch.object(orchestrator.tscn_reader, "parse", return_value=nodes):
            # Act
            is_valid, issues = orchestrator.validate()

        # Assert
        assert is_valid is False
        assert len(issues) > 0
        assert any(issue.severity == "error" for issue in issues)

    def test_validate_with_terrain_provider(
        self, sample_map_data: MapData, sample_tscn_nodes: list[TscnNode], tmp_path: Path
    ):
        """Test validate runs height validation with terrain provider."""
        # Arrange
        output_path = tmp_path / "test.tscn"
        terrain = FixedHeightProvider(fixed_height=1.0)
        orchestrator = ValidationOrchestrator(
            source_data=sample_map_data,
            output_tscn_path=output_path,
            terrain_provider=terrain,
        )

        with patch.object(orchestrator.tscn_reader, "parse", return_value=sample_tscn_nodes):
            # Act
            is_valid, issues = orchestrator.validate()

        # Assert
        assert is_valid is True

    def test_validate_without_terrain_provider_skips_height_checks(
        self, sample_map_data: MapData, sample_tscn_nodes: list[TscnNode], tmp_path: Path
    ):
        """Test validate skips height validation without terrain provider."""
        # Arrange
        output_path = tmp_path / "test.tscn"
        orchestrator = ValidationOrchestrator(
            source_data=sample_map_data,
            output_tscn_path=output_path,
            terrain_provider=None,
        )

        with patch.object(orchestrator.tscn_reader, "parse", return_value=sample_tscn_nodes):
            # Act
            is_valid, issues = orchestrator.validate()

        # Assert
        assert is_valid is True
        # No height validation issues should be present
        height_issues = [i for i in issues if i.category == "height"]
        assert len(height_issues) == 0


class TestRunValidators:
    """Tests for ValidationOrchestrator._run_validators() method."""

    def test_run_validators_executes_all_validators(
        self, sample_map_data: MapData, sample_tscn_nodes: list[TscnNode], tmp_path: Path
    ):
        """Test _run_validators executes all validators."""
        # Arrange
        output_path = tmp_path / "test.tscn"
        orchestrator = ValidationOrchestrator(
            source_data=sample_map_data, output_tscn_path=output_path
        )

        comparison = orchestrator.map_comparator.compare(sample_map_data, sample_tscn_nodes)

        # Act
        orchestrator._run_validators(comparison, sample_tscn_nodes)

        # Assert
        # Should have run all validators with no errors/warnings (may have info issues)
        error_count = sum(1 for i in orchestrator.issues if i.severity in ["error", "warning"])
        assert error_count == 0

    def test_run_validators_collects_issues_from_multiple_validators(
        self, sample_map_data: MapData, tmp_path: Path
    ):
        """Test _run_validators collects issues from multiple validators."""
        # Arrange
        output_path = tmp_path / "test.tscn"
        orchestrator = ValidationOrchestrator(
            source_data=sample_map_data, output_tscn_path=output_path
        )

        # Create problematic nodes (out of bounds + missing spawns)
        nodes = [
            TscnNode(
                name="OutOfBounds",
                position=Vector3(5000.0, 0.0, 5000.0),  # Way out of bounds
                rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                properties={},
                raw_content="",
            )
        ]

        comparison = orchestrator.map_comparator.compare(sample_map_data, nodes)

        # Act
        orchestrator._run_validators(comparison, nodes)

        # Assert
        assert len(orchestrator.issues) > 0
        # Should have spawn count errors AND bounds warnings
        assert any(i.category == "missing" for i in orchestrator.issues)
        assert any(i.category == "bounds" for i in orchestrator.issues)


class TestPrintReport:
    """Tests for ValidationOrchestrator._print_report() method."""

    def test_print_report_with_no_issues(self, sample_map_data: MapData, tmp_path: Path, capsys):
        """Test _print_report with no issues."""
        # Arrange
        output_path = tmp_path / "test.tscn"
        orchestrator = ValidationOrchestrator(
            source_data=sample_map_data, output_tscn_path=output_path
        )
        orchestrator.issues = []

        # Act
        orchestrator._print_report()

        # Assert
        captured = capsys.readouterr()
        assert "ALL VALIDATION CHECKS PASSED" in captured.out

    def test_print_report_with_errors(self, sample_map_data: MapData, tmp_path: Path, capsys):
        """Test _print_report with errors."""
        # Arrange
        from bfportal.validation.validators import ValidationIssue

        output_path = tmp_path / "test.tscn"
        orchestrator = ValidationOrchestrator(
            source_data=sample_map_data, output_tscn_path=output_path
        )
        orchestrator.issues = [
            ValidationIssue(
                severity="error",
                category="missing",
                message="Test error",
                expected_value="4",
                actual_value="0",
            )
        ]

        # Act
        orchestrator._print_report()

        # Assert
        captured = capsys.readouterr()
        assert "ERRORS (1)" in captured.out
        assert "Test error" in captured.out

    def test_print_report_with_warnings(self, sample_map_data: MapData, tmp_path: Path, capsys):
        """Test _print_report with warnings."""
        # Arrange
        from bfportal.validation.validators import ValidationIssue

        output_path = tmp_path / "test.tscn"
        orchestrator = ValidationOrchestrator(
            source_data=sample_map_data, output_tscn_path=output_path
        )
        orchestrator.issues = [
            ValidationIssue(
                severity="warning",
                category="positioning",
                message="Test warning",
                object_name="TestObject",
            )
        ]

        # Act
        orchestrator._print_report()

        # Assert
        captured = capsys.readouterr()
        assert "WARNINGS (1)" in captured.out
        assert "Test warning" in captured.out
        assert "TestObject" in captured.out

    def test_print_report_with_info(self, sample_map_data: MapData, tmp_path: Path, capsys):
        """Test _print_report with info messages."""
        # Arrange
        from bfportal.validation.validators import ValidationIssue

        output_path = tmp_path / "test.tscn"
        orchestrator = ValidationOrchestrator(
            source_data=sample_map_data, output_tscn_path=output_path
        )
        orchestrator.issues = [
            ValidationIssue(severity="info", category="rotation", message="Test info")
        ]

        # Act
        orchestrator._print_report()

        # Assert
        captured = capsys.readouterr()
        assert "INFO (1)" in captured.out
        assert "Test info" in captured.out

    def test_print_report_with_mixed_severities(
        self, sample_map_data: MapData, tmp_path: Path, capsys
    ):
        """Test _print_report with mixed severity levels."""
        # Arrange
        from bfportal.validation.validators import ValidationIssue

        output_path = tmp_path / "test.tscn"
        orchestrator = ValidationOrchestrator(
            source_data=sample_map_data, output_tscn_path=output_path
        )
        orchestrator.issues = [
            ValidationIssue(severity="error", category="missing", message="Error 1"),
            ValidationIssue(severity="warning", category="positioning", message="Warning 1"),
            ValidationIssue(severity="info", category="rotation", message="Info 1"),
        ]

        # Act
        orchestrator._print_report()

        # Assert
        captured = capsys.readouterr()
        assert "ERRORS (1)" in captured.out
        assert "WARNINGS (1)" in captured.out
        assert "INFO (1)" in captured.out
