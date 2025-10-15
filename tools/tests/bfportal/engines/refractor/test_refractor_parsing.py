#!/usr/bin/env python3
"""Integration tests for RefractorEngine parsing methods."""

import sys
from pathlib import Path
from unittest.mock import create_autospec

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from bfportal.core.interfaces import Rotation, Team, Transform, Vector3
from bfportal.engines.refractor.refractor_base import RefractorEngine
from bfportal.parsers.con_parser import ConFileSet


class ConcreteRefractorEngine(RefractorEngine):
    """Concrete implementation for testing."""

    def get_game_name(self) -> str:
        """Return test game name."""
        return "TestGame"

    def get_engine_version(self) -> str:
        """Return test engine version."""
        return "Refractor 1.0"

    def get_game_mode_default(self) -> str:
        """Return test game mode."""
        return "Conquest"


class TestRefractorEngineParseMap:
    """Tests for parse_map template method."""

    def test_parse_map_raises_error_for_nonexistent_directory(self):
        """Test parse_map raises FileNotFoundError for invalid path."""
        # Arrange
        engine = ConcreteRefractorEngine()
        invalid_path = Path("/nonexistent/map/path")

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Map directory not found"):
            engine.parse_map(invalid_path)

    def test_parse_map_creates_complete_map_data(self, tmp_path: Path, monkeypatch):
        """Test parse_map creates MapData with all components."""
        # Arrange
        engine = ConcreteRefractorEngine()
        map_dir = tmp_path / "TestMap"
        map_dir.mkdir()

        # Create mock ConFileSet that returns parsed data using autospec
        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.con_files = ["init.con"]
        mock_con_files.parse_all.return_value = {
            "init.con": {
                "objects": [
                    {
                        "name": "SpawnPoint_1_1",
                        "type": "SpawnPoint",
                        "properties": {},
                    },
                    {
                        "name": "SpawnPoint_2_1",
                        "type": "SpawnPoint",
                        "properties": {},
                    },
                ]
            }
        }

        # Mock ConFileSet constructor
        def mock_con_file_set_constructor(path: Path):
            assert path == map_dir
            return mock_con_files

        monkeypatch.setattr(
            "bfportal.engines.refractor.refractor_base.ConFileSet",
            mock_con_file_set_constructor,
        )

        # Mock ConParser.parse_transform to return valid transforms
        def mock_parse_transform(obj: dict):
            return Transform(position=Vector3(100.0, 0.0, 100.0), rotation=Rotation(0.0, 0.0, 0.0))

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)

        # Act
        map_data = engine.parse_map(map_dir)

        # Assert
        assert map_data.map_name == "TestMap"
        assert map_data.game_mode == "Conquest"
        assert len(map_data.team1_spawns) >= 0
        assert len(map_data.team2_spawns) >= 0
        assert map_data.bounds is not None
        assert map_data.metadata["game"] == "TestGame"
        assert map_data.metadata["engine"] == "Refractor 1.0"

    def test_parse_map_prints_progress_information(self, tmp_path: Path, monkeypatch, capsys):
        """Test parse_map prints progress information."""
        # Arrange
        engine = ConcreteRefractorEngine()
        map_dir = tmp_path / "Kursk"
        map_dir.mkdir()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.con_files = ["init.con", "objects.con"]
        mock_con_files.parse_all.return_value = {"init.con": {"objects": []}}

        monkeypatch.setattr(
            "bfportal.engines.refractor.refractor_base.ConFileSet",
            lambda path: mock_con_files,
        )

        # Act
        engine.parse_map(map_dir)
        captured = capsys.readouterr()

        # Assert
        assert "Parsing TestGame Map: Kursk" in captured.out
        assert "Found 2 .con files" in captured.out
        assert "Map parsing complete" in captured.out


