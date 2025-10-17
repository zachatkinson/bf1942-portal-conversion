#!/usr/bin/env python3
"""Tests for VegetationSnapper.

Tests the vegetation snapping logic that adjusts trees, bushes, and other
natural vegetation to terrain height with appropriate offsets.
"""

from unittest.mock import MagicMock

import pytest

from tools.bfportal.terrain.snappers.vegetation_snapper import VegetationSnapper


class TestVegetationSnapper:
    """Tests for VegetationSnapper class."""

    @pytest.fixture
    def mock_terrain(self):
        """Provide mocked terrain provider."""
        terrain = MagicMock()
        terrain.get_height_at.return_value = 10.0
        return terrain

    @pytest.fixture
    def vegetation_snapper(self, mock_terrain):
        """Provide VegetationSnapper instance."""
        return VegetationSnapper(mock_terrain)

    def test_get_category_name_returns_vegetation(self, vegetation_snapper):
        """Test get_category_name returns 'Vegetation'."""
        # Act
        result = vegetation_snapper.get_category_name()

        # Assert
        assert result == "Vegetation"

    def test_can_snap_recognizes_trees(self, vegetation_snapper):
        """Test can_snap identifies tree objects."""
        # Act & Assert
        assert vegetation_snapper.can_snap("Tree_Pine_01", "Tree") is True
        assert vegetation_snapper.can_snap("Birch_Large", "Birch") is True
        assert vegetation_snapper.can_snap("Oak_Medium", None) is True
        assert vegetation_snapper.can_snap("tree_small", None) is True

    def test_can_snap_recognizes_bushes(self, vegetation_snapper):
        """Test can_snap identifies bush objects."""
        # Act & Assert
        assert vegetation_snapper.can_snap("Bush_01", "Bush") is True
        assert vegetation_snapper.can_snap("Shrub_Large", "Shrub") is True
        assert vegetation_snapper.can_snap("bush_green", None) is True

    def test_can_snap_recognizes_grass(self, vegetation_snapper):
        """Test can_snap identifies grass objects."""
        # Act & Assert
        assert vegetation_snapper.can_snap("Grass_Patch_01", "Grass") is True
        assert vegetation_snapper.can_snap("grass_tall", None) is True

    def test_can_snap_recognizes_plants(self, vegetation_snapper):
        """Test can_snap identifies plant objects."""
        # Act & Assert
        assert vegetation_snapper.can_snap("Plant_Fern", "Plant") is True
        assert vegetation_snapper.can_snap("Fern_Large", "Fern") is True

    def test_can_snap_rejects_non_vegetation(self, vegetation_snapper):
        """Test can_snap rejects non-vegetation objects."""
        # Act & Assert
        assert vegetation_snapper.can_snap("Building_01", "Building") is False
        assert vegetation_snapper.can_snap("Rock_Large", "Rock") is False
        assert vegetation_snapper.can_snap("Crate_Wood", None) is False

    def test_calculate_snapped_height_snaps_to_terrain(self, vegetation_snapper, mock_terrain):
        """Test calculate_snapped_height snaps vegetation to terrain."""
        # Arrange
        mock_terrain.get_height_at.return_value = 15.0

        # Act
        result = vegetation_snapper.calculate_snapped_height(
            x=100.0, z=200.0, current_y=5.0, node_name="Tree_Pine_01"
        )

        # Assert
        assert result.snapped_y == 15.0
        assert result.original_y == 5.0
        assert result.was_adjusted is True
        assert "vegetation" in result.reason.lower() or "terrain" in result.reason.lower()
        mock_terrain.get_height_at.assert_called()

    def test_calculate_snapped_height_with_small_offset(self, vegetation_snapper, mock_terrain):
        """Test calculate_snapped_height may apply small vertical offset for vegetation."""
        # Arrange
        mock_terrain.get_height_at.return_value = 10.0

        # Act
        result = vegetation_snapper.calculate_snapped_height(
            x=100.0, z=200.0, current_y=5.0, node_name="Grass_Patch_01"
        )

        # Assert - May have small offset but should be close to terrain
        assert abs(result.snapped_y - 10.0) <= 1.0  # Within 1m of terrain
        assert result.was_adjusted is True
