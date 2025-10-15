#!/usr/bin/env python3
"""Unit tests for ConParser."""

import sys
from pathlib import Path
from typing import Any
from unittest.mock import mock_open, patch

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bfportal.core.exceptions import ParseError
from bfportal.core.interfaces import Team
from bfportal.parsers.con_parser import ConFileSet, ConParser


class TestConParserCanParse:
    """Test cases for ConParser.can_parse()."""

    def test_can_parse_con_file(self):
        """Test that .con files are recognized."""
        parser = ConParser()

        result = parser.can_parse(Path("test.con"))

        assert result is True

    def test_can_parse_con_file_uppercase(self):
        """Test that .CON files are recognized (case-insensitive)."""
        parser = ConParser()

        result = parser.can_parse(Path("test.CON"))

        assert result is True

    def test_cannot_parse_other_extensions(self):
        """Test that non-.con files are rejected."""
        parser = ConParser()

        result_txt = parser.can_parse(Path("test.txt"))
        result_sct = parser.can_parse(Path("test.sct"))
        result_json = parser.can_parse(Path("test.json"))

        assert result_txt is False
        assert result_sct is False
        assert result_json is False


class TestConParserBasicParsing:
    """Test cases for basic .con file parsing."""

    def test_parse_file_not_found(self, tmp_path):
        """Test that parsing nonexistent file raises ParseError."""
        parser = ConParser()
        nonexistent_file = tmp_path / "nonexistent.con"

        # Act & Assert
        with pytest.raises(ParseError, match="File not found"):
            parser.parse(nonexistent_file)

    def test_parse_empty_file(self, tmp_path):
        """Test parsing empty .con file."""
        parser = ConParser()
        con_file = tmp_path / "empty.con"
        con_file.write_text("")

        result = parser.parse(con_file)

        assert result["file"] == str(con_file)
        assert result["objects"] == []
        assert result["raw_content"] == ""

    def test_parse_comments_only(self, tmp_path):
        """Test parsing file with only comments."""
        parser = ConParser()
        con_file = tmp_path / "comments.con"
        con_file.write_text(
            """rem This is a comment
// This is also a comment
rem Another comment
"""
        )

        result = parser.parse(con_file)

        assert result["objects"] == []

    def test_parse_objecttemplate_create(self, tmp_path):
        """Test parsing ObjectTemplate.create statements."""
        parser = ConParser()
        con_file = tmp_path / "template.con"
        con_file.write_text(
            """ObjectTemplate.create ObjectSpawner MySpawner
ObjectTemplate.create ControlPoint CP1
"""
        )

        result = parser.parse(con_file)

        objects = result["objects"]
        assert len(objects) == 2
        assert objects[0]["name"] == "MySpawner"
        assert objects[0]["type"] == "ObjectSpawner"
        assert objects[1]["name"] == "CP1"
        assert objects[1]["type"] == "ControlPoint"

    def test_parse_object_create(self, tmp_path):
        """Test parsing Object.create statements (BF1942 instances)."""
        parser = ConParser()
        con_file = tmp_path / "instance.con"
        con_file.write_text(
            """Object.create Bunker_01
Object.create Tree_Pine_Large
"""
        )

        result = parser.parse(con_file)

        objects = result["objects"]
        assert len(objects) == 2
        assert objects[0]["name"] == "Bunker_01"
        assert objects[0]["type"] == "Bunker_01"  # Type is same as name for instances
        assert objects[1]["name"] == "Tree_Pine_Large"
        assert objects[1]["type"] == "Tree_Pine_Large"


