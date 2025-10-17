#!/usr/bin/env python3
"""Tests for base snapper interfaces and result classes.

Tests the abstract base classes and data structures used by all terrain snappers.
"""

import pytest

from tools.bfportal.terrain.snappers.base_snapper import (
    IObjectSnapper,
    ITerrainProvider,
    SnapResult,
)


class TestSnapResult:
    """Tests for SnapResult dataclass."""

    def test_snap_result_with_adjustment(self):
        """Test SnapResult for adjusted object."""
        # Arrange & Act
        result = SnapResult(
            snapped_y=10.5,
            original_y=5.0,
            was_adjusted=True,
            reason="Snapped to terrain height",
        )

        # Assert
        assert result.snapped_y == 10.5
        assert result.original_y == 5.0
        assert result.was_adjusted is True
        assert result.reason == "Snapped to terrain height"

    def test_snap_result_no_adjustment(self):
        """Test SnapResult for object not adjusted."""
        # Arrange & Act
        result = SnapResult(
            snapped_y=5.0,
            original_y=5.0,
            was_adjusted=False,
            reason="Already at correct height",
        )

        # Assert
        assert result.snapped_y == 5.0
        assert result.original_y == 5.0
        assert result.was_adjusted is False
        assert result.reason == "Already at correct height"

    def test_snap_result_calculates_delta(self):
        """Test SnapResult height delta calculation."""
        # Arrange
        result = SnapResult(
            snapped_y=15.0,
            original_y=10.0,
            was_adjusted=True,
            reason="Test",
        )

        # Act
        delta = result.snapped_y - result.original_y

        # Assert
        assert delta == 5.0


class TestIObjectSnapper:
    """Tests for IObjectSnapper interface."""

    def test_interface_has_required_methods(self):
        """Test IObjectSnapper defines required abstract methods."""
        # Arrange
        abstract_methods = IObjectSnapper.__abstractmethods__

        # Assert
        assert "can_snap" in abstract_methods
        assert "calculate_snapped_height" in abstract_methods
        assert "get_category_name" in abstract_methods

    def test_cannot_instantiate_interface_directly(self):
        """Test IObjectSnapper cannot be instantiated directly."""
        # Act & Assert
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IObjectSnapper()


class TestITerrainProvider:
    """Tests for ITerrainProvider interface."""

    def test_interface_is_protocol(self):
        """Test ITerrainProvider is a Protocol."""
        # Assert - Protocols have get_height_at method
        assert hasattr(ITerrainProvider, "get_height_at")

    def test_cannot_instantiate_protocol_directly(self):
        """Test ITerrainProvider Protocol cannot be instantiated directly."""
        # Act & Assert
        with pytest.raises(TypeError, match="Protocols cannot be instantiated"):
            ITerrainProvider()
