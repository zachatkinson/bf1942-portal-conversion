#!/usr/bin/env python3
"""Tests for portal_parse.py CLI script."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bfportal.core.exceptions import BFPortalError, ParseError
from bfportal.core.interfaces import Team, Vector3
from portal_parse import PortalParseApp, main

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_map_data():
    """Create mock map data structure matching portal_parse expectations."""
    # Arrange
    bounds_mock = SimpleNamespace(
        min=Vector3(x=-100.0, y=0.0, z=-100.0), max=Vector3(x=100.0, y=50.0, z=100.0)
    )

    spawn1 = SimpleNamespace(
        name="Spawn_1_1",
        team=Team.TEAM_1,
        transform=SimpleNamespace(
            position=Vector3(x=10.0, y=5.0, z=10.0),
            rotation=SimpleNamespace(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    )

    spawn2 = SimpleNamespace(
        name="Spawn_2_1",
        team=Team.TEAM_2,
        transform=SimpleNamespace(
            position=Vector3(x=-10.0, y=5.0, z=-10.0),
            rotation=SimpleNamespace(pitch=0.0, yaw=270.0, roll=0.0),
        ),
    )

    hq1 = SimpleNamespace(
        name="HQ_Team1",
        team=Team.TEAM_1,
        transform=SimpleNamespace(position=Vector3(x=20.0, y=0.0, z=20.0)),
    )

    hq2 = SimpleNamespace(
        name="HQ_Team2",
        team=Team.TEAM_2,
        transform=SimpleNamespace(position=Vector3(x=-20.0, y=0.0, z=-20.0)),
    )

    cp = SimpleNamespace(
        name="CapturePoint_1",
        transform=SimpleNamespace(position=Vector3(x=0.0, y=0.0, z=0.0)),
    )

    obj = SimpleNamespace(
        name="Building_01",
        asset_type="Building",
        team=Team.NEUTRAL,
        transform=SimpleNamespace(
            position=Vector3(x=5.0, y=0.0, z=5.0),
            rotation=SimpleNamespace(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    )

    map_data = SimpleNamespace(
        name="TestMap",
        bounds=bounds_mock,
        spawn_points=[spawn1, spawn2],
        hqs=[hq1, hq2],
        capture_points=[cp],
        game_objects=[obj],
    )

    return map_data


@pytest.fixture
def mock_map_data_minimal():
    """Create minimal mock map data for edge case testing."""
    # Arrange
    map_data = SimpleNamespace(
        name="MinimalMap",
        bounds=None,
        spawn_points=[],
        hqs=[],
        capture_points=[],
        game_objects=[],
    )

    return map_data


# ============================================================================
# Tests for PortalParseApp.__init__
# ============================================================================


class TestPortalParseAppInit:
    """Tests for PortalParseApp.__init__() initialization."""

    def test_initializes_app_successfully(self):
        """Test successful app initialization."""
        # Arrange
        # N/A

        # Act
        app = PortalParseApp()

        # Assert
        assert isinstance(app, PortalParseApp)


# ============================================================================
# Tests for PortalParseApp.parse_args
# ============================================================================


class TestPortalParseAppParseArgs:
    """Tests for PortalParseApp.parse_args() method."""

    def test_parse_args_with_required_arguments_succeeds(self):
        """Test argument parsing with required arguments succeeds."""
        # Arrange
        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            "/path/to/map",
        ]

        # Act
        with patch("sys.argv", test_args):
            args = app.parse_args()

        # Assert
        assert args.game == "bf1942"
        assert args.map_path == Path("/path/to/map")
        assert args.output is None
        assert args.format == "summary"
        assert args.verbose is False

    def test_parse_args_with_bfvietnam_game_succeeds(self):
        """Test argument parsing with bfvietnam game succeeds."""
        # Arrange
        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bfvietnam",
            "--map-path",
            "/path/to/map",
        ]

        # Act
        with patch("sys.argv", test_args):
            args = app.parse_args()

        # Assert
        assert args.game == "bfvietnam"

    def test_parse_args_with_bf2_game_succeeds(self):
        """Test argument parsing with bf2 game succeeds."""
        # Arrange
        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf2",
            "--map-path",
            "/path/to/map",
        ]

        # Act
        with patch("sys.argv", test_args):
            args = app.parse_args()

        # Assert
        assert args.game == "bf2"

    def test_parse_args_with_bf2142_game_succeeds(self):
        """Test argument parsing with bf2142 game succeeds."""
        # Arrange
        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf2142",
            "--map-path",
            "/path/to/map",
        ]

        # Act
        with patch("sys.argv", test_args):
            args = app.parse_args()

        # Assert
        assert args.game == "bf2142"

    def test_parse_args_with_output_file_succeeds(self):
        """Test argument parsing with output file succeeds."""
        # Arrange
        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            "/path/to/map",
            "--output",
            "/output/data.json",
        ]

        # Act
        with patch("sys.argv", test_args):
            args = app.parse_args()

        # Assert
        assert args.output == Path("/output/data.json")

    def test_parse_args_with_json_format_succeeds(self):
        """Test argument parsing with json format succeeds."""
        # Arrange
        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            "/path/to/map",
            "--format",
            "json",
        ]

        # Act
        with patch("sys.argv", test_args):
            args = app.parse_args()

        # Assert
        assert args.format == "json"

    def test_parse_args_with_summary_format_succeeds(self):
        """Test argument parsing with summary format succeeds."""
        # Arrange
        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            "/path/to/map",
            "--format",
            "summary",
        ]

        # Act
        with patch("sys.argv", test_args):
            args = app.parse_args()

        # Assert
        assert args.format == "summary"

    def test_parse_args_with_verbose_flag_succeeds(self):
        """Test argument parsing with verbose flag succeeds."""
        # Arrange
        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            "/path/to/map",
            "--verbose",
        ]

        # Act
        with patch("sys.argv", test_args):
            args = app.parse_args()

        # Assert
        assert args.verbose is True


# ============================================================================
# Tests for PortalParseApp.create_engine
# ============================================================================


class TestPortalParseAppCreateEngine:
    """Tests for PortalParseApp.create_engine() method."""

    def test_create_engine_returns_bf1942_engine(self):
        """Test create_engine returns BF1942Engine for bf1942."""
        # Arrange
        app = PortalParseApp()
        app.args = SimpleNamespace(game="bf1942")  # type: ignore[assignment]

        # Act
        engine = app.create_engine()

        # Assert
        assert engine.get_game_name() == "BF1942"

    def test_create_engine_returns_bfvietnam_engine(self):
        """Test create_engine returns BFVietnamEngine for bfvietnam."""
        # Arrange
        app = PortalParseApp()
        app.args = SimpleNamespace(game="bfvietnam")  # type: ignore[assignment]

        # Act
        engine = app.create_engine()

        # Assert
        assert engine.get_game_name() == "BFVietnam"

    def test_create_engine_returns_bf2_engine(self):
        """Test create_engine returns BF2Engine for bf2."""
        # Arrange
        app = PortalParseApp()
        app.args = SimpleNamespace(game="bf2")  # type: ignore[assignment]

        # Act
        engine = app.create_engine()

        # Assert
        assert engine.get_game_name() == "BF2"

    def test_create_engine_returns_bf2142_engine(self):
        """Test create_engine returns BF2142Engine for bf2142."""
        # Arrange
        app = PortalParseApp()
        app.args = SimpleNamespace(game="bf2142")  # type: ignore[assignment]

        # Act
        engine = app.create_engine()

        # Assert
        assert engine.get_game_name() == "BF2142"

    def test_create_engine_raises_error_for_unknown_game(self):
        """Test create_engine raises ValueError for unknown game."""
        # Arrange
        app = PortalParseApp()
        app.args = SimpleNamespace(game="unknown_game")  # type: ignore[assignment]

        # Act & Assert
        with pytest.raises(ValueError, match="Unknown game: unknown_game"):
            app.create_engine()


# ============================================================================
# Tests for PortalParseApp.format_map_data_summary
# ============================================================================


class TestPortalParseAppFormatMapDataSummary:
    """Tests for PortalParseApp.format_map_data_summary() method."""

    def test_format_map_data_summary_with_full_data_succeeds(self, mock_map_data):
        """Test formatting summary with complete map data succeeds."""
        # Arrange
        app = PortalParseApp()

        # Act
        summary = app.format_map_data_summary(mock_map_data)

        # Assert
        assert "Map: TestMap" in summary
        assert "Bounds:" in summary
        assert "Min: (-100.0, 0.0, -100.0)" in summary
        assert "Max: (100.0, 50.0, 100.0)" in summary
        assert "Size: 200.0m x 200.0m" in summary
        assert "Spawn Points:" in summary
        assert "Team 1: 1 spawns" in summary
        assert "Team 2: 1 spawns" in summary
        assert "Headquarters:" in summary
        assert "Team 1: 1 HQ(s)" in summary
        assert "Team 2: 1 HQ(s)" in summary
        assert "Capture Points: 1" in summary
        assert "CapturePoint_1" in summary
        assert "Game Objects: 1" in summary
        assert "Building: 1" in summary

    def test_format_map_data_summary_with_minimal_data_succeeds(self, mock_map_data_minimal):
        """Test formatting summary with minimal map data succeeds."""
        # Arrange
        app = PortalParseApp()

        # Act
        summary = app.format_map_data_summary(mock_map_data_minimal)

        # Assert
        assert "Map: MinimalMap" in summary
        assert "Team 1: 0 spawns" in summary
        assert "Team 2: 0 spawns" in summary
        assert "Team 1: 0 HQ(s)" in summary
        assert "Team 2: 0 HQ(s)" in summary

    def test_format_map_data_summary_without_bounds_succeeds(self, mock_map_data):
        """Test formatting summary without bounds succeeds."""
        # Arrange
        app = PortalParseApp()
        mock_map_data.bounds = None

        # Act
        summary = app.format_map_data_summary(mock_map_data)

        # Assert
        assert "Map: TestMap" in summary
        assert "Bounds:" not in summary

    def test_format_map_data_summary_without_capture_points_succeeds(self, mock_map_data):
        """Test formatting summary without capture points succeeds."""
        # Arrange
        app = PortalParseApp()
        mock_map_data.capture_points = []

        # Act
        summary = app.format_map_data_summary(mock_map_data)

        # Assert
        assert "Map: TestMap" in summary
        assert "Capture Points:" not in summary

    def test_format_map_data_summary_without_game_objects_succeeds(self, mock_map_data):
        """Test formatting summary without game objects succeeds."""
        # Arrange
        app = PortalParseApp()
        mock_map_data.game_objects = []

        # Act
        summary = app.format_map_data_summary(mock_map_data)

        # Assert
        assert "Map: TestMap" in summary
        assert "Game Objects:" not in summary

    def test_format_map_data_summary_with_multiple_asset_types_shows_top_ten(self):
        """Test formatting summary with many asset types shows top 10."""
        # Arrange
        app = PortalParseApp()
        map_data = SimpleNamespace(
            name="TestMap",
            bounds=None,
            spawn_points=[],
            hqs=[],
            capture_points=[],
            game_objects=[
                SimpleNamespace(
                    asset_type=f"Asset_{i % 15}",
                    transform=SimpleNamespace(position=Vector3(0, 0, 0)),
                )
                for i in range(100)
            ],
        )

        # Act
        summary = app.format_map_data_summary(map_data)

        # Assert
        assert "Game Objects: 100" in summary
        lines = summary.split("\n")
        asset_lines = [line for line in lines if line.strip().startswith("- Asset_")]
        assert len(asset_lines) == 10


# ============================================================================
# Tests for PortalParseApp.format_map_data_json
# ============================================================================


class TestPortalParseAppFormatMapDataJson:
    """Tests for PortalParseApp.format_map_data_json() method."""

    def test_format_map_data_json_with_full_data_succeeds(self, mock_map_data):
        """Test formatting JSON with complete map data succeeds."""
        # Arrange
        app = PortalParseApp()

        # Act
        json_str = app.format_map_data_json(mock_map_data)

        # Assert
        data = json.loads(json_str)
        assert data["name"] == "TestMap"
        assert data["bounds"]["min"]["x"] == -100.0
        assert data["bounds"]["max"]["x"] == 100.0
        assert len(data["spawn_points"]) == 2
        assert len(data["hqs"]) == 2
        assert len(data["capture_points"]) == 1
        assert len(data["game_objects"]) == 1

    def test_format_map_data_json_with_minimal_data_succeeds(self, mock_map_data_minimal):
        """Test formatting JSON with minimal map data succeeds."""
        # Arrange
        app = PortalParseApp()

        # Act
        json_str = app.format_map_data_json(mock_map_data_minimal)

        # Assert
        data = json.loads(json_str)
        assert data["name"] == "MinimalMap"
        assert data["bounds"] is None
        assert data["spawn_points"] == []
        assert data["hqs"] == []
        assert data["capture_points"] == []
        assert data["game_objects"] == []

    def test_format_map_data_json_includes_spawn_transform_data(self, mock_map_data):
        """Test JSON includes spawn point transform data."""
        # Arrange
        app = PortalParseApp()

        # Act
        json_str = app.format_map_data_json(mock_map_data)

        # Assert
        data = json.loads(json_str)
        spawn = data["spawn_points"][0]
        assert spawn["name"] == "Spawn_1_1"
        assert spawn["team"] == 1
        assert spawn["position"]["x"] == 10.0
        assert spawn["rotation"]["yaw"] == 90.0

    def test_format_map_data_json_includes_hq_data(self, mock_map_data):
        """Test JSON includes HQ data."""
        # Arrange
        app = PortalParseApp()

        # Act
        json_str = app.format_map_data_json(mock_map_data)

        # Assert
        data = json.loads(json_str)
        hq = data["hqs"][0]
        assert hq["name"] == "HQ_Team1"
        assert hq["team"] == 1
        assert hq["position"]["x"] == 20.0

    def test_format_map_data_json_includes_capture_point_data(self, mock_map_data):
        """Test JSON includes capture point data."""
        # Arrange
        app = PortalParseApp()

        # Act
        json_str = app.format_map_data_json(mock_map_data)

        # Assert
        data = json.loads(json_str)
        cp = data["capture_points"][0]
        assert cp["name"] == "CapturePoint_1"
        assert cp["position"]["x"] == 0.0

    def test_format_map_data_json_includes_game_object_data(self, mock_map_data):
        """Test JSON includes game object data."""
        # Arrange
        app = PortalParseApp()

        # Act
        json_str = app.format_map_data_json(mock_map_data)

        # Assert
        data = json.loads(json_str)
        obj = data["game_objects"][0]
        assert obj["name"] == "Building_01"
        assert obj["asset_type"] == "Building"
        assert obj["team"] == 0
        assert obj["position"]["x"] == 5.0

    def test_format_map_data_json_handles_none_team_in_game_object(self):
        """Test JSON handles None team in game object."""
        # Arrange
        app = PortalParseApp()
        map_data = SimpleNamespace(
            name="TestMap",
            bounds=None,
            spawn_points=[],
            hqs=[],
            capture_points=[],
            game_objects=[
                SimpleNamespace(
                    name="Building_01",
                    asset_type="Building",
                    team=None,
                    transform=SimpleNamespace(
                        position=Vector3(x=5.0, y=0.0, z=5.0),
                        rotation=SimpleNamespace(pitch=0.0, yaw=0.0, roll=0.0),
                    ),
                )
            ],
        )

        # Act
        json_str = app.format_map_data_json(map_data)

        # Assert
        data = json.loads(json_str)
        assert data["game_objects"][0]["team"] == 0


# ============================================================================
# Tests for PortalParseApp.run
# ============================================================================


class TestPortalParseAppRun:
    """Tests for PortalParseApp.run() method."""

    def test_run_returns_success_with_valid_map(self, tmp_path, mock_map_data, capsys):
        """Test run returns success code with valid map."""
        # Arrange
        map_path = tmp_path / "TestMap"
        map_path.mkdir()
        (map_path / "init.con").write_text("rem Test")

        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            str(map_path),
        ]

        mock_engine = Mock(spec=["parse_map"])
        mock_engine.parse_map.return_value = mock_map_data

        # Act
        with (
            patch("sys.argv", test_args),
            patch.object(app, "create_engine", return_value=mock_engine),
        ):
            result = app.run()

        # Assert
        assert result == 0
        captured = capsys.readouterr()
        assert "Portal Map Parser" in captured.out

    def test_run_returns_error_when_map_path_not_found(self, tmp_path, capsys):
        """Test run returns error when map path doesn't exist."""
        # Arrange
        nonexistent_path = tmp_path / "NonExistent"
        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            str(nonexistent_path),
        ]

        # Act
        with patch("sys.argv", test_args):
            result = app.run()

        # Assert
        captured = capsys.readouterr()
        assert result == 1
        assert "Error: Map path not found" in captured.out

    def test_run_handles_parse_error_gracefully(self, tmp_path, capsys):
        """Test run handles ParseError gracefully."""
        # Arrange
        map_path = tmp_path / "TestMap"
        map_path.mkdir()

        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            str(map_path),
        ]

        mock_engine = Mock(spec=["parse_map"])
        mock_engine.parse_map.side_effect = ParseError("Test parse error")

        # Act
        with (
            patch("sys.argv", test_args),
            patch.object(app, "create_engine", return_value=mock_engine),
        ):
            result = app.run()

        # Assert
        captured = capsys.readouterr()
        assert result == 1
        assert "Parse error: Test parse error" in captured.out

    def test_run_handles_bfportal_error_gracefully(self, tmp_path, capsys):
        """Test run handles BFPortalError gracefully."""
        # Arrange
        map_path = tmp_path / "TestMap"
        map_path.mkdir()

        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            str(map_path),
        ]

        mock_engine = Mock(spec=["parse_map"])
        mock_engine.parse_map.side_effect = BFPortalError("Test BFPortal error")

        # Act
        with (
            patch("sys.argv", test_args),
            patch.object(app, "create_engine", return_value=mock_engine),
        ):
            result = app.run()

        # Assert
        captured = capsys.readouterr()
        assert result == 1
        assert "Error: Test BFPortal error" in captured.out

    def test_run_handles_unexpected_error_gracefully(self, tmp_path, capsys):
        """Test run handles unexpected Exception gracefully."""
        # Arrange
        map_path = tmp_path / "TestMap"
        map_path.mkdir()

        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            str(map_path),
        ]

        mock_engine = Mock(spec=["parse_map"])
        mock_engine.parse_map.side_effect = RuntimeError("Unexpected error")

        # Act
        with (
            patch("sys.argv", test_args),
            patch.object(app, "create_engine", return_value=mock_engine),
        ):
            result = app.run()

        # Assert
        captured = capsys.readouterr()
        assert result == 1
        assert "Unexpected error: Unexpected error" in captured.out

    def test_run_outputs_json_format_when_specified(self, tmp_path, mock_map_data, capsys):
        """Test run outputs JSON format when specified."""
        # Arrange
        map_path = tmp_path / "TestMap"
        map_path.mkdir()

        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            str(map_path),
            "--format",
            "json",
        ]

        mock_engine = Mock(spec=["parse_map"])
        mock_engine.parse_map.return_value = mock_map_data

        # Act
        with (
            patch("sys.argv", test_args),
            patch.object(app, "create_engine", return_value=mock_engine),
        ):
            result = app.run()

        # Assert
        captured = capsys.readouterr()
        assert result == 0
        assert '"name": "TestMap"' in captured.out

    def test_run_writes_output_to_file_when_specified(self, tmp_path, mock_map_data, capsys):
        """Test run writes output to file when specified."""
        # Arrange
        map_path = tmp_path / "TestMap"
        map_path.mkdir()
        output_file = tmp_path / "output" / "data.json"

        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            str(map_path),
            "--output",
            str(output_file),
        ]

        mock_engine = Mock(spec=["parse_map"])
        mock_engine.parse_map.return_value = mock_map_data

        # Act
        with (
            patch("sys.argv", test_args),
            patch.object(app, "create_engine", return_value=mock_engine),
        ):
            result = app.run()

        # Assert
        captured = capsys.readouterr()
        assert result == 0
        assert output_file.exists()
        assert "Output written to:" in captured.out
        content = output_file.read_text()
        assert "TestMap" in content

    def test_run_shows_verbose_output_when_flag_set(self, tmp_path, mock_map_data, capsys):
        """Test run shows verbose output when flag set."""
        # Arrange
        map_path = tmp_path / "TestMap"
        map_path.mkdir()

        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            str(map_path),
            "--verbose",
        ]

        mock_engine = Mock(spec=["parse_map"])
        mock_engine.parse_map.return_value = mock_map_data

        # Act
        with (
            patch("sys.argv", test_args),
            patch.object(app, "create_engine", return_value=mock_engine),
        ):
            result = app.run()

        # Assert
        captured = capsys.readouterr()
        assert result == 0
        assert "Parsing BF1942 map" in captured.out
        assert "Successfully parsed map" in captured.out

    def test_run_hides_banner_when_verbose(self, tmp_path, mock_map_data, capsys):
        """Test run hides banner when verbose enabled."""
        # Arrange
        map_path = tmp_path / "TestMap"
        map_path.mkdir()

        app = PortalParseApp()
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            str(map_path),
            "--verbose",
        ]

        mock_engine = Mock(spec=["parse_map"])
        mock_engine.parse_map.return_value = mock_map_data

        # Act
        with (
            patch("sys.argv", test_args),
            patch.object(app, "create_engine", return_value=mock_engine),
        ):
            result = app.run()

        # Assert
        captured = capsys.readouterr()
        assert result == 0
        # Banner has emoji and "Portal Map Parser"
        lines = captured.out.split("\n")
        banner_lines = [line for line in lines if "Portal Map Parser" in line]
        assert len(banner_lines) == 0


# ============================================================================
# Tests for main() function
# ============================================================================


class TestMainFunction:
    """Tests for main() CLI entry point."""

    def test_main_calls_app_run_and_exits(self):
        """Test main function calls app.run() and exits."""
        # Arrange
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            "/path/to/map",
        ]

        # Act & Assert
        with (
            patch("sys.argv", test_args),
            patch.object(PortalParseApp, "run", return_value=0) as mock_run,
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 0
        mock_run.assert_called_once()

    def test_main_exits_with_error_code_on_failure(self):
        """Test main function exits with error code on failure."""
        # Arrange
        test_args = [
            "portal_parse.py",
            "--game",
            "bf1942",
            "--map-path",
            "/path/to/map",
        ]

        # Act & Assert
        with (
            patch("sys.argv", test_args),
            patch.object(PortalParseApp, "run", return_value=1) as mock_run,
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 1
        mock_run.assert_called_once()
