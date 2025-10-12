#!/usr/bin/env python3
"""Unit tests for CoordinateOffset."""

import sys
from pathlib import Path

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bfportal.core.interfaces import GameObject, Rotation, Team, Transform, Vector3
from bfportal.transforms.coordinate_offset import CoordinateOffset


class TestCoordinateOffsetCentroidCalculation:
    """Test cases for centroid calculation."""

    def test_calculate_centroid_single_object(self):
        """Test centroid calculation with a single object."""
        offset_calculator = CoordinateOffset()

        obj = GameObject(
            name="tree_01",
            asset_type="Tree_Pine",
            transform=Transform(
                position=Vector3(100.0, 50.0, 200.0),
                rotation=Rotation(0.0, 0.0, 0.0),
            ),
            team=Team.NEUTRAL,
            properties={},
        )

        centroid = offset_calculator.calculate_centroid([obj])

        # Centroid should be the single object's position
        assert centroid.x == 100.0
        assert centroid.y == 50.0
        assert centroid.z == 200.0

    def test_calculate_centroid_multiple_objects(self):
        """Test centroid calculation with multiple objects."""
        offset_calculator = CoordinateOffset()

        objects = [
            GameObject(
                name="obj1",
                asset_type="Tree",
                transform=Transform(
                    position=Vector3(0.0, 10.0, 0.0),
                    rotation=Rotation(0.0, 0.0, 0.0),
                ),
                team=Team.NEUTRAL,
                properties={},
            ),
            GameObject(
                name="obj2",
                asset_type="Rock",
                transform=Transform(
                    position=Vector3(100.0, 20.0, 100.0),
                    rotation=Rotation(0.0, 0.0, 0.0),
                ),
                team=Team.NEUTRAL,
                properties={},
            ),
            GameObject(
                name="obj3",
                asset_type="Building",
                transform=Transform(
                    position=Vector3(200.0, 30.0, 200.0),
                    rotation=Rotation(0.0, 0.0, 0.0),
                ),
                team=Team.NEUTRAL,
                properties={},
            ),
        ]

        centroid = offset_calculator.calculate_centroid(objects)

        # Average of (0, 100, 200) = 100 for X
        # Average of (0, 100, 200) = 100 for Z
        # Average of (10, 20, 30) = 20 for Y
        assert centroid.x == 100.0
        assert centroid.y == 20.0
        assert centroid.z == 100.0

    def test_calculate_centroid_empty_list(self):
        """Test centroid calculation with empty object list."""
        offset_calculator = CoordinateOffset()

        centroid = offset_calculator.calculate_centroid([])

        # Should return origin for empty list
        assert centroid.x == 0.0
        assert centroid.y == 0.0
        assert centroid.z == 0.0

    def test_calculate_centroid_negative_coordinates(self):
        """Test centroid calculation with negative coordinates."""
        offset_calculator = CoordinateOffset()

        objects = [
            GameObject(
                name="obj1",
                asset_type="Tree",
                transform=Transform(
                    position=Vector3(-100.0, 5.0, -50.0),
                    rotation=Rotation(0.0, 0.0, 0.0),
                ),
                team=Team.NEUTRAL,
                properties={},
            ),
            GameObject(
                name="obj2",
                asset_type="Rock",
                transform=Transform(
                    position=Vector3(100.0, 15.0, 50.0),
                    rotation=Rotation(0.0, 0.0, 0.0),
                ),
                team=Team.NEUTRAL,
                properties={},
            ),
        ]

        centroid = offset_calculator.calculate_centroid(objects)

        # Average of (-100, 100) = 0
        assert centroid.x == 0.0
        assert centroid.y == 10.0
        assert centroid.z == 0.0


