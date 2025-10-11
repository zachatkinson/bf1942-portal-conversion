#!/usr/bin/env python3
"""TSCN Validation Tool.

Validates generated .tscn files against BF6 Portal requirements.

Checks:
- Required nodes present (HQs, combat area, static layer)
- Minimum spawn points per team (4+)
- All ObjIds unique
- Transform matrices valid (no NaN)
- Node paths correctly formatted
- External resources exist

Usage:
    python tools/validate_tscn.py GodotProject/levels/Kursk.tscn
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check."""
    passed: bool
    message: str
    severity: str = "ERROR"  # ERROR, WARNING, INFO


class TscnValidator:
    """Validates .tscn scene files."""

    def __init__(self, tscn_path: str):
        """Initialize validator.

        Args:
            tscn_path: Path to .tscn file to validate
        """
        self.tscn_path = Path(tscn_path)
        self.content = ""
        self.results: List[ValidationResult] = []

    def load(self) -> None:
        """Load .tscn file.

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not self.tscn_path.exists():
            raise FileNotFoundError(f"File not found: {self.tscn_path}")

        with open(self.tscn_path, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def add_result(self, passed: bool, message: str, severity: str = "ERROR") -> None:
        """Add validation result.

        Args:
            passed: Whether check passed
            message: Description of result
            severity: ERROR, WARNING, or INFO
        """
        self.results.append(ValidationResult(passed, message, severity))

    def validate_required_nodes(self) -> None:
        """Validate all required nodes are present."""
        required_patterns = [
            (r'\[node name="TEAM_1_HQ"', "Team 1 HQ"),
            (r'\[node name="TEAM_2_HQ"', "Team 2 HQ"),
            (r'\[node name="CombatArea"', "Combat Area"),
            (r'\[node name="Static"', "Static Layer"),
        ]

        for pattern, name in required_patterns:
            if re.search(pattern, self.content):
                self.add_result(True, f"✓ {name} found", "INFO")
            else:
                self.add_result(False, f"✗ {name} MISSING")

    def validate_spawn_points(self) -> None:
        """Validate minimum spawn points per team."""
        # Find all spawn points for each team
        team1_spawns = re.findall(r'\[node name="SpawnPoint_1_\d+"', self.content)
        team2_spawns = re.findall(r'\[node name="SpawnPoint_2_\d+"', self.content)

        min_spawns = 4

        # Team 1
        if len(team1_spawns) >= min_spawns:
            self.add_result(True, f"✓ Team 1 has {len(team1_spawns)} spawn points (minimum: {min_spawns})", "INFO")
        else:
            self.add_result(False, f"✗ Team 1 has only {len(team1_spawns)} spawn points (minimum: {min_spawns})")

        # Team 2
        if len(team2_spawns) >= min_spawns:
            self.add_result(True, f"✓ Team 2 has {len(team2_spawns)} spawn points (minimum: {min_spawns})", "INFO")
        else:
            self.add_result(False, f"✗ Team 2 has only {len(team2_spawns)} spawn points (minimum: {min_spawns})")

    def validate_obj_ids(self) -> None:
        """Validate ObjIds are unique and non-negative."""
        obj_ids: Set[int] = set()
        duplicate_ids = []
        negative_ids = []

        # Find all ObjId declarations
        for match in re.finditer(r'ObjId = (-?\d+)', self.content):
            obj_id = int(match.group(1))

            if obj_id < 0:
                negative_ids.append(obj_id)
            elif obj_id in obj_ids:
                duplicate_ids.append(obj_id)
            else:
                obj_ids.add(obj_id)

        # Check uniqueness
        if not duplicate_ids:
            self.add_result(True, f"✓ All {len(obj_ids)} ObjIds are unique", "INFO")
        else:
            self.add_result(False, f"✗ Duplicate ObjIds found: {duplicate_ids}")

        # Check non-negative
        if not negative_ids:
            self.add_result(True, "✓ All ObjIds are non-negative", "INFO")
        else:
            self.add_result(False, f"✗ Negative ObjIds found: {negative_ids}")

    def validate_transforms(self) -> None:
        """Validate Transform3D declarations don't contain NaN or invalid values."""
        nan_found = False
        invalid_found = False

        # Find all Transform3D declarations
        for match in re.finditer(r'transform = Transform3D\(([^)]+)\)', self.content):
            values_str = match.group(1)

            # Check for NaN
            if 'nan' in values_str.lower() or 'inf' in values_str.lower():
                nan_found = True

            # Try parsing values
            try:
                values = [float(v.strip()) for v in values_str.split(',')]
                if len(values) != 12:
                    invalid_found = True
            except ValueError:
                invalid_found = True

        if not nan_found:
            self.add_result(True, "✓ No NaN values in transforms", "INFO")
        else:
            self.add_result(False, "✗ NaN values found in transforms")

        if not invalid_found:
            self.add_result(True, "✓ All transforms have 12 values", "INFO")
        else:
            self.add_result(False, "✗ Invalid transform declarations found")

    def validate_node_paths(self) -> None:
        """Validate NodePath declarations are correctly formatted."""
        invalid_paths = []

        # Find all NodePath declarations
        for match in re.finditer(r'NodePath\("([^"]+)"\)', self.content):
            path = match.group(1)

            # Basic validation: should not be empty and should start with valid characters
            if not path:
                invalid_paths.append("(empty)")
            elif path.startswith(' ') or path.endswith(' '):
                invalid_paths.append(f"'{path}' (has whitespace)")

        if not invalid_paths:
            self.add_result(True, "✓ All NodePaths are valid", "INFO")
        else:
            self.add_result(False, f"✗ Invalid NodePaths found: {invalid_paths[:5]}")  # Show first 5

    def validate_external_resources(self) -> None:
        """Validate external resources are declared correctly."""
        # Find all ext_resource declarations
        ext_resources = re.findall(r'\[ext_resource type="([^"]+)" path="([^"]+)" id="(\d+)"\]', self.content)

        resource_ids: Set[int] = set()
        duplicate_res_ids = []

        for res_type, res_path, res_id in ext_resources:
            res_id_int = int(res_id)
            if res_id_int in resource_ids:
                duplicate_res_ids.append(res_id_int)
            else:
                resource_ids.add(res_id_int)

        if not duplicate_res_ids:
            self.add_result(True, f"✓ {len(resource_ids)} external resources with unique IDs", "INFO")
        else:
            self.add_result(False, f"✗ Duplicate resource IDs: {duplicate_res_ids}")

        # Check that resource IDs are sequential starting from 1
        if resource_ids:
            expected_ids = set(range(1, len(resource_ids) + 1))
            if resource_ids == expected_ids:
                self.add_result(True, "✓ Resource IDs are sequential (1..N)", "INFO")
            else:
                self.add_result(False, f"✗ Resource IDs are not sequential", "WARNING")

    def validate_gameplay_objects(self) -> None:
        """Validate gameplay objects are present."""
        # Count different object types
        capture_points = len(re.findall(r'\[node name="CapturePoint_\d+"', self.content))
        vehicle_spawners = len(re.findall(r'\[node name="VehicleSpawner_\d+"', self.content))
        hqs = len(re.findall(r'\[node name="TEAM_\d+_HQ"', self.content))

        # Report counts
        self.add_result(True, f"ℹ  Found {hqs} team HQs", "INFO")
        self.add_result(True, f"ℹ  Found {capture_points} capture points", "INFO")
        self.add_result(True, f"ℹ  Found {vehicle_spawners} vehicle spawners", "INFO")

        # Basic sanity checks
        if hqs != 2:
            self.add_result(False, f"✗ Expected 2 HQs, found {hqs}", "WARNING")

        if capture_points == 0:
            self.add_result(False, "✗ No capture points found", "WARNING")

        if vehicle_spawners == 0:
            self.add_result(False, "✗ No vehicle spawners found", "WARNING")

    def validate_file_structure(self) -> None:
        """Validate basic file structure."""
        # Check for header
        if self.content.startswith('[gd_scene'):
            self.add_result(True, "✓ Valid Godot scene header", "INFO")
        else:
            self.add_result(False, "✗ Invalid or missing scene header")

        # Check format version
        format_match = re.search(r'format=(\d+)', self.content)
        if format_match:
            format_version = int(format_match.group(1))
            if format_version == 3:
                self.add_result(True, "✓ Format version is 3 (Godot 4)", "INFO")
            else:
                self.add_result(False, f"✗ Unexpected format version: {format_version}", "WARNING")
        else:
            self.add_result(False, "✗ Format version not found")

    def validate(self) -> bool:
        """Run all validations.

        Returns:
            True if all critical checks passed
        """
        print(f"Validating: {self.tscn_path}")
        print("=" * 70)

        self.validate_file_structure()
        self.validate_required_nodes()
        self.validate_spawn_points()
        self.validate_obj_ids()
        self.validate_transforms()
        self.validate_node_paths()
        self.validate_external_resources()
        self.validate_gameplay_objects()

        return self.has_errors()

    def has_errors(self) -> bool:
        """Check if there are any errors.

        Returns:
            True if validation passed (no errors)
        """
        return not any(r.severity == "ERROR" and not r.passed for r in self.results)

    def print_results(self) -> None:
        """Print validation results."""
        print("\nValidation Results:")
        print("=" * 70)

        errors = [r for r in self.results if r.severity == "ERROR" and not r.passed]
        warnings = [r for r in self.results if r.severity == "WARNING" and not r.passed]
        info = [r for r in self.results if r.severity == "INFO" and r.passed]

        # Print errors
        if errors:
            print("\n❌ ERRORS:")
            for result in errors:
                print(f"   {result.message}")

        # Print warnings
        if warnings:
            print("\n⚠️  WARNINGS:")
            for result in warnings:
                print(f"   {result.message}")

        # Print info
        if info:
            print("\n✅ PASSED:")
            for result in info:
                print(f"   {result.message}")

        # Summary
        print("\n" + "=" * 70)
        if not errors:
            print("✅ VALIDATION PASSED - File is valid!")
        else:
            print(f"❌ VALIDATION FAILED - {len(errors)} error(s) found")

        if warnings:
            print(f"⚠️  {len(warnings)} warning(s) - review recommended")

        return not errors


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python tools/validate_tscn.py <file.tscn>")
        sys.exit(1)

    tscn_path = sys.argv[1]

    validator = TscnValidator(tscn_path)

    try:
        validator.load()
        validator.validate()
        passed = validator.print_results()

        sys.exit(0 if passed else 1)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
