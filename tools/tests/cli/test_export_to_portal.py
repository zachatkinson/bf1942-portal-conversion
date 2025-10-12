#!/usr/bin/env python3
"""Tests for export_to_portal.py CLI script."""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from export_to_portal import create_experience_file, export_tscn_to_spatial, main


class TestExportTscnToSpatial:
    """Tests for export_tscn_to_spatial() function."""

    def test_exports_tscn_successfully(self, tmp_path: Path):
        """Test successful .tscn to .spatial.json export."""
        # Arrange
        tscn_path = tmp_path / "TestMap.tscn"
        tscn_path.write_text("[gd_scene]\n")
        asset_dir = tmp_path / "FbExportData"
        asset_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        spatial_path = output_dir / "TestMap.spatial.json"
        spatial_path.write_text(json.dumps({"Portal_Dynamic": [], "Static": []}))
        mock_result = MagicMock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stderr = ""

        # Act
        with patch("export_to_portal.subprocess.run", return_value=mock_result):
            result = export_tscn_to_spatial(tscn_path, asset_dir, output_dir)

        # Assert
        assert result == spatial_path

    def test_raises_error_when_export_script_missing(self, tmp_path: Path):
        """Test error raised when export script doesn't exist."""
        # Arrange
        tscn_path = tmp_path / "TestMap.tscn"
        tscn_path.write_text("[gd_scene]\n")
        asset_dir = tmp_path / "FbExportData"
        output_dir = tmp_path / "output"

        # Act & Assert
        with (
            patch("export_to_portal.Path.exists", return_value=False),
            pytest.raises(RuntimeError, match="Export script not found"),
        ):
            export_tscn_to_spatial(tscn_path, asset_dir, output_dir)

    def test_raises_error_when_subprocess_fails(self, tmp_path: Path):
        """Test error raised when subprocess returns non-zero."""
        # Arrange
        tscn_path = tmp_path / "TestMap.tscn"
        tscn_path.write_text("[gd_scene]\n")
        asset_dir = tmp_path / "FbExportData"
        asset_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        mock_result = MagicMock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 1
        mock_result.stderr = "Export failed"

        # Act & Assert
        with (
            patch("export_to_portal.subprocess.run", return_value=mock_result),
            pytest.raises(RuntimeError, match="Export failed"),
        ):
            export_tscn_to_spatial(tscn_path, asset_dir, output_dir)

    def test_raises_error_when_output_file_not_created(self, tmp_path: Path):
        """Test error raised when expected output file doesn't exist."""
        # Arrange
        tscn_path = tmp_path / "TestMap.tscn"
        tscn_path.write_text("[gd_scene]\n")
        asset_dir = tmp_path / "FbExportData"
        asset_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        mock_result = MagicMock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0

        # Act & Assert
        with (
            patch("export_to_portal.subprocess.run", return_value=mock_result),
            pytest.raises(RuntimeError, match="Expected output file not created"),
        ):
            export_tscn_to_spatial(tscn_path, asset_dir, output_dir)


class TestCreateExperienceFileFromExportToPortal:
    """Tests for create_experience_file() in export_to_portal."""

    def test_creates_experience_from_spatial_file(self, tmp_path: Path):
        """Test creating experience file from spatial.json."""
        # Arrange
        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        spatial_path = tmp_path / "TestMap.spatial.json"
        spatial_path.write_text(spatial_data)

        # Act
        with patch("export_to_portal.Path.mkdir"):
            output_path = create_experience_file(
                map_name="TestMap",
                spatial_path=spatial_path,
                base_map="MP_Tungsten",
                max_players_per_team=32,
                game_mode="Conquest",
            )

        # Assert
        assert output_path.exists()
        experience_data = json.loads(output_path.read_text())
        assert experience_data["name"] == "TestMap - BF1942 Classic"
        assert experience_data["gameMode"] == "Conquest"

    def test_uses_custom_description(self, tmp_path: Path):
        """Test custom description is used when provided."""
        # Arrange
        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        spatial_path = tmp_path / "TestMap.spatial.json"
        spatial_path.write_text(spatial_data)
        custom_desc = "Custom description"

        # Act
        with patch("export_to_portal.Path.mkdir"):
            output_path = create_experience_file(
                map_name="TestMap",
                spatial_path=spatial_path,
                base_map="MP_Tungsten",
                max_players_per_team=32,
                game_mode="Conquest",
                description=custom_desc,
            )

        # Assert
        experience_data = json.loads(output_path.read_text())
        assert experience_data["description"] == custom_desc