class TestConParserPositionParsing:
    """Test cases for position parsing."""

    def test_parse_objecttemplate_setposition(self, tmp_path):
        """Test parsing ObjectTemplate.setPosition."""
        parser = ConParser()
        con_file = tmp_path / "position.con"
        con_file.write_text(
            """ObjectTemplate.create ObjectSpawner TestSpawner
ObjectTemplate.setPosition 100.5/50.25/200.75
"""
        )

        result = parser.parse(con_file)

        obj = result["objects"][0]
        assert "position" in obj
        assert obj["position"]["x"] == 100.5
        assert obj["position"]["y"] == 50.25
        assert obj["position"]["z"] == 200.75

    def test_parse_object_absoluteposition(self, tmp_path):
        """Test parsing Object.absolutePosition (BF1942 instance format)."""
        parser = ConParser()
        con_file = tmp_path / "abs_position.con"
        con_file.write_text(
            """Object.create TestObject
Object.absolutePosition -50.0/10.0/75.5
"""
        )

        result = parser.parse(con_file)

        obj = result["objects"][0]
        assert "position" in obj
        assert obj["position"]["x"] == -50.0
        assert obj["position"]["y"] == 10.0
        assert obj["position"]["z"] == 75.5

    def test_parse_position_negative_values(self, tmp_path):
        """Test parsing positions with negative values."""
        parser = ConParser()
        con_file = tmp_path / "negative.con"
        con_file.write_text(
            """ObjectTemplate.create ObjectSpawner TestSpawner
ObjectTemplate.setPosition -100.0/-50.0/-200.0
"""
        )

        result = parser.parse(con_file)

        obj = result["objects"][0]
        assert obj["position"]["x"] == -100.0
        assert obj["position"]["y"] == -50.0
        assert obj["position"]["z"] == -200.0

    def test_parse_position_scientific_notation(self, tmp_path):
        """Test parsing positions with scientific notation."""
        parser = ConParser()
        con_file = tmp_path / "scientific.con"
        con_file.write_text(
            """ObjectTemplate.create ObjectSpawner TestSpawner
ObjectTemplate.setPosition 1.5e2/5.25e1/2.0e-1
"""
        )

        result = parser.parse(con_file)

        obj = result["objects"][0]
        assert obj["position"]["x"] == 150.0
        assert obj["position"]["y"] == 52.5
        assert obj["position"]["z"] == 0.2


class TestConParserRotationParsing:
    """Test cases for rotation parsing."""

    def test_parse_objecttemplate_setrotation(self, tmp_path):
        """Test parsing ObjectTemplate.setRotation."""
        parser = ConParser()
        con_file = tmp_path / "rotation.con"
        con_file.write_text(
            """ObjectTemplate.create ObjectSpawner TestSpawner
ObjectTemplate.setRotation 0.0/90.0/0.0
"""
        )

        result = parser.parse(con_file)

        obj = result["objects"][0]
        assert "rotation" in obj
        assert obj["rotation"]["pitch"] == 0.0
        assert obj["rotation"]["yaw"] == 90.0
        assert obj["rotation"]["roll"] == 0.0

    def test_parse_object_rotation(self, tmp_path):
        """Test parsing Object.rotation (BF1942 instance format)."""
        parser = ConParser()
        con_file = tmp_path / "obj_rotation.con"
        con_file.write_text(
            """Object.create TestObject
Object.rotation 45.0/180.0/90.0
"""
        )

        result = parser.parse(con_file)

        obj = result["objects"][0]
        assert "rotation" in obj
        assert obj["rotation"]["pitch"] == 45.0
        assert obj["rotation"]["yaw"] == 180.0
        assert obj["rotation"]["roll"] == 90.0

    def test_parse_rotation_negative_values(self, tmp_path):
        """Test parsing rotations with negative values."""
        parser = ConParser()
        con_file = tmp_path / "negative_rot.con"
        con_file.write_text(
            """ObjectTemplate.create ObjectSpawner TestSpawner
ObjectTemplate.setRotation -45.0/-90.0/-180.0
"""
        )

        result = parser.parse(con_file)

        obj = result["objects"][0]
        assert obj["rotation"]["pitch"] == -45.0
        assert obj["rotation"]["yaw"] == -90.0
        assert obj["rotation"]["roll"] == -180.0


