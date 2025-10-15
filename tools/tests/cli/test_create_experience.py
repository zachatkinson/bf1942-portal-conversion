#!/usr/bin/env python3
"""Tests for create_experience.py CLI script."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from create_experience import create_experience_file, main


class TestCreateExperienceFile:
    """Tests for create_experience_file() function."""

    def test_creates_experience_with_valid_spatial_file(self, tmp_path: Path):
        """Test creating experience file from valid spatial.json."""
        # Arrange
        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        spatial_path = tmp_path / "test.spatial.json"
        spatial_path.write_text(spatial_data)

        # Act
        with patch("create_experience.Path.mkdir"):
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
        assert experience_data["mutators"]["MaxPlayerCount_PerTeam"] == 32
        assert len(experience_data["mapRotation"]) == 1

    def test_raises_error_when_spatial_file_missing(self, tmp_path: Path):
        """Test error raised when spatial file doesn't exist."""
        # Arrange
        spatial_path = tmp_path / "missing.spatial.json"

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Spatial file not found"):
            create_experience_file(
                map_name="TestMap",
                spatial_path=spatial_path,
                base_map="MP_Tungsten",
                max_players_per_team=32,
                game_mode="Conquest",
            )

    def test_uses_custom_description_when_provided(self, tmp_path: Path):
        """Test custom description is used when provided."""
        # Arrange
        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        spatial_path = tmp_path / "test.spatial.json"
        spatial_path.write_text(spatial_data)
        custom_desc = "Custom experience description"

        # Act
        with patch("create_experience.Path.mkdir"):
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

    def test_creates_default_description_when_none_provided(self, tmp_path: Path):
        """Test default description is generated when none provided."""
        # Arrange
        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        spatial_path = tmp_path / "test.spatial.json"
        spatial_path.write_text(spatial_data)

        # Act
        with patch("create_experience.Path.mkdir"):
            output_path = create_experience_file(
                map_name="Kursk",
                spatial_path=spatial_path,
                base_map="MP_Tungsten",
                max_players_per_team=32,
                game_mode="Conquest",
            )

        # Assert
        experience_data = json.loads(output_path.read_text())
        assert "Kursk" in experience_data["description"]
        assert "Battlefield 1942" in experience_data["description"]

    def test_encodes_spatial_data_as_base64(self, tmp_path: Path):
        """Test spatial data is properly base64 encoded."""
        # Arrange
        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        spatial_path = tmp_path / "test.spatial.json"
        spatial_path.write_text(spatial_data)

        # Act
        with patch("create_experience.Path.mkdir"):
            output_path = create_experience_file(
                map_name="TestMap",
                spatial_path=spatial_path,
                base_map="MP_Tungsten",
                max_players_per_team=32,
                game_mode="Conquest",
            )

        # Assert
        experience_data = json.loads(output_path.read_text())
        spatial_attachment = experience_data["mapRotation"][0]["spatialAttachment"]
        assert "attachmentData" in spatial_attachment
        assert "original" in spatial_attachment["attachmentData"]
        # Base64 encoded data should be present
        assert len(spatial_attachment["attachmentData"]["original"]) > 0

    def test_sets_correct_map_rotation_id_pattern(self, tmp_path: Path):
        """Test map rotation ID follows MP_<MapName>-ModBuilderCustom0 pattern."""
        # Arrange
        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        spatial_path = tmp_path / "test.spatial.json"
        spatial_path.write_text(spatial_data)

        # Act
        with patch("create_experience.Path.mkdir"):
            output_path = create_experience_file(
                map_name="TestMap",
                spatial_path=spatial_path,
                base_map="MP_Outskirts",
                max_players_per_team=32,
                game_mode="Conquest",
            )

        # Assert
        experience_data = json.loads(output_path.read_text())
        rotation_id = experience_data["mapRotation"][0]["id"]
        assert rotation_id == "MP_Outskirts-ModBuilderCustom0"

    def test_sets_team_composition_correctly(self, tmp_path: Path):
        """Test team composition is set correctly for both teams."""
        # Arrange
        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        spatial_path = tmp_path / "test.spatial.json"
        spatial_path.write_text(spatial_data)

        # Act
        with patch("create_experience.Path.mkdir"):
            output_path = create_experience_file(
                map_name="TestMap",
                spatial_path=spatial_path,
                base_map="MP_Tungsten",
                max_players_per_team=64,
                game_mode="Conquest",
            )

        # Assert
        experience_data = json.loads(output_path.read_text())
        team_composition = experience_data["teamComposition"]
        assert len(team_composition) == 2
        assert team_composition[0][1]["humanCapacity"] == 64
        assert team_composition[1][1]["humanCapacity"] == 64

    def test_creates_experiences_directory_if_missing(self, tmp_path: Path):
        """Test experiences directory is created if it doesn't exist."""
        # Arrange
        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        spatial_path = tmp_path / "test.spatial.json"
        spatial_path.write_text(spatial_data)

        # Act
        with patch("create_experience.Path.mkdir") as mock_mkdir:
            create_experience_file(
                map_name="TestMap",
                spatial_path=spatial_path,
                base_map="MP_Tungsten",
                max_players_per_team=32,
                game_mode="Conquest",
            )

            # Assert
            mock_mkdir.assert_called_once_with(exist_ok=True)

    def test_supports_different_game_modes(self, tmp_path: Path):
        """Test experience creation with different game modes."""
        # Arrange
        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        spatial_path = tmp_path / "test.spatial.json"
        spatial_path.write_text(spatial_data)

        # Act
        with patch("create_experience.Path.mkdir"):
            output_path = create_experience_file(
                map_name="TestMap",
                spatial_path=spatial_path,
                base_map="MP_Tungsten",
                max_players_per_team=32,
                game_mode="Rush",
            )

        # Assert
        experience_data = json.loads(output_path.read_text())
        assert experience_data["gameMode"] == "Rush"


