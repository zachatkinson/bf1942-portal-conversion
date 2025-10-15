#!/usr/bin/env python3
"""Tests for orientation detection and matching."""

import sys
from pathlib import Path

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from bfportal.orientation import Orientation, OrientationMatcher
from bfportal.orientation.interfaces import OrientationAnalysis
from bfportal.orientation.orientation_matcher import RotationResult


class TestOrientation:
    """Tests for Orientation enum."""

    def test_orientation_has_north_south(self):
        """Test Orientation enum has NORTH_SOUTH value."""
        # Arrange & Act
        orientation = Orientation.NORTH_SOUTH

        # Assert
        assert orientation.value == "north_south"

    def test_orientation_has_east_west(self):
        """Test Orientation enum has EAST_WEST value."""
        # Arrange & Act
        orientation = Orientation.EAST_WEST

        # Assert
        assert orientation.value == "east_west"

    def test_orientation_has_square(self):
        """Test Orientation enum has SQUARE value."""
        # Arrange & Act
        orientation = Orientation.SQUARE

        # Assert
        assert orientation.value == "square"


class TestOrientationAnalysis:
    """Tests for OrientationAnalysis dataclass."""

    def test_creates_analysis_with_all_fields(self):
        """Test creating OrientationAnalysis with all fields."""
        # Arrange & Act
        analysis = OrientationAnalysis(
            orientation=Orientation.NORTH_SOUTH,
            width_x=1000.0,
            depth_z=2000.0,
            ratio=2.0,
            confidence="high",
        )

        # Assert
        assert analysis.orientation == Orientation.NORTH_SOUTH
        assert analysis.width_x == 1000.0
        assert analysis.depth_z == 2000.0
        assert analysis.ratio == 2.0
        assert analysis.confidence == "high"


class TestRotationResult:
    """Tests for RotationResult dataclass."""

    def test_creates_rotation_result_with_all_fields(self):
        """Test creating RotationResult with all fields."""
        # Arrange & Act
        result = RotationResult(
            rotation_degrees=90,
            rotation_needed=True,
            source_orientation=Orientation.NORTH_SOUTH,
            destination_orientation=Orientation.EAST_WEST,
            confidence="high",
            reasoning="Test reason",
        )

        # Assert
        assert result.rotation_degrees == 90
        assert result.rotation_needed is True
        assert result.source_orientation == Orientation.NORTH_SOUTH
        assert result.destination_orientation == Orientation.EAST_WEST
        assert result.confidence == "high"
        assert result.reasoning == "Test reason"


