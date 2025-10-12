#!/usr/bin/env python3
"""Tests for PortalRebaseApp CLI."""

from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from bfportal.core.exceptions import BFPortalError
from bfportal.core.interfaces import Vector3
from portal_rebase import PORTAL_BASE_CENTERS, PortalRebaseApp


class TestPortalBaseCenters:
    """Tests for PORTAL_BASE_CENTERS constant."""

    def test_portal_base_centers_contains_all_terrains(self):
        """Test PORTAL_BASE_CENTERS includes all known Portal terrains."""
        # Arrange
        expected_terrains = [
            "MP_Tungsten",
            "MP_Outskirts",
            "MP_Aftermath",
            "MP_Battery",
            "MP_Everglades",
            "MP_Breakaway",
            "MP_Nexus",
        ]

        # Act
        actual_terrains = list(PORTAL_BASE_CENTERS.keys())

        # Assert
        assert set(expected_terrains) == set(actual_terrains)

    def test_portal_base_centers_all_have_zero_origin(self):
        """Test all Portal base terrains use (0, 0, 0) center."""
        # Arrange
        expected_center = Vector3(0.0, 0.0, 0.0)

        # Act & Assert
        for terrain, center in PORTAL_BASE_CENTERS.items():
            assert center == expected_center, f"{terrain} should have zero center"


class TestPortalRebaseAppInit:
    """Tests for PortalRebaseApp.__init__()."""

    def test_initializes_successfully(self):
        """Test PortalRebaseApp initializes with no arguments."""
        # Arrange & Act
        app = PortalRebaseApp()

        # Assert
        assert isinstance(app, PortalRebaseApp)


class TestParseArgs:
    """Tests for PortalRebaseApp.parse_args()."""

    def test_parse_args_with_minimal_required_arguments(self):
        """Test parse_args with only required arguments."""
        # Arrange
        app = PortalRebaseApp()
        test_args = [
            "--input",
            "GodotProject/levels/Kursk.tscn",
            "--output",
            "GodotProject/levels/Kursk_outskirts.tscn",
            "--new-base",
            "MP_Outskirts",
        ]

        with patch("sys.argv", ["portal_rebase.py"] + test_args):
            # Act
            args = app.parse_args()

        # Assert
        assert args.input == Path("GodotProject/levels/Kursk.tscn")
        assert args.output == Path("GodotProject/levels/Kursk_outskirts.tscn")
        assert args.new_base == "MP_Outskirts"
        assert args.heightmap is None
        assert args.terrain_size == 2048
        assert args.min_height == 0.0
        assert args.max_height == 200.0

    def test_parse_args_with_custom_heightmap_options(self):
        """Test parse_args with custom heightmap and height range."""
        # Arrange
        app = PortalRebaseApp()
        test_args = [
            "--input",
            "input.tscn",
            "--output",
            "output.tscn",
            "--new-base",
            "MP_Tungsten",
            "--heightmap",
            "terrain.png",
            "--terrain-size",
            "4096",
            "--min-height",
            "50",
            "--max-height",
            "150",
        ]

        with patch("sys.argv", ["portal_rebase.py"] + test_args):
            # Act
            args = app.parse_args()

        # Assert
        assert args.heightmap == Path("terrain.png")
        assert args.terrain_size == 4096
        assert args.min_height == 50.0
        assert args.max_height == 150.0

    def test_parse_args_with_custom_map_center(self):
        """Test parse_args with custom map center coordinates."""
        # Arrange
        app = PortalRebaseApp()
        test_args = [
            "--input",
            "input.tscn",
            "--output",
            "output.tscn",
            "--new-base",
            "MP_Battery",
            "--map-center-x",
            "100.5",
            "--map-center-z",
            "-200.75",
        ]

        with patch("sys.argv", ["portal_rebase.py"] + test_args):
            # Act
            args = app.parse_args()

        # Assert
        assert args.map_center_x == 100.5
        assert args.map_center_z == -200.75

    def test_parse_args_rejects_invalid_base_terrain(self):
        """Test parse_args rejects invalid base terrain choice."""
        # Arrange
        app = PortalRebaseApp()
        test_args = [
            "--input",
            "input.tscn",
            "--output",
            "output.tscn",
            "--new-base",
            "MP_InvalidTerrain",
        ]

        with (
            patch("sys.argv", ["portal_rebase.py"] + test_args),
            pytest.raises(SystemExit),
        ):
            # Act & Assert
            app.parse_args()


