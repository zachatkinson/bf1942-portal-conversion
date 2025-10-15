#!/usr/bin/env python3
"""Test scale parsing from BF1942 .con files."""

import pytest
from bfportal.parsers.con_parser import ConParser


class TestScaleParsing:
    """Tests for ConParser scale value extraction."""

    def test_scale_parsing_extracts_all_components(self, tmp_path):
        """Test that ConParser correctly extracts scale values from .con files.

        Given: .con file with Object.geometry.scale defined
        When: Parsing the file with ConParser
        Then: Scale values are correctly extracted for x, y, z components
        """
        # Arrange
        test_content = """
Object.create Tree_01
Object.absolutePosition 100/50/200
Object.rotation 0/45/0
Object.geometry.scale 0.88/0.96/0.84
Object.setTeam 0
"""
        test_file = tmp_path / "test_scale.con"
        test_file.write_text(test_content)
        parser = ConParser()

        # Act
        result = parser.parse(test_file)

        # Assert
        assert len(result["objects"]) == 1
        obj = result["objects"][0]
        assert "scale" in obj
        scale_dict = obj["scale"]
        assert scale_dict["x"] == pytest.approx(0.88)
        assert scale_dict["y"] == pytest.approx(0.96)
        assert scale_dict["z"] == pytest.approx(0.84)

    def test_scale_parsing_included_in_transform(self, tmp_path):
        """Test that scale values are included in Transform extraction.

        Given: .con file with Object.geometry.scale defined
        When: Extracting transform via parse_transform()
        Then: Transform includes scale with correct values
        """
        # Arrange
        test_content = """
Object.create Tree_01
Object.absolutePosition 100/50/200
Object.rotation 0/45/0
Object.geometry.scale 0.88/0.96/0.84
Object.setTeam 0
"""
        test_file = tmp_path / "test_scale.con"
        test_file.write_text(test_content)
        parser = ConParser()
        result = parser.parse(test_file)
        obj = result["objects"][0]

        # Act
        transform = parser.parse_transform(obj)

        # Assert
        assert transform is not None
        assert transform.scale is not None
        assert transform.scale.x == pytest.approx(0.88)
        assert transform.scale.y == pytest.approx(0.96)
        assert transform.scale.z == pytest.approx(0.84)

    def test_missing_scale_defaults_to_one(self, tmp_path):
        """Test that objects without scale default to (1, 1, 1).

        Given: .con file WITHOUT Object.geometry.scale
        When: Extracting transform via parse_transform()
        Then: Transform has default scale of (1.0, 1.0, 1.0)
        """
        # Arrange
        test_content = """
Object.create Tree_02
Object.absolutePosition 100/50/200
Object.rotation 0/45/0
Object.setTeam 0
"""
        test_file = tmp_path / "test_no_scale.con"
        test_file.write_text(test_content)
        parser = ConParser()
        result = parser.parse(test_file)
        obj = result["objects"][0]

        # Act
        transform = parser.parse_transform(obj)

        # Assert
        assert "scale" not in obj  # Scale not in raw parsed data
        assert transform is not None
        assert transform.scale is not None  # But transform has default
        assert transform.scale.x == pytest.approx(1.0)
        assert transform.scale.y == pytest.approx(1.0)
        assert transform.scale.z == pytest.approx(1.0)

    def test_scale_parsing_with_scientific_notation(self, tmp_path):
        """Test that scale parsing handles scientific notation values.

        Given: .con file with scale in scientific notation (e.g., 1.5e-1)
        When: Parsing the file with ConParser
        Then: Scale values are correctly parsed
        """
        # Arrange
        test_content = """
Object.create Tree_03
Object.absolutePosition 100/50/200
Object.geometry.scale 1.5e-1/2.0e0/3.5e-2
Object.setTeam 0
"""
        test_file = tmp_path / "test_scale_scientific.con"
        test_file.write_text(test_content)
        parser = ConParser()

        # Act
        result = parser.parse(test_file)

        # Assert
        obj = result["objects"][0]
        assert "scale" in obj
        scale_dict = obj["scale"]
        assert scale_dict["x"] == pytest.approx(0.15)
        assert scale_dict["y"] == pytest.approx(2.0)
        assert scale_dict["z"] == pytest.approx(0.035)

    def test_scale_parsing_with_negative_values(self, tmp_path):
        """Test that scale parsing handles negative scale values (mirroring).

        Given: .con file with negative scale values
        When: Parsing the file with ConParser
        Then: Negative scale values are correctly extracted
        """
        # Arrange
        test_content = """
Object.create Tree_04
Object.absolutePosition 100/50/200
Object.geometry.scale -1.0/1.0/1.0
Object.setTeam 0
"""
        test_file = tmp_path / "test_scale_negative.con"
        test_file.write_text(test_content)
        parser = ConParser()

        # Act
        result = parser.parse(test_file)

        # Assert
        obj = result["objects"][0]
        assert "scale" in obj
        scale_dict = obj["scale"]
        assert scale_dict["x"] == pytest.approx(-1.0)
        assert scale_dict["y"] == pytest.approx(1.0)
        assert scale_dict["z"] == pytest.approx(1.0)