class TestOrientationMatcher:
    """Tests for OrientationMatcher."""

    def test_match_both_square_no_rotation(self):
        """Test matching when both source and destination are square."""
        # Arrange
        matcher = OrientationMatcher()
        source = OrientationAnalysis(Orientation.SQUARE, 1000.0, 1000.0, 1.0, "high")
        dest = OrientationAnalysis(Orientation.SQUARE, 2000.0, 2000.0, 1.0, "high")

        # Act
        result = matcher.match(source, dest)

        # Assert
        assert result.rotation_needed is False
        assert result.rotation_degrees == 0
        assert result.confidence == "high"
        assert "square" in result.reasoning.lower()

    def test_match_source_square_destination_oriented(self):
        """Test matching when source is square but destination is oriented."""
        # Arrange
        matcher = OrientationMatcher()
        source = OrientationAnalysis(Orientation.SQUARE, 1000.0, 1000.0, 1.0, "high")
        dest = OrientationAnalysis(Orientation.NORTH_SOUTH, 1000.0, 2000.0, 2.0, "high")

        # Act
        result = matcher.match(source, dest)

        # Assert
        assert result.rotation_needed is False
        assert result.rotation_degrees == 0
        assert "square" in result.reasoning.lower()
        assert "fits destination" in result.reasoning.lower()

    def test_match_destination_square_source_oriented(self):
        """Test matching when destination is square but source is oriented."""
        # Arrange
        matcher = OrientationMatcher()
        source = OrientationAnalysis(Orientation.NORTH_SOUTH, 1000.0, 2000.0, 2.0, "high")
        dest = OrientationAnalysis(Orientation.SQUARE, 2000.0, 2000.0, 1.0, "high")

        # Act
        result = matcher.match(source, dest)

        # Assert
        assert result.rotation_needed is False
        assert result.rotation_degrees == 0
        assert "square" in result.reasoning.lower()
        assert "accommodates" in result.reasoning.lower()

    def test_match_same_orientation_no_rotation(self):
        """Test matching when both have same orientation."""
        # Arrange
        matcher = OrientationMatcher()
        source = OrientationAnalysis(Orientation.NORTH_SOUTH, 1000.0, 2000.0, 2.0, "high")
        dest = OrientationAnalysis(Orientation.NORTH_SOUTH, 1500.0, 3000.0, 2.0, "high")

        # Act
        result = matcher.match(source, dest)

        # Assert
        assert result.rotation_needed is False
        assert result.rotation_degrees == 0
        assert "north_south" in result.reasoning.lower()

    def test_match_north_south_to_east_west_preserves_orientation(self):
        """Test matching N/S source to E/W destination preserves original orientation."""
        # Arrange
        matcher = OrientationMatcher()
        source = OrientationAnalysis(Orientation.NORTH_SOUTH, 1000.0, 2000.0, 2.0, "high")
        dest = OrientationAnalysis(Orientation.EAST_WEST, 3000.0, 1500.0, 2.0, "high")

        # Act
        result = matcher.match(source, dest)

        # Assert
        assert result.rotation_needed is False
        assert result.rotation_degrees == 0
        assert "n/s" in result.reasoning.lower()
        assert "e/w" in result.reasoning.lower()
        assert "preserving" in result.reasoning.lower()

    def test_match_east_west_to_north_south_preserves_orientation(self):
        """Test matching E/W source to N/S destination preserves original orientation."""
        # Arrange
        matcher = OrientationMatcher()
        source = OrientationAnalysis(Orientation.EAST_WEST, 3000.0, 1500.0, 2.0, "high")
        dest = OrientationAnalysis(Orientation.NORTH_SOUTH, 1000.0, 2000.0, 2.0, "high")

        # Act
        result = matcher.match(source, dest)

        # Assert
        assert result.rotation_needed is False
        assert result.rotation_degrees == 0
        assert "e/w" in result.reasoning.lower()
        assert "n/s" in result.reasoning.lower()
        assert "preserving" in result.reasoning.lower()

    def test_match_confidence_propagates_low(self):
        """Test confidence is low if either analysis is low."""
        # Arrange
        matcher = OrientationMatcher()
        source = OrientationAnalysis(Orientation.NORTH_SOUTH, 1000.0, 2000.0, 2.0, "low")
        dest = OrientationAnalysis(Orientation.NORTH_SOUTH, 1500.0, 3000.0, 2.0, "high")

        # Act
        result = matcher.match(source, dest)

        # Assert
        assert result.confidence == "low"

    def test_match_confidence_propagates_medium(self):
        """Test confidence is medium if one analysis is medium."""
        # Arrange
        matcher = OrientationMatcher()
        source = OrientationAnalysis(Orientation.NORTH_SOUTH, 1000.0, 2000.0, 2.0, "medium")
        dest = OrientationAnalysis(Orientation.NORTH_SOUTH, 1500.0, 3000.0, 2.0, "high")

        # Act
        result = matcher.match(source, dest)

        # Assert
        assert result.confidence == "medium"

    def test_match_confidence_high_when_both_high(self):
        """Test confidence is high when both analyses are high."""
        # Arrange
        matcher = OrientationMatcher()
        source = OrientationAnalysis(Orientation.NORTH_SOUTH, 1000.0, 2000.0, 2.0, "high")
        dest = OrientationAnalysis(Orientation.NORTH_SOUTH, 1500.0, 3000.0, 2.0, "high")

        # Act
        result = matcher.match(source, dest)

        # Assert
        assert result.confidence == "high"

    def test_suggest_rotation_axis_returns_y(self):
        """Test suggest_rotation_axis always returns Y axis."""
        # Arrange
        matcher = OrientationMatcher()
        rotation_result = RotationResult(
            rotation_degrees=90,
            rotation_needed=True,
            source_orientation=Orientation.NORTH_SOUTH,
            destination_orientation=Orientation.EAST_WEST,
            confidence="high",
            reasoning="Test",
        )

        # Act
        axis = matcher.suggest_rotation_axis(rotation_result)

        # Assert
        assert axis == "Y"

    def test_format_report_includes_key_information(self):
        """Test format_report includes all key information."""
        # Arrange
        matcher = OrientationMatcher()
        rotation_result = RotationResult(
            rotation_degrees=90,
            rotation_needed=True,
            source_orientation=Orientation.NORTH_SOUTH,
            destination_orientation=Orientation.EAST_WEST,
            confidence="high",
            reasoning="Test rotation reason",
        )

        # Act
        report = matcher.format_report(rotation_result)

        # Assert
        assert "ORIENTATION ANALYSIS" in report
        assert "NORTH_SOUTH" in report
        assert "EAST_WEST" in report
        assert "HIGH" in report
        assert "YES" in report
        assert "90°" in report
        assert "Y" in report  # Rotation axis
        assert "Test rotation reason" in report

    def test_format_report_no_rotation_case(self):
        """Test format_report for case with no rotation needed."""
        # Arrange
        matcher = OrientationMatcher()
        rotation_result = RotationResult(
            rotation_degrees=0,
            rotation_needed=False,
            source_orientation=Orientation.SQUARE,
            destination_orientation=Orientation.SQUARE,
            confidence="high",
            reasoning="Both square",
        )

        # Act
        report = matcher.format_report(rotation_result)

        # Assert
        assert "ORIENTATION ANALYSIS" in report
        assert "NO" in report
        assert "90°" not in report  # Should not mention rotation angle
        assert "Both square" in report