class TestConParserScaleParsing:
    """Test cases for scale parsing."""

    def test_parse_object_geometry_scale(self, tmp_path):
        """Test parsing Object.geometry.scale (BF1942 instance format)."""
        # Arrange
        parser = ConParser()
        con_file = tmp_path / "scale.con"
        con_file.write_text(
            """Object.create TestObject
Object.geometry.scale 2.0/1.5/0.5
"""
        )

        # Act
        result = parser.parse(con_file)

        # Assert
        obj = result["objects"][0]
        assert "scale" in obj
        assert obj["scale"]["x"] == 2.0
        assert obj["scale"]["y"] == 1.5
        assert obj["scale"]["z"] == 0.5

    def test_parse_scale_uniform(self, tmp_path):
        """Test parsing uniform scale values."""
        # Arrange
        parser = ConParser()
        con_file = tmp_path / "uniform_scale.con"
        con_file.write_text(
            """Object.create TestObject
Object.geometry.scale 3.0/3.0/3.0
"""
        )

        # Act
        result = parser.parse(con_file)

        # Assert
        obj = result["objects"][0]
        assert obj["scale"]["x"] == 3.0
        assert obj["scale"]["y"] == 3.0
        assert obj["scale"]["z"] == 3.0


class TestConParserTeamParsing:
    """Test cases for team parsing."""

    def test_parse_objecttemplate_setteam(self, tmp_path):
        """Test parsing ObjectTemplate.setTeam."""
        parser = ConParser()
        con_file = tmp_path / "team.con"
        con_file.write_text(
            """ObjectTemplate.create ObjectSpawner Spawner1
ObjectTemplate.setTeam 1

ObjectTemplate.create ObjectSpawner Spawner2
ObjectTemplate.setTeam 2
"""
        )

        result = parser.parse(con_file)

        objects = result["objects"]
        assert objects[0]["team"] == 1
        assert objects[1]["team"] == 2

    def test_parse_object_setteam(self, tmp_path):
        """Test parsing Object.setTeam (BF1942 instance format)."""
        parser = ConParser()
        con_file = tmp_path / "obj_team.con"
        con_file.write_text(
            """Object.create Bunker_German
Object.setTeam 1

Object.create Bunker_Soviet
Object.setTeam 2
"""
        )

        result = parser.parse(con_file)

        objects = result["objects"]
        assert objects[0]["team"] == 1
        assert objects[1]["team"] == 2

    def test_parse_team_zero_neutral(self, tmp_path):
        """Test parsing team 0 (neutral)."""
        parser = ConParser()
        con_file = tmp_path / "neutral.con"
        con_file.write_text(
            """ObjectTemplate.create ObjectSpawner NeutralSpawner
ObjectTemplate.setTeam 0
"""
        )

        result = parser.parse(con_file)

        obj = result["objects"][0]
        assert obj["team"] == 0


class TestConParserGenericProperties:
    """Test cases for generic property parsing."""

    def test_parse_generic_objecttemplate_properties(self, tmp_path):
        """Test parsing generic ObjectTemplate properties."""
        parser = ConParser()
        con_file = tmp_path / "properties.con"
        con_file.write_text(
            """ObjectTemplate.create ObjectSpawner TestSpawner
ObjectTemplate.activeSafe 1
ObjectTemplate.maxSpawnDelay 10
ObjectTemplate.spawnDelay 5
ObjectTemplate.nrOfObjectToSpawn 3
"""
        )

        result = parser.parse(con_file)

        obj = result["objects"][0]
        props = obj["properties"]
        assert props["activeSafe"] == "1"
        assert props["maxSpawnDelay"] == "10"
        assert props["spawnDelay"] == "5"
        assert props["nrOfObjectToSpawn"] == "3"

    def test_parse_generic_object_properties(self, tmp_path):
        """Test parsing generic Object properties (BF1942 instance format)."""
        parser = ConParser()
        con_file = tmp_path / "obj_properties.con"
        con_file.write_text(
            """Object.create TestObject
Object.radius 50.0
Object.controlPointId 1
Object.isControlPoint 1
"""
        )

        result = parser.parse(con_file)

        obj = result["objects"][0]
        props = obj["properties"]
        assert props["radius"] == "50.0"
        assert props["controlPointId"] == "1"
        assert props["isControlPoint"] == "1"

    def test_parse_property_with_string_value(self, tmp_path):
        """Test parsing properties with string values."""
        parser = ConParser()
        con_file = tmp_path / "string_prop.con"
        con_file.write_text(
            """ObjectTemplate.create ObjectSpawner TestSpawner
ObjectTemplate.geometry Bunker_Mesh
ObjectTemplate.mapMaterial 0 Concrete 0
"""
        )

        result = parser.parse(con_file)

        obj = result["objects"][0]
        props = obj["properties"]
        assert props["geometry"] == "Bunker_Mesh"
        assert props["mapMaterial"] == "0 Concrete 0"