class TestRefractorEngineParseSpawns:
    """Tests for _parse_spawns method."""

    def test_parse_spawns_extracts_team1_spawns(self, monkeypatch):
        """Test _parse_spawns extracts team1 spawn points."""
        # Arrange
        engine = ConcreteRefractorEngine()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.parse_all.return_value = {
            "spawns.con": {
                "objects": [
                    {"name": "SpawnPoint_1_1", "type": "SpawnPoint", "properties": {}},
                    {"name": "SpawnPoint_1_2", "type": "SpawnPoint", "properties": {}},
                    {"name": "SpawnPoint_2_1", "type": "SpawnPoint", "properties": {}},
                ]
            }
        }

        def mock_parse_transform(obj: dict):
            return Transform(position=Vector3(100.0, 0.0, 100.0), rotation=Rotation(0.0, 90.0, 0.0))

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)

        # Act
        spawns = engine._parse_spawns(mock_con_files, Team.TEAM_1)

        # Assert
        assert len(spawns) == 2
        assert all(spawn.team == Team.TEAM_1 for spawn in spawns)
        assert spawns[0].name == "SpawnPoint_1_1"
        assert spawns[1].name == "SpawnPoint_1_2"

    def test_parse_spawns_extracts_team2_spawns(self, monkeypatch):
        """Test _parse_spawns extracts team2 spawn points."""
        # Arrange
        engine = ConcreteRefractorEngine()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.parse_all.return_value = {
            "spawns.con": {
                "objects": [
                    {"name": "SpawnPoint_1_1", "type": "SpawnPoint", "properties": {}},
                    {"name": "SpawnPoint_2_1", "type": "SpawnPoint", "properties": {}},
                    {"name": "SpawnPoint_2_2", "type": "SpawnPoint", "properties": {}},
                ]
            }
        }

        def mock_parse_transform(obj: dict):
            return Transform(
                position=Vector3(200.0, 0.0, 200.0), rotation=Rotation(0.0, 180.0, 0.0)
            )

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)

        # Act
        spawns = engine._parse_spawns(mock_con_files, Team.TEAM_2)

        # Assert
        assert len(spawns) == 2
        assert all(spawn.team == Team.TEAM_2 for spawn in spawns)

    def test_parse_spawns_excludes_neutral_spawns_from_teams(self, monkeypatch):
        """Test _parse_spawns excludes neutral spawns from team HQs."""
        # Arrange
        engine = ConcreteRefractorEngine()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.parse_all.return_value = {
            "spawns.con": {
                "objects": [
                    {"name": "SpawnPoint_1_1", "type": "SpawnPoint", "properties": {}},
                    {"name": "SpawnPoint_3_1", "type": "SpawnPoint", "properties": {}},
                    {"name": "SpawnPoint_4_1", "type": "SpawnPoint", "properties": {}},
                ]
            }
        }

        def mock_parse_transform(obj: dict):
            return Transform(position=Vector3(300.0, 0.0, 300.0), rotation=Rotation(0.0, 0.0, 0.0))

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)

        # Act
        team1_spawns = engine._parse_spawns(mock_con_files, Team.TEAM_1)

        # Assert - Only team1 spawn included, neutral spawns excluded
        assert len(team1_spawns) == 1
        assert team1_spawns[0].name == "SpawnPoint_1_1"

    def test_parse_spawns_skips_objects_without_transform(self, monkeypatch):
        """Test _parse_spawns skips objects with invalid transforms."""
        # Arrange
        engine = ConcreteRefractorEngine()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.parse_all.return_value = {
            "spawns.con": {
                "objects": [
                    {"name": "SpawnPoint_1_1", "type": "SpawnPoint", "properties": {}},
                    {"name": "SpawnPoint_1_2", "type": "SpawnPoint", "properties": {}},
                ]
            }
        }

        call_count = [0]

        def mock_parse_transform(obj: dict):
            call_count[0] += 1
            if call_count[0] == 1:
                return Transform(
                    position=Vector3(100.0, 0.0, 100.0), rotation=Rotation(0.0, 0.0, 0.0)
                )
            return None  # Second spawn has invalid transform

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)

        # Act
        spawns = engine._parse_spawns(mock_con_files, Team.TEAM_1)

        # Assert - Only first spawn included
        assert len(spawns) == 1

    def test_parse_spawns_warns_if_too_few_spawns(self, monkeypatch, capsys):
        """Test _parse_spawns warns when fewer than 4 spawns found."""
        # Arrange
        engine = ConcreteRefractorEngine()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.parse_all.return_value = {
            "spawns.con": {
                "objects": [
                    {"name": "SpawnPoint_1_1", "type": "SpawnPoint", "properties": {}},
                ]
            }
        }

        def mock_parse_transform(obj: dict):
            return Transform(position=Vector3(100.0, 0.0, 100.0), rotation=Rotation(0.0, 0.0, 0.0))

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)

        # Act
        engine._parse_spawns(mock_con_files, Team.TEAM_1)
        captured = capsys.readouterr()

        # Assert
        assert "Only 1 spawns found" in captured.out
        assert "Portal requires minimum 4" in captured.out


