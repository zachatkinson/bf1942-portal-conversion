#!/usr/bin/env python3
"""Unit tests for TSCN transform parsing utilities."""

import sys
from pathlib import Path

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bfportal.utils.tscn_utils import TscnTransformParser


class TestTscnTransformParser:
    """Test cases for TscnTransformParser class."""

    def test_parse_identity_transform(self):
        """Test parsing identity transform (no rotation, zero position)."""
        # Arrange
        transform_str = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)"

        # Act
        rotation, position = TscnTransformParser.parse(transform_str)

        # Assert
        assert rotation == [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        assert position == [0.0, 0.0, 0.0]

    def test_parse_with_position(self):
        """Test parsing transform with position but no rotation."""
        # Arrange
        transform_str = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 50, -200)"

        # Act
        rotation, position = TscnTransformParser.parse(transform_str)

        # Assert
        assert rotation == [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        assert position == [100.0, 50.0, -200.0]

    def test_parse_with_rotation(self):
        """Test parsing transform with rotation matrix."""
        # Arrange
        # 90-degree rotation around Y-axis
        transform_str = "Transform3D(0, 0, 1, 0, 1, 0, -1, 0, 0, 10, 20, 30)"

        # Act
        rotation, position = TscnTransformParser.parse(transform_str)

        # Assert
        assert rotation == [0.0, 0.0, 1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0]
        assert position == [10.0, 20.0, 30.0]

    def test_parse_with_negative_values(self):
        """Test parsing transform with negative values."""
        # Arrange
        transform_str = "Transform3D(-1, 0, 0, 0, -1, 0, 0, 0, -1, -10, -20, -30)"

        # Act
        rotation, position = TscnTransformParser.parse(transform_str)

        # Assert
        assert rotation == [-1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, -1.0]
        assert position == [-10.0, -20.0, -30.0]

    def test_parse_with_decimal_values(self):
        """Test parsing transform with decimal values."""
        # Arrange
        transform_str = "Transform3D(0.707, 0.707, 0, -0.707, 0.707, 0, 0, 0, 1, 3.14, 2.71, 1.41)"

        # Act
        rotation, position = TscnTransformParser.parse(transform_str)

        # Assert
        assert rotation == pytest.approx([0.707, 0.707, 0.0, -0.707, 0.707, 0.0, 0.0, 0.0, 1.0])
        assert position == pytest.approx([3.14, 2.71, 1.41])

    def test_parse_with_scientific_notation(self):
        """Test parsing transform with scientific notation."""
        # Arrange
        transform_str = "Transform3D(1e0, 0e0, 0e0, 0e0, 1e0, 0e0, 0e0, 0e0, 1e0, 1e3, 2e2, 3e1)"

        # Act
        rotation, position = TscnTransformParser.parse(transform_str)

        # Assert
        assert rotation == [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        assert position == [1000.0, 200.0, 30.0]

    def test_parse_with_extra_whitespace(self):
        """Test parsing transform with extra whitespace."""
        # Arrange
        transform_str = "Transform3D( 1 , 0 , 0 , 0 , 1 , 0 , 0 , 0 , 1 , 10 , 20 , 30 )"

        # Act
        rotation, position = TscnTransformParser.parse(transform_str)

        # Assert
        assert rotation == [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        assert position == [10.0, 20.0, 30.0]

    def test_parse_invalid_format_missing_parentheses(self):
        """Test parsing fails with missing parentheses."""
        # Arrange
        transform_str = "Transform3D 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid Transform3D format"):
            TscnTransformParser.parse(transform_str)

    def test_parse_invalid_format_wrong_value_count(self):
        """Test parsing fails with wrong number of values."""
        # Arrange
        transform_str = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1)"  # Only 9 values

        # Act & Assert
        with pytest.raises(ValueError, match="Expected 12 values"):
            TscnTransformParser.parse(transform_str)

    def test_parse_invalid_format_non_numeric(self):
        """Test parsing fails with non-numeric values."""
        # Arrange
        transform_str = "Transform3D(a, b, c, d, e, f, g, h, i, j, k, l)"

        # Act & Assert
        with pytest.raises(ValueError):
            TscnTransformParser.parse(transform_str)

    def test_format_identity_transform(self):
        """Test formatting identity transform."""
        # Arrange
        rotation = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        position = [0, 0, 0]

        # Act
        result = TscnTransformParser.format(rotation, position)  # type: ignore[arg-type]

        # Assert
        assert result == "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)"

    def test_format_with_position(self):
        """Test formatting transform with position."""
        # Arrange
        rotation = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        position = [100, 50, -200]

        # Act
        result = TscnTransformParser.format(rotation, position)  # type: ignore[arg-type]

        # Assert
        assert result == "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 50, -200)"

    def test_format_with_decimals(self):
        """Test formatting transform with decimal values."""
        # Arrange
        rotation = [0.707107, 0.707107, 0, -0.707107, 0.707107, 0, 0, 0, 1]
        position = [3.14159, 2.71828, 1.41421]

        # Act
        result = TscnTransformParser.format(rotation, position)  # type: ignore[arg-type]

        # Assert
        # Check format uses compact notation
        assert "Transform3D(" in result
        assert "0.707107" in result
        assert "3.14159" in result

    def test_format_invalid_rotation_length(self):
        """Test formatting fails with invalid rotation matrix length."""
        # Arrange
        rotation = [1, 0, 0, 0, 1, 0]  # Only 6 values
        position = [0, 0, 0]

        # Act & Assert
        with pytest.raises(ValueError, match="Rotation matrix must have 9 values"):
            TscnTransformParser.format(rotation, position)  # type: ignore[arg-type]

    def test_format_invalid_position_length(self):
        """Test formatting fails with invalid position length."""
        # Arrange
        rotation = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        position = [0, 0]  # Only 2 values

        # Act & Assert
        with pytest.raises(ValueError, match="Position must have 3 values"):
            TscnTransformParser.format(rotation, position)  # type: ignore[arg-type]

    def test_extract_from_line_with_transform(self):
        """Test extracting Transform3D from a .tscn line."""
        # Arrange
        line = "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 30)"

        # Act
        result = TscnTransformParser.extract_from_line(line)

        # Assert
        assert result == "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 30)"

    def test_extract_from_line_without_transform(self):
        """Test extracting from line without Transform3D returns None."""
        # Arrange
        line = 'name = "SpawnPoint_1"'

        # Act
        result = TscnTransformParser.extract_from_line(line)

        # Assert
        assert result is None

    def test_extract_from_line_with_prefix(self):
        """Test extracting Transform3D with prefix text."""
        # Arrange
        line = '[node name="Object"] transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)'

        # Act
        result = TscnTransformParser.extract_from_line(line)

        # Assert
        assert result == "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)"

    def test_replace_in_line(self):
        """Test replacing Transform3D in a line."""
        # Arrange
        line = "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)"
        new_transform = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 200, 300)"

        # Act
        result = TscnTransformParser.replace_in_line(line, new_transform)

        # Assert
        assert result == "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 200, 300)"

    def test_replace_in_line_preserves_formatting(self):
        """Test replacing Transform3D preserves line formatting."""
        # Arrange
        line = "  transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)  # comment"
        new_transform = "Transform3D(0, 0, 1, 0, 1, 0, -1, 0, 0, 50, 50, 50)"

        # Act
        result = TscnTransformParser.replace_in_line(line, new_transform)

        # Assert
        assert result.startswith("  transform = ")
        assert result.endswith("  # comment")
        assert "Transform3D(0, 0, 1, 0, 1, 0, -1, 0, 0, 50, 50, 50)" in result

    def test_parse_and_format_roundtrip(self):
        """Test that parse and format are inverse operations."""
        # Arrange
        original = "Transform3D(0.707, -0.707, 0, 0.707, 0.707, 0, 0, 0, 1, 100, 200, 300)"

        # Act
        rotation, position = TscnTransformParser.parse(original)
        result = TscnTransformParser.format(rotation, position)  # type: ignore[arg-type]
        # Parse the result again to compare values (not string format)
        rotation2, position2 = TscnTransformParser.parse(result)

        # Assert
        assert rotation == pytest.approx(rotation2)
        assert position == pytest.approx(position2)