class TestMainFunctionFromExportToPortal:
    """Tests for main() CLI entry point in export_to_portal."""

    def test_returns_error_when_tscn_file_missing(self):
        """Test main returns error code when .tscn file doesn't exist."""
        # Arrange
        test_args = ["export_to_portal.py", "NonExistentMap"]

        # Act
        with (
            patch("sys.argv", test_args),
            patch("export_to_portal.Path.exists", return_value=False),
        ):
            result = main()

        # Assert
        assert result == 1

    def test_lists_available_maps_when_tscn_file_missing(self, tmp_path: Path):
        """Test main lists available maps when .tscn file doesn't exist and levels dir exists."""
        # Arrange
        levels_dir = tmp_path / "GodotProject" / "levels"
        levels_dir.mkdir(parents=True)
        (levels_dir / "Map1.tscn").write_text("[gd_scene]\n")
        (levels_dir / "Map2.tscn").write_text("[gd_scene]\n")
        test_args = ["export_to_portal.py", "NonExistentMap"]

        # Act
        with (
            patch("sys.argv", test_args),
            patch("export_to_portal.Path.cwd", return_value=tmp_path),
        ):
            result = main()

        # Assert
        assert result == 1

    def test_returns_error_when_asset_dir_missing(self, tmp_path: Path):
        """Test main returns error code when FbExportData doesn't exist."""
        # Arrange
        tscn_path = tmp_path / "GodotProject" / "levels" / "TestMap.tscn"
        tscn_path.parent.mkdir(parents=True)
        tscn_path.write_text("[gd_scene]\n")
        test_args = ["export_to_portal.py", "TestMap"]

        # Act
        with (
            patch("sys.argv", test_args),
            patch("export_to_portal.Path.cwd", return_value=tmp_path),
        ):
            result = main()

        # Assert
        assert result == 1

    def test_returns_success_when_export_completes(self, tmp_path: Path):
        """Test main returns success code when export completes."""
        # Arrange
        tscn_path = tmp_path / "GodotProject" / "levels" / "TestMap.tscn"
        tscn_path.parent.mkdir(parents=True)
        tscn_path.write_text("[gd_scene]\n")
        asset_dir = tmp_path / "FbExportData"
        asset_dir.mkdir()
        output_dir = asset_dir / "levels"
        output_dir.mkdir()
        spatial_path = output_dir / "TestMap.spatial.json"
        spatial_path.write_text(json.dumps({"Portal_Dynamic": [], "Static": []}))

        test_args = ["export_to_portal.py", "TestMap"]

        # Act
        with (
            patch("sys.argv", test_args),
            patch("export_to_portal.Path.cwd", return_value=tmp_path),
            patch("export_to_portal.export_tscn_to_spatial", return_value=spatial_path),
            patch("export_to_portal.create_experience_file") as mock_create,
        ):
            mock_create.return_value = tmp_path / "TestMap_Experience.json"
            result = main()

        # Assert
        assert result == 0

    def test_returns_error_when_exception_occurs_during_export(self, tmp_path: Path):
        """Test main returns error code when exception is raised during export."""
        # Arrange
        tscn_path = tmp_path / "GodotProject" / "levels" / "TestMap.tscn"
        tscn_path.parent.mkdir(parents=True)
        tscn_path.write_text("[gd_scene]\n")
        asset_dir = tmp_path / "FbExportData"
        asset_dir.mkdir()
        output_dir = asset_dir / "levels"
        output_dir.mkdir()
        test_args = ["export_to_portal.py", "TestMap"]

        # Act
        with (
            patch("sys.argv", test_args),
            patch("export_to_portal.Path.cwd", return_value=tmp_path),
            patch("export_to_portal.export_tscn_to_spatial", side_effect=RuntimeError("Test error")),
        ):
            result = main()

        # Assert
        assert result == 1