class TestConParserCompleteObjects:
    """Test cases for parsing complete objects with all properties."""

    def test_parse_complete_spawn_point(self, tmp_path):
        """Test parsing complete spawn point with position, rotation, and team."""
        parser = ConParser()
        con_file = tmp_path / "spawn.con"
        con_file.write_text(
            """ObjectTemplate.create ObjectSpawner SpawnPoint_1_1
ObjectTemplate.setPosition 150.0/25.0/300.0
ObjectTemplate.setRotation 0.0/45.0/0.0
ObjectTemplate.setTeam 1
ObjectTemplate.activeSafe 1
"""
        )

        result = parser.parse(con_file)

        obj = result["objects"][0]
        assert obj["name"] == "SpawnPoint_1_1"
        assert obj["type"] == "ObjectSpawner"
        assert obj["position"]["x"] == 150.0
        assert obj["position"]["y"] == 25.0
        assert obj["position"]["z"] == 300.0
        assert obj["rotation"]["pitch"] == 0.0
        assert obj["rotation"]["yaw"] == 45.0
        assert obj["rotation"]["roll"] == 0.0
        assert obj["team"] == 1
        assert obj["properties"]["activeSafe"] == "1"

    def test_parse_multiple_complete_objects(self, tmp_path):
        """Test parsing multiple complete objects."""
        parser = ConParser()
        con_file = tmp_path / "multiple.con"
        con_file.write_text(
            """ObjectTemplate.create ControlPoint CP1
ObjectTemplate.setPosition 100.0/0.0/100.0
ObjectTemplate.setRotation 0.0/0.0/0.0
ObjectTemplate.radius 50.0

ObjectTemplate.create ObjectSpawner Spawn1
ObjectTemplate.setPosition 120.0/0.0/120.0
ObjectTemplate.setRotation 0.0/90.0/0.0
ObjectTemplate.setTeam 1

ObjectTemplate.create ObjectSpawner Spawn2
ObjectTemplate.setPosition 80.0/0.0/80.0
ObjectTemplate.setRotation 0.0/270.0/0.0
ObjectTemplate.setTeam 2
"""
        )

        result = parser.parse(con_file)

        objects = result["objects"]
        assert len(objects) == 3
        assert objects[0]["name"] == "CP1"
        assert objects[1]["name"] == "Spawn1"
        assert objects[1]["team"] == 1
        assert objects[2]["name"] == "Spawn2"
        assert objects[2]["team"] == 2


