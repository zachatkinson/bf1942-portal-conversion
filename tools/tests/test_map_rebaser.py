#!/usr/bin/env python3
"""Unit tests for MapRebaser."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bfportal.core.interfaces import (
    GameObject,
    IBoundsValidator,
    ICoordinateOffset,
    ITerrainProvider,
    Rotation,
    Team,
    Transform,
    Vector3,
)
from bfportal.transforms.map_rebaser import MapRebaser


class TestMapRebaserInitialization:
    """Test cases for MapRebaser initialization."""

    def test_init_stores_dependencies(self):
        """Test that initialization stores terrain, offset calculator, and bounds validator."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)
        bounds_validator = Mock(spec=IBoundsValidator)

        rebaser = MapRebaser(terrain, offset_calc, bounds_validator)

        assert rebaser.terrain is terrain
        assert rebaser.offset_calc is offset_calc
        assert rebaser.bounds_validator is bounds_validator

    def test_init_allows_none_bounds_validator(self):
        """Test that bounds validator can be None."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)

        rebaser = MapRebaser(terrain, offset_calc, None)

        assert rebaser.bounds_validator is None


class TestMapRebaserOffsetCalculation:
    """Test cases for offset calculation during rebasing."""

    def test_calculate_centroid_called_with_objects(self):
        """Test that centroid is calculated from parsed objects."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)
        offset_calc.calculate_centroid.return_value = Vector3(100.0, 50.0, 200.0)
        offset_calc.calculate_offset.return_value = Vector3(0.0, 0.0, 0.0)
        offset_calc.apply_offset.side_effect = lambda t, o: t

        terrain.get_height_at.return_value = 50.0

        rebaser = MapRebaser(terrain, offset_calc, None)

        # Create a simple test .tscn file
        test_tscn = Path(__file__).parent / "test_rebaser_input.tscn"
        test_tscn.write_text(
            '[node name="TestObject" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 50, 200)\n"
        )

        try:
            output_tscn = test_tscn.parent / "test_rebaser_output.tscn"
            new_center = Vector3(0.0, 0.0, 0.0)

            rebaser.rebase_map(test_tscn, output_tscn, "MP_Outskirts", new_center)

            # Verify centroid calculation was called
            offset_calc.calculate_centroid.assert_called_once()
            objects_arg = offset_calc.calculate_centroid.call_args[0][0]
            assert len(objects_arg) > 0

        finally:
            test_tscn.unlink(missing_ok=True)
            output_tscn.unlink(missing_ok=True)

    def test_calculate_offset_with_new_center(self):
        """Test that offset is calculated between current and new center."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)

        current_centroid = Vector3(100.0, 50.0, 200.0)
        new_center = Vector3(50.0, 25.0, 100.0)
        expected_offset = Vector3(-50.0, -25.0, -100.0)

        offset_calc.calculate_centroid.return_value = current_centroid
        offset_calc.calculate_offset.return_value = expected_offset
        offset_calc.apply_offset.side_effect = lambda t, o: Transform(
            Vector3(t.position.x + o.x, t.position.y + o.y, t.position.z + o.z), t.rotation
        )

        terrain.get_height_at.return_value = 25.0

        rebaser = MapRebaser(terrain, offset_calc, None)

        # Create test .tscn file
        test_tscn = Path(__file__).parent / "test_rebaser_offset.tscn"
        test_tscn.write_text(
            '[node name="TestObject" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 50, 200)\n"
        )

        try:
            output_tscn = test_tscn.parent / "test_rebaser_offset_output.tscn"

            stats = rebaser.rebase_map(test_tscn, output_tscn, "MP_Outskirts", new_center)

            # Verify offset calculation was called with correct parameters
            offset_calc.calculate_offset.assert_called_once_with(current_centroid, new_center)

            # Verify offset is in stats
            assert stats["offset_applied"]["x"] == expected_offset.x
            assert stats["offset_applied"]["y"] == expected_offset.y
            assert stats["offset_applied"]["z"] == expected_offset.z

        finally:
            test_tscn.unlink(missing_ok=True)
            output_tscn.unlink(missing_ok=True)

    def test_apply_offset_to_each_object(self):
        """Test that offset is applied to each rebased object."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)

        offset = Vector3(-50.0, 0.0, -100.0)
        offset_calc.calculate_centroid.return_value = Vector3(100.0, 0.0, 200.0)
        offset_calc.calculate_offset.return_value = offset

        # Track apply_offset calls
        apply_offset_calls = []

        def mock_apply_offset(transform, off):
            apply_offset_calls.append((transform, off))
            return Transform(
                Vector3(
                    transform.position.x + off.x, transform.position.y, transform.position.z + off.z
                ),
                transform.rotation,
            )

        offset_calc.apply_offset.side_effect = mock_apply_offset
        terrain.get_height_at.return_value = 0.0

        rebaser = MapRebaser(terrain, offset_calc, None)

        # Create test .tscn with multiple objects
        test_tscn = Path(__file__).parent / "test_rebaser_multi.tscn"
        test_tscn.write_text(
            '[node name="Object1" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 0, 200)\n"
            '[node name="Object2" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 150, 0, 250)\n"
        )

        try:
            output_tscn = test_tscn.parent / "test_rebaser_multi_output.tscn"

            rebaser.rebase_map(test_tscn, output_tscn, "MP_Outskirts", Vector3(0.0, 0.0, 0.0))

            # Verify apply_offset was called for each object
            assert len(apply_offset_calls) >= 2

        finally:
            test_tscn.unlink(missing_ok=True)
            output_tscn.unlink(missing_ok=True)