class TestRefractorEngineParseHQ:
    """Tests for _parse_hq method."""

    def test_parse_hq_calculates_centroid_from_spawns(self):
        """Test _parse_hq calculates HQ position as spawn centroid."""
        # Arrange
        engine = ConcreteRefractorEngine()
        mock_con_files = create_autospec(ConFileSet, instance=True)

        from bfportal.core.interfaces import SpawnPoint

        spawns = [
            SpawnPoint(
                name="spawn1",
                transform=Transform(
                    position=Vector3(0.0, 10.0, 0.0), rotation=Rotation(0.0, 0.0, 0.0)
                ),
                team=Team.TEAM_1,
            ),
            SpawnPoint(
                name="spawn2",
                transform=Transform(
                    position=Vector3(100.0, 20.0, 100.0),
                    rotation=Rotation(0.0, 0.0, 0.0),
                ),
                team=Team.TEAM_1,
            ),
            SpawnPoint(
                name="spawn3",
                transform=Transform(
                    position=Vector3(200.0, 30.0, 200.0),
                    rotation=Rotation(0.0, 0.0, 0.0),
                ),
                team=Team.TEAM_1,
            ),
        ]

        # Act
        hq = engine._parse_hq(mock_con_files, Team.TEAM_1, spawns)

        # Expected centroid: (0+100+200)/3, (10+20+30)/3, (0+100+200)/3
        # = 100.0, 20.0, 100.0

        # Assert
        assert hq.position.x == pytest.approx(100.0)
        assert hq.position.y == pytest.approx(20.0)
        assert hq.position.z == pytest.approx(100.0)
        assert hq.rotation.pitch == 0.0
        assert hq.rotation.yaw == 0.0
        assert hq.rotation.roll == 0.0

    def test_parse_hq_returns_default_position_with_no_spawns(self):
        """Test _parse_hq returns default position when no spawns."""
        # Arrange
        engine = ConcreteRefractorEngine()
        mock_con_files = create_autospec(ConFileSet, instance=True)

        # Act
        hq = engine._parse_hq(mock_con_files, Team.TEAM_1, [])

        # Assert - Default fallback position
        assert hq.position.x == 0.0
        assert hq.position.y == 0.0
        assert hq.position.z == 0.0


