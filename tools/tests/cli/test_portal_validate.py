#!/usr/bin/env python3
"""Tests for portal_validate.py CLI script."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bfportal.cli import (
    EXIT_VALIDATION_ERROR,
)
from portal_validate import (
    PortalMapValidator,
    PortalValidateApp,
    ValidationResult,
    main,
)

# Fixtures


@pytest.fixture
def valid_asset_catalog():
    """Create a valid asset catalog structure."""
    return {
        "AssetTypes": [
            {
                "type": "TestAsset",
                "directory": "Test/Assets",
                "constants": [],
                "properties": [],
                "levelRestrictions": [],
            }
        ]
    }


@pytest.fixture
def valid_tscn_content():
    """Create valid .tscn file content with all required elements."""
    return """[gd_scene load_steps=7 format=3]

[node name="Kursk" type="Node3D"]

[node name="TEAM_1_HQ" parent="." node_paths=PackedStringArray("HQArea", "InfantrySpawns")]
HQArea = NodePath("HQ_Team1")
InfantrySpawns = [NodePath("SpawnPoint_1_1"), NodePath("SpawnPoint_1_2"), NodePath("SpawnPoint_1_3"), NodePath("SpawnPoint_1_4")]

[node name="SpawnPoint_1_1" parent="TEAM_1_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)

[node name="SpawnPoint_1_2" parent="TEAM_1_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)

[node name="SpawnPoint_1_3" parent="TEAM_1_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)

[node name="SpawnPoint_1_4" parent="TEAM_1_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)

[node name="TEAM_2_HQ" parent="." node_paths=PackedStringArray("HQArea", "InfantrySpawns")]
HQArea = NodePath("HQ_Team2")
InfantrySpawns = [NodePath("SpawnPoint_2_1"), NodePath("SpawnPoint_2_2"), NodePath("SpawnPoint_2_3"), NodePath("SpawnPoint_2_4")]

[node name="SpawnPoint_2_1" parent="TEAM_2_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)

[node name="SpawnPoint_2_2" parent="TEAM_2_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)

[node name="SpawnPoint_2_3" parent="TEAM_2_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)

[node name="SpawnPoint_2_4" parent="TEAM_2_HQ"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)

[node name="CombatArea" parent="." node_paths=PackedStringArray("CombatVolume")]
CombatVolume = NodePath("CollisionPolygon3D")

[node name="CollisionPolygon3D" parent="CombatArea"]
points = PackedVector2Array([0, 0, 100, 0, 100, 100, 0, 100])
"""


@pytest.fixture
def minimal_tscn_content():
    """Create minimal .tscn file content for testing failures."""
    return """[gd_scene load_steps=1 format=3]

[node name="EmptyMap" type="Node3D"]
"""


# Tests for ValidationResult dataclass


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_creates_validation_result_with_defaults(self):
        """Test creating ValidationResult with default severity."""
        # Arrange
        check_name = "Test Check"
        passed = True
        message = "Test message"

        # Act
        result = ValidationResult(check_name=check_name, passed=passed, message=message)

        # Assert
        assert result.check_name == check_name
        assert result.passed == passed
        assert result.message == message
        assert result.severity == "error"

    def test_creates_validation_result_with_custom_severity(self):
        """Test creating ValidationResult with custom severity."""
        # Arrange
        check_name = "Test Check"
        passed = False
        message = "Test message"
        severity = "warning"

        # Act
        result = ValidationResult(
            check_name=check_name, passed=passed, message=message, severity=severity
        )

        # Assert
        assert result.check_name == check_name
        assert result.passed == passed
        assert result.message == message
        assert result.severity == severity


# Tests for PortalMapValidator.__init__


class TestPortalMapValidatorInit:
    """Tests for PortalMapValidator.__init__() initialization."""

    def test_initializes_validator_successfully(self, tmp_path: Path, valid_asset_catalog):
        """Test successful validator initialization with valid asset catalog."""
        # Arrange
        catalog_path = tmp_path / "FbExportData" / "asset_types.json"
        catalog_path.parent.mkdir(parents=True)
        catalog_path.write_text(json.dumps(valid_asset_catalog))

        # Act
        validator = PortalMapValidator(tmp_path)

        # Assert
        assert validator.sdk_root == tmp_path
        assert validator.asset_catalog == valid_asset_catalog
        assert validator.results == []

    def test_initializes_with_empty_catalog_when_file_missing(self, tmp_path: Path, capsys):
        """Test initialization with empty catalog when asset_types.json missing."""
        # Arrange
        # No catalog file created

        # Act
        validator = PortalMapValidator(tmp_path)
        captured = capsys.readouterr()

        # Assert
        assert validator.asset_catalog == {"AssetTypes": []}
        assert "Warning: Asset catalog not found" in captured.out


# Tests for PortalMapValidator._load_asset_catalog


class TestLoadAssetCatalog:
    """Tests for PortalMapValidator._load_asset_catalog() method."""

    def test_loads_valid_asset_catalog(self, tmp_path: Path, valid_asset_catalog):
        """Test loading valid asset catalog from file."""
        # Arrange
        catalog_path = tmp_path / "FbExportData" / "asset_types.json"
        catalog_path.parent.mkdir(parents=True)
        catalog_path.write_text(json.dumps(valid_asset_catalog))
        validator = PortalMapValidator(tmp_path)

        # Act
        catalog = validator.asset_catalog

        # Assert
        assert catalog == valid_asset_catalog

    def test_returns_empty_catalog_when_file_missing(self, tmp_path: Path, capsys):
        """Test returns empty catalog when file doesn't exist."""
        # Arrange
        # No catalog file created

        # Act
        validator = PortalMapValidator(tmp_path)
        captured = capsys.readouterr()

        # Assert
        assert validator.asset_catalog == {"AssetTypes": []}
        assert "Warning: Asset catalog not found" in captured.out


# Tests for PortalMapValidator.validate_map


class TestValidateMap:
    """Tests for PortalMapValidator.validate_map() method."""

    def test_validates_map_successfully_with_valid_content(
        self, tmp_path: Path, valid_tscn_content, valid_asset_catalog, capsys
    ):
        """Test successful validation with valid .tscn file."""
        # Arrange
        catalog_path = tmp_path / "FbExportData" / "asset_types.json"
        catalog_path.parent.mkdir(parents=True)
        catalog_path.write_text(json.dumps(valid_asset_catalog))

        tscn_path = tmp_path / "TestMap.tscn"
        tscn_path.write_text(valid_tscn_content)

        validator = PortalMapValidator(tmp_path)

        # Act
        result = validator.validate_map(tscn_path)

        # Assert
        assert result is True
        assert len(validator.results) > 0

    def test_validates_map_fails_with_errors(
        self, tmp_path: Path, minimal_tscn_content, valid_asset_catalog, capsys
    ):
        """Test validation fails with invalid .tscn file."""
        # Arrange
        catalog_path = tmp_path / "FbExportData" / "asset_types.json"
        catalog_path.parent.mkdir(parents=True)
        catalog_path.write_text(json.dumps(valid_asset_catalog))

        tscn_path = tmp_path / "TestMap.tscn"
        tscn_path.write_text(minimal_tscn_content)

        validator = PortalMapValidator(tmp_path)

        # Act
        result = validator.validate_map(tscn_path)

        # Assert
        assert result is False
        errors = [r for r in validator.results if not r.passed and r.severity == "error"]
        assert len(errors) > 0

    def test_clears_previous_results_on_new_validation(
        self, tmp_path: Path, valid_tscn_content, valid_asset_catalog, capsys
    ):
        """Test results are cleared when validating a new map."""
        # Arrange
        catalog_path = tmp_path / "FbExportData" / "asset_types.json"
        catalog_path.parent.mkdir(parents=True)
        catalog_path.write_text(json.dumps(valid_asset_catalog))

        tscn_path = tmp_path / "TestMap.tscn"
        tscn_path.write_text(valid_tscn_content)

        validator = PortalMapValidator(tmp_path)
        validator.results = [ValidationResult("Old", True, "Old result")]

        # Act
        validator.validate_map(tscn_path)

        # Assert
        assert not any(r.message == "Old result" for r in validator.results)


# Tests for PortalMapValidator._validate_structure


class TestValidateStructure:
    """Tests for PortalMapValidator._validate_structure() method."""

    def test_validates_structure_passes_with_valid_format(self, tmp_path: Path):
        """Test structure validation passes with valid Godot format."""
        # Arrange
        content = '[gd_scene load_steps=7 format=3]\n[node name="Root" type="Node3D"]'
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_structure(content)

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 2
        assert any("Scene Format" in r.check_name for r in passed_results)
        assert any("Root Node" in r.check_name for r in passed_results)

    def test_validates_structure_fails_with_invalid_format(self, tmp_path: Path):
        """Test structure validation fails with invalid format."""
        # Arrange
        content = '[gd_scene load_steps=7 format=2]\n[node name="Root" type="Node3D"]'
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_structure(content)

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "error"]
        assert len(errors) >= 1
        assert any("Scene Format" in r.check_name for r in errors)

    def test_validates_structure_fails_with_missing_root_node(self, tmp_path: Path):
        """Test structure validation fails with missing Node3D root."""
        # Arrange
        content = '[gd_scene load_steps=7 format=3]\n[node name="Root" type="Node2D"]'
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_structure(content)

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "error"]
        assert len(errors) >= 1
        assert any("Root Node" in r.check_name for r in errors)


# Tests for PortalMapValidator._validate_hqs


class TestValidateHqs:
    """Tests for PortalMapValidator._validate_hqs() method."""

    def test_validates_hqs_passes_with_two_team_hqs(self, tmp_path: Path):
        """Test HQ validation passes with both team HQs present."""
        # Arrange
        content = """
[node name="TEAM_1_HQ" parent="."]
HQArea = NodePath("HQ_Team1")
[node name="TEAM_2_HQ" parent="."]
HQArea = NodePath("HQ_Team2")
"""
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_hqs(content)

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert any("Team HQs" in r.check_name for r in passed_results)

    def test_validates_hqs_fails_with_only_one_hq(self, tmp_path: Path):
        """Test HQ validation fails with only one HQ."""
        # Arrange
        content = """
[node name="TEAM_1_HQ" parent="."]
HQArea = NodePath("HQ_Team1")
"""
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_hqs(content)

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "error"]
        assert len(errors) >= 1
        assert any("Team HQs" in r.check_name for r in errors)
        assert any("Found only 1 HQ" in r.message for r in errors)

    def test_validates_hqs_warns_on_missing_hq_area_reference(self, tmp_path: Path):
        """Test HQ validation warns when HQArea reference missing."""
        # Arrange
        content = """
[node name="TEAM_1_HQ" parent="."]
[node name="TEAM_2_HQ" parent="."]
HQArea = NodePath("HQ_Team2")
"""
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_hqs(content)

        # Assert
        warnings = [r for r in validator.results if not r.passed and r.severity == "warning"]
        assert len(warnings) >= 1
        assert any("Team 1 HQ Area" in r.check_name for r in warnings)


# Tests for PortalMapValidator._validate_spawns


class TestValidateSpawns:
    """Tests for PortalMapValidator._validate_spawns() method."""

    def test_validates_spawns_passes_with_sufficient_spawns(self, tmp_path: Path):
        """Test spawn validation passes with 4+ spawns per team."""
        # Arrange
        content = """
[node name="SpawnPoint_1_1" parent="."]
[node name="SpawnPoint_1_2" parent="."]
[node name="SpawnPoint_1_3" parent="."]
[node name="SpawnPoint_1_4" parent="."]
[node name="SpawnPoint_2_1" parent="."]
[node name="SpawnPoint_2_2" parent="."]
[node name="SpawnPoint_2_3" parent="."]
[node name="SpawnPoint_2_4" parent="."]
"""
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_spawns(content)

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 2
        assert any("Team 1 Spawns" in r.check_name for r in passed_results)
        assert any("Team 2 Spawns" in r.check_name for r in passed_results)

    def test_validates_spawns_fails_with_insufficient_team1_spawns(self, tmp_path: Path):
        """Test spawn validation fails with < 4 team 1 spawns."""
        # Arrange
        content = """
[node name="SpawnPoint_1_1" parent="."]
[node name="SpawnPoint_1_2" parent="."]
[node name="SpawnPoint_2_1" parent="."]
[node name="SpawnPoint_2_2" parent="."]
[node name="SpawnPoint_2_3" parent="."]
[node name="SpawnPoint_2_4" parent="."]
"""
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_spawns(content)

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "error"]
        assert len(errors) >= 1
        assert any("Team 1 Spawns" in r.check_name for r in errors)
        assert any("only 2 spawn(s)" in r.message for r in errors)

    def test_validates_spawns_fails_with_insufficient_team2_spawns(self, tmp_path: Path):
        """Test spawn validation fails with < 4 team 2 spawns."""
        # Arrange
        content = """
[node name="SpawnPoint_1_1" parent="."]
[node name="SpawnPoint_1_2" parent="."]
[node name="SpawnPoint_1_3" parent="."]
[node name="SpawnPoint_1_4" parent="."]
[node name="SpawnPoint_2_1" parent="."]
"""
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_spawns(content)

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "error"]
        assert len(errors) >= 1
        assert any("Team 2 Spawns" in r.check_name for r in errors)
        assert any("only 1 spawn(s)" in r.message for r in errors)


# Tests for PortalMapValidator._validate_combat_area


class TestValidateCombatArea:
    """Tests for PortalMapValidator._validate_combat_area() method."""

    def test_validates_combat_area_passes_with_complete_definition(self, tmp_path: Path):
        """Test combat area validation passes with complete definition."""
        # Arrange
        content = """
[node name="CombatArea" parent="."]
CombatVolume = NodePath("CollisionPolygon3D")
points = PackedVector2Array([0, 0, 100, 0, 100, 100, 0, 100])
"""
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_combat_area(content)

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 1
        assert any("Combat Area" in r.check_name for r in passed_results)

    def test_validates_combat_area_fails_with_missing_node(self, tmp_path: Path):
        """Test combat area validation fails with missing CombatArea node."""
        # Arrange
        content = '[node name="Root" type="Node3D"]'
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_combat_area(content)

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "error"]
        assert len(errors) >= 1
        assert any("Combat Area" in r.check_name for r in errors)
        assert any("Missing CombatArea node" in r.message for r in errors)

    def test_validates_combat_area_fails_with_missing_volume_reference(self, tmp_path: Path):
        """Test combat area validation fails with missing CombatVolume."""
        # Arrange
        content = '[node name="CombatArea" parent="."]'
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_combat_area(content)

        # Assert
        errors = [r for r in validator.results if not r.passed and r.severity == "error"]
        assert len(errors) >= 1
        assert any("Combat Volume" in r.check_name for r in errors)

    def test_validates_combat_area_warns_on_missing_polygon_points(self, tmp_path: Path):
        """Test combat area validation warns when polygon points missing."""
        # Arrange
        content = """
[node name="CombatArea" parent="."]
CombatVolume = NodePath("CollisionPolygon3D")
"""
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_combat_area(content)

        # Assert
        warnings = [r for r in validator.results if not r.passed and r.severity == "warning"]
        assert len(warnings) >= 1
        assert any("Combat Boundary" in r.check_name for r in warnings)


# Tests for PortalMapValidator._validate_assets


class TestValidateAssets:
    """Tests for PortalMapValidator._validate_assets() method."""

    def test_validates_assets_reports_no_custom_assets(self, tmp_path: Path):
        """Test asset validation reports no custom assets in empty map."""
        # Arrange
        content = """
[node name="TEAM_1_HQ" parent="."]
[node name="SpawnPoint_1_1" parent="."]
"""
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_assets(content)

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 1
        assert any("Assets" in r.check_name for r in passed_results)
        assert any("No custom assets found" in r.message for r in passed_results)

    def test_validates_assets_reports_found_assets(self, tmp_path: Path):
        """Test asset validation reports found custom assets."""
        # Arrange
        content = """
[node name="TEAM_1_HQ" parent="."]
[node name="Building_01" parent="."]
[node name="Tree_Pine_Large" parent="."]
[node name="Rock_Granite_Medium" parent="."]
"""
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_assets(content)

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 1
        assert any("Assets" in r.check_name for r in passed_results)
        assert any("Found 3 asset references" in r.message for r in passed_results)


# Tests for PortalMapValidator._validate_bounds


class TestValidateBounds:
    """Tests for PortalMapValidator._validate_bounds() method."""

    def test_validates_bounds_passes_with_polygon_defined(self, tmp_path: Path):
        """Test bounds validation passes when polygon is defined."""
        # Arrange
        content = "points = PackedVector2Array([0, 0, 100, 0, 100, 100, 0, 100])"
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_bounds(content)

        # Assert
        passed_results = [r for r in validator.results if r.passed]
        assert len(passed_results) >= 1
        assert any("Bounds Check" in r.check_name for r in passed_results)

    def test_validates_bounds_warns_without_polygon(self, tmp_path: Path):
        """Test bounds validation warns when polygon not defined."""
        # Arrange
        content = '[node name="Root" type="Node3D"]'
        validator = PortalMapValidator(tmp_path)

        # Act
        validator._validate_bounds(content)

        # Assert
        warnings = [r for r in validator.results if not r.passed and r.severity == "warning"]
        assert len(warnings) >= 1
        assert any("Bounds Check" in r.check_name for r in warnings)
        assert any("Cannot validate bounds" in r.message for r in warnings)


# Tests for PortalMapValidator._report_results


class TestReportResults:
    """Tests for PortalMapValidator._report_results() method."""

    def test_reports_results_with_errors_and_warnings(self, tmp_path: Path, capsys):
        """Test result reporting with errors and warnings."""
        # Arrange
        validator = PortalMapValidator(tmp_path)
        validator.results = [
            ValidationResult("Error Check", False, "Error message", "error"),
            ValidationResult("Warning Check", False, "Warning message", "warning"),
            ValidationResult("Info Check", True, "Info message", "info"),
        ]

        # Act
        validator._report_results()
        captured = capsys.readouterr()

        # Assert
        assert "ERRORS" in captured.out
        assert "Error Check" in captured.out
        assert "WARNINGS" in captured.out
        assert "Warning Check" in captured.out
        assert "PASSED" in captured.out
        assert "Info Check" in captured.out
        assert "VALIDATION FAILED" in captured.out

    def test_reports_results_with_only_warnings(self, tmp_path: Path, capsys):
        """Test result reporting with only warnings."""
        # Arrange
        validator = PortalMapValidator(tmp_path)
        validator.results = [
            ValidationResult("Warning Check", False, "Warning message", "warning"),
            ValidationResult("Info Check", True, "Info message", "info"),
        ]

        # Act
        validator._report_results()
        captured = capsys.readouterr()

        # Assert
        assert "ERRORS:" not in captured.out
        assert "WARNINGS:" in captured.out
        assert "VALIDATION PASSED WITH WARNINGS" in captured.out

    def test_reports_results_with_all_passed(self, tmp_path: Path, capsys):
        """Test result reporting when all checks passed."""
        # Arrange
        validator = PortalMapValidator(tmp_path)
        validator.results = [
            ValidationResult("Check 1", True, "Passed", "info"),
            ValidationResult("Check 2", True, "Passed", "info"),
        ]

        # Act
        validator._report_results()
        captured = capsys.readouterr()

        # Assert
        assert "ERRORS:" not in captured.out
        assert "WARNINGS:" not in captured.out
        assert "VALIDATION PASSED" in captured.out
        assert "All 2 checks passed" in captured.out


# Tests for PortalValidateApp.parse_args


class TestPortalValidateAppParseArgs:
    """Tests for PortalValidateApp.parse_args() method."""

    def test_parses_args_with_single_map(self):
        """Test argument parsing with single map file."""
        # Arrange
        app = PortalValidateApp()
        test_args = ["portal_validate.py", "TestMap.tscn"]

        # Act
        with patch("sys.argv", test_args):
            args = app.parse_args()

        # Assert
        assert len(args.maps) == 1
        assert args.maps[0] == Path("TestMap.tscn")
        assert args.sdk_root == Path.cwd()
        assert args.strict is False

    def test_parses_args_with_multiple_maps(self):
        """Test argument parsing with multiple map files."""
        # Arrange
        app = PortalValidateApp()
        test_args = ["portal_validate.py", "Map1.tscn", "Map2.tscn", "Map3.tscn"]

        # Act
        with patch("sys.argv", test_args):
            args = app.parse_args()

        # Assert
        assert len(args.maps) == 3
        assert args.maps[0] == Path("Map1.tscn")
        assert args.maps[1] == Path("Map2.tscn")
        assert args.maps[2] == Path("Map3.tscn")

    def test_parses_args_with_custom_sdk_root(self):
        """Test argument parsing with custom SDK root."""
        # Arrange
        app = PortalValidateApp()
        test_args = ["portal_validate.py", "--sdk-root", "/custom/path", "TestMap.tscn"]

        # Act
        with patch("sys.argv", test_args):
            args = app.parse_args()

        # Assert
        assert args.sdk_root == Path("/custom/path")

    def test_parses_args_with_strict_flag(self):
        """Test argument parsing with strict flag."""
        # Arrange
        app = PortalValidateApp()
        test_args = ["portal_validate.py", "--strict", "TestMap.tscn"]

        # Act
        with patch("sys.argv", test_args):
            args = app.parse_args()

        # Assert
        assert args.strict is True


# Tests for PortalValidateApp.run


class TestPortalValidateAppRun:
    """Tests for PortalValidateApp.run() method."""

    def test_run_returns_success_with_valid_map(
        self, tmp_path: Path, valid_tscn_content, valid_asset_catalog, capsys
    ):
        """Test run returns success code with valid map."""
        # Arrange
        catalog_path = tmp_path / "FbExportData" / "asset_types.json"
        catalog_path.parent.mkdir(parents=True)
        catalog_path.write_text(json.dumps(valid_asset_catalog))

        tscn_path = tmp_path / "TestMap.tscn"
        tscn_path.write_text(valid_tscn_content)

        app = PortalValidateApp()
        test_args = ["portal_validate.py", "--sdk-root", str(tmp_path), str(tscn_path)]

        # Act
        with patch("sys.argv", test_args):
            result = app.run()

        # Assert
        assert result == 0

    def test_run_returns_error_with_invalid_map(
        self, tmp_path: Path, minimal_tscn_content, valid_asset_catalog, capsys
    ):
        """Test run returns error code with invalid map."""
        # Arrange
        catalog_path = tmp_path / "FbExportData" / "asset_types.json"
        catalog_path.parent.mkdir(parents=True)
        catalog_path.write_text(json.dumps(valid_asset_catalog))

        tscn_path = tmp_path / "TestMap.tscn"
        tscn_path.write_text(minimal_tscn_content)

        app = PortalValidateApp()
        test_args = ["portal_validate.py", "--sdk-root", str(tmp_path), str(tscn_path)]

        # Act
        with patch("sys.argv", test_args):
            result = app.run()

        # Assert
        assert result == EXIT_VALIDATION_ERROR

    def test_run_returns_error_when_map_not_found(self, tmp_path: Path, capsys):
        """Test run returns error when map file doesn't exist."""
        # Arrange
        catalog_path = tmp_path / "FbExportData" / "asset_types.json"
        catalog_path.parent.mkdir(parents=True)
        catalog_path.write_text(json.dumps({"AssetTypes": []}))

        nonexistent_path = tmp_path / "NonExistent.tscn"

        app = PortalValidateApp()
        test_args = ["portal_validate.py", "--sdk-root", str(tmp_path), str(nonexistent_path)]

        # Act
        with patch("sys.argv", test_args):
            result = app.run()
        captured = capsys.readouterr()

        # Assert
        assert result == EXIT_VALIDATION_ERROR
        assert "Map not found" in captured.out

    def test_run_handles_exception_during_validation(
        self, tmp_path: Path, valid_tscn_content, capsys
    ):
        """Test run handles exception during validation gracefully."""
        # Arrange
        catalog_path = tmp_path / "FbExportData" / "asset_types.json"
        catalog_path.parent.mkdir(parents=True)
        catalog_path.write_text(json.dumps({"AssetTypes": []}))

        tscn_path = tmp_path / "TestMap.tscn"
        tscn_path.write_text(valid_tscn_content)

        app = PortalValidateApp()
        test_args = ["portal_validate.py", "--sdk-root", str(tmp_path), str(tscn_path)]

        # Act
        with (
            patch("sys.argv", test_args),
            patch.object(
                PortalMapValidator, "validate_map", side_effect=RuntimeError("Test error")
            ),
        ):
            result = app.run()
        captured = capsys.readouterr()

        # Assert
        assert result == EXIT_VALIDATION_ERROR
        assert "Error validating" in captured.out

    def test_run_validates_multiple_maps_and_reports_summary(
        self, tmp_path: Path, valid_tscn_content, valid_asset_catalog, capsys
    ):
        """Test run validates multiple maps and reports summary."""
        # Arrange
        catalog_path = tmp_path / "FbExportData" / "asset_types.json"
        catalog_path.parent.mkdir(parents=True)
        catalog_path.write_text(json.dumps(valid_asset_catalog))

        tscn_path1 = tmp_path / "TestMap1.tscn"
        tscn_path1.write_text(valid_tscn_content)

        tscn_path2 = tmp_path / "TestMap2.tscn"
        tscn_path2.write_text(valid_tscn_content)

        app = PortalValidateApp()
        test_args = [
            "portal_validate.py",
            "--sdk-root",
            str(tmp_path),
            str(tscn_path1),
            str(tscn_path2),
        ]

        # Act
        with patch("sys.argv", test_args):
            result = app.run()
        captured = capsys.readouterr()

        # Assert
        assert result == 0
        assert "Overall Summary: 2 map(s) validated" in captured.out
        assert "All maps passed validation" in captured.out

    def test_run_validates_multiple_maps_with_failures(
        self, tmp_path: Path, valid_tscn_content, minimal_tscn_content, valid_asset_catalog, capsys
    ):
        """Test run validates multiple maps with some failures."""
        # Arrange
        catalog_path = tmp_path / "FbExportData" / "asset_types.json"
        catalog_path.parent.mkdir(parents=True)
        catalog_path.write_text(json.dumps(valid_asset_catalog))

        tscn_path1 = tmp_path / "ValidMap.tscn"
        tscn_path1.write_text(valid_tscn_content)

        tscn_path2 = tmp_path / "InvalidMap.tscn"
        tscn_path2.write_text(minimal_tscn_content)

        app = PortalValidateApp()
        test_args = [
            "portal_validate.py",
            "--sdk-root",
            str(tmp_path),
            str(tscn_path1),
            str(tscn_path2),
        ]

        # Act
        with patch("sys.argv", test_args):
            result = app.run()
        captured = capsys.readouterr()

        # Assert
        assert result == EXIT_VALIDATION_ERROR
        assert "Overall Summary: 2 map(s) validated" in captured.out
        assert "Some maps failed validation" in captured.out


# Tests for main() function


class TestMainFunction:
    """Tests for main() CLI entry point."""

    def test_main_calls_app_run_and_exits(self, tmp_path: Path):
        """Test main function calls app.run() and exits."""
        # Arrange
        test_args = ["portal_validate.py", "TestMap.tscn"]

        # Act & Assert
        with (
            patch("sys.argv", test_args),
            patch.object(PortalValidateApp, "run", return_value=0),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 0

    def test_main_exits_with_error_code_on_failure(self, tmp_path: Path):
        """Test main function exits with error code on failure."""
        # Arrange
        test_args = ["portal_validate.py", "TestMap.tscn"]

        # Act & Assert
        with (
            patch("sys.argv", test_args),
            patch.object(PortalValidateApp, "run", return_value=1),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 1