class TestMapRebaserHeightAdjustment:
    """Test cases for height adjustment on new terrain."""

    def test_height_adjusted_when_above_tolerance(self):
        """Test that object height is adjusted when above terrain by more than tolerance."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)

        # Object at y=50, terrain at y=10 (40m difference > tolerance)
        terrain.get_height_at.return_value = 10.0

        offset_calc.calculate_centroid.return_value = Vector3(0.0, 50.0, 0.0)
        offset_calc.calculate_offset.return_value = Vector3(0.0, 0.0, 0.0)
        offset_calc.apply_offset.side_effect = lambda t, o: t

        rebaser = MapRebaser(terrain, offset_calc, None)

        # Create test .tscn file
        test_tscn = Path(__file__).parent / "test_rebaser_height.tscn"
        test_tscn.write_text(
            '[node name="TestObject" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 50, 0)\n"
        )

        try:
            output_tscn = test_tscn.parent / "test_rebaser_height_output.tscn"

            stats = rebaser.rebase_map(
                test_tscn, output_tscn, "MP_Outskirts", Vector3(0.0, 0.0, 0.0)
            )

            # Verify height adjustment occurred
            assert stats["height_adjusted"] == 1
            terrain.get_height_at.assert_called()

        finally:
            test_tscn.unlink(missing_ok=True)
            output_tscn.unlink(missing_ok=True)

    def test_height_not_adjusted_within_tolerance(self):
        """Test that object height is not adjusted when within tolerance."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)

        # Object at y=11, terrain at y=10 (1m difference < tolerance of 2m)
        terrain.get_height_at.return_value = 10.0

        offset_calc.calculate_centroid.return_value = Vector3(0.0, 11.0, 0.0)
        offset_calc.calculate_offset.return_value = Vector3(0.0, 0.0, 0.0)
        offset_calc.apply_offset.side_effect = lambda t, o: t

        rebaser = MapRebaser(terrain, offset_calc, None)

        # Create test .tscn file
        test_tscn = Path(__file__).parent / "test_rebaser_no_height.tscn"
        test_tscn.write_text(
            '[node name="TestObject" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 11, 0)\n"
        )

        try:
            output_tscn = test_tscn.parent / "test_rebaser_no_height_output.tscn"

            stats = rebaser.rebase_map(
                test_tscn, output_tscn, "MP_Outskirts", Vector3(0.0, 0.0, 0.0)
            )

            # Verify no height adjustment occurred
            assert stats["height_adjusted"] == 0

        finally:
            test_tscn.unlink(missing_ok=True)
            output_tscn.unlink(missing_ok=True)

    def test_out_of_bounds_tracked_on_terrain_error(self):
        """Test that objects outside terrain bounds are tracked."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)

        # Terrain query raises exception for out of bounds
        terrain.get_height_at.side_effect = Exception("Out of terrain bounds")

        offset_calc.calculate_centroid.return_value = Vector3(0.0, 0.0, 0.0)
        offset_calc.calculate_offset.return_value = Vector3(0.0, 0.0, 0.0)
        offset_calc.apply_offset.side_effect = lambda t, o: t

        rebaser = MapRebaser(terrain, offset_calc, None)

        # Create test .tscn file
        test_tscn = Path(__file__).parent / "test_rebaser_bounds.tscn"
        test_tscn.write_text(
            '[node name="TestObject" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 9999, 0, 9999)\n"
        )

        try:
            output_tscn = test_tscn.parent / "test_rebaser_bounds_output.tscn"

            stats = rebaser.rebase_map(
                test_tscn, output_tscn, "MP_Outskirts", Vector3(0.0, 0.0, 0.0)
            )

            # Verify out of bounds was tracked
            assert stats["out_of_bounds"] == 1

        finally:
            test_tscn.unlink(missing_ok=True)
            output_tscn.unlink(missing_ok=True)


class TestMapRebaserTscnParsing:
    """Test cases for .tscn file parsing."""

    def test_parse_tscn_extracts_objects(self):
        """Test that _parse_tscn extracts game objects correctly."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)

        rebaser = MapRebaser(terrain, offset_calc, None)

        # Create test .tscn file
        test_tscn = Path(__file__).parent / "test_rebaser_parse.tscn"
        test_tscn.write_text(
            '[node name="TestObject" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 50, 200)\n"
            '[node name="AnotherObject" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 150, 60, 250)\n"
        )

        try:
            objects = rebaser._parse_tscn(test_tscn)

            assert len(objects) == 2
            assert objects[0].name == "TestObject"
            assert objects[1].name == "AnotherObject"

        finally:
            test_tscn.unlink(missing_ok=True)

    def test_parse_tscn_skips_special_nodes(self):
        """Test that special nodes (HQ, Spawn, Combat, etc.) are skipped."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)

        rebaser = MapRebaser(terrain, offset_calc, None)

        # Create test .tscn file with special nodes
        test_tscn = Path(__file__).parent / "test_rebaser_special.tscn"
        test_tscn.write_text(
            '[node name="TEAM_1_HQ" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)\n"
            '[node name="SpawnPoint_1" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 0, 10)\n"
            '[node name="CombatArea" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 20, 0, 20)\n"
            '[node name="Static" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 30, 0, 30)\n"
            '[node name="Terrain" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 40, 0, 40)\n"
            '[node name="RegularObject" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 50, 0, 50)\n"
        )

        try:
            objects = rebaser._parse_tscn(test_tscn)

            # Only RegularObject should be parsed
            assert len(objects) == 1
            assert objects[0].name == "RegularObject"

        finally:
            test_tscn.unlink(missing_ok=True)

    def test_parse_tscn_extracts_position_correctly(self):
        """Test that positions are extracted correctly from transform matrix."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)

        rebaser = MapRebaser(terrain, offset_calc, None)

        # Create test .tscn file with specific position
        test_tscn = Path(__file__).parent / "test_rebaser_position.tscn"
        test_tscn.write_text(
            '[node name="TestObject" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 123.45, 67.89, 234.56)\n"
        )

        try:
            objects = rebaser._parse_tscn(test_tscn)

            assert len(objects) == 1
            assert objects[0].transform.position.x == pytest.approx(123.45)
            assert objects[0].transform.position.y == pytest.approx(67.89)
            assert objects[0].transform.position.z == pytest.approx(234.56)

        finally:
            test_tscn.unlink(missing_ok=True)