class TestRefractorEngineParseGameObjects:
    """Tests for _parse_game_objects method."""

    def test_parse_game_objects_extracts_buildings_and_props(self, monkeypatch):
        """Test _parse_game_objects extracts game objects."""
        # Arrange
        engine = ConcreteRefractorEngine()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.parse_all.return_value = {
            "objects.con": {
                "objects": [
                    {
                        "name": "Bunker_01",
                        "type": "Building_Bunker",
                        "properties": {"health": 1000},
                    },
                    {
                        "name": "Tree_Pine",
                        "type": "Tree_Pine_Large",
                        "properties": {},
                    },
                ]
            }
        }

        def mock_parse_transform(obj: dict):
            return Transform(position=Vector3(50.0, 0.0, 50.0), rotation=Rotation(0.0, 45.0, 0.0))

        def mock_parse_team(obj: dict):
            return Team.NEUTRAL

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)
        monkeypatch.setattr(engine.con_parser, "parse_team", mock_parse_team)

        # Act
        objects = engine._parse_game_objects(mock_con_files)

        # Assert
        assert len(objects) == 2
        assert objects[0].name == "Bunker_01"
        assert objects[0].asset_type == "Building_Bunker"
        assert objects[0].properties["health"] == 1000
        assert objects[1].name == "Tree_Pine"

    def test_parse_game_objects_handles_spawners_and_excludes_control_points(self, monkeypatch):
        """Test _parse_game_objects includes ObjectSpawners with special handling and excludes ControlPoints."""
        # Arrange
        engine = ConcreteRefractorEngine()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.parse_all.return_value = {
            "objects.con": {
                "objects": [
                    {
                        "name": "TankSpawner",
                        "type": "ObjectSpawner",
                        "properties": {},
                    },
                    {
                        "name": "CP_Center",
                        "type": "ControlPoint",
                        "properties": {},
                    },
                    {
                        "name": "Building_01",
                        "type": "Building",
                        "properties": {},
                    },
                ]
            }
        }

        def mock_parse_transform(obj: dict):
            return Transform(position=Vector3(0.0, 0.0, 0.0), rotation=Rotation(0.0, 0.0, 0.0))

        def mock_parse_team(obj: dict):
            return Team.NEUTRAL

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)
        monkeypatch.setattr(engine.con_parser, "parse_team", mock_parse_team)

        # Mock spawner_parser.get_template to return SpawnerTemplate only for ObjectSpawner
        from bfportal.parsers.spawner_template_parser import SpawnerTemplate

        def mock_get_template(obj_type: str):
            if obj_type == "objectspawner":
                return SpawnerTemplate(
                    name="objectspawner", team1_vehicle="M4A3", team2_vehicle="T34-85"
                )
            return None  # Not a spawner template

        monkeypatch.setattr(engine.spawner_parser, "get_template", mock_get_template)

        # Act
        objects = engine._parse_game_objects(mock_con_files)

        # Assert - TankSpawner (ObjectSpawner) and Building_01 included, CP_Center (ControlPoint) excluded
        assert len(objects) == 2
        assert objects[0].name == "TankSpawner"
        # asset_type will be lowercase vehicle type (lines 626, 640 of refractor_base.py)
        assert objects[0].asset_type.lower() in ["objectspawner", "m4a3", "t34-85"]
        assert objects[1].name == "Building_01"
        assert objects[1].asset_type.lower() == "building"

    def test_parse_game_objects_skips_objects_without_transform(self, monkeypatch):
        """Test _parse_game_objects skips objects with invalid transforms."""
        # Arrange
        engine = ConcreteRefractorEngine()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.parse_all.return_value = {
            "objects.con": {
                "objects": [
                    {"name": "Building_01", "type": "Building", "properties": {}},
                    {"name": "Building_02", "type": "Building", "properties": {}},
                ]
            }
        }

        call_count = [0]

        def mock_parse_transform(obj: dict):
            call_count[0] += 1
            if call_count[0] == 1:
                return Transform(position=Vector3(0.0, 0.0, 0.0), rotation=Rotation(0.0, 0.0, 0.0))
            return None

        def mock_parse_team(obj: dict):
            return Team.NEUTRAL

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)
        monkeypatch.setattr(engine.con_parser, "parse_team", mock_parse_team)

        # Act
        objects = engine._parse_game_objects(mock_con_files)

        # Assert - Only first object included
        assert len(objects) == 1
        assert objects[0].name == "Building_01"


