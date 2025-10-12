#!/usr/bin/env python3
"""Validation orchestrator that coordinates multiple validators.

Single Responsibility: Only coordinates validators and produces final report.
Does not perform validation logic itself.
"""

from pathlib import Path
from typing import List, Optional, Tuple

from ..core.interfaces import MapData
from ..terrain.terrain_provider import ITerrainProvider
from .map_comparator import MapComparator, MapComparison
from .tscn_reader import TscnNode, TscnReader
from .validators import (
    BoundsValidator,
    CapturePointValidator,
    HeightValidator,
    OrientationValidator,
    PositioningValidator,
    SpawnCountValidator,
    ValidationIssue,
)


class ValidationOrchestrator:
    """Orchestrates validation of conversion.

    Single Responsibility: Only coordinates validators and formats output.
    Dependency Inversion: Depends on abstractions (IValidator, ITerrainProvider).
    """

    def __init__(
        self,
        source_data: MapData,
        output_tscn_path: Path,
        terrain_provider: Optional[ITerrainProvider] = None,
        terrain_size: float = 2048.0,
    ):
        """Initialize orchestrator.

        Args:
            source_data: Parsed source map data
            output_tscn_path: Path to generated .tscn file
            terrain_provider: Optional terrain height provider
            terrain_size: Terrain size in meters
        """
        self.source_data = source_data
        self.output_tscn_path = output_tscn_path
        self.terrain_provider = terrain_provider
        self.terrain_size = terrain_size

        # Components (Dependency Injection)
        self.tscn_reader = TscnReader(output_tscn_path)
        self.map_comparator = MapComparator()

        self.issues: List[ValidationIssue] = []

    def validate(self) -> Tuple[bool, List[ValidationIssue]]:
        """Run all validation checks.

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        print("=" * 70)
        print("CONVERSION VALIDATION")
        print("=" * 70)
        print(f"Source: {self.source_data.metadata.get('source_path', 'Unknown')}")
        print(f"Output: {self.output_tscn_path}")
        print()

        # Step 1: Parse output .tscn
        print("📂 Parsing generated .tscn file...")
        output_nodes = self.tscn_reader.parse()
        print(f"   Found {len(output_nodes)} nodes with transforms")
        print()

        # Step 2: Compare source vs output
        print("🔍 Comparing source vs output...")
        comparison = self.map_comparator.compare(self.source_data, output_nodes)
        print(
            f"   Source: {comparison.source_team1_spawn_count} T1 spawns, "
            f"{comparison.source_team2_spawn_count} T2 spawns, "
            f"{comparison.source_capture_point_count} CPs, "
            f"{comparison.source_object_count} objects"
        )
        print(
            f"   Output: {comparison.output_team1_spawn_count} T1 spawns, "
            f"{comparison.output_team2_spawn_count} T2 spawns, "
            f"{comparison.output_capture_point_count} CPs, "
            f"{len(output_nodes)} nodes"
        )
        print()

        # Step 3: Run validators
        self._run_validators(comparison, output_nodes)

        # Step 4: Report results
        self._print_report()

        # Check if validation passed
        has_errors = any(issue.severity == "error" for issue in self.issues)
        return (not has_errors, self.issues)

    def _run_validators(self, comparison: MapComparison, output_nodes: List[TscnNode]):
        """Run all validators.

        Single Responsibility: Only runs validators and collects issues.
        Open/Closed Principle: Can add new validators without modifying this method.

        Args:
            comparison: MapComparison result
            output_nodes: Parsed output nodes
        """
        # Spawn count validation
        print("🔍 Validating spawn counts...")
        spawn_validator = SpawnCountValidator(comparison)
        spawn_issues = spawn_validator.validate()
        self.issues.extend(spawn_issues)
        if not spawn_issues:
            print(
                f"   ✅ Team 1 spawns: {comparison.output_team1_spawn_count}/{comparison.source_team1_spawn_count}"
            )
            print(
                f"   ✅ Team 2 spawns: {comparison.output_team2_spawn_count}/{comparison.source_team2_spawn_count}"
            )
        else:
            for issue in spawn_issues:
                print(
                    f"   ❌ {issue.message}: expected {issue.expected_value}, got {issue.actual_value}"
                )

        # Capture point validation
        print("🔍 Validating capture points...")
        cp_validator = CapturePointValidator(comparison)
        cp_issues = cp_validator.validate()
        self.issues.extend(cp_issues)
        if not cp_issues:
            print(
                f"   ✅ Capture points: {comparison.output_capture_point_count}/{comparison.source_capture_point_count}"
            )
        else:
            for issue in cp_issues:
                print(
                    f"   ❌ {issue.message}: expected {issue.expected_value}, got {issue.actual_value}"
                )

        # Positioning validation
        print("🔍 Validating coordinate positioning...")
        pos_validator = PositioningValidator(output_nodes)
        pos_issues = pos_validator.validate()
        self.issues.extend(pos_issues)
        if not pos_issues:
            centroid = self.map_comparator.calculate_position_centroid(output_nodes)
            print(f"   ✅ Map centered at ({centroid.x:.1f}, {centroid.z:.1f})")
        else:
            for issue in pos_issues:
                print(
                    f"   ⚠️  {issue.message}: expected {issue.expected_value}, got {issue.actual_value}"
                )

        # Height validation
        if self.terrain_provider:
            print("🔍 Validating heights...")
            height_validator = HeightValidator(output_nodes, self.terrain_provider)
            height_issues = height_validator.validate()
            self.issues.extend(height_issues)

            spawns = [n for n in output_nodes if "SpawnPoint" in n.name]
            error_count = sum(1 for i in height_issues if i.severity in ["error", "warning"])

            if error_count == 0:
                print(f"   ✅ All {len(spawns)} spawn heights validated")
            else:
                print(f"   ⚠️  {error_count}/{len(spawns)} spawns have height issues")
        else:
            print("🔍 Validating heights...")
            print("   ⚠️  No heightmap provided, skipping terrain height validation")

        # Bounds validation
        print("🔍 Validating bounds...")
        max_distance = self.terrain_size / 2 + 200  # Add 200m buffer
        bounds_validator = BoundsValidator(output_nodes, max_distance)
        bounds_issues = bounds_validator.validate()
        self.issues.extend(bounds_issues)
        if not bounds_issues:
            print(f"   ✅ All {len(output_nodes)} objects within bounds")
        else:
            for issue in bounds_issues:
                print(f"   ⚠️  {issue.message}")

        # Orientation validation
        print("🔍 Validating orientations...")
        orient_validator = OrientationValidator(output_nodes)
        orient_issues = orient_validator.validate()
        self.issues.extend(orient_issues)

        identity_count = sum(
            1 for node in output_nodes if orient_validator._is_identity_matrix(node.rotation_matrix)
        )
        rotated_count = len(output_nodes) - identity_count
        print(f"   ℹ️  {identity_count} objects with no rotation, {rotated_count} rotated")

    def _print_report(self):
        """Print validation report.

        Single Responsibility: Only formats and prints report.
        """
        print()
        print("=" * 70)
        print("VALIDATION REPORT")
        print("=" * 70)

        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]
        info = [i for i in self.issues if i.severity == "info"]

        if errors:
            print(f"\n❌ ERRORS ({len(errors)}):")
            for issue in errors:
                print(f"   • {issue.message}")
                if issue.expected_value:
                    print(f"     Expected: {issue.expected_value}, Got: {issue.actual_value}")

        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for issue in warnings:
                print(f"   • {issue.message}")
                if issue.object_name:
                    print(f"     Object: {issue.object_name}")
                if issue.expected_value:
                    print(f"     Expected: {issue.expected_value}, Got: {issue.actual_value}")

        if info:
            print(f"\nℹ️  INFO ({len(info)}):")
            for issue in info:
                print(f"   • {issue.message}")

        if not errors and not warnings:
            print("\n✅ ALL VALIDATION CHECKS PASSED!")

        print("=" * 70)