class TestConParserTransformExtraction:
    """Test cases for parse_transform() method."""

    def test_parse_transform_with_position_and_rotation(self):
        """Test extracting Transform from object with position and rotation."""
        parser = ConParser()
        obj_dict = {
            "name": "TestObject",
            "position": {"x": 100.0, "y": 50.0, "z": 200.0},
            "rotation": {"pitch": 10.0, "yaw": 45.0, "roll": 0.0},
        }

        transform = parser.parse_transform(obj_dict)

        assert transform is not None
        assert transform.position.x == 100.0
        assert transform.position.y == 50.0
        assert transform.position.z == 200.0
        assert transform.rotation.pitch == 10.0
        assert transform.rotation.yaw == 45.0
        assert transform.rotation.roll == 0.0

    def test_parse_transform_position_only(self):
        """Test extracting Transform from object with only position."""
        parser = ConParser()
        obj_dict = {
            "name": "TestObject",
            "position": {"x": 100.0, "y": 50.0, "z": 200.0},
        }

        transform = parser.parse_transform(obj_dict)

        assert transform is not None
        assert transform.position.x == 100.0
        assert transform.position.y == 50.0
        assert transform.position.z == 200.0
        # Rotation should default to (0, 0, 0)
        assert transform.rotation.pitch == 0.0
        assert transform.rotation.yaw == 0.0
        assert transform.rotation.roll == 0.0

    def test_parse_transform_no_position_returns_none(self):
        """Test that parse_transform returns None if no position."""
        parser = ConParser()
        obj_dict = {
            "name": "TestObject",
            "rotation": {"pitch": 10.0, "yaw": 45.0, "roll": 0.0},
        }

        transform = parser.parse_transform(obj_dict)

        assert transform is None

    def test_parse_transform_empty_dict_returns_none(self):
        """Test that parse_transform returns None for empty dict."""
        parser = ConParser()
        obj_dict: dict[str, object] = {}

        transform = parser.parse_transform(obj_dict)

        assert transform is None

    def test_parse_transform_partial_position(self):
        """Test extracting Transform with partial position data (defaults to 0)."""
        parser = ConParser()
        obj_dict = {
            "name": "TestObject",
            "position": {"x": 100.0, "z": 200.0},  # Missing y
        }

        transform = parser.parse_transform(obj_dict)

        assert transform is not None
        assert transform.position.x == 100.0
        assert transform.position.y == 0.0  # Default
        assert transform.position.z == 200.0

    def test_parse_transform_with_scale(self):
        """Test extracting Transform with position, rotation, and scale."""
        # Arrange
        parser = ConParser()
        obj_dict = {
            "name": "TestObject",
            "position": {"x": 100.0, "y": 50.0, "z": 200.0},
            "rotation": {"pitch": 10.0, "yaw": 45.0, "roll": 0.0},
            "scale": {"x": 2.0, "y": 1.5, "z": 0.5},
        }

        # Act
        transform = parser.parse_transform(obj_dict)

        # Assert
        assert transform is not None
        assert transform.position.x == 100.0
        assert transform.position.y == 50.0
        assert transform.position.z == 200.0
        assert transform.rotation.pitch == 10.0
        assert transform.rotation.yaw == 45.0
        assert transform.rotation.roll == 0.0
        assert transform.scale is not None
        assert transform.scale.x == 2.0
        assert transform.scale.y == 1.5
        assert transform.scale.z == 0.5

    def test_parse_transform_without_scale_defaults_to_one(self):
        """Test extracting Transform without scale defaults to (1, 1, 1).

        Note: Transform.__post_init__ sets scale to (1, 1, 1) if None.
        """
        # Arrange
        parser = ConParser()
        obj_dict = {
            "name": "TestObject",
            "position": {"x": 100.0, "y": 50.0, "z": 200.0},
        }

        # Act
        transform = parser.parse_transform(obj_dict)

        # Assert
        assert transform is not None
        assert transform.scale is not None
        assert transform.scale.x == 1.0
        assert transform.scale.y == 1.0
        assert transform.scale.z == 1.0

    def test_parse_transform_partial_scale(self):
        """Test extracting Transform with partial scale data (defaults to 1.0)."""
        # Arrange
        parser = ConParser()
        obj_dict = {
            "name": "TestObject",
            "position": {"x": 100.0, "y": 50.0, "z": 200.0},
            "scale": {"x": 2.0, "z": 3.0},  # Missing y
        }

        # Act
        transform = parser.parse_transform(obj_dict)

        # Assert
        assert transform is not None
        assert transform.scale is not None
        assert transform.scale.x == 2.0
        assert transform.scale.y == 1.0  # Default
        assert transform.scale.z == 3.0


