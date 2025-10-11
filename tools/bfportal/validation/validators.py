#!/usr/bin/env python3
"""Individual validators following Single Responsibility Principle.

Each validator is responsible for validating ONE specific aspect of the conversion.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

from ..core.interfaces import Vector3
from ..terrain.terrain_provider import ITerrainProvider
from .tscn_reader import TscnNode
from .map_comparator import MapComparison


@dataclass
class ValidationIssue:
    """Represents a validation issue found during checking."""
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'positioning', 'height', 'rotation', 'bounds', 'missing'
    message: str
    object_name: str = ""
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None


class IValidator(ABC):
    """Interface for validators.

    Interface Segregation Principle: Each validator implements only what it needs.
    """

    @abstractmethod
    def validate(self) -> List[ValidationIssue]:
        """Run validation and return issues found.

        Returns:
            List of ValidationIssue objects
        """
        pass


class SpawnCountValidator(IValidator):
    """Validates spawn point counts match source.

    Single Responsibility: Only validates spawn counts.
    """

    def __init__(self, comparison: MapComparison):
        """Initialize validator.

        Args:
            comparison: MapComparison with source vs output counts
        """
        self.comparison = comparison

    def validate(self) -> List[ValidationIssue]:
        """Validate spawn counts."""
        issues = []

        # Check Team 1 spawns
        if self.comparison.source_team1_spawn_count != self.comparison.output_team1_spawn_count:
            issues.append(ValidationIssue(
                severity='error',
                category='missing',
                message='Team 1 spawn count mismatch',
                expected_value=str(self.comparison.source_team1_spawn_count),
                actual_value=str(self.comparison.output_team1_spawn_count)
            ))

        # Check Team 2 spawns
        if self.comparison.source_team2_spawn_count != self.comparison.output_team2_spawn_count:
            issues.append(ValidationIssue(
                severity='error',
                category='missing',
                message='Team 2 spawn count mismatch',
                expected_value=str(self.comparison.source_team2_spawn_count),
                actual_value=str(self.comparison.output_team2_spawn_count)
            ))

        return issues


class CapturePointValidator(IValidator):
    """Validates capture point counts.

    Single Responsibility: Only validates capture points.
    """

    def __init__(self, comparison: MapComparison):
        """Initialize validator.

        Args:
            comparison: MapComparison with source vs output counts
        """
        self.comparison = comparison

    def validate(self) -> List[ValidationIssue]:
        """Validate capture point counts."""
        issues = []

        if self.comparison.has_capture_point_mismatch():
            issues.append(ValidationIssue(
                severity='error',
                category='missing',
                message='Capture point count mismatch',
                expected_value=str(self.comparison.source_capture_point_count),
                actual_value=str(self.comparison.output_capture_point_count)
            ))

        return issues


class PositioningValidator(IValidator):
    """Validates coordinate positioning is correct.

    Single Responsibility: Only validates positioning/centering.
    """

    def __init__(self, output_nodes: List[TscnNode], tolerance: float = 50.0):
        """Initialize validator.

        Args:
            output_nodes: List of output nodes
            tolerance: Maximum allowed distance from origin (meters)
        """
        self.output_nodes = output_nodes
        self.tolerance = tolerance

    def validate(self) -> List[ValidationIssue]:
        """Validate map is centered at origin."""
        issues = []

        if not self.output_nodes:
            return issues

        # Calculate centroid
        total_x = sum(node.position.x for node in self.output_nodes)
        total_z = sum(node.position.z for node in self.output_nodes)
        count = len(self.output_nodes)

        avg_x = total_x / count
        avg_z = total_z / count

        # Check if centered
        if abs(avg_x) > self.tolerance or abs(avg_z) > self.tolerance:
            issues.append(ValidationIssue(
                severity='warning',
                category='positioning',
                message='Map not centered at origin',
                expected_value='(~0, ~0)',
                actual_value=f'({avg_x:.1f}, {avg_z:.1f})'
            ))

        return issues


class HeightValidator(IValidator):
    """Validates object heights match terrain.

    Single Responsibility: Only validates heights.
    """

    def __init__(
        self,
        nodes: List[TscnNode],
        terrain_provider: Optional[ITerrainProvider],
        tolerance: float = 2.0,
        expected_offset: float = 1.0
    ):
        """Initialize validator.

        Args:
            nodes: List of nodes to validate
            terrain_provider: Terrain height provider (can be None)
            tolerance: Maximum allowed height difference (meters)
            expected_offset: Expected offset above terrain (meters)
        """
        self.nodes = nodes
        self.terrain_provider = terrain_provider
        self.tolerance = tolerance
        self.expected_offset = expected_offset

    def validate(self) -> List[ValidationIssue]:
        """Validate object heights."""
        issues = []

        if not self.terrain_provider:
            return issues

        # Validate spawn heights
        spawns = [n for n in self.nodes if 'SpawnPoint' in n.name]

        height_errors = 0
        for spawn in spawns:
            pos = spawn.position

            try:
                terrain_height = self.terrain_provider.get_height_at(pos.x, pos.z)
                expected_height = terrain_height + self.expected_offset
                height_diff = abs(pos.y - expected_height)

                if height_diff > self.tolerance:
                    height_errors += 1
                    if height_errors <= 3:  # Only report first 3
                        issues.append(ValidationIssue(
                            severity='warning',
                            category='height',
                            message='Spawn height mismatch',
                            object_name=spawn.name,
                            expected_value=f'{expected_height:.1f}m',
                            actual_value=f'{pos.y:.1f}m'
                        ))
            except Exception:
                # Out of bounds or error - skip
                pass

        return issues


class BoundsValidator(IValidator):
    """Validates all objects are within reasonable bounds.

    Single Responsibility: Only validates bounds.
    """

    def __init__(self, nodes: List[TscnNode], max_distance: float):
        """Initialize validator.

        Args:
            nodes: List of nodes to validate
            max_distance: Maximum allowed distance from origin (meters)
        """
        self.nodes = nodes
        self.max_distance = max_distance

    def validate(self) -> List[ValidationIssue]:
        """Validate object bounds."""
        issues = []

        out_of_bounds = []
        for node in self.nodes:
            pos = node.position
            distance = (pos.x**2 + pos.z**2)**0.5

            if distance > self.max_distance:
                out_of_bounds.append(node.name)

        if out_of_bounds:
            issues.append(ValidationIssue(
                severity='warning',
                category='bounds',
                message=f'{len(out_of_bounds)} objects outside expected bounds',
                actual_value=f'Max distance: {self.max_distance}m'
            ))

        return issues


class OrientationValidator(IValidator):
    """Validates object orientations are reasonable.

    Single Responsibility: Only validates orientation/rotation.
    """

    def __init__(self, nodes: List[TscnNode]):
        """Initialize validator.

        Args:
            nodes: List of nodes to validate
        """
        self.nodes = nodes

    def validate(self) -> List[ValidationIssue]:
        """Validate object orientations."""
        issues = []

        identity_count = 0
        rotated_count = 0

        for node in self.nodes:
            if self._is_identity_matrix(node.rotation_matrix):
                identity_count += 1
            else:
                rotated_count += 1

        # If ALL objects are identity, that might indicate orientation issues
        if rotated_count == 0 and identity_count > 10:
            issues.append(ValidationIssue(
                severity='info',
                category='rotation',
                message='No objects have rotation - verify orientations are correct',
                actual_value=f'{identity_count} objects all have identity rotation'
            ))

        return issues

    def _is_identity_matrix(self, matrix: List[float]) -> bool:
        """Check if rotation matrix is identity.

        Args:
            matrix: 3x3 rotation matrix (9 values)

        Returns:
            True if identity matrix
        """
        if len(matrix) != 9:
            return False

        # Check if it's identity matrix (1,0,0, 0,1,0, 0,0,1)
        return (
            abs(matrix[0] - 1.0) < 0.01 and abs(matrix[4] - 1.0) < 0.01 and
            abs(matrix[8] - 1.0) < 0.01 and
            abs(matrix[1]) < 0.01 and abs(matrix[2]) < 0.01 and
            abs(matrix[3]) < 0.01 and abs(matrix[5]) < 0.01 and
            abs(matrix[6]) < 0.01 and abs(matrix[7]) < 0.01
        )