class TestMainFunction:
    """Tests for main() CLI entry point."""

    def test_returns_error_when_spatial_file_missing(self):
        """Test main returns error code when spatial file doesn't exist."""
        # Arrange
        test_args = ["create_experience.py", "NonExistentMap"]

        # Act
        with (
            patch("sys.argv", test_args),
            patch("create_experience.Path.exists", return_value=False),
        ):
            result = main()

        # Assert
        assert result == 1

    def test_returns_success_when_experience_created(self, tmp_path: Path):
        """Test main returns success code when experience is created successfully."""
        # Arrange
        test_args = ["create_experience.py", "TestMap"]
        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        spatial_path = tmp_path / "TestMap.spatial.json"
        spatial_path.write_text(spatial_data)

        # Act
        with (
            patch("sys.argv", test_args),
            patch("create_experience.get_spatial_json_path", return_value=spatial_path),
            patch("create_experience.create_experience_file") as mock_create,
        ):
            mock_create.return_value = tmp_path / "TestMap_Experience.json"
            result = main()

        # Assert
        assert result == 0

    def test_main_lists_available_spatial_files_when_file_missing_returns_error(
        self, tmp_path: Path, capsys
    ):
        """Test main lists available spatial files when requested file is missing."""
        # Arrange
        test_args = ["create_experience.py", "NonExistentMap"]
        levels_dir = tmp_path / "FbExportData" / "levels"
        levels_dir.mkdir(parents=True)
        (levels_dir / "Kursk.spatial.json").write_text("{}")
        (levels_dir / "ElAlamein.spatial.json").write_text("{}")

        # Mock spatial path to non-existent file, and mock get_project_root to return tmp_path
        nonexistent_spatial = tmp_path / "FbExportData" / "levels" / "NonExistentMap.spatial.json"

        # Act
        with (
            patch("sys.argv", test_args),
            patch("create_experience.get_spatial_json_path", return_value=nonexistent_spatial),
            patch("bfportal.generators.constants.paths.get_project_root", return_value=tmp_path),
        ):
            result = main()

        # Assert
        assert result == 1
        captured = capsys.readouterr()
        assert "Available spatial files:" in captured.err
        assert "Kursk" in captured.err
        assert "ElAlamein" in captured.err

    def test_main_shows_export_hint_when_no_spatial_files_exist_returns_error(
        self, tmp_path: Path, capsys
    ):
        """Test main shows export hint when levels directory has no spatial files."""
        # Arrange
        test_args = ["create_experience.py", "TestMap"]
        levels_dir = tmp_path / "FbExportData" / "levels"
        levels_dir.mkdir(parents=True)

        # Mock spatial path to non-existent file, and mock get_project_root to return tmp_path
        nonexistent_spatial = tmp_path / "FbExportData" / "levels" / "TestMap.spatial.json"

        # Act
        with (
            patch("sys.argv", test_args),
            patch("create_experience.get_spatial_json_path", return_value=nonexistent_spatial),
            patch("bfportal.generators.constants.paths.get_project_root", return_value=tmp_path),
        ):
            result = main()

        # Assert
        assert result == 1
        captured = capsys.readouterr()
        assert "(none found)" in captured.err
        assert "Did you export the map first?" in captured.err
        assert "bash tools/export_map.sh TestMap" in captured.err

    def test_main_handles_exception_during_creation_returns_error(self, tmp_path: Path, capsys):
        """Test main handles exceptions during experience creation with traceback."""
        # Arrange
        test_args = ["create_experience.py", "TestMap"]
        spatial_path = tmp_path / "TestMap.spatial.json"
        spatial_path.write_text("{}")

        # Act
        with (
            patch("sys.argv", test_args),
            patch("create_experience.get_spatial_json_path", return_value=spatial_path),
            patch(
                "create_experience.create_experience_file",
                side_effect=ValueError("Test exception"),
            ),
        ):
            result = main()

        # Assert
        assert result == 1
        captured = capsys.readouterr()
        assert "Error: Test exception" in captured.err
        assert "Traceback" in captured.err
