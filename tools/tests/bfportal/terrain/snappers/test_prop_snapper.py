#!/usr/bin/env python3
"""Tests for PropSnapper.

Tests the prop snapping logic that adjusts static objects like buildings,
crates, and other environmental props to terrain height.
"""

from unittest.mock import MagicMock

import pytest

from tools.bfportal.terrain.snappers.prop_snapper import PropSnapper


class TestPropSnapper:
    """Tests for PropSnapper class."""

    @pytest.fixture
    def mock_terrain(self):
        """Provide mocked terrain provider."""
        terrain = MagicMock()
        terrain.get_height_at.return_value = 10.0
        return terrain

    @pytest.fixture
    def prop_snapper(self, mock_terrain):
        """Provide PropSnapper instance."""
        return PropSnapper(mock_terrain)

    def test_get_category_name_returns_props(self, prop_snapper):
        """Test get_category_name returns 'Props'."""
        # Act
        result = prop_snapper.get_category_name()

        # Assert
        assert result == "Props"

    def test_can_snap_returns_true_for_any_object(self, prop_snapper):
        """Test can_snap returns True (catch-all snapper)."""
        # Act
        result1 = prop_snapper.can_snap("Building_01", "Building")
        result2 = prop_snapper.can_snap("Crate_Large", "Crate")
        result3 = prop_snapper.can_snap("Unknown_Type", None)

        # Assert
        assert result1 is True
        assert result2 is True
        assert result3 is True

    def test_calculate_snapped_height_snaps_to_terrain(self, prop_snapper, mock_terrain):
        """Test calculate_snapped_height snaps object to terrain."""
        # Arrange
        mock_terrain.get_height_at.return_value = 15.0

        # Act
        result = prop_snapper.calculate_snapped_height(
            x=100.0, z=200.0, current_y=5.0, node_name="Building_01"
        )

        # Assert
        # Result should use multipoint sampling (minimum of sampled points)
        assert result.was_adjusted is True
        assert result.original_y == 5.0
        # Snapped height should be close to terrain (15.0) possibly with small offset
        assert 14.0 <= result.snapped_y <= 16.0
        mock_terrain.get_height_at.assert_called()  # Called multiple times for sampling

    def test_calculate_snapped_height_no_adjustment_when_within_tolerance(
        self, prop_snapper, mock_terrain
    ):
        """Test calculate_snapped_height doesn't adjust when within 0.1m tolerance."""
        # Arrange
        mock_terrain.get_height_at.return_value = 10.0

        # Act - Within 0.1m tolerance
        result = prop_snapper.calculate_snapped_height(
            x=100.0, z=200.0, current_y=10.05, node_name="Crate_01"
        )

        # Assert - Should not adjust (within tolerance)
        assert result.was_adjusted is False
        assert result.original_y == 10.05

    def test_calculate_snapped_height_skips_water_objects(self, prop_snapper, mock_terrain):
        """Test calculate_snapped_height skips water bodies."""
        # Act
        result = prop_snapper.calculate_snapped_height(
            x=100.0, z=200.0, current_y=5.0, node_name="lake_kursk_01"
        )

        # Assert - Should skip (water body)
        assert result.was_adjusted is False
        assert result.snapped_y == 5.0  # Keeps original
        assert "Skipped" in result.reason