class TestCoordinateOffsetCalculation:
    """Test cases for offset calculation."""

    def test_calculate_offset_positive_shift(self):
        """Test calculating offset with positive shift."""
        offset_calculator = CoordinateOffset()

        source_center = Vector3(100.0, 50.0, 200.0)
        target_center = Vector3(500.0, 0.0, 800.0)

        offset = offset_calculator.calculate_offset(source_center, target_center)

        # Offset should move source to target
        assert offset.x == 400.0  # 500 - 100
        assert offset.y == 0.0  # Y is always 0 (not offset)
        assert offset.z == 600.0  # 800 - 200

    def test_calculate_offset_negative_shift(self):
        """Test calculating offset with negative shift."""
        offset_calculator = CoordinateOffset()

        source_center = Vector3(500.0, 100.0, 800.0)
        target_center = Vector3(100.0, 0.0, 200.0)

        offset = offset_calculator.calculate_offset(source_center, target_center)

        # Offset should move source to target
        assert offset.x == -400.0  # 100 - 500
        assert offset.y == 0.0  # Y is always 0
        assert offset.z == -600.0  # 200 - 800

    def test_calculate_offset_zero_shift(self):
        """Test calculating offset when centers are the same."""
        offset_calculator = CoordinateOffset()

        source_center = Vector3(100.0, 50.0, 200.0)
        target_center = Vector3(100.0, 75.0, 200.0)

        offset = offset_calculator.calculate_offset(source_center, target_center)

        # No X/Z offset needed, Y ignored
        assert offset.x == 0.0
        assert offset.y == 0.0
        assert offset.z == 0.0

    def test_calculate_offset_ignores_y(self):
        """Test that offset calculation ignores Y coordinate."""
        offset_calculator = CoordinateOffset()

        source_center = Vector3(0.0, 1000.0, 0.0)
        target_center = Vector3(0.0, -1000.0, 0.0)

        offset = offset_calculator.calculate_offset(source_center, target_center)

        # Y difference is 2000 but should be ignored
        assert offset.x == 0.0
        assert offset.y == 0.0
        assert offset.z == 0.0


class TestCoordinateOffsetApplication:
    """Test cases for applying offsets to transforms."""

    def test_apply_offset_positive(self):
        """Test applying positive offset to transform."""
        offset_calculator = CoordinateOffset()

        transform = Transform(
            position=Vector3(100.0, 50.0, 200.0),
            rotation=Rotation(45.0, 90.0, 0.0),
        )
        offset = Vector3(50.0, 0.0, 75.0)

        new_transform = offset_calculator.apply_offset(transform, offset)

        # Position should be adjusted
        assert new_transform.position.x == 150.0
        assert new_transform.position.y == 50.0
        assert new_transform.position.z == 275.0

        # Rotation should be preserved
        assert new_transform.rotation.pitch == 45.0
        assert new_transform.rotation.yaw == 90.0
        assert new_transform.rotation.roll == 0.0

        # Original should be unchanged
        assert transform.position.x == 100.0
        assert transform.position.z == 200.0

    def test_apply_offset_negative(self):
        """Test applying negative offset to transform."""
        offset_calculator = CoordinateOffset()

        transform = Transform(
            position=Vector3(100.0, 50.0, 200.0),
            rotation=Rotation(0.0, 0.0, 0.0),
        )
        offset = Vector3(-100.0, 0.0, -150.0)

        new_transform = offset_calculator.apply_offset(transform, offset)

        assert new_transform.position.x == 0.0
        assert new_transform.position.y == 50.0
        assert new_transform.position.z == 50.0

    def test_apply_offset_zero(self):
        """Test applying zero offset to transform."""
        offset_calculator = CoordinateOffset()

        transform = Transform(
            position=Vector3(100.0, 50.0, 200.0),
            rotation=Rotation(0.0, 0.0, 0.0),
        )
        offset = Vector3(0.0, 0.0, 0.0)

        new_transform = offset_calculator.apply_offset(transform, offset)

        # Position should be unchanged
        assert new_transform.position.x == 100.0
        assert new_transform.position.y == 50.0
        assert new_transform.position.z == 200.0

    def test_apply_offset_preserves_scale(self):
        """Test that applying offset preserves scale."""
        offset_calculator = CoordinateOffset()

        transform = Transform(
            position=Vector3(100.0, 50.0, 200.0),
            rotation=Rotation(0.0, 0.0, 0.0),
            scale=Vector3(2.0, 1.5, 3.0),
        )
        offset = Vector3(50.0, 0.0, 75.0)

        new_transform = offset_calculator.apply_offset(transform, offset)

        # Scale should be preserved
        assert new_transform.scale is not None
        assert new_transform.scale.x == 2.0
        assert new_transform.scale.y == 1.5
        assert new_transform.scale.z == 3.0


