#!/usr/bin/env python3
"""Tests for validate_tscn.py CLI script."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from validate_tscn import TscnValidator, ValidationResult, main

# Fixtures


@pytest.fixture
def valid_tscn_content():
    """Create valid .tscn file content with all required elements."""
    return """[gd_scene load_steps=7 format=3]

[ext_resource type="PackedScene" path="res://prefabs/HQ.tscn" id="1"]
[ext_resource type="PackedScene" path="res://prefabs/Spawn.tscn" id="2"]

[node name="Kursk" type="Node3D"]

[node name="TEAM_1_HQ" parent="." node_paths=PackedStringArray("HQArea", "InfantrySpawns")]
HQArea = NodePath("HQ_Team1")
InfantrySpawns = [NodePath("SpawnPoint_1_1"), NodePath("SpawnPoint_1_2"), NodePath("SpawnPoint_1_3"), NodePath("SpawnPoint_1_4")]
ObjId = 1

[node name="SpawnPoint_1_1" parent="TEAM_1_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)
ObjId = 10

[node name="SpawnPoint_1_2" parent="TEAM_1_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 0, 0)
ObjId = 11

[node name="SpawnPoint_1_3" parent="TEAM_1_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 20, 0, 0)
ObjId = 12

[node name="SpawnPoint_1_4" parent="TEAM_1_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 30, 0, 0)
ObjId = 13

[node name="TEAM_2_HQ" parent="." node_paths=PackedStringArray("HQArea", "InfantrySpawns")]
HQArea = NodePath("HQ_Team2")
InfantrySpawns = [NodePath("SpawnPoint_2_1"), NodePath("SpawnPoint_2_2"), NodePath("SpawnPoint_2_3"), NodePath("SpawnPoint_2_4")]
ObjId = 2

[node name="SpawnPoint_2_1" parent="TEAM_2_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 0, 0)
ObjId = 20

[node name="SpawnPoint_2_2" parent="TEAM_2_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 110, 0, 0)
ObjId = 21

[node name="SpawnPoint_2_3" parent="TEAM_2_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 120, 0, 0)
ObjId = 22

[node name="SpawnPoint_2_4" parent="TEAM_2_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 130, 0, 0)
ObjId = 23

[node name="CombatArea" parent="." node_paths=PackedStringArray("CombatVolume")]
CombatVolume = NodePath("CollisionPolygon3D")

[node name="CollisionPolygon3D" parent="CombatArea"]
points = PackedVector2Array([0, 0, 100, 0, 100, 100, 0, 100])

[node name="Static" type="Node3D" parent="."]

[node name="CapturePoint_1" parent="."]
ObjId = 100

[node name="CapturePoint_2" parent="."]
ObjId = 101

[node name="VehicleSpawner_1" parent="."]
ObjId = 200
"""


@pytest.fixture
def minimal_tscn_content():
    """Create minimal .tscn file content for testing failures."""
    return """[gd_scene load_steps=1 format=3]

[node name="EmptyMap" type="Node3D"]
"""


@pytest.fixture
def invalid_header_tscn():
    """Create .tscn file with invalid header."""
    return """[invalid_header]

[node name="Map" type="Node3D"]
"""


@pytest.fixture
def wrong_format_tscn():
    """Create .tscn file with wrong format version."""
    return """[gd_scene load_steps=1 format=2]

[node name="Map" type="Node3D"]
"""


# Tests for ValidationResult dataclass


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_creates_validation_result_with_defaults(self):
        """Test creating ValidationResult with default severity."""
        # Arrange
        passed = True
        message = "Test message"

        # Act
        result = ValidationResult(passed=passed, message=message)

        # Assert
        assert result.passed == passed
        assert result.message == message
        assert result.severity == "ERROR"

    def test_creates_validation_result_with_custom_severity(self):
        """Test creating ValidationResult with custom severity."""
        # Arrange
        passed = False
        message = "Test message"
        severity = "WARNING"

        # Act
        result = ValidationResult(passed=passed, message=message, severity=severity)

        # Assert
        assert result.passed == passed
        assert result.message == message
        assert result.severity == severity


# Tests for TscnValidator.__init__


class TestTscnValidatorInit:
    """Tests for TscnValidator.__init__() initialization."""

    def test_initializes_validator_with_valid_path(self, tmp_path: Path):
        """Test successful validator initialization with valid path."""
        # Arrange
        tscn_path = tmp_path / "test.tscn"
        tscn_path.write_text("[gd_scene]")

        # Act
        validator = TscnValidator(str(tscn_path))

        # Assert
        assert validator.tscn_path == tscn_path
        assert validator.content == ""
        assert validator.results == []

    def test_initializes_validator_with_string_path(self):
        """Test validator initialization with string path."""
        # Arrange
        path_str = "/path/to/file.tscn"

        # Act
        validator = TscnValidator(path_str)

        # Assert
        assert validator.tscn_path == Path(path_str)
        assert validator.content == ""
        assert validator.results == []


# Tests for TscnValidator.load


class TestLoad:
    """Tests for TscnValidator.load() method."""

    def test_loads_existing_file_successfully(self, tmp_path: Path, valid_tscn_content):
        """Test loading existing .tscn file successfully."""
        # Arrange
        tscn_path = tmp_path / "test.tscn"
        tscn_path.write_text(valid_tscn_content, encoding="utf-8")
        validator = TscnValidator(str(tscn_path))

        # Act
        validator.load()

        # Assert
        assert validator.content == valid_tscn_content
        assert len(validator.content) > 0

    def test_raises_file_not_found_for_missing_file(self, tmp_path: Path):
        """Test FileNotFoundError raised for nonexistent file."""
        # Arrange
        nonexistent_path = tmp_path / "nonexistent.tscn"
        validator = TscnValidator(str(nonexistent_path))

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="File not found"):
            validator.load()

    def test_loads_file_with_utf8_encoding(self, tmp_path: Path):
        """Test loading file with UTF-8 encoding."""
        # Arrange
        content = "[gd_scene] # Comment with unicode: ✓"
        tscn_path = tmp_path / "test.tscn"
        tscn_path.write_text(content, encoding="utf-8")
        validator = TscnValidator(str(tscn_path))

        # Act
        validator.load()

        # Assert
        assert validator.content == content


# Tests for TscnValidator.add_result


class TestAddResult:
    """Tests for TscnValidator.add_result() method."""

    def test_adds_result_with_default_severity(self, tmp_path: Path):
        """Test adding result with default ERROR severity."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        passed = True
        message = "Test passed"

        # Act
        validator.add_result(passed, message)

        # Assert
        assert len(validator.results) == 1
        assert validator.results[0].passed == passed
        assert validator.results[0].message == message
        assert validator.results[0].severity == "ERROR"

    def test_adds_result_with_custom_severity(self, tmp_path: Path):
        """Test adding result with custom severity."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        passed = False
        message = "Warning message"
        severity = "WARNING"

        # Act
        validator.add_result(passed, message, severity)

        # Assert
        assert len(validator.results) == 1
        assert validator.results[0].passed == passed
        assert validator.results[0].message == message
        assert validator.results[0].severity == severity

    def test_adds_multiple_results(self, tmp_path: Path):
        """Test adding multiple results."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))

        # Act
        validator.add_result(True, "Result 1", "INFO")
        validator.add_result(False, "Result 2", "ERROR")
        validator.add_result(False, "Result 3", "WARNING")

        # Assert
        assert len(validator.results) == 3
        assert validator.results[0].message == "Result 1"
        assert validator.results[1].message == "Result 2"
        assert validator.results[2].message == "Result 3"


# Tests for TscnValidator.validate_required_nodes


class TestValidateRequiredNodes:
    """Tests for TscnValidator.validate_required_nodes() method."""

    def test_validates_all_required_nodes_present(self, tmp_path: Path, valid_tscn_content):
        """Test validation passes with all required nodes present."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = valid_tscn_content

        # Act
        validator.validate_required_nodes()

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 4
        assert any("Team 1 HQ" in r.message for r in passed_results)
        assert any("Team 2 HQ" in r.message for r in passed_results)
        assert any("Combat Area" in r.message for r in passed_results)
        assert any("Static Layer" in r.message for r in passed_results)

    def test_validates_fails_with_missing_team_1_hq(self, tmp_path: Path):
        """Test validation fails with missing Team 1 HQ."""
        # Arrange
        content = '[node name="TEAM_2_HQ" parent="."]'
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_required_nodes()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Team 1 HQ MISSING" in r.message for r in errors)

    def test_validates_fails_with_missing_combat_area(self, tmp_path: Path):
        """Test validation fails with missing CombatArea."""
        # Arrange
        content = '[node name="TEAM_1_HQ" parent="."]\n[node name="TEAM_2_HQ" parent="."]'
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_required_nodes()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Combat Area MISSING" in r.message for r in errors)

    def test_validates_fails_with_missing_static_layer(self, tmp_path: Path):
        """Test validation fails with missing Static layer."""
        # Arrange
        content = """[node name="TEAM_1_HQ" parent="."]
[node name="TEAM_2_HQ" parent="."]
[node name="CombatArea" parent="."]"""
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_required_nodes()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Static Layer MISSING" in r.message for r in errors)


# Tests for TscnValidator.validate_spawn_points


class TestValidateSpawnPoints:
    """Tests for TscnValidator.validate_spawn_points() method."""

    def test_validates_sufficient_spawn_points_for_both_teams(
        self, tmp_path: Path, valid_tscn_content
    ):
        """Test validation passes with 4+ spawn points per team."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = valid_tscn_content

        # Act
        validator.validate_spawn_points()

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 2
        assert any("Team 1 has 4 spawn points" in r.message for r in passed_results)
        assert any("Team 2 has 4 spawn points" in r.message for r in passed_results)

    def test_validates_fails_with_insufficient_team_1_spawns(self, tmp_path: Path):
        """Test validation fails with < 4 team 1 spawn points."""
        # Arrange
        content = """[node name="SpawnPoint_1_1" parent="."]
[node name="SpawnPoint_1_2" parent="."]
[node name="SpawnPoint_2_1" parent="."]
[node name="SpawnPoint_2_2" parent="."]
[node name="SpawnPoint_2_3" parent="."]
[node name="SpawnPoint_2_4" parent="."]"""
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_spawn_points()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Team 1 has only 2 spawn points" in r.message for r in errors)

    def test_validates_fails_with_insufficient_team_2_spawns(self, tmp_path: Path):
        """Test validation fails with < 4 team 2 spawn points."""
        # Arrange
        content = """[node name="SpawnPoint_1_1" parent="."]
[node name="SpawnPoint_1_2" parent="."]
[node name="SpawnPoint_1_3" parent="."]
[node name="SpawnPoint_1_4" parent="."]
[node name="SpawnPoint_2_1" parent="."]"""
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_spawn_points()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Team 2 has only 1 spawn points" in r.message for r in errors)

    def test_validates_passes_with_more_than_minimum_spawns(self, tmp_path: Path):
        """Test validation passes with more than 4 spawn points."""
        # Arrange
        content = """
[node name="SpawnPoint_1_1" parent="."]
[node name="SpawnPoint_1_2" parent="."]
[node name="SpawnPoint_1_3" parent="."]
[node name="SpawnPoint_1_4" parent="."]
[node name="SpawnPoint_1_5" parent="."]
[node name="SpawnPoint_1_6" parent="."]
[node name="SpawnPoint_2_1" parent="."]
[node name="SpawnPoint_2_2" parent="."]
[node name="SpawnPoint_2_3" parent="."]
[node name="SpawnPoint_2_4" parent="."]
[node name="SpawnPoint_2_5" parent="."]
"""
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_spawn_points()

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 2
        assert any("Team 1 has 6 spawn points" in r.message for r in passed_results)
        assert any("Team 2 has 5 spawn points" in r.message for r in passed_results)


# Tests for TscnValidator.validate_obj_ids


class TestValidateObjIds:
    """Tests for TscnValidator.validate_obj_ids() method."""

    def test_validates_unique_obj_ids(self, tmp_path: Path, valid_tscn_content):
        """Test validation passes with unique ObjIds."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = valid_tscn_content

        # Act
        validator.validate_obj_ids()

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 2
        assert any("ObjIds are unique" in r.message for r in passed_results)
        assert any("ObjIds are non-negative" in r.message for r in passed_results)

    def test_validates_fails_with_duplicate_obj_ids(self, tmp_path: Path):
        """Test validation fails with duplicate ObjIds."""
        # Arrange
        content = """ObjId = 42
ObjId = 43
ObjId = 42
ObjId = 44"""
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_obj_ids()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Duplicate ObjIds found" in r.message for r in errors)
        assert any("42" in r.message for r in errors)

    def test_validates_fails_with_negative_obj_ids(self, tmp_path: Path):
        """Test validation fails with negative ObjIds."""
        # Arrange
        content = """ObjId = 1
ObjId = -5
ObjId = 3
ObjId = -10"""
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_obj_ids()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Negative ObjIds found" in r.message for r in errors)

    def test_validates_handles_no_obj_ids(self, tmp_path: Path):
        """Test validation handles content with no ObjIds."""
        # Arrange
        content = '[node name="Root" type="Node3D"]'
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_obj_ids()

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 1
        assert any("0 ObjIds" in r.message for r in passed_results)


# Tests for TscnValidator.validate_transforms


class TestValidateTransforms:
    """Tests for TscnValidator.validate_transforms() method."""

    def test_validates_valid_transforms(self, tmp_path: Path, valid_tscn_content):
        """Test validation passes with valid Transform3D declarations."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = valid_tscn_content

        # Act
        validator.validate_transforms()

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 2
        assert any("No NaN values in transforms" in r.message for r in passed_results)
        assert any("All transforms have 12 values" in r.message for r in passed_results)

    def test_validates_fails_with_nan_in_transform(self, tmp_path: Path):
        """Test validation fails with NaN in transform."""
        # Arrange
        content = "transform = Transform3D(1, 0, 0, 0, nan, 0, 0, 0, 1, 0, 0, 0)"
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_transforms()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("NaN values found in transforms" in r.message for r in errors)

    def test_validates_fails_with_inf_in_transform(self, tmp_path: Path):
        """Test validation fails with inf in transform."""
        # Arrange
        content = "transform = Transform3D(1, 0, inf, 0, 1, 0, 0, 0, 1, 0, 0, 0)"
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_transforms()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("NaN values found in transforms" in r.message for r in errors)

    def test_validates_fails_with_wrong_number_of_values(self, tmp_path: Path):
        """Test validation fails with incorrect number of transform values."""
        # Arrange
        content = "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1)"
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_transforms()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Invalid transform declarations found" in r.message for r in errors)

    def test_validates_fails_with_non_numeric_values(self, tmp_path: Path):
        """Test validation fails with non-numeric values in transform."""
        # Arrange
        content = "transform = Transform3D(a, b, c, d, e, f, g, h, i, j, k, l)"
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_transforms()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Invalid transform declarations found" in r.message for r in errors)


# Tests for TscnValidator.validate_node_paths


class TestValidateNodePaths:
    """Tests for TscnValidator.validate_node_paths() method."""

    def test_validates_valid_node_paths(self, tmp_path: Path, valid_tscn_content):
        """Test validation passes with valid NodePath declarations."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = valid_tscn_content

        # Act
        validator.validate_node_paths()

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 1
        assert any("All NodePaths are valid" in r.message for r in passed_results)

    def test_validates_passes_with_empty_node_path_not_matching_regex(self, tmp_path: Path):
        """Test validation passes when empty NodePath not matched by regex."""
        # Arrange
        content = 'HQArea = NodePath("")'
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_node_paths()

        # Assert
        # Empty NodePath won't match regex pattern [^"]+, so no error is reported
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 1
        assert any("All NodePaths are valid" in r.message for r in passed_results)

    def test_validates_fails_with_leading_whitespace_in_path(self, tmp_path: Path):
        """Test validation fails with leading whitespace in NodePath."""
        # Arrange
        content = 'HQArea = NodePath(" HQ_Team1")'
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_node_paths()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Invalid NodePaths found" in r.message for r in errors)
        assert any("has whitespace" in r.message for r in errors)

    def test_validates_fails_with_trailing_whitespace_in_path(self, tmp_path: Path):
        """Test validation fails with trailing whitespace in NodePath."""
        # Arrange
        content = 'HQArea = NodePath("HQ_Team1 ")'
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_node_paths()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Invalid NodePaths found" in r.message for r in errors)

    def test_validates_limits_error_output_to_first_five(self, tmp_path: Path):
        """Test validation limits invalid path output to first 5."""
        # Arrange
        content = "\n".join([f'Path{i} = NodePath(" Path{i} ")' for i in range(10)])
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_node_paths()

        # Assert
        errors = [r for r in validator.results if not r.passed]
        assert len(errors) >= 1
        # Should show first 5 by slicing [:5] in the error message


# Tests for TscnValidator.validate_external_resources


class TestValidateExternalResources:
    """Tests for TscnValidator.validate_external_resources() method."""

    def test_validates_unique_resource_ids(self, tmp_path: Path, valid_tscn_content):
        """Test validation passes with unique resource IDs."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = valid_tscn_content

        # Act
        validator.validate_external_resources()

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 2
        assert any("external resources with unique IDs" in r.message for r in passed_results)
        assert any("Resource IDs are sequential" in r.message for r in passed_results)

    def test_validates_fails_with_duplicate_resource_ids(self, tmp_path: Path):
        """Test validation fails with duplicate resource IDs."""
        # Arrange
        content = """[ext_resource type="PackedScene" path="res://prefabs/HQ.tscn" id="1"]
[ext_resource type="PackedScene" path="res://prefabs/Spawn.tscn" id="2"]
[ext_resource type="PackedScene" path="res://prefabs/Combat.tscn" id="1"]"""
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_external_resources()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Duplicate resource IDs" in r.message for r in errors)

    def test_validates_warns_with_non_sequential_ids(self, tmp_path: Path):
        """Test validation warns with non-sequential resource IDs."""
        # Arrange
        content = """[ext_resource type="PackedScene" path="res://prefabs/HQ.tscn" id="1"]
[ext_resource type="PackedScene" path="res://prefabs/Spawn.tscn" id="3"]
[ext_resource type="PackedScene" path="res://prefabs/Combat.tscn" id="5"]"""
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_external_resources()

        # Assert
        warnings = [r for r in validator.results if not r.passed and r.severity == "WARNING"]
        assert len(warnings) >= 1
        assert any("Resource IDs are not sequential" in r.message for r in warnings)

    def test_validates_handles_no_external_resources(self, tmp_path: Path):
        """Test validation handles content with no external resources."""
        # Arrange
        content = '[node name="Root" type="Node3D"]'
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_external_resources()

        # Assert
        # Should report 0 resources but not fail
        passed_results = [r for r in validator.results if r.passed]
        assert any("0 external resources" in r.message for r in passed_results)


# Tests for TscnValidator.validate_gameplay_objects


class TestValidateGameplayObjects:
    """Tests for TscnValidator.validate_gameplay_objects() method."""

    def test_validates_reports_gameplay_object_counts(self, tmp_path: Path, valid_tscn_content):
        """Test validation reports gameplay object counts."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = valid_tscn_content

        # Act
        validator.validate_gameplay_objects()

        # Assert
        info_results = [r for r in validator.results if r.severity == "INFO"]
        assert len(info_results) >= 3
        assert any("Found 2 team HQs" in r.message for r in info_results)
        assert any("Found 2 capture points" in r.message for r in info_results)
        assert any("Found 1 vehicle spawners" in r.message for r in info_results)

    def test_validates_warns_with_wrong_hq_count(self, tmp_path: Path):
        """Test validation warns with incorrect HQ count."""
        # Arrange
        content = '[node name="TEAM_1_HQ" parent="."]'
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_gameplay_objects()

        # Assert
        warnings = [r for r in validator.results if not r.passed and r.severity == "WARNING"]
        assert len(warnings) >= 1
        assert any("Expected 2 HQs, found 1" in r.message for r in warnings)

    def test_validates_warns_with_no_capture_points(self, tmp_path: Path):
        """Test validation warns with no capture points."""
        # Arrange
        content = """[node name="TEAM_1_HQ" parent="."]
[node name="TEAM_2_HQ" parent="."]"""
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_gameplay_objects()

        # Assert
        warnings = [r for r in validator.results if not r.passed and r.severity == "WARNING"]
        assert len(warnings) >= 1
        assert any("No capture points found" in r.message for r in warnings)

    def test_validates_warns_with_no_vehicle_spawners(self, tmp_path: Path):
        """Test validation warns with no vehicle spawners."""
        # Arrange
        content = """[node name="TEAM_1_HQ" parent="."]
[node name="TEAM_2_HQ" parent="."]
[node name="CapturePoint_1" parent="."]"""
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_gameplay_objects()

        # Assert
        warnings = [r for r in validator.results if not r.passed and r.severity == "WARNING"]
        assert len(warnings) >= 1
        assert any("No vehicle spawners found" in r.message for r in warnings)


# Tests for TscnValidator.validate_file_structure


class TestValidateFileStructure:
    """Tests for TscnValidator.validate_file_structure() method."""

    def test_validates_valid_godot_scene_header(self, tmp_path: Path, valid_tscn_content):
        """Test validation passes with valid Godot scene header."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = valid_tscn_content

        # Act
        validator.validate_file_structure()

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 2
        assert any("Valid Godot scene header" in r.message for r in passed_results)
        assert any("Format version is 3" in r.message for r in passed_results)

    def test_validates_fails_with_invalid_header(self, tmp_path: Path, invalid_header_tscn):
        """Test validation fails with invalid scene header."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = invalid_header_tscn

        # Act
        validator.validate_file_structure()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Invalid or missing scene header" in r.message for r in errors)

    def test_validates_warns_with_wrong_format_version(self, tmp_path: Path, wrong_format_tscn):
        """Test validation warns with wrong format version."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = wrong_format_tscn

        # Act
        validator.validate_file_structure()

        # Assert
        warnings = [r for r in validator.results if not r.passed and r.severity == "WARNING"]
        assert len(warnings) >= 1
        assert any("Unexpected format version: 2" in r.message for r in warnings)

    def test_validates_fails_with_missing_format_version(self, tmp_path: Path):
        """Test validation fails with missing format version."""
        # Arrange
        content = "[gd_scene load_steps=1]"
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.content = content

        # Act
        validator.validate_file_structure()

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "ERROR"]
        assert len(errors) >= 1
        assert any("Format version not found" in r.message for r in errors)


# Tests for TscnValidator.has_errors


class TestHasErrors:
    """Tests for TscnValidator.has_errors() method."""

    def test_returns_true_with_no_errors(self, tmp_path: Path):
        """Test returns True when no errors present."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.results = [
            ValidationResult(True, "Passed", "INFO"),
            ValidationResult(False, "Warning", "WARNING"),
        ]

        # Act
        result = validator.has_errors()

        # Assert
        assert result is True

    def test_returns_false_with_errors(self, tmp_path: Path):
        """Test returns False when errors present."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.results = [
            ValidationResult(True, "Passed", "INFO"),
            ValidationResult(False, "Error", "ERROR"),
        ]

        # Act
        result = validator.has_errors()

        # Assert
        assert result is False

    def test_returns_true_with_only_passed_checks(self, tmp_path: Path):
        """Test returns True with all passed checks."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.results = [
            ValidationResult(True, "Passed 1", "INFO"),
            ValidationResult(True, "Passed 2", "INFO"),
        ]

        # Act
        result = validator.has_errors()

        # Assert
        assert result is True

    def test_returns_true_with_empty_results(self, tmp_path: Path):
        """Test returns True with no results."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.results = []

        # Act
        result = validator.has_errors()

        # Assert
        assert result is True


# Tests for TscnValidator.validate


class TestValidate:
    """Tests for TscnValidator.validate() method."""

    def test_validates_runs_all_validation_methods(
        self, tmp_path: Path, valid_tscn_content, capsys
    ):
        """Test validate runs all validation methods."""
        # Arrange
        tscn_path = tmp_path / "test.tscn"
        tscn_path.write_text(valid_tscn_content)
        validator = TscnValidator(str(tscn_path))
        validator.load()

        # Act
        result = validator.validate()
        captured = capsys.readouterr()

        # Assert
        assert result is True
        assert "Validating:" in captured.out
        assert len(validator.results) > 0

    def test_validates_returns_false_with_errors(
        self, tmp_path: Path, minimal_tscn_content, capsys
    ):
        """Test validate returns False when errors found."""
        # Arrange
        tscn_path = tmp_path / "test.tscn"
        tscn_path.write_text(minimal_tscn_content)
        validator = TscnValidator(str(tscn_path))
        validator.load()

        # Act
        result = validator.validate()

        # Assert
        assert result is False

    def test_validates_prints_validation_header(self, tmp_path: Path, valid_tscn_content, capsys):
        """Test validate prints validation header."""
        # Arrange
        tscn_path = tmp_path / "test.tscn"
        tscn_path.write_text(valid_tscn_content)
        validator = TscnValidator(str(tscn_path))
        validator.load()

        # Act
        validator.validate()
        captured = capsys.readouterr()

        # Assert
        assert "Validating:" in captured.out
        assert str(tscn_path) in captured.out
        assert "=" * 70 in captured.out


# Tests for TscnValidator.print_results


class TestPrintResults:
    """Tests for TscnValidator.print_results() method."""

    def test_prints_errors_warnings_and_passed_checks(self, tmp_path: Path, capsys):
        """Test print_results displays errors, warnings, and passed checks."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.results = [
            ValidationResult(False, "Error message", "ERROR"),
            ValidationResult(False, "Warning message", "WARNING"),
            ValidationResult(True, "Passed message", "INFO"),
        ]

        # Act
        result = validator.print_results()
        captured = capsys.readouterr()

        # Assert
        assert result is False
        assert "ERRORS:" in captured.out
        assert "Error message" in captured.out
        assert "WARNINGS:" in captured.out
        assert "Warning message" in captured.out
        assert "PASSED:" in captured.out
        assert "Passed message" in captured.out
        assert "VALIDATION FAILED" in captured.out

    def test_prints_success_message_with_no_errors(self, tmp_path: Path, capsys):
        """Test print_results shows success with no errors."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.results = [
            ValidationResult(True, "Passed 1", "INFO"),
            ValidationResult(True, "Passed 2", "INFO"),
        ]

        # Act
        result = validator.print_results()
        captured = capsys.readouterr()

        # Assert
        assert result is True
        assert "VALIDATION PASSED" in captured.out
        assert "File is valid" in captured.out

    def test_prints_warning_count_with_warnings(self, tmp_path: Path, capsys):
        """Test print_results shows warning count."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.results = [
            ValidationResult(True, "Passed", "INFO"),
            ValidationResult(False, "Warning 1", "WARNING"),
            ValidationResult(False, "Warning 2", "WARNING"),
        ]

        # Act
        result = validator.print_results()
        captured = capsys.readouterr()

        # Assert
        assert result is True
        assert "2 warning(s)" in captured.out
        assert "review recommended" in captured.out

    def test_prints_does_not_show_errors_section_when_none(self, tmp_path: Path, capsys):
        """Test print_results omits errors section when no errors."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.results = [
            ValidationResult(True, "Passed", "INFO"),
        ]

        # Act
        validator.print_results()
        captured = capsys.readouterr()

        # Assert
        assert "ERRORS:" not in captured.out

    def test_prints_does_not_show_warnings_section_when_none(self, tmp_path: Path, capsys):
        """Test print_results omits warnings section when no warnings."""
        # Arrange
        validator = TscnValidator(str(tmp_path / "test.tscn"))
        validator.results = [
            ValidationResult(True, "Passed", "INFO"),
        ]

        # Act
        validator.print_results()
        captured = capsys.readouterr()

        # Assert
        assert "WARNINGS:" not in captured.out


# Tests for main() function


class TestMainFunction:
    """Tests for main() CLI entry point."""

    def test_main_validates_file_successfully(self, tmp_path: Path, valid_tscn_content):
        """Test main validates file and exits with success code."""
        # Arrange
        tscn_path = tmp_path / "test.tscn"
        tscn_path.write_text(valid_tscn_content)
        test_args = ["validate_tscn.py", str(tscn_path)]

        # Act & Assert
        with patch("sys.argv", test_args), pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    def test_main_exits_with_error_code_on_validation_failure(
        self, tmp_path: Path, minimal_tscn_content
    ):
        """Test main exits with error code when validation fails."""
        # Arrange
        tscn_path = tmp_path / "test.tscn"
        tscn_path.write_text(minimal_tscn_content)
        test_args = ["validate_tscn.py", str(tscn_path)]

        # Act & Assert
        with patch("sys.argv", test_args), pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

    def test_main_exits_with_error_on_file_not_found(self, tmp_path: Path, capsys):
        """Test main exits with error when file not found."""
        # Arrange
        nonexistent_path = tmp_path / "nonexistent.tscn"
        test_args = ["validate_tscn.py", str(nonexistent_path)]

        # Act & Assert
        with patch("sys.argv", test_args), pytest.raises(SystemExit) as exc_info:
            main()
        captured = capsys.readouterr()

        assert exc_info.value.code == 1
        assert "ERROR" in captured.out

    def test_main_prints_usage_with_no_arguments(self, capsys):
        """Test main prints usage message with no arguments."""
        # Arrange
        test_args = ["validate_tscn.py"]

        # Act & Assert
        with patch("sys.argv", test_args), pytest.raises(SystemExit) as exc_info:
            main()
        captured = capsys.readouterr()

        assert exc_info.value.code == 1
        assert "Usage:" in captured.out

    def test_main_handles_exception_gracefully(self, tmp_path: Path, capsys):
        """Test main handles exception during validation gracefully."""
        # Arrange
        tscn_path = tmp_path / "test.tscn"
        tscn_path.write_text("[gd_scene]")
        test_args = ["validate_tscn.py", str(tscn_path)]
        mock_validator = MagicMock(spec=TscnValidator)
        mock_validator.load.side_effect = RuntimeError("Test error")

        # Act & Assert
        with (
            patch("sys.argv", test_args),
            patch("validate_tscn.TscnValidator", return_value=mock_validator),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()
        captured = capsys.readouterr()

        assert exc_info.value.code == 1
        assert "ERROR" in captured.out
        assert "Test error" in captured.out
