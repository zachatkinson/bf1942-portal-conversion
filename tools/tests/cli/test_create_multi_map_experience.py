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
        filter_criteria = {}

        # Act
        result = filter_maps(maps, filter_criteria)

        # Assert
        assert len(result) == 3


class TestLoadSpatialData:
    """Tests for load_spatial_data() function."""

    def test_loads_and_encodes_spatial_data(self, tmp_path: Path):
        """Test loading and base64 encoding spatial data."""
        # Arrange
        spatial_data = json.dumps({"Portal_Dynamic": [], "Static": []})
        spatial_dir = tmp_path / "FbExportData" / "levels"
        spatial_dir.mkdir(parents=True)
        spatial_path = spatial_dir / "Kursk.spatial.json"
        spatial_path.write_text(spatial_data)
        map_entry = {"id": "kursk", "display_name": "Kursk"}

        # Act
        result = load_spatial_data(map_entry, tmp_path)

        # Assert
        assert len(result) > 0  # Base64 encoded data
        import base64

        decoded = base64.b64decode(result).decode("utf-8")
        assert decoded == spatial_data

    def test_raises_error_when_spatial_file_missing(self, tmp_path: Path):
        """Test error raised when spatial file doesn't exist."""
        # Arrange
        map_entry = {"id": "missing_map", "display_name": "MissingMap"}

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Spatial file not found"):
            load_spatial_data(map_entry, tmp_path)


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
        result = create_multi_map_experience(
            maps=maps,
            experience_name="Test Experience",
            description="Test description",
            game_mode="Conquest",
            max_players_per_team=32,
            project_root=tmp_path,
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
        result = create_multi_map_experience(
            maps=maps,
            experience_name="Test Experience",
            description="Test",
            game_mode="Conquest",
            max_players_per_team=32,
            project_root=tmp_path,
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
        with pytest.raises(RuntimeError, match="No maps were successfully loaded"):
            create_multi_map_experience(
                maps=maps,
                experience_name="Test",
                description="Test",
                game_mode="Conquest",
                max_players_per_team=32,
                project_root=tmp_path,
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
        result = create_multi_map_experience(
            maps=maps,
            experience_name="Test",
            description="Test",
            game_mode="Conquest",
            max_players_per_team=32,
            project_root=tmp_path,
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
        result = create_multi_map_experience(
            maps=maps,
            experience_name="Test",
            description="Test",
            game_mode="Conquest",
            max_players_per_team=64,
            project_root=tmp_path,
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
        registry_data = {"maps": [], "experience_templates": {}}
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
        with patch("sys.argv", test_args):
            with patch("create_multi_map_experience.Path.cwd", return_value=tmp_path):
                result = main()

        # Assert
        assert result == 0