class TestCoordinateOffsetScaling:
    """Test cases for applying scale factors to transforms."""

    def test_apply_scale_shrink(self):
        """Test applying scale factor to shrink a transform."""
        offset_calculator = CoordinateOffset()

        transform = Transform(
            position=Vector3(100.0, 50.0, 200.0),
            rotation=Rotation(45.0, 90.0, 0.0),
        )
        scale_factor = 0.5

        new_transform = offset_calculator.apply_scale(transform, scale_factor)

        # Position should be scaled (except Y)
        assert new_transform.position.x == 50.0
        assert new_transform.position.y == 50.0  # Y unchanged
        assert new_transform.position.z == 100.0

        # Rotation should be preserved
        assert new_transform.rotation.pitch == 45.0
        assert new_transform.rotation.yaw == 90.0

    def test_apply_scale_enlarge(self):
        """Test applying scale factor to enlarge a transform."""
        offset_calculator = CoordinateOffset()

        transform = Transform(
            position=Vector3(100.0, 50.0, 200.0),
            rotation=Rotation(0.0, 0.0, 0.0),
        )
        scale_factor = 2.0

        new_transform = offset_calculator.apply_scale(transform, scale_factor)

        # Position should be scaled (except Y)
        assert new_transform.position.x == 200.0
        assert new_transform.position.y == 50.0  # Y unchanged
        assert new_transform.position.z == 400.0

    def test_apply_scale_zero(self):
        """Test applying zero scale factor."""
        offset_calculator = CoordinateOffset()

        transform = Transform(
            position=Vector3(100.0, 50.0, 200.0),
            rotation=Rotation(0.0, 0.0, 0.0),
        )
        scale_factor = 0.0

        new_transform = offset_calculator.apply_scale(transform, scale_factor)

        # Position should be at origin (except Y)
        assert new_transform.position.x == 0.0
        assert new_transform.position.y == 50.0  # Y unchanged
        assert new_transform.position.z == 0.0

    def test_apply_scale_preserves_rotation(self):
        """Test that scaling preserves rotation."""
        offset_calculator = CoordinateOffset()

        transform = Transform(
            position=Vector3(100.0, 50.0, 200.0),
            rotation=Rotation(30.0, 45.0, 60.0),
        )
        scale_factor = 0.75

        new_transform = offset_calculator.apply_scale(transform, scale_factor)

        # Rotation should be unchanged
        assert new_transform.rotation.pitch == 30.0
        assert new_transform.rotation.yaw == 45.0
        assert new_transform.rotation.roll == 60.0

    def test_apply_scale_preserves_original_scale(self):
        """Test that scaling preserves the original scale property."""
        offset_calculator = CoordinateOffset()

        transform = Transform(
            position=Vector3(100.0, 50.0, 200.0),
            rotation=Rotation(0.0, 0.0, 0.0),
            scale=Vector3(2.0, 2.0, 2.0),
        )
        scale_factor = 0.5

        new_transform = offset_calculator.apply_scale(transform, scale_factor)

        # Scale property should be preserved (not affected)
        assert new_transform.scale is not None
        assert new_transform.scale.x == 2.0
        assert new_transform.scale.y == 2.0
        assert new_transform.scale.z == 2.0


class TestCoordinateOffsetIntegration:
    """Integration tests for complete offset workflow."""

    def test_complete_offset_workflow(self):
        """Test complete workflow: calculate centroid, offset, and apply."""
        offset_calculator = CoordinateOffset()

        # Create objects centered around (500, 100, 500)
        objects = [
            GameObject(
                name="obj1",
                asset_type="Tree",
                transform=Transform(
                    position=Vector3(400.0, 50.0, 400.0),
                    rotation=Rotation(0.0, 0.0, 0.0),
                ),
                team=Team.NEUTRAL,
                properties={},
            ),
            GameObject(
                name="obj2",
                asset_type="Rock",
                transform=Transform(
                    position=Vector3(600.0, 150.0, 600.0),
                    rotation=Rotation(0.0, 0.0, 0.0),
                ),
                team=Team.NEUTRAL,
                properties={},
            ),
        ]

        # Calculate centroid
        centroid = offset_calculator.calculate_centroid(objects)
        assert centroid.x == 500.0
        assert centroid.z == 500.0

        # Calculate offset to move to origin
        target_center = Vector3(0.0, 0.0, 0.0)
        offset = offset_calculator.calculate_offset(centroid, target_center)
        assert offset.x == -500.0
        assert offset.z == -500.0

        # Apply offset to first object
        new_transform = offset_calculator.apply_offset(objects[0].transform, offset)
        assert new_transform.position.x == -100.0  # 400 - 500
        assert new_transform.position.z == -100.0  # 400 - 500

    def test_combined_offset_and_scale(self):
        """Test applying both offset and scale to transform."""
        offset_calculator = CoordinateOffset()

        transform = Transform(
            position=Vector3(100.0, 50.0, 100.0),
            rotation=Rotation(0.0, 45.0, 0.0),
        )

        # First apply scale
        scaled = offset_calculator.apply_scale(transform, 0.5)
        assert scaled.position.x == 50.0
        assert scaled.position.z == 50.0

        # Then apply offset
        offset = Vector3(50.0, 0.0, 50.0)
        final = offset_calculator.apply_offset(scaled, offset)

        # Final position should be (100, 50, 100)
        assert final.position.x == 100.0
        assert final.position.y == 50.0
        assert final.position.z == 100.0

        # Rotation should be preserved
        assert final.rotation.yaw == 45.0