class TestConParserTeamExtraction:
    """Test cases for parse_team() method."""

    def test_parse_team_team1(self):
        """Test extracting Team.TEAM_1."""
        parser = ConParser()
        obj_dict = {"team": 1}

        team = parser.parse_team(obj_dict)

        assert team == Team.TEAM_1

    def test_parse_team_team2(self):
        """Test extracting Team.TEAM_2."""
        parser = ConParser()
        obj_dict = {"team": 2}

        team = parser.parse_team(obj_dict)

        assert team == Team.TEAM_2

    def test_parse_team_neutral(self):
        """Test extracting Team.NEUTRAL (team 0)."""
        parser = ConParser()
        obj_dict = {"team": 0}

        team = parser.parse_team(obj_dict)

        assert team == Team.NEUTRAL

    def test_parse_team_missing_defaults_neutral(self):
        """Test that missing team defaults to NEUTRAL."""
        parser = ConParser()
        obj_dict: dict[str, object] = {}

        team = parser.parse_team(obj_dict)

        assert team == Team.NEUTRAL

    def test_parse_team_invalid_defaults_neutral(self):
        """Test that invalid team values default to NEUTRAL."""
        parser = ConParser()
        obj_dict_3 = {"team": 3}
        obj_dict_neg = {"team": -1}

        team_3 = parser.parse_team(obj_dict_3)
        team_neg = parser.parse_team(obj_dict_neg)

        assert team_3 == Team.NEUTRAL
        assert team_neg == Team.NEUTRAL

    def test_parse_team_fallback_to_osid_team1(self):
        """Test team extraction falls back to setOSId property for Team 1."""
        # Arrange
        parser = ConParser()
        obj_dict = {"team": 0, "properties": {"setOSId": "1"}}

        # Act
        team = parser.parse_team(obj_dict)

        # Assert
        assert team == Team.TEAM_1

    def test_parse_team_fallback_to_osid_team2(self):
        """Test team extraction falls back to setOSId property for Team 2."""
        # Arrange
        parser = ConParser()
        obj_dict = {"team": 0, "properties": {"setOSId": "2"}}

        # Act
        team = parser.parse_team(obj_dict)

        # Assert
        assert team == Team.TEAM_2

    def test_parse_team_explicit_team_overrides_osid(self):
        """Test that explicit team value overrides setOSId."""
        # Arrange
        parser = ConParser()
        obj_dict = {"team": 1, "properties": {"setOSId": "2"}}

        # Act
        team = parser.parse_team(obj_dict)

        # Assert - Should use explicit team value, not OSId
        assert team == Team.TEAM_1

    def test_parse_team_fallback_osid_invalid_defaults_neutral(self):
        """Test that invalid setOSId value defaults to NEUTRAL."""
        # Arrange
        parser = ConParser()
        obj_dict = {"team": 0, "properties": {"setOSId": "invalid"}}

        # Act
        team = parser.parse_team(obj_dict)

        # Assert
        assert team == Team.NEUTRAL


class TestConParserErrorHandling:
    """Test cases for error handling in ConParser."""

    def test_parse_file_read_error_raises_parseerror(self, tmp_path):
        """Test that file read errors raise ParseError."""
        # Arrange
        parser = ConParser()
        con_file = tmp_path / "test.con"
        con_file.write_text("test content")

        # Act & Assert
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = OSError("Permission denied")
            with pytest.raises(ParseError, match="Failed to read"):
                parser.parse(con_file)


