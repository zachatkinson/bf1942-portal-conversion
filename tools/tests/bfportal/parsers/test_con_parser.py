#!/usr/bin/env python3
"""Unit tests for ConParser."""

import sys
from pathlib import Path

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bfportal.core.exceptions import ParseError
from bfportal.core.interfaces import Team
from bfportal.parsers.con_parser import ConParser


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