class TestRefractorEngineParseCapturePoints:
    """Tests for _parse_capture_points method."""

    def test_parse_capture_points_extracts_control_points(self, monkeypatch):
        """Test _parse_capture_points extracts ControlPoint objects."""
        # Arrange
        engine = ConcreteRefractorEngine()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.parse_all.return_value = {
            "controlpoints.con": {
                "objects": [
                    {
                        "name": "CP_Center",
                        "type": "ControlPoint",
                        "properties": {"radius": 75.0},
                    },
                    {
                        "name": "CP_North",
                        "type": "ControlPoint",
                        "properties": {"radius": 60.0},
                    },
                ]
            }
        }

        def mock_parse_transform(obj: dict):
            return Transform(position=Vector3(0.0, 0.0, 0.0), rotation=Rotation(0.0, 0.0, 0.0))

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)

        # Act
        capture_points = engine._parse_capture_points(mock_con_files)

        # Assert
        assert len(capture_points) == 2
        assert capture_points[0].name == "CP_Center"
        assert capture_points[0].radius == 75.0
        assert capture_points[1].name == "CP_North"
        assert capture_points[1].radius == 60.0

    def test_parse_capture_points_excludes_hq_bases(self, monkeypatch):
        """Test _parse_capture_points excludes team HQ bases."""
        # Arrange
        engine = ConcreteRefractorEngine()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.parse_all.return_value = {
            "controlpoints.con": {
                "objects": [
                    {
                        "name": "base_axis",
                        "type": "ControlPoint",
                        "properties": {},
                    },
                    {
                        "name": "base_allies",
                        "type": "ControlPoint",
                        "properties": {},
                    },
                    {
                        "name": "CP_Center",
                        "type": "ControlPoint",
                        "properties": {},
                    },
                ]
            }
        }

        def mock_parse_transform(obj: dict):
            return Transform(position=Vector3(0.0, 0.0, 0.0), rotation=Rotation(0.0, 0.0, 0.0))

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)

        # Act
        capture_points = engine._parse_capture_points(mock_con_files)

        # Assert - Only neutral CP included, HQ bases excluded
        assert len(capture_points) == 1
        assert capture_points[0].name == "CP_Center"

    def test_parse_capture_points_associates_neutral_spawns(self, monkeypatch):
        """Test _parse_capture_points associates neutral spawns to CPs."""
        # Arrange
        engine = ConcreteRefractorEngine()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.parse_all.return_value = {
            "map.con": {
                "objects": [
                    {
                        "name": "CP_Center",
                        "type": "ControlPoint",
                        "properties": {},
                    },
                    {
                        "name": "spawn_3_1",
                        "type": "SpawnPoint",
                        "properties": {},
                    },
                    {
                        "name": "spawn_3_2",
                        "type": "SpawnPoint",
                        "properties": {},
                    },
                ]
            }
        }

        def mock_parse_transform(obj: dict):
            return Transform(position=Vector3(100.0, 0.0, 100.0), rotation=Rotation(0.0, 0.0, 0.0))

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)

        # Act
        capture_points = engine._parse_capture_points(mock_con_files)

        # Assert
        assert len(capture_points) == 1
        cp = capture_points[0]
        assert cp.team1_spawns is not None
        assert cp.team2_spawns is not None
        assert len(cp.team1_spawns) == 2  # Both spawns added to team1
        assert len(cp.team2_spawns) == 2  # Both spawns added to team2
        assert cp.team1_spawns[0].team == Team.NEUTRAL
        assert cp.team2_spawns[0].team == Team.NEUTRAL

    def test_parse_capture_points_updates_position_from_spawn_centroid(self, monkeypatch):
        """Test _parse_capture_points updates CP position to spawn centroid."""
        # Arrange
        engine = ConcreteRefractorEngine()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.parse_all.return_value = {
            "map.con": {
                "objects": [
                    {
                        "name": "CP_Center",
                        "type": "ControlPoint",
                        "properties": {},
                    },
                    {
                        "name": "spawn_3_1",
                        "type": "SpawnPoint",
                        "properties": {},
                    },
                    {
                        "name": "spawn_3_2",
                        "type": "SpawnPoint",
                        "properties": {},
                    },
                ]
            }
        }

        call_count = [0]

        def mock_parse_transform(obj: dict):
            call_count[0] += 1
            if call_count[0] == 1:
                # CP placeholder position
                return Transform(position=Vector3(0.0, 0.0, 0.0), rotation=Rotation(0.0, 45.0, 0.0))
            elif call_count[0] == 2:
                return Transform(
                    position=Vector3(100.0, 10.0, 100.0),
                    rotation=Rotation(0.0, 0.0, 0.0),
                )
            else:
                return Transform(
                    position=Vector3(200.0, 20.0, 200.0),
                    rotation=Rotation(0.0, 0.0, 0.0),
                )

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)

        # Act
        capture_points = engine._parse_capture_points(mock_con_files)

        # Expected centroid: (100+200)/2, (10+20)/2, (100+200)/2 = 150, 15, 150
        cp = capture_points[0]

        # Assert
        assert cp.transform.position.x == pytest.approx(150.0)
        assert cp.transform.position.y == pytest.approx(15.0)
        assert cp.transform.position.z == pytest.approx(150.0)
        # Rotation should be preserved from original CP
        assert cp.transform.rotation.yaw == pytest.approx(45.0)

    def test_parse_capture_points_uses_default_radius_if_not_specified(self, monkeypatch):
        """Test _parse_capture_points uses default radius when not specified."""
        # Arrange
        engine = ConcreteRefractorEngine()

        mock_con_files = create_autospec(ConFileSet, instance=True)
        mock_con_files.parse_all.return_value = {
            "controlpoints.con": {
                "objects": [
                    {
                        "name": "CP_NoRadius",
                        "type": "ControlPoint",
                        "properties": {},
                    }
                ]
            }
        }

        def mock_parse_transform(obj: dict):
            return Transform(position=Vector3(0.0, 0.0, 0.0), rotation=Rotation(0.0, 0.0, 0.0))

        monkeypatch.setattr(engine.con_parser, "parse_transform", mock_parse_transform)

        # Act
        capture_points = engine._parse_capture_points(mock_con_files)

        # Assert - Default radius is 50.0
        assert capture_points[0].radius == 50.0