class TestConFileSetInitialization:
    """Test cases for ConFileSet initialization."""

    def test_init_with_existing_directory_finds_con_files(self, tmp_path):
        """Test initialization with existing directory finds .con files.

        Note: ConFileSet only includes Conquest mode files, Init files, and StaticObjects.con
        to avoid conflicts from TDM, CTF, and SinglePlayer modes.
        """
        # Arrange - Create files that match the Conquest/Init/StaticObjects filters
        conquest_dir = tmp_path / "Conquest"
        conquest_dir.mkdir()
        (conquest_dir / "Objects.con").write_text("ObjectTemplate.create Test TestObj")
        (conquest_dir / "Spawns.con").write_text("ObjectTemplate.create Spawner Spawn1")
        (tmp_path / "Init.con").write_text("game.setCustomGameVersion 1.6")
        (tmp_path / "StaticObjects.con").write_text("ObjectTemplate.create StaticMesh Tree1")

        # Act
        fileset = ConFileSet(tmp_path)

        # Assert
        assert len(fileset.con_files) == 4
        assert conquest_dir / "Objects.con" in fileset.con_files
        assert conquest_dir / "Spawns.con" in fileset.con_files
        assert tmp_path / "Init.con" in fileset.con_files
        assert tmp_path / "StaticObjects.con" in fileset.con_files

    def test_init_with_nonexistent_directory_has_empty_list(self, tmp_path):
        """Test initialization with nonexistent directory creates empty file list."""
        # Arrange
        nonexistent_dir = tmp_path / "nonexistent"

        # Act
        fileset = ConFileSet(nonexistent_dir)

        # Assert
        assert fileset.con_files == []
        assert fileset.map_dir == nonexistent_dir

    def test_init_filters_out_non_conquest_game_modes(self, tmp_path):
        """Test initialization excludes TDM, CTF, and SinglePlayer modes."""
        # Arrange - Create files from different game modes
        conquest_dir = tmp_path / "Conquest"
        conquest_dir.mkdir()
        (conquest_dir / "Objects.con").write_text("ObjectTemplate.create Test TestObj")

        tdm_dir = tmp_path / "TDM"
        tdm_dir.mkdir()
        (tdm_dir / "Objects.con").write_text("ObjectTemplate.create Test TestObj")

        ctf_dir = tmp_path / "Ctf"
        ctf_dir.mkdir()
        (ctf_dir / "Objects.con").write_text("ObjectTemplate.create Test TestObj")

        sp_dir = tmp_path / "SinglePlayer"
        sp_dir.mkdir()
        (sp_dir / "Objects.con").write_text("ObjectTemplate.create Test TestObj")

        # Act
        fileset = ConFileSet(tmp_path)

        # Assert - Only Conquest file should be included
        assert len(fileset.con_files) == 1
        assert conquest_dir / "Objects.con" in fileset.con_files
        assert tdm_dir / "Objects.con" not in fileset.con_files
        assert ctf_dir / "Objects.con" not in fileset.con_files
        assert sp_dir / "Objects.con" not in fileset.con_files

    def test_init_includes_staticobjects_regardless_of_path(self, tmp_path):
        """Test initialization includes StaticObjects.con even without Conquest in path."""
        # Arrange
        (tmp_path / "StaticObjects.con").write_text("ObjectTemplate.create Test TestObj")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "StaticObjects.con").write_text("ObjectTemplate.create Test TestObj")

        # Act
        fileset = ConFileSet(tmp_path)

        # Assert - Both StaticObjects.con files should be included
        assert len(fileset.con_files) == 2
        assert tmp_path / "StaticObjects.con" in fileset.con_files
        assert subdir / "StaticObjects.con" in fileset.con_files


class TestConFileSetFindFile:
    """Test cases for ConFileSet.find_file()."""

    def test_find_file_finds_matching_file(self, tmp_path):
        """Test finding file by pattern match."""
        # Arrange - Create Conquest mode files
        conquest_dir = tmp_path / "Conquest"
        conquest_dir.mkdir()
        (conquest_dir / "Objects.con").write_text("test")
        (conquest_dir / "Spawns.con").write_text("test")
        fileset = ConFileSet(tmp_path)

        # Act
        result = fileset.find_file("Objects")

        # Assert
        assert result == conquest_dir / "Objects.con"

    def test_find_file_case_insensitive_match(self, tmp_path):
        """Test finding file with case-insensitive pattern."""
        # Arrange - Create Conquest mode file
        conquest_dir = tmp_path / "Conquest"
        conquest_dir.mkdir()
        (conquest_dir / "Objects.con").write_text("test")
        fileset = ConFileSet(tmp_path)

        # Act
        result = fileset.find_file("objects")

        # Assert
        assert result == conquest_dir / "Objects.con"

    def test_find_file_no_match_returns_none(self, tmp_path):
        """Test finding file returns None when no match found."""
        # Arrange - Create Conquest mode file
        conquest_dir = tmp_path / "Conquest"
        conquest_dir.mkdir()
        (conquest_dir / "Objects.con").write_text("test")
        fileset = ConFileSet(tmp_path)

        # Act
        result = fileset.find_file("Vehicles")

        # Assert
        assert result is None