class TestCreateTerrainProvider:
    """Tests for PortalRebaseApp.create_terrain_provider()."""

    def test_create_terrain_provider_with_custom_heightmap(self, tmp_path: Path):
        """Test create_terrain_provider with custom heightmap path."""
        # Arrange
        app = PortalRebaseApp()
        heightmap = tmp_path / "test_heightmap.png"
        heightmap.write_text("fake png data")
        app.args = Namespace(
            heightmap=heightmap,
            terrain_size=2048,
            min_height=10.0,
            max_height=100.0,
            new_base="MP_Tungsten",
        )

        with patch("portal_rebase.CustomHeightmapProvider", spec=True) as mock_provider:
            # Act
            app.create_terrain_provider()

        # Assert
        mock_provider.assert_called_once_with(
            heightmap_path=heightmap,
            terrain_size=(2048, 2048),
            height_range=(10.0, 100.0),
        )

    def test_create_terrain_provider_raises_when_heightmap_missing(self):
        """Test create_terrain_provider raises FileNotFoundError for missing heightmap."""
        # Arrange
        app = PortalRebaseApp()
        app.args = Namespace(
            heightmap=Path("/nonexistent/heightmap.png"),
            terrain_size=2048,
            min_height=0.0,
            max_height=200.0,
            new_base="MP_Tungsten",
        )

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Heightmap not found"):
            app.create_terrain_provider()

    def test_create_terrain_provider_tungsten_builtin(self):
        """Test create_terrain_provider creates TungstenTerrainProvider."""
        # Arrange
        app = PortalRebaseApp()
        app.args = Namespace(heightmap=None, new_base="MP_Tungsten")

        with patch("portal_rebase.TungstenTerrainProvider", spec=True) as mock_provider:
            # Act
            app.create_terrain_provider()

        # Assert
        mock_provider.assert_called_once()

    def test_create_terrain_provider_outskirts_builtin(self):
        """Test create_terrain_provider creates OutskirtsTerrainProvider."""
        # Arrange
        app = PortalRebaseApp()
        app.args = Namespace(heightmap=None, new_base="MP_Outskirts")

        with patch("portal_rebase.OutskirtsTerrainProvider", spec=True) as mock_provider:
            # Act
            app.create_terrain_provider()

        # Assert
        mock_provider.assert_called_once()

    def test_create_terrain_provider_fallback_for_unsupported_terrain(self):
        """Test create_terrain_provider falls back to TungstenTerrainProvider for unsupported terrains."""
        # Arrange
        app = PortalRebaseApp()
        app.args = Namespace(heightmap=None, new_base="MP_Nexus")

        with patch("portal_rebase.TungstenTerrainProvider", spec=True) as mock_provider:
            # Act
            app.create_terrain_provider()

        # Assert
        mock_provider.assert_called_once()


