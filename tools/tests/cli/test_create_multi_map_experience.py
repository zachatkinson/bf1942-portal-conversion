#!/usr/bin/env python3
"""Tests for create_multi_map_experience.py CLI script."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from create_multi_map_experience import (
    create_multi_map_experience,
    filter_maps,
    load_registry,
    load_spatial_data,
    main,
)


class TestLoadRegistry:
    """Tests for load_registry() function."""

    def test_loads_valid_registry(self, tmp_path: Path):
        """Test loading valid maps registry."""
        # Arrange
        registry_data = {
            "maps": [{"id": "kursk", "display_name": "Kursk", "status": "complete"}],
            "experience_templates": {},
        }
        registry_path = tmp_path / "maps_registry.json"
        registry_path.write_text(json.dumps(registry_data))

        # Act
        result = load_registry(registry_path)

        # Assert
        assert "maps" in result
        assert len(result["maps"]) == 1
        assert result["maps"][0]["id"] == "kursk"

    def test_raises_error_when_registry_missing(self, tmp_path: Path):
        """Test error raised when registry file doesn't exist."""
        # Arrange
        registry_path = tmp_path / "missing_registry.json"

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Maps registry not found"):
            load_registry(registry_path)


class TestFilterMaps:
    """Tests for filter_maps() function."""

    def test_filters_by_status(self):
        """Test filtering maps by status."""
        # Arrange
        maps = [
            {"id": "map1", "status": "complete"},
            {"id": "map2", "status": "in_progress"},
            {"id": "map3", "status": "complete"},
        ]
        filter_criteria = {"status": "complete"}

        # Act
        result = filter_maps(maps, filter_criteria)

        # Assert
        assert len(result) == 2
        assert all(m["status"] == "complete" for m in result)

    def test_filters_by_multiple_criteria(self):
        """Test filtering maps by multiple criteria."""
        # Arrange
        maps = [
            {"id": "map1", "status": "complete", "era": "WW2"},
            {"id": "map2", "status": "complete", "era": "Modern"},
            {"id": "map3", "status": "in_progress", "era": "WW2"},
        ]
        filter_criteria = {"status": "complete", "era": "WW2"}

        # Act
        result = filter_maps(maps, filter_criteria)

        # Assert
        assert len(result) == 1
        assert result[0]["id"] == "map1"

    def test_returns_all_maps_with_empty_criteria(self):
        """Test returns all maps when filter criteria is empty."""
        # Arrange
        maps = [{"id": "map1"}, {"id": "map2"}, {"id": "map3"}]
        filter_criteria: dict[str, str] = {}

        # Act
        result = filter_maps(maps, filter_criteria)

        # Assert
        assert len(result) == 3


class TestLoadSpatialData:
    """Tests for load_spatial_data() function."""

    def test_loads_and_encodes_spatial_data(self, tmp_path: Path):
        """Test loading and base64 encoding spatial data."""
        # Arrange
        import base64

        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        spatial_dir = tmp_path / "FbExportData" / "levels"
        spatial_dir.mkdir(parents=True)
        spatial_path = spatial_dir / "Kursk.spatial.json"
        spatial_path.write_text(spatial_data)
        map_entry = {"id": "kursk", "display_name": "Kursk"}

        # Act
        with (
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
            patch(
                "create_multi_map_experience.get_spatial_json_path",
                autospec=True,
                return_value=spatial_path,
            ),
        ):
            result = load_spatial_data(map_entry)

        # Assert
        assert len(result) > 0  # Base64 encoded data
        decoded = base64.b64decode(result).decode("utf-8")
        assert decoded == spatial_data

    def test_raises_error_when_spatial_file_missing(self, tmp_path: Path):
        """Test error raised when spatial file doesn't exist."""
        # Arrange
        map_entry = {"id": "missing_map", "display_name": "MissingMap"}
        missing_path = tmp_path / "FbExportData" / "levels" / "MissingMap.spatial.json"

        # Act & Assert
        with (
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
            patch(
                "create_multi_map_experience.get_spatial_json_path",
                autospec=True,
                return_value=missing_path,
            ),
            pytest.raises(FileNotFoundError, match="Spatial file not found"),
        ):
            load_spatial_data(map_entry)

    def test_uses_custom_spatial_path_when_provided(self, tmp_path: Path):
        """Test uses custom spatial_path from map entry when provided."""
        # Arrange
        import base64

        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        custom_spatial_dir = tmp_path / "custom" / "path"
        custom_spatial_dir.mkdir(parents=True)
        custom_spatial_path = custom_spatial_dir / "custom.spatial.json"
        custom_spatial_path.write_text(spatial_data)
        map_entry = {
            "id": "custom_map",
            "display_name": "CustomMap",
            "spatial_path": "custom/path/custom.spatial.json",
        }

        # Act
        with patch(
            "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
        ):
            result = load_spatial_data(map_entry)

        # Assert
        assert len(result) > 0
        decoded = base64.b64decode(result).decode("utf-8")
        assert decoded == spatial_data


