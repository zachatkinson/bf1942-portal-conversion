#!/usr/bin/env python3
"""Comprehensive tests for TscnReader class.

Tests cover:
- Initialization
- File parsing (success and error paths)
- Node block parsing
- Property extraction
- Node filtering by pattern
- Node filtering by team
- Edge cases and error handling
"""

from pathlib import Path

import pytest
from bfportal.core.interfaces import Vector3
from bfportal.validation.tscn_reader import TscnNode, TscnReader

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_tscn_content() -> str:
    """Create sample .tscn file content for testing.

    Returns:
        Valid .tscn file content with multiple nodes
    """
    return """[gd_scene load_steps=7 format=3]

[node name="MAP_NAME" type="Node3D"]

[node name="TEAM_1_HQ" parent="." instance=ExtResource("HQ_PlayerSpawner")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100.0, 50.0, 200.0)
Team = 1
ObjId = 1

[node name="SpawnPoint_1_1" parent="TEAM_1_HQ" instance=ExtResource("SpawnPoint")]
transform = Transform3D(0.707, -0.707, 0, 0.707, 0.707, 0, 0, 0, 1, 110.0, 51.0, 210.0)
ObjId = 10

[node name="TEAM_2_HQ" parent="." instance=ExtResource("HQ_PlayerSpawner")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, -100.0, 50.0, -200.0)
Team = 2
ObjId = 2

[node name="CapturePoint_A" parent="." instance=ExtResource("CapturePoint")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0.0, 45.0, 0.0)
ObjId = 100

[node name="StaticObject" parent="Static" instance=ExtResource("Tree")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 50.0, 40.0, 60.0)

[node name="NoTransform" parent="." instance=ExtResource("Marker")]
visible = true
"""


@pytest.fixture
def valid_tscn_file(tmp_path: Path, sample_tscn_content: str) -> Path:
    """Create a valid .tscn file for testing.

    Args:
        tmp_path: Pytest temporary directory
        sample_tscn_content: Sample content fixture

    Returns:
        Path to created .tscn file
    """
    tscn_file = tmp_path / "test_map.tscn"
    tscn_file.write_text(sample_tscn_content)
    return tscn_file