class TestMapRebaserTscnGeneration:
    """Test cases for .tscn file generation."""

    def test_generate_tscn_creates_file(self):
        """Test that _generate_tscn creates output file."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)

        rebaser = MapRebaser(terrain, offset_calc, None)

        output_tscn = Path(__file__).parent / "test_rebaser_output.tscn"

        try:
            objects = [
                GameObject(
                    name="TestObject",
                    asset_type="Tree",
                    transform=Transform(Vector3(0.0, 0.0, 0.0), Rotation(0, 0, 0)),
                    team=Team.NEUTRAL,
                    properties={},
                )
            ]

            rebaser._generate_tscn(objects, output_tscn, "MP_Outskirts")

            assert output_tscn.exists()
            assert output_tscn.stat().st_size > 0

        finally:
            output_tscn.unlink(missing_ok=True)

    def test_generate_tscn_includes_base_terrain_name(self):
        """Test that generated .tscn includes base terrain name."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)

        rebaser = MapRebaser(terrain, offset_calc, None)

        output_tscn = Path(__file__).parent / "test_rebaser_terrain_name.tscn"

        try:
            objects = []
            rebaser._generate_tscn(objects, output_tscn, "MP_CustomTerrain")

            content = output_tscn.read_text()
            assert "MP_CustomTerrain" in content

        finally:
            output_tscn.unlink(missing_ok=True)