class TestConFileSetParseAll:
    """Test cases for ConFileSet.parse_all()."""

    def test_parse_all_parses_multiple_files(self, tmp_path):
        """Test parsing all .con files in directory."""
        # Arrange - Create Conquest mode files
        conquest_dir = tmp_path / "Conquest"
        conquest_dir.mkdir()
        (conquest_dir / "Objects.con").write_text("ObjectTemplate.create Test TestObj")
        (conquest_dir / "Spawns.con").write_text("ObjectTemplate.create Spawner Spawn1")
        fileset = ConFileSet(tmp_path)

        # Act
        results = fileset.parse_all()

        # Assert
        assert "Objects.con" in results
        assert "Spawns.con" in results
        assert len(results["Objects.con"]["objects"]) == 1
        assert len(results["Spawns.con"]["objects"]) == 1

    def test_parse_all_handles_parse_errors_gracefully(self, tmp_path, capsys):
        """Test parse_all continues on errors and prints warning."""
        # Arrange - Create Conquest mode files
        conquest_dir = tmp_path / "Conquest"
        conquest_dir.mkdir()
        (conquest_dir / "valid.con").write_text("ObjectTemplate.create Test TestObj")
        (conquest_dir / "invalid.con").write_text("valid content")
        fileset = ConFileSet(tmp_path)

        def mock_parse_with_error(file_path: Path) -> dict[str, Any]:
            if "invalid" in str(file_path):
                raise ParseError("Test error")
            # Parse valid file normally
            return {
                "file": str(file_path),
                "objects": [{"name": "TestObj", "type": "Test", "properties": {}}],
                "raw_content": "ObjectTemplate.create Test TestObj",
            }

        # Act
        with patch.object(fileset.parser, "parse", side_effect=mock_parse_with_error):
            results = fileset.parse_all()

        # Assert
        assert "valid.con" in results
        assert "invalid.con" not in results
        captured = capsys.readouterr()
        assert "Failed to parse invalid.con" in captured.out


class TestConFileSetGetObjectsByType:
    """Test cases for ConFileSet.get_objects_by_type()."""

    def test_get_objects_by_type_finds_matching_objects(self, tmp_path):
        """Test finding objects by type across multiple files."""
        # Arrange - Create Conquest mode files
        conquest_dir = tmp_path / "Conquest"
        conquest_dir.mkdir()
        (conquest_dir / "file1.con").write_text(
            """ObjectTemplate.create ControlPoint CP1
ObjectTemplate.create ObjectSpawner Spawn1
"""
        )
        (conquest_dir / "file2.con").write_text(
            """ObjectTemplate.create ControlPoint CP2
ObjectTemplate.create Vehicle Tank1
"""
        )
        fileset = ConFileSet(tmp_path)

        # Act
        control_points = fileset.get_objects_by_type("ControlPoint")

        # Assert
        assert len(control_points) == 2
        assert control_points[0]["name"] == "CP1"
        assert control_points[1]["name"] == "CP2"

    def test_get_objects_by_type_handles_parse_errors_gracefully(self, tmp_path):
        """Test get_objects_by_type continues on parse errors."""
        # Arrange - Create Conquest mode files
        conquest_dir = tmp_path / "Conquest"
        conquest_dir.mkdir()
        (conquest_dir / "valid.con").write_text("ObjectTemplate.create Test TestObj")
        (conquest_dir / "invalid.con").write_text("valid content")
        fileset = ConFileSet(tmp_path)

        def mock_parse_with_error(file_path: Path) -> dict[str, Any]:
            if "invalid" in str(file_path):
                raise ParseError("Test error")
            # Parse valid file normally
            return {
                "file": str(file_path),
                "objects": [{"name": "TestObj", "type": "Test", "properties": {}}],
                "raw_content": "ObjectTemplate.create Test TestObj",
            }

        # Act
        with patch.object(fileset.parser, "parse", side_effect=mock_parse_with_error):
            results = fileset.get_objects_by_type("Test")

        # Assert
        assert len(results) == 1
        assert results[0]["name"] == "TestObj"

    def test_get_objects_by_type_returns_empty_list_when_no_match(self, tmp_path):
        """Test get_objects_by_type returns empty list when no matches."""
        # Arrange - Create Conquest mode file
        conquest_dir = tmp_path / "Conquest"
        conquest_dir.mkdir()
        (conquest_dir / "file1.con").write_text("ObjectTemplate.create Test TestObj")
        fileset = ConFileSet(tmp_path)

        # Act
        results = fileset.get_objects_by_type("NonexistentType")

        # Assert
        assert results == []