@pytest.fixture
def expected_nodes() -> list[TscnNode]:
    """Create expected parsed nodes from sample content.

    Returns:
        List of expected TscnNode objects
    """
    return [
        TscnNode(
            name="TEAM_1_HQ",
            position=Vector3(100.0, 50.0, 200.0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={"team": 1, "objid": 1, "parent": "."},
            raw_content='parent="." instance=ExtResource("HQ_PlayerSpawner")\ntransform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100.0, 50.0, 200.0)\nTeam = 1\nObjId = 1\n\n',
        ),
        TscnNode(
            name="SpawnPoint_1_1",
            position=Vector3(110.0, 51.0, 210.0),
            rotation_matrix=[0.707, -0.707, 0, 0.707, 0.707, 0, 0, 0, 1],
            properties={"objid": 10, "parent": "TEAM_1_HQ"},
            raw_content='parent="TEAM_1_HQ" instance=ExtResource("SpawnPoint")\ntransform = Transform3D(0.707, -0.707, 0, 0.707, 0.707, 0, 0, 0, 1, 110.0, 51.0, 210.0)\nObjId = 10\n\n',
        ),
        TscnNode(
            name="TEAM_2_HQ",
            position=Vector3(-100.0, 50.0, -200.0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={"team": 2, "objid": 2, "parent": "."},
            raw_content='parent="." instance=ExtResource("HQ_PlayerSpawner")\ntransform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, -100.0, 50.0, -200.0)\nTeam = 2\nObjId = 2\n\n',
        ),
        TscnNode(
            name="CapturePoint_A",
            position=Vector3(0.0, 45.0, 0.0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={"objid": 100, "parent": "."},
            raw_content='parent="." instance=ExtResource("CapturePoint")\ntransform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0.0, 45.0, 0.0)\nObjId = 100\n\n',
        ),
        TscnNode(
            name="StaticObject",
            position=Vector3(50.0, 40.0, 60.0),
            rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            properties={"parent": "Static"},
            raw_content='parent="Static" instance=ExtResource("Tree")\ntransform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 50.0, 40.0, 60.0)\n\n',
        ),
    ]


# ============================================================================
# Test TscnReader Initialization
# ============================================================================


def test_init_stores_tscn_path_successfully(tmp_path: Path):
    """Test TscnReader.__init__ stores path successfully."""
    # Arrange
    tscn_path = tmp_path / "test.tscn"

    # Act
    reader = TscnReader(tscn_path)

    # Assert
    assert reader.tscn_path == tscn_path
    assert reader.nodes == []


def test_init_accepts_nonexistent_path(tmp_path: Path):
    """Test TscnReader.__init__ accepts path that doesn't exist yet."""
    # Arrange
    tscn_path = tmp_path / "nonexistent.tscn"

    # Act
    reader = TscnReader(tscn_path)

    # Assert
    assert reader.tscn_path == tscn_path
    assert reader.nodes == []


def test_init_initializes_empty_nodes_list(tmp_path: Path):
    """Test TscnReader.__init__ initializes empty nodes list."""
    # Arrange
    tscn_path = tmp_path / "test.tscn"

    # Act
    reader = TscnReader(tscn_path)

    # Assert
    assert isinstance(reader.nodes, list)
    assert len(reader.nodes) == 0


# ============================================================================
# Test TscnReader.parse() - Success Cases
# ============================================================================


def test_parse_reads_valid_tscn_file_successfully(valid_tscn_file: Path):
    """Test parse() reads and parses valid .tscn file successfully."""
    # Arrange
    reader = TscnReader(valid_tscn_file)

    # Act
    nodes = reader.parse()

    # Assert
    assert len(nodes) == 5  # 5 nodes with transforms in sample content
    assert all(isinstance(node, TscnNode) for node in nodes)


def test_parse_extracts_node_names_correctly(valid_tscn_file: Path):
    """Test parse() extracts node names correctly."""
    # Arrange
    reader = TscnReader(valid_tscn_file)

    # Act
    nodes = reader.parse()

    # Assert
    node_names = [node.name for node in nodes]
    assert "TEAM_1_HQ" in node_names
    assert "SpawnPoint_1_1" in node_names
    assert "TEAM_2_HQ" in node_names
    assert "CapturePoint_A" in node_names
    assert "StaticObject" in node_names


def test_parse_extracts_positions_correctly(valid_tscn_file: Path):
    """Test parse() extracts positions correctly from Transform3D."""
    # Arrange
    reader = TscnReader(valid_tscn_file)

    # Act
    nodes = reader.parse()

    # Assert
    team1_hq = next(n for n in nodes if n.name == "TEAM_1_HQ")
    assert team1_hq.position == Vector3(100.0, 50.0, 200.0)

    team2_hq = next(n for n in nodes if n.name == "TEAM_2_HQ")
    assert team2_hq.position == Vector3(-100.0, 50.0, -200.0)


def test_parse_extracts_rotation_matrices_correctly(valid_tscn_file: Path):
    """Test parse() extracts rotation matrices correctly."""
    # Arrange
    reader = TscnReader(valid_tscn_file)

    # Act
    nodes = reader.parse()

    # Assert
    team1_hq = next(n for n in nodes if n.name == "TEAM_1_HQ")
    assert team1_hq.rotation_matrix == [1, 0, 0, 0, 1, 0, 0, 0, 1]

    spawn_point = next(n for n in nodes if n.name == "SpawnPoint_1_1")
    assert spawn_point.rotation_matrix == [0.707, -0.707, 0, 0.707, 0.707, 0, 0, 0, 1]


def test_parse_stores_nodes_in_instance_variable(valid_tscn_file: Path):
    """Test parse() stores nodes in self.nodes."""
    # Arrange
    reader = TscnReader(valid_tscn_file)

    # Act
    result = reader.parse()

    # Assert
    assert reader.nodes is result
    assert len(reader.nodes) == 5


def test_parse_skips_nodes_without_transform(valid_tscn_file: Path):
    """Test parse() skips nodes without transform property."""
    # Arrange
    reader = TscnReader(valid_tscn_file)

    # Act
    nodes = reader.parse()

    # Assert
    node_names = [node.name for node in nodes]
    assert "NoTransform" not in node_names  # This node has no transform
    assert "MAP_NAME" not in node_names  # Root node with no transform


def test_parse_handles_empty_file(tmp_path: Path):
    """Test parse() handles empty .tscn file."""
    # Arrange
    empty_file = tmp_path / "empty.tscn"
    empty_file.write_text("")
    reader = TscnReader(empty_file)

    # Act
    nodes = reader.parse()

    # Assert
    assert nodes == []


def test_parse_handles_file_with_only_header(tmp_path: Path):
    """Test parse() handles file with only header and no nodes."""
    # Arrange
    header_only = tmp_path / "header_only.tscn"
    header_only.write_text("[gd_scene load_steps=1 format=3]\n")
    reader = TscnReader(header_only)

    # Act
    nodes = reader.parse()

    # Assert
    assert nodes == []


# ============================================================================
# Test TscnReader.parse() - Error Cases
# ============================================================================


def test_parse_raises_filenotfounderror_when_file_missing(tmp_path: Path):
    """Test parse() raises FileNotFoundError when file doesn't exist."""
    # Arrange
    missing_file = tmp_path / "missing.tscn"
    reader = TscnReader(missing_file)

    # Act & Assert
    with pytest.raises(FileNotFoundError) as exc_info:
        reader.parse()

    assert "TSCN file not found" in str(exc_info.value)
    assert str(missing_file) in str(exc_info.value)


def test_parse_handles_malformed_transform_gracefully(tmp_path: Path):
    """Test parse() skips nodes with malformed Transform3D."""
    # Arrange
    malformed_content = """[gd_scene load_steps=1 format=3]

[node name="BadNode" type="Node3D"]
transform = Transform3D(1, 0, 0, 0, 1, 0)  # Only 6 values instead of 12

[node name="GoodNode" type="Node3D"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 30)
"""
    malformed_file = tmp_path / "malformed.tscn"
    malformed_file.write_text(malformed_content)
    reader = TscnReader(malformed_file)

    # Act
    nodes = reader.parse()

    # Assert
    assert len(nodes) == 1  # Only GoodNode should be parsed
    assert nodes[0].name == "GoodNode"


def test_parse_handles_negative_coordinates(tmp_path: Path):
    """Test parse() correctly handles negative coordinates."""
    # Arrange
    negative_content = """[gd_scene load_steps=1 format=3]

[node name="NegativeNode" type="Node3D"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, -50.5, -100.25, -200.75)
"""
    negative_file = tmp_path / "negative.tscn"
    negative_file.write_text(negative_content)
    reader = TscnReader(negative_file)

    # Act
    nodes = reader.parse()

    # Assert
    assert len(nodes) == 1
    assert nodes[0].position == Vector3(-50.5, -100.25, -200.75)


# ============================================================================
# Test TscnReader._parse_node_block()
# ============================================================================


def test_parse_node_block_returns_none_without_transform(tmp_path: Path):
    """Test _parse_node_block() returns None when no transform found."""
    # Arrange
    reader = TscnReader(tmp_path / "test.tscn")
    node_content = 'parent="." instance=ExtResource("Something")\nvisible = true'

    # Act
    result = reader._parse_node_block("TestNode", node_content)

    # Assert
    assert result is None


def test_parse_node_block_returns_none_with_wrong_value_count(tmp_path: Path):
    """Test _parse_node_block() returns None with wrong number of transform values."""
    # Arrange
    reader = TscnReader(tmp_path / "test.tscn")
    node_content = "transform = Transform3D(1, 0, 0, 0, 1, 0)"  # Only 6 values

    # Act
    result = reader._parse_node_block("TestNode", node_content)

    # Assert
    assert result is None


def test_parse_node_block_creates_tscn_node_with_valid_data(tmp_path: Path):
    """Test _parse_node_block() creates TscnNode with valid transform data."""
    # Arrange
    reader = TscnReader(tmp_path / "test.tscn")
    node_content = """parent="." instance=ExtResource("Test")
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 30)
Team = 1
ObjId = 42
"""

    # Act
    result = reader._parse_node_block("TestNode", node_content)

    # Assert
    assert result is not None
    assert isinstance(result, TscnNode)
    assert result.name == "TestNode"
    assert result.position == Vector3(10, 20, 30)
    assert result.rotation_matrix == [1, 0, 0, 0, 1, 0, 0, 0, 1]
    assert result.properties["team"] == 1
    assert result.properties["objid"] == 42


def test_parse_node_block_stores_raw_content(tmp_path: Path):
    """Test _parse_node_block() stores raw node content."""
    # Arrange
    reader = TscnReader(tmp_path / "test.tscn")
    node_content = "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)\nObjId = 5"

    # Act
    result = reader._parse_node_block("TestNode", node_content)

    # Assert
    assert result is not None
    assert result.raw_content == node_content


def test_parse_node_block_handles_scientific_notation(tmp_path: Path):
    """Test _parse_node_block() handles scientific notation in transforms."""
    # Arrange
    reader = TscnReader(tmp_path / "test.tscn")
    node_content = "transform = Transform3D(1e0, 0, 0, 0, 1.0, 0, 0, 0, 1, 1e2, 2.5e1, 3.0e-1)"

    # Act
    result = reader._parse_node_block("TestNode", node_content)

    # Assert
    assert result is not None
    assert result.position == Vector3(100.0, 25.0, 0.3)


def test_parse_node_block_handles_whitespace_in_transform(tmp_path: Path):
    """Test _parse_node_block() handles various whitespace in Transform3D."""
    # Arrange
    reader = TscnReader(tmp_path / "test.tscn")
    node_content = "transform = Transform3D(  1,0  ,0,0,  1,0,0,0,1,  10,  20,30  )"

    # Act
    result = reader._parse_node_block("TestNode", node_content)

    # Assert
    assert result is not None
    assert result.position == Vector3(10, 20, 30)


# ============================================================================
# Test TscnReader._extract_properties()
# ============================================================================


def test_extract_properties_extracts_team_property(tmp_path: Path):
    """Test _extract_properties() extracts Team property correctly."""
    # Arrange
    reader = TscnReader(tmp_path / "test.tscn")
    node_content = "Team = 1\nObjId = 5"

    # Act
    properties = reader._extract_properties(node_content)

    # Assert
    assert properties["team"] == 1


def test_extract_properties_extracts_objid_property(tmp_path: Path):
    """Test _extract_properties() extracts ObjId property correctly."""
    # Arrange
    reader = TscnReader(tmp_path / "test.tscn")
    node_content = "ObjId = 42\nTeam = 2"

    # Act
    properties = reader._extract_properties(node_content)

    # Assert
    assert properties["objid"] == 42


def test_extract_properties_extracts_parent_property(tmp_path: Path):
    """Test _extract_properties() extracts parent property correctly."""
    # Arrange
    reader = TscnReader(tmp_path / "test.tscn")
    node_content = 'parent="TEAM_1_HQ" instance=ExtResource("SpawnPoint")'

    # Act
    properties = reader._extract_properties(node_content)

    # Assert
    assert properties["parent"] == "TEAM_1_HQ"


def test_extract_properties_returns_empty_dict_with_no_properties(tmp_path: Path):
    """Test _extract_properties() returns empty dict when no properties found."""
    # Arrange
    reader = TscnReader(tmp_path / "test.tscn")
    node_content = "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)"

    # Act
    properties = reader._extract_properties(node_content)

    # Assert
    assert properties == {}


def test_extract_properties_extracts_all_properties_together(tmp_path: Path):
    """Test _extract_properties() extracts all properties together."""
    # Arrange
    reader = TscnReader(tmp_path / "test.tscn")
    node_content = 'parent="." instance=ExtResource("Test")\nTeam = 1\nObjId = 99'

    # Act
    properties = reader._extract_properties(node_content)

    # Assert
    assert properties["team"] == 1
    assert properties["objid"] == 99
    assert properties["parent"] == "."


def test_extract_properties_handles_multidigit_numbers(tmp_path: Path):
    """Test _extract_properties() handles multi-digit numbers correctly."""
    # Arrange
    reader = TscnReader(tmp_path / "test.tscn")
    node_content = "Team = 12\nObjId = 9999"

    # Act
    properties = reader._extract_properties(node_content)

    # Assert
    assert properties["team"] == 12
    assert properties["objid"] == 9999


def test_extract_properties_ignores_unmatched_patterns(tmp_path: Path):
    """Test _extract_properties() ignores content that doesn't match patterns."""
    # Arrange
    reader = TscnReader(tmp_path / "test.tscn")
    node_content = "SomeOtherProperty = 5\nvisible = true\nTeam = 2"

    # Act
    properties = reader._extract_properties(node_content)

    # Assert
    assert properties == {"team": 2}  # Only Team is extracted
    assert "SomeOtherProperty" not in properties


# ============================================================================
# Test TscnReader.get_nodes_by_pattern()
# ============================================================================


def test_get_nodes_by_pattern_returns_matching_nodes(valid_tscn_file: Path):
    """Test get_nodes_by_pattern() returns nodes matching pattern."""
    # Arrange
    reader = TscnReader(valid_tscn_file)
    reader.parse()

    # Act
    spawn_nodes = reader.get_nodes_by_pattern(r"SpawnPoint")

    # Assert
    assert len(spawn_nodes) == 1
    assert spawn_nodes[0].name == "SpawnPoint_1_1"


def test_get_nodes_by_pattern_returns_empty_list_with_no_matches(valid_tscn_file: Path):
    """Test get_nodes_by_pattern() returns empty list when no matches."""
    # Arrange
    reader = TscnReader(valid_tscn_file)
    reader.parse()

    # Act
    result = reader.get_nodes_by_pattern(r"NonExistent")

    # Assert
    assert result == []


def test_get_nodes_by_pattern_supports_regex_patterns(valid_tscn_file: Path):
    """Test get_nodes_by_pattern() supports complex regex patterns."""
    # Arrange
    reader = TscnReader(valid_tscn_file)
    reader.parse()

    # Act
    hq_nodes = reader.get_nodes_by_pattern(r"TEAM_\d+_HQ")

    # Assert
    assert len(hq_nodes) == 2
    node_names = [n.name for n in hq_nodes]
    assert "TEAM_1_HQ" in node_names
    assert "TEAM_2_HQ" in node_names


def test_get_nodes_by_pattern_supports_partial_matches(valid_tscn_file: Path):
    """Test get_nodes_by_pattern() supports partial name matches."""
    # Arrange
    reader = TscnReader(valid_tscn_file)
    reader.parse()

    # Act
    result = reader.get_nodes_by_pattern(r"Capture")

    # Assert
    assert len(result) == 1
    assert result[0].name == "CapturePoint_A"


def test_get_nodes_by_pattern_is_case_sensitive(valid_tscn_file: Path):
    """Test get_nodes_by_pattern() is case sensitive by default."""
    # Arrange
    reader = TscnReader(valid_tscn_file)
    reader.parse()

    # Act
    result = reader.get_nodes_by_pattern(r"team_1_hq")  # lowercase

    # Assert
    assert len(result) == 0  # Should not match TEAM_1_HQ


def test_get_nodes_by_pattern_handles_special_regex_chars(valid_tscn_file: Path):
    """Test get_nodes_by_pattern() handles special regex characters."""
    # Arrange
    reader = TscnReader(valid_tscn_file)
    reader.parse()

    # Act
    result = reader.get_nodes_by_pattern(r"SpawnPoint_1_\d+")

    # Assert
    assert len(result) == 1
    assert result[0].name == "SpawnPoint_1_1"


# ============================================================================
# Test TscnReader.get_nodes_by_team()
# ============================================================================


def test_get_nodes_by_team_returns_team1_nodes(valid_tscn_file: Path):
    """Test get_nodes_by_team() returns Team 1 nodes correctly."""
    # Arrange
    reader = TscnReader(valid_tscn_file)
    reader.parse()

    # Act
    team1_nodes = reader.get_nodes_by_team(1)

    # Assert
    assert len(team1_nodes) == 1
    assert team1_nodes[0].name == "TEAM_1_HQ"
    assert team1_nodes[0].properties["team"] == 1


def test_get_nodes_by_team_returns_team2_nodes(valid_tscn_file: Path):
    """Test get_nodes_by_team() returns Team 2 nodes correctly."""
    # Arrange
    reader = TscnReader(valid_tscn_file)
    reader.parse()

    # Act
    team2_nodes = reader.get_nodes_by_team(2)

    # Assert
    assert len(team2_nodes) == 1
    assert team2_nodes[0].name == "TEAM_2_HQ"
    assert team2_nodes[0].properties["team"] == 2


def test_get_nodes_by_team_returns_empty_list_for_nonexistent_team(valid_tscn_file: Path):
    """Test get_nodes_by_team() returns empty list for nonexistent team."""
    # Arrange
    reader = TscnReader(valid_tscn_file)
    reader.parse()

    # Act
    result = reader.get_nodes_by_team(99)

    # Assert
    assert result == []


def test_get_nodes_by_team_filters_nodes_without_team_property(valid_tscn_file: Path):
    """Test get_nodes_by_team() excludes nodes without team property."""
    # Arrange
    reader = TscnReader(valid_tscn_file)
    reader.parse()

    # Act
    team1_nodes = reader.get_nodes_by_team(1)

    # Assert
    # SpawnPoint_1_1, CapturePoint_A, and StaticObject don't have Team property
    assert all(n.name in ["TEAM_1_HQ"] for n in team1_nodes)


def test_get_nodes_by_team_handles_zero_team(tmp_path: Path):
    """Test get_nodes_by_team() handles team 0 (neutral)."""
    # Arrange
    content = """[gd_scene load_steps=1 format=3]

[node name="NeutralObject" type="Node3D"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)
Team = 0
"""
    neutral_file = tmp_path / "neutral.tscn"
    neutral_file.write_text(content)
    reader = TscnReader(neutral_file)
    reader.parse()

    # Act
    neutral_nodes = reader.get_nodes_by_team(0)

    # Assert
    assert len(neutral_nodes) == 1
    assert neutral_nodes[0].properties["team"] == 0


# ============================================================================
# Test TscnNode Dataclass
# ============================================================================


def test_tscn_node_dataclass_creation():
    """Test TscnNode dataclass can be created correctly."""
    # Arrange & Act
    node = TscnNode(
        name="TestNode",
        position=Vector3(1.0, 2.0, 3.0),
        rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
        properties={"team": 1, "objid": 5},
        raw_content="test content",
    )

    # Assert
    assert node.name == "TestNode"
    assert node.position == Vector3(1.0, 2.0, 3.0)
    assert node.rotation_matrix == [1, 0, 0, 0, 1, 0, 0, 0, 1]
    assert node.properties == {"team": 1, "objid": 5}
    assert node.raw_content == "test content"


def test_tscn_node_dataclass_equality():
    """Test TscnNode dataclass equality comparison."""
    # Arrange
    node1 = TscnNode(
        name="Test",
        position=Vector3(1, 2, 3),
        rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
        properties={},
        raw_content="",
    )
    node2 = TscnNode(
        name="Test",
        position=Vector3(1, 2, 3),
        rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
        properties={},
        raw_content="",
    )

    # Act & Assert
    assert node1 == node2


def test_tscn_node_dataclass_inequality():
    """Test TscnNode dataclass inequality comparison."""
    # Arrange
    node1 = TscnNode(
        name="Test1",
        position=Vector3(1, 2, 3),
        rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
        properties={},
        raw_content="",
    )
    node2 = TscnNode(
        name="Test2",
        position=Vector3(1, 2, 3),
        rotation_matrix=[1, 0, 0, 0, 1, 0, 0, 0, 1],
        properties={},
        raw_content="",
    )

    # Act & Assert
    assert node1 != node2


# ============================================================================
# Test Edge Cases and Integration
# ============================================================================


def test_parse_multiple_times_appends_to_nodes_list(valid_tscn_file: Path):
    """Test calling parse() multiple times appends to nodes list."""
    # Arrange
    reader = TscnReader(valid_tscn_file)

    # Act
    first_parse = reader.parse()
    first_count = len(first_parse)
    second_parse = reader.parse()

    # Assert
    assert first_parse is second_parse  # Same list object
    assert len(second_parse) == first_count * 2  # Nodes are appended
    assert reader.nodes is second_parse  # Reader stores same reference


def test_parse_with_unicode_node_names(tmp_path: Path):
    """Test parse() handles unicode characters in node names."""
    # Arrange
    unicode_content = """[gd_scene load_steps=1 format=3]

[node name="Node_café_🎮" type="Node3D"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)
"""
    unicode_file = tmp_path / "unicode.tscn"
    unicode_file.write_text(unicode_content, encoding="utf-8")
    reader = TscnReader(unicode_file)

    # Act
    nodes = reader.parse()

    # Assert
    assert len(nodes) == 1
    assert "café" in nodes[0].name
    assert "🎮" in nodes[0].name


def test_parse_with_large_coordinate_values(tmp_path: Path):
    """Test parse() handles very large coordinate values."""
    # Arrange
    large_content = """[gd_scene load_steps=1 format=3]

[node name="FarNode" type="Node3D"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 999999.5, -999999.5, 1000000.0)
"""
    large_file = tmp_path / "large.tscn"
    large_file.write_text(large_content)
    reader = TscnReader(large_file)

    # Act
    nodes = reader.parse()

    # Assert
    assert len(nodes) == 1
    assert nodes[0].position == Vector3(999999.5, -999999.5, 1000000.0)


def test_integration_parse_and_filter_by_pattern_and_team(valid_tscn_file: Path):
    """Test integration: parse, then filter by both pattern and team."""
    # Arrange
    reader = TscnReader(valid_tscn_file)

    # Act
    reader.parse()
    hq_nodes = reader.get_nodes_by_pattern(r"TEAM_\d+_HQ")
    team1_hqs = [n for n in hq_nodes if n.properties.get("team") == 1]

    # Assert
    assert len(hq_nodes) == 2
    assert len(team1_hqs) == 1
    assert team1_hqs[0].name == "TEAM_1_HQ"