class TestCreateMultiMapExperience:
    """Tests for create_multi_map_experience() function."""

    def test_creates_experience_with_multiple_maps(self, tmp_path: Path):
        """Test creating multi-map experience."""
        # Arrange
        spatial_dir = tmp_path / "FbExportData" / "levels"
        spatial_dir.mkdir(parents=True)
        for map_name in ["Kursk", "ElAlamein"]:
            spatial_path = spatial_dir / f"{map_name}.spatial.json"
            spatial_path.write_text(json.dumps({"Portal_Dynamic": [], "Static": []}))

        maps = [
            {
                "id": "kursk",
                "display_name": "Kursk",
                "base_map": "MP_Tungsten",
                "base_map_display": "Tungsten",
                "status": "complete",
            },
            {
                "id": "el_alamein",
                "display_name": "ElAlamein",
                "base_map": "MP_Outskirts",
                "base_map_display": "Outskirts",
                "status": "complete",
            },
        ]

        # Act
        with (
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
            patch(
                "create_multi_map_experience.get_spatial_json_path",
                side_effect=lambda name: tmp_path
                / "FbExportData"
                / "levels"
                / f"{name}.spatial.json",
            ),
        ):
            result = create_multi_map_experience(
                maps=maps,
                experience_name="Test Experience",
                description="Test description",
                game_mode="Conquest",
                max_players_per_team=32,
            )

        # Assert
        assert result["name"] == "Test Experience"
        assert result["description"] == "Test description"
        assert len(result["mapRotation"]) == 2

    def test_skips_incomplete_maps(self, tmp_path: Path):
        """Test skips maps with status != complete."""
        # Arrange
        spatial_dir = tmp_path / "FbExportData" / "levels"
        spatial_dir.mkdir(parents=True)
        spatial_path = spatial_dir / "Kursk.spatial.json"
        spatial_path.write_text(json.dumps({"Portal_Dynamic": [], "Static": []}))

        maps = [
            {
                "id": "kursk",
                "display_name": "Kursk",
                "base_map": "MP_Tungsten",
                "base_map_display": "Tungsten",
                "status": "complete",
            },
            {
                "id": "incomplete",
                "display_name": "Incomplete",
                "base_map": "MP_Tungsten",
                "base_map_display": "Tungsten",
                "status": "in_progress",
            },
        ]

        # Act
        with (
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
            patch(
                "create_multi_map_experience.get_spatial_json_path",
                side_effect=lambda name: tmp_path
                / "FbExportData"
                / "levels"
                / f"{name}.spatial.json",
            ),
        ):
            result = create_multi_map_experience(
                maps=maps,
                experience_name="Test Experience",
                description="Test",
                game_mode="Conquest",
                max_players_per_team=32,
            )

        # Assert
        assert len(result["mapRotation"]) == 1

    def test_raises_error_when_no_maps_loaded(self, tmp_path: Path):
        """Test error raised when no maps are successfully loaded."""
        # Arrange
        maps = [
            {
                "id": "missing",
                "display_name": "Missing",
                "base_map": "MP_Tungsten",
                "base_map_display": "Tungsten",
                "status": "complete",
            },
        ]

        # Act & Assert
        with (
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
            patch(
                "create_multi_map_experience.get_spatial_json_path",
                side_effect=lambda name: tmp_path
                / "FbExportData"
                / "levels"
                / f"{name}.spatial.json",
            ),
            pytest.raises(RuntimeError, match="No maps were successfully loaded"),
        ):
            create_multi_map_experience(
                maps=maps,
                experience_name="Test",
                description="Test",
                game_mode="Conquest",
                max_players_per_team=32,
            )

    def test_sets_correct_map_metadata(self, tmp_path: Path):
        """Test map metadata includes correct mapIdx."""
        # Arrange
        spatial_dir = tmp_path / "FbExportData" / "levels"
        spatial_dir.mkdir(parents=True)
        for map_name in ["Map1", "Map2"]:
            spatial_path = spatial_dir / f"{map_name}.spatial.json"
            spatial_path.write_text(json.dumps({"Portal_Dynamic": [], "Static": []}))

        maps = [
            {
                "id": "map1",
                "display_name": "Map1",
                "base_map": "MP_Tungsten",
                "base_map_display": "Tungsten",
                "status": "complete",
            },
            {
                "id": "map2",
                "display_name": "Map2",
                "base_map": "MP_Tungsten",
                "base_map_display": "Tungsten",
                "status": "complete",
            },
        ]

        # Act
        with (
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
            patch(
                "create_multi_map_experience.get_spatial_json_path",
                side_effect=lambda name: tmp_path
                / "FbExportData"
                / "levels"
                / f"{name}.spatial.json",
            ),
        ):
            result = create_multi_map_experience(
                maps=maps,
                experience_name="Test",
                description="Test",
                game_mode="Conquest",
                max_players_per_team=32,
            )

        # Assert
        assert result["mapRotation"][0]["spatialAttachment"]["metadata"] == "mapIdx=0"
        assert result["mapRotation"][1]["spatialAttachment"]["metadata"] == "mapIdx=1"

    def test_sets_team_composition_for_player_count(self, tmp_path: Path):
        """Test team composition matches max_players_per_team."""
        # Arrange
        spatial_dir = tmp_path / "FbExportData" / "levels"
        spatial_dir.mkdir(parents=True)
        spatial_path = spatial_dir / "Kursk.spatial.json"
        spatial_path.write_text(json.dumps({"Portal_Dynamic": [], "Static": []}))

        maps = [
            {
                "id": "kursk",
                "display_name": "Kursk",
                "base_map": "MP_Tungsten",
                "base_map_display": "Tungsten",
                "status": "complete",
            },
        ]

        # Act
        with (
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
            patch(
                "create_multi_map_experience.get_spatial_json_path",
                side_effect=lambda name: tmp_path
                / "FbExportData"
                / "levels"
                / f"{name}.spatial.json",
            ),
        ):
            result = create_multi_map_experience(
                maps=maps,
                experience_name="Test",
                description="Test",
                game_mode="Conquest",
                max_players_per_team=64,
            )

        # Assert
        assert result["teamComposition"][0][1]["humanCapacity"] == 64
        assert result["teamComposition"][1][1]["humanCapacity"] == 64