class TestMapRebaserStatistics:
    """Test cases for rebasing statistics."""

    def test_stats_includes_total_objects(self):
        """Test that statistics include total object count."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)

        offset_calc.calculate_centroid.return_value = Vector3(0.0, 0.0, 0.0)
        offset_calc.calculate_offset.return_value = Vector3(0.0, 0.0, 0.0)
        offset_calc.apply_offset.side_effect = lambda t, o: t
        terrain.get_height_at.return_value = 0.0

        rebaser = MapRebaser(terrain, offset_calc, None)

        # Create test .tscn with 3 objects
        test_tscn = Path(__file__).parent / "test_rebaser_stats.tscn"
        test_tscn.write_text(
            '[node name="Object1" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)\n"
            '[node name="Object2" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 0, 10)\n"
            '[node name="Object3" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 20, 0, 20)\n"
        )

        try:
            output_tscn = test_tscn.parent / "test_rebaser_stats_output.tscn"

            stats = rebaser.rebase_map(
                test_tscn, output_tscn, "MP_Outskirts", Vector3(0.0, 0.0, 0.0)
            )

            assert stats["total_objects"] == 3

        finally:
            test_tscn.unlink(missing_ok=True)
            output_tscn.unlink(missing_ok=True)

    def test_stats_tracks_height_adjusted_and_out_of_bounds(self):
        """Test that statistics track height adjustments and out of bounds objects."""
        terrain = Mock(spec=ITerrainProvider)
        offset_calc = Mock(spec=ICoordinateOffset)

        # First object: within tolerance
        # Second object: needs adjustment
        # Third object: out of bounds
        heights = [5.0, 10.0, None]
        height_calls = [0]

        def get_height_side_effect(x, z):
            idx = height_calls[0]
            height_calls[0] += 1
            if heights[idx] is None:
                raise Exception("Out of bounds")
            return heights[idx]

        terrain.get_height_at.side_effect = get_height_side_effect

        offset_calc.calculate_centroid.return_value = Vector3(0.0, 0.0, 0.0)
        offset_calc.calculate_offset.return_value = Vector3(0.0, 0.0, 0.0)
        offset_calc.apply_offset.side_effect = lambda t, o: t

        rebaser = MapRebaser(terrain, offset_calc, None)

        # Create test .tscn
        test_tscn = Path(__file__).parent / "test_rebaser_tracking.tscn"
        test_tscn.write_text(
            '[node name="Object1" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 5, 0)\n"  # Within tolerance
            '[node name="Object2" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 50, 10)\n"  # Needs adjustment
            '[node name="Object3" instance=Resource("test")]\n'
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 9999, 0, 9999)\n"  # Out of bounds
        )

        try:
            output_tscn = test_tscn.parent / "test_rebaser_tracking_output.tscn"

            stats = rebaser.rebase_map(
                test_tscn, output_tscn, "MP_Outskirts", Vector3(0.0, 0.0, 0.0)
            )

            assert stats["height_adjusted"] == 1
            assert stats["out_of_bounds"] == 1

        finally:
            test_tscn.unlink(missing_ok=True)
            output_tscn.unlink(missing_ok=True)