class TestRun:
    """Tests for PortalRebaseApp.run()."""

    def test_run_returns_error_when_input_file_missing(self, tmp_path: Path):
        """Test run returns error code 1 when input file does not exist."""
        # Arrange
        app = PortalRebaseApp()
        test_args = [
            "--input",
            str(tmp_path / "nonexistent.tscn"),
            "--output",
            str(tmp_path / "output.tscn"),
            "--new-base",
            "MP_Tungsten",
        ]

        with patch("sys.argv", ["portal_rebase.py"] + test_args):
            # Act
            result = app.run()

        # Assert
        assert result == 1

    def test_run_succeeds_with_valid_inputs_and_default_center(self, tmp_path: Path, capsys):
        """Test run succeeds with valid inputs using default map center."""
        # Arrange
        app = PortalRebaseApp()
        input_file = tmp_path / "input.tscn"
        output_file = tmp_path / "output.tscn"
        input_file.write_text("[gd_scene]\n")

        test_args = [
            "--input",
            str(input_file),
            "--output",
            str(output_file),
            "--new-base",
            "MP_Outskirts",
        ]

        mock_stats = {
            "total_objects": 42,
            "height_adjusted": 40,
            "out_of_bounds": 2,
            "offset_applied": {"x": 10.0, "y": 0.0, "z": -5.0},
        }

        with (
            patch("sys.argv", ["portal_rebase.py"] + test_args),
            patch.object(app, "create_terrain_provider", return_value=MagicMock()),
            patch("portal_rebase.CoordinateOffset", spec=True),
            patch("portal_rebase.MapRebaser", spec=True) as mock_rebaser_class,
        ):
            mock_rebaser = MagicMock()
            mock_rebaser.rebase_map.return_value = mock_stats
            mock_rebaser_class.return_value = mock_rebaser

            # Act
            result = app.run()

        # Assert
        assert result == 0
        mock_rebaser.rebase_map.assert_called_once()
        captured = capsys.readouterr()
        assert "✅ Rebasing Complete!" in captured.out
        assert "Total objects: 42" in captured.out

    def test_run_succeeds_with_custom_map_center(self, tmp_path: Path):
        """Test run succeeds with custom map center coordinates."""
        # Arrange
        app = PortalRebaseApp()
        input_file = tmp_path / "input.tscn"
        output_file = tmp_path / "output.tscn"
        input_file.write_text("[gd_scene]\n")

        test_args = [
            "--input",
            str(input_file),
            "--output",
            str(output_file),
            "--new-base",
            "MP_Tungsten",
            "--map-center-x",
            "500",
            "--map-center-z",
            "-300",
        ]

        mock_stats = {
            "total_objects": 10,
            "height_adjusted": 9,
            "out_of_bounds": 1,
            "offset_applied": {"x": 0.0, "y": 0.0, "z": 0.0},
        }

        with (
            patch("sys.argv", ["portal_rebase.py"] + test_args),
            patch.object(app, "create_terrain_provider", return_value=MagicMock()),
            patch("portal_rebase.CoordinateOffset", spec=True),
            patch("portal_rebase.MapRebaser", spec=True) as mock_rebaser_class,
        ):
            mock_rebaser = MagicMock()
            mock_rebaser.rebase_map.return_value = mock_stats
            mock_rebaser_class.return_value = mock_rebaser

            # Act
            result = app.run()

        # Assert
        assert result == 0
        call_args = mock_rebaser.rebase_map.call_args
        assert call_args.kwargs["new_map_center"] == Vector3(500.0, 0.0, -300.0)

    def test_run_handles_bfportal_error_gracefully(self, tmp_path: Path, capsys):
        """Test run handles BFPortalError and returns error code 1."""
        # Arrange
        app = PortalRebaseApp()
        input_file = tmp_path / "input.tscn"
        output_file = tmp_path / "output.tscn"
        input_file.write_text("[gd_scene]\n")

        test_args = [
            "--input",
            str(input_file),
            "--output",
            str(output_file),
            "--new-base",
            "MP_Battery",
        ]

        with (
            patch("sys.argv", ["portal_rebase.py"] + test_args),
            patch.object(app, "create_terrain_provider", return_value=MagicMock()),
            patch("portal_rebase.CoordinateOffset", spec=True),
            patch("portal_rebase.MapRebaser", spec=True) as mock_rebaser_class,
        ):
            mock_rebaser = MagicMock()
            mock_rebaser.rebase_map.side_effect = BFPortalError("Test error message")
            mock_rebaser_class.return_value = mock_rebaser

            # Act
            result = app.run()

        # Assert
        assert result == 1
        captured = capsys.readouterr()
        assert "❌ Error: Test error message" in captured.out

    def test_run_handles_unexpected_exception_gracefully(self, tmp_path: Path, capsys):
        """Test run handles unexpected exceptions and returns error code 1."""
        # Arrange
        app = PortalRebaseApp()
        input_file = tmp_path / "input.tscn"
        output_file = tmp_path / "output.tscn"
        input_file.write_text("[gd_scene]\n")

        test_args = [
            "--input",
            str(input_file),
            "--output",
            str(output_file),
            "--new-base",
            "MP_Everglades",
        ]

        with (
            patch("sys.argv", ["portal_rebase.py"] + test_args),
            patch.object(app, "create_terrain_provider", return_value=MagicMock()),
            patch("portal_rebase.CoordinateOffset", spec=True),
            patch("portal_rebase.MapRebaser", spec=True) as mock_rebaser_class,
        ):
            mock_rebaser = MagicMock()
            mock_rebaser.rebase_map.side_effect = RuntimeError("Unexpected error")
            mock_rebaser_class.return_value = mock_rebaser

            # Act
            result = app.run()

        # Assert
        assert result == 1
        captured = capsys.readouterr()
        assert "❌ Unexpected error: Unexpected error" in captured.out

    def test_run_creates_output_directory_if_missing(self, tmp_path: Path):
        """Test run creates output directory structure if it doesn't exist."""
        # Arrange
        app = PortalRebaseApp()
        input_file = tmp_path / "input.tscn"
        output_dir = tmp_path / "nested" / "output" / "dir"
        output_file = output_dir / "output.tscn"
        input_file.write_text("[gd_scene]\n")

        test_args = [
            "--input",
            str(input_file),
            "--output",
            str(output_file),
            "--new-base",
            "MP_Breakaway",
        ]

        mock_stats = {
            "total_objects": 5,
            "height_adjusted": 5,
            "out_of_bounds": 0,
            "offset_applied": {"x": 0.0, "y": 0.0, "z": 0.0},
        }

        with (
            patch("sys.argv", ["portal_rebase.py"] + test_args),
            patch.object(app, "create_terrain_provider", return_value=MagicMock()),
            patch("portal_rebase.CoordinateOffset", spec=True),
            patch("portal_rebase.MapRebaser", spec=True) as mock_rebaser_class,
        ):
            mock_rebaser = MagicMock()
            mock_rebaser.rebase_map.return_value = mock_stats
            mock_rebaser_class.return_value = mock_rebaser

            # Act
            result = app.run()

        # Assert
        assert result == 0
        assert output_dir.exists()
        assert output_dir.is_dir()


class TestMain:
    """Tests for main() entry point."""

    def test_main_calls_run_and_exits(self, tmp_path: Path):
        """Test main() creates app, calls run(), and exits with correct code."""
        # Arrange
        input_file = tmp_path / "input.tscn"
        input_file.write_text("[gd_scene]\n")

        test_args = [
            "portal_rebase.py",
            "--input",
            str(input_file),
            "--output",
            str(tmp_path / "output.tscn"),
            "--new-base",
            "MP_Tungsten",
        ]

        with (
            patch("sys.argv", test_args),
            patch("portal_rebase.PortalRebaseApp", spec=True) as mock_app_class,
        ):
            mock_app = MagicMock()
            mock_app.run.return_value = 42
            mock_app_class.return_value = mock_app

            # Act & Assert
            with pytest.raises(SystemExit) as exc_info:
                from portal_rebase import main

                main()

            assert exc_info.value.code == 42
            mock_app.run.assert_called_once()