class TestMainFunction:
    """Tests for main() CLI entry point."""

    def test_returns_error_when_registry_missing(self):
        """Test main returns error code when registry doesn't exist."""
        # Arrange
        test_args = ["create_multi_map_experience.py", "--registry", "missing.json"]

        # Act
        with patch("sys.argv", test_args):
            result = main()

        # Assert
        assert result == 1

    def test_returns_error_when_template_not_found(self, tmp_path: Path):
        """Test main returns error code when template doesn't exist."""
        # Arrange
        registry_data: dict[str, list | dict] = {"maps": [], "experience_templates": {}}
        registry_path = tmp_path / "registry.json"
        registry_path.write_text(json.dumps(registry_data))
        test_args = [
            "create_multi_map_experience.py",
            "--registry",
            str(registry_path),
            "--template",
            "missing_template",
        ]

        # Act
        with patch("sys.argv", test_args):
            result = main()

        # Assert
        assert result == 1

    def test_prints_available_templates_when_template_not_found(self, tmp_path: Path, capsys):
        """Test main prints available templates when requested template not found."""
        # Arrange
        registry_data: dict[str, list | dict] = {
            "maps": [],
            "experience_templates": {
                "template1": {},
                "template2": {},
            },
        }
        registry_path = tmp_path / "registry.json"
        registry_path.write_text(json.dumps(registry_data))
        test_args = [
            "create_multi_map_experience.py",
            "--registry",
            str(registry_path),
            "--template",
            "missing_template",
        ]

        # Act
        with patch("sys.argv", test_args):
            result = main()

        captured = capsys.readouterr()

        # Assert
        assert result == 1
        assert "template1" in captured.err
        assert "template2" in captured.err

    def test_warns_when_specific_maps_not_found_in_registry(self, tmp_path: Path, capsys):
        """Test main warns when specific maps requested but not found."""
        # Arrange
        spatial_dir = tmp_path / "FbExportData" / "levels"
        spatial_dir.mkdir(parents=True)
        spatial_path = spatial_dir / "Kursk.spatial.json"
        spatial_path.write_text(json.dumps({"Portal_Dynamic": [], "Static": []}))

        registry_data = {
            "maps": [
                {
                    "id": "kursk",
                    "display_name": "Kursk",
                    "base_map": "MP_Tungsten",
                    "base_map_display": "Tungsten",
                    "status": "complete",
                }
            ],
            "experience_templates": {
                "test_template": {
                    "name": "Test",
                    "description": "Test",
                    "game_mode": "Conquest",
                    "max_players": 32,
                    "map_filter": {},
                }
            },
        }
        registry_path = tmp_path / "registry.json"
        registry_path.write_text(json.dumps(registry_data))
        test_args = [
            "create_multi_map_experience.py",
            "--registry",
            str(registry_path),
            "--template",
            "test_template",
            "--maps",
            "kursk",
            "missing_map1",
            "missing_map2",
        ]

        # Act
        with (
            patch("sys.argv", test_args),
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
        ):
            result = main()

        captured = capsys.readouterr()

        # Assert
        assert result == 0
        assert "missing_map1" in captured.out
        assert "missing_map2" in captured.out

    def test_returns_error_when_no_maps_matched_criteria(self, tmp_path: Path):
        """Test main returns error code when no maps match filter criteria."""
        # Arrange
        registry_data = {
            "maps": [
                {
                    "id": "kursk",
                    "display_name": "Kursk",
                    "base_map": "MP_Tungsten",
                    "base_map_display": "Tungsten",
                    "status": "in_progress",
                }
            ],
            "experience_templates": {
                "test_template": {
                    "name": "Test",
                    "description": "Test",
                    "game_mode": "Conquest",
                    "max_players": 32,
                    "map_filter": {"status": "complete"},
                }
            },
        }
        registry_path = tmp_path / "registry.json"
        registry_path.write_text(json.dumps(registry_data))
        test_args = [
            "create_multi_map_experience.py",
            "--registry",
            str(registry_path),
            "--template",
            "test_template",
        ]

        # Act
        with (
            patch("sys.argv", test_args),
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
        ):
            result = main()

        # Assert
        assert result == 1

    def test_uses_custom_output_path_when_provided(self, tmp_path: Path):
        """Test main uses custom output path when --output specified."""
        # Arrange
        spatial_dir = tmp_path / "FbExportData" / "levels"
        spatial_dir.mkdir(parents=True)
        spatial_path = spatial_dir / "Kursk.spatial.json"
        spatial_path.write_text(json.dumps({"Portal_Dynamic": [], "Static": []}))

        custom_output = tmp_path / "custom" / "my_experience.json"
        custom_output.parent.mkdir(parents=True)

        registry_data = {
            "maps": [
                {
                    "id": "kursk",
                    "display_name": "Kursk",
                    "base_map": "MP_Tungsten",
                    "base_map_display": "Tungsten",
                    "status": "complete",
                }
            ],
            "experience_templates": {
                "test_template": {
                    "name": "Test Experience",
                    "description": "Test",
                    "game_mode": "Conquest",
                    "max_players": 32,
                    "map_filter": {"status": "complete"},
                }
            },
        }
        registry_path = tmp_path / "registry.json"
        registry_path.write_text(json.dumps(registry_data))
        test_args = [
            "create_multi_map_experience.py",
            "--registry",
            str(registry_path),
            "--template",
            "test_template",
            "--output",
            str(custom_output),
        ]

        # Act
        with (
            patch("sys.argv", test_args),
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
        ):
            result = main()

        # Assert
        assert result == 0
        assert custom_output.exists()

    def test_returns_success_when_experience_created(self, tmp_path: Path):
        """Test main returns success code when experience is created."""
        # Arrange
        spatial_dir = tmp_path / "FbExportData" / "levels"
        spatial_dir.mkdir(parents=True)
        spatial_path = spatial_dir / "Kursk.spatial.json"
        spatial_path.write_text(json.dumps({"Portal_Dynamic": [], "Static": []}))

        registry_data = {
            "maps": [
                {
                    "id": "kursk",
                    "display_name": "Kursk",
                    "base_map": "MP_Tungsten",
                    "base_map_display": "Tungsten",
                    "status": "complete",
                }
            ],
            "experience_templates": {
                "test_template": {
                    "name": "Test",
                    "description": "Test",
                    "game_mode": "Conquest",
                    "max_players": 32,
                    "map_filter": {"status": "complete"},
                }
            },
        }
        registry_path = tmp_path / "registry.json"
        registry_path.write_text(json.dumps(registry_data))
        test_args = [
            "create_multi_map_experience.py",
            "--registry",
            str(registry_path),
            "--template",
            "test_template",
        ]

        # Act
        with (
            patch("sys.argv", test_args),
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
        ):
            result = main()

        # Assert
        assert result == 0

    def test_custom_mode_sets_modbuilder_gamemode_custom(self, tmp_path: Path):
        """Test --mode custom sets modbuilder_gamemode to CUSTOM."""
        # Arrange
        spatial_dir = tmp_path / "FbExportData" / "levels"
        spatial_dir.mkdir(parents=True)
        spatial_path = spatial_dir / "Kursk.spatial.json"
        spatial_path.write_text(json.dumps({"Portal_Dynamic": [], "Static": []}))

        registry_data = {
            "maps": [
                {
                    "id": "kursk",
                    "display_name": "Kursk",
                    "base_map": "MP_Tungsten",
                    "base_map_display": "Tungsten",
                    "status": "complete",
                }
            ],
            "experience_templates": {
                "test_template": {
                    "name": "Test",
                    "description": "Test",
                    "game_mode": "Conquest",
                    "max_players": 32,
                    "map_filter": {"status": "complete"},
                }
            },
        }
        registry_path = tmp_path / "registry.json"
        registry_path.write_text(json.dumps(registry_data))
        test_args = [
            "create_multi_map_experience.py",
            "--registry",
            str(registry_path),
            "--template",
            "test_template",
            "--mode",
            "custom",
        ]

        # Act
        with (
            patch("sys.argv", test_args),
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
        ):
            result = main()

        # Assert
        assert result == 0
        # Verify experience file created with custom mode
        experiences_dir = tmp_path / "experiences" / "multi"
        experience_file = experiences_dir / "Test_Experience.json"
        assert experience_file.exists()

        with open(experience_file, encoding="utf-8") as f:
            experience = json.load(f)
            # MODBUILDER_GAMEMODE_CUSTOM = 2
            assert experience["mutators"]["ModBuilder_GameMode"] == 2

    def test_verified_mode_sets_modbuilder_gamemode_verified(self, tmp_path: Path):
        """Test --mode verified (default) sets modbuilder_gamemode to VERIFIED."""
        # Arrange
        spatial_dir = tmp_path / "FbExportData" / "levels"
        spatial_dir.mkdir(parents=True)
        spatial_path = spatial_dir / "Kursk.spatial.json"
        spatial_path.write_text(json.dumps({"Portal_Dynamic": [], "Static": []}))

        registry_data = {
            "maps": [
                {
                    "id": "kursk",
                    "display_name": "Kursk",
                    "base_map": "MP_Tungsten",
                    "base_map_display": "Tungsten",
                    "status": "complete",
                }
            ],
            "experience_templates": {
                "test_template": {
                    "name": "Test",
                    "description": "Test",
                    "game_mode": "Conquest",
                    "max_players": 32,
                    "map_filter": {"status": "complete"},
                }
            },
        }
        registry_path = tmp_path / "registry.json"
        registry_path.write_text(json.dumps(registry_data))
        test_args = [
            "create_multi_map_experience.py",
            "--registry",
            str(registry_path),
            "--template",
            "test_template",
            "--mode",
            "verified",
        ]

        # Act
        with (
            patch("sys.argv", test_args),
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
        ):
            result = main()

        # Assert
        assert result == 0
        # Verify experience file created with verified mode
        experiences_dir = tmp_path / "experiences" / "multi"
        experience_file = experiences_dir / "Test_Experience.json"
        assert experience_file.exists()

        with open(experience_file, encoding="utf-8") as f:
            experience = json.load(f)
            # MODBUILDER_GAMEMODE_VERIFIED = 0
            assert experience["mutators"]["ModBuilder_GameMode"] == 0

    def test_override_flags_take_precedence_over_template(self, tmp_path: Path):
        """Test CLI override flags take precedence over template values."""
        # Arrange
        spatial_dir = tmp_path / "FbExportData" / "levels"
        spatial_dir.mkdir(parents=True)
        spatial_path = spatial_dir / "Kursk.spatial.json"
        spatial_path.write_text(json.dumps({"Portal_Dynamic": [], "Static": []}))

        registry_data = {
            "maps": [
                {
                    "id": "kursk",
                    "display_name": "Kursk",
                    "base_map": "MP_Tungsten",
                    "base_map_display": "Tungsten",
                    "status": "complete",
                }
            ],
            "experience_templates": {
                "test_template": {
                    "name": "Template Name",
                    "description": "Template Description",
                    "game_mode": "Conquest",
                    "max_players": 32,
                    "map_filter": {"status": "complete"},
                }
            },
        }
        registry_path = tmp_path / "registry.json"
        registry_path.write_text(json.dumps(registry_data))
        test_args = [
            "create_multi_map_experience.py",
            "--registry",
            str(registry_path),
            "--template",
            "test_template",
            "--name",
            "Custom Name",
            "--description",
            "Custom Description",
            "--game-mode",
            "TeamDeathmatch",
            "--max-players",
            "64",
        ]

        # Act
        with (
            patch("sys.argv", test_args),
            patch(
                "create_multi_map_experience.get_project_root", autospec=True, return_value=tmp_path
            ),
        ):
            result = main()

        # Assert
        assert result == 0
        experiences_dir = tmp_path / "experiences" / "multi"
        experience_file = experiences_dir / "Custom_Name_Experience.json"
        assert experience_file.exists()

        with open(experience_file, encoding="utf-8") as f:
            experience = json.load(f)
            assert experience["name"] == "Custom Name"
            assert experience["description"] == "Custom Description"
            assert experience["teamComposition"][0][1]["humanCapacity"] == 64
