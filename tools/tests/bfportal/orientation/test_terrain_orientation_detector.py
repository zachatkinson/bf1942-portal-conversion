#!/usr/bin/env python3
"""Tests for TerrainOrientationDetector."""

import sys
from pathlib import Path
from unittest.mock import Mock

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pytest
from bfportal.orientation import Orientation
from bfportal.orientation.interfaces import OrientationAnalysis
from bfportal.orientation.terrain_orientation_detector import TerrainOrientationDetector
from bfportal.terrain.terrain_provider import ITerrainProvider


@pytest.fixture
def mock_terrain_provider():
    """Create a mock terrain provider."""
    provider = Mock(spec=ITerrainProvider)
    return provider


@pytest.fixture
def sample_heightmap_path(tmp_path):
    """Create a temporary heightmap file path."""
    return tmp_path / "test_heightmap.png"


class TestTerrainOrientationDetectorInit:
    """Tests for TerrainOrientationDetector initialization."""

    def test_init_with_default_parameters_sets_attributes(self):
        """Test initialization with default parameters sets correct attributes."""
        # Arrange & Act
        detector = TerrainOrientationDetector()

        # Assert
        assert detector.terrain_provider is None
        assert detector.heightmap_path is None
        assert detector.terrain_size == (2048.0, 2048.0)
        assert detector.threshold == 1.2

    def test_init_with_terrain_provider_sets_provider(self, mock_terrain_provider):
        """Test initialization with terrain provider sets provider attribute."""
        # Arrange & Act
        detector = TerrainOrientationDetector(terrain_provider=mock_terrain_provider)

        # Assert
        assert detector.terrain_provider is mock_terrain_provider

    def test_init_with_heightmap_path_sets_path(self, sample_heightmap_path):
        """Test initialization with heightmap path sets path attribute."""
        # Arrange & Act
        detector = TerrainOrientationDetector(heightmap_path=sample_heightmap_path)

        # Assert
        assert detector.heightmap_path == sample_heightmap_path

    def test_init_with_custom_terrain_size_sets_size(self):
        """Test initialization with custom terrain size sets size attribute."""
        # Arrange
        custom_size = (1024.0, 2048.0)

        # Act
        detector = TerrainOrientationDetector(terrain_size=custom_size)

        # Assert
        assert detector.terrain_size == custom_size

    def test_init_with_custom_threshold_sets_threshold(self):
        """Test initialization with custom threshold sets threshold attribute."""
        # Arrange
        custom_threshold = 1.5

        # Act
        detector = TerrainOrientationDetector(threshold=custom_threshold)

        # Assert
        assert detector.threshold == custom_threshold

    def test_init_with_all_parameters_sets_all_attributes(
        self, mock_terrain_provider, sample_heightmap_path
    ):
        """Test initialization with all parameters sets all attributes."""
        # Arrange
        custom_size = (1536.0, 1024.0)
        custom_threshold = 1.8

        # Act
        detector = TerrainOrientationDetector(
            terrain_provider=mock_terrain_provider,
            heightmap_path=sample_heightmap_path,
            terrain_size=custom_size,
            threshold=custom_threshold,
        )

        # Assert
        assert detector.terrain_provider is mock_terrain_provider
        assert detector.heightmap_path == sample_heightmap_path
        assert detector.terrain_size == custom_size
        assert detector.threshold == custom_threshold


class TestTerrainOrientationDetectorDetectOrientation:
    """Tests for detect_orientation method."""

    def test_detect_orientation_square_terrain_returns_square(self):
        """Test detect_orientation with square terrain returns SQUARE orientation."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2048.0, 2048.0))

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert result.width_x == 2048.0
        assert result.depth_z == 2048.0
        assert result.ratio == 1.0
        assert result.confidence == "low"

    def test_detect_orientation_east_west_high_ratio_returns_east_west_high_confidence(self):
        """Test detect_orientation with high E/W ratio returns EAST_WEST with high confidence."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(3000.0, 2000.0), threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.EAST_WEST
        assert result.width_x == 3000.0
        assert result.depth_z == 2000.0
        assert result.ratio == 1.5
        assert result.confidence == "high"

    def test_detect_orientation_north_south_high_ratio_returns_north_south_high_confidence(self):
        """Test detect_orientation with high N/S ratio returns NORTH_SOUTH with high confidence."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(1000.0, 2000.0), threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.NORTH_SOUTH
        assert result.width_x == 1000.0
        assert result.depth_z == 2000.0
        assert result.ratio == 2.0
        assert result.confidence == "high"

    def test_detect_orientation_east_west_medium_ratio_returns_east_west_medium_confidence(self):
        """Test detect_orientation with medium E/W ratio returns EAST_WEST with medium confidence."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2500.0, 2000.0), threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.EAST_WEST
        assert result.width_x == 2500.0
        assert result.depth_z == 2000.0
        assert result.ratio == 1.25
        assert result.confidence == "medium"

    def test_detect_orientation_north_south_medium_ratio_returns_north_south_medium_confidence(
        self,
    ):
        """Test detect_orientation with medium N/S ratio returns NORTH_SOUTH with medium confidence."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2000.0, 2500.0), threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.NORTH_SOUTH
        assert result.width_x == 2000.0
        assert result.depth_z == 2500.0
        assert result.ratio == 1.25
        assert result.confidence == "medium"

    def test_detect_orientation_east_west_low_ratio_returns_square_low_confidence(self):
        """Test detect_orientation with low E/W ratio returns SQUARE with low confidence."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2200.0, 2000.0), threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert result.width_x == 2200.0
        assert result.depth_z == 2000.0
        assert result.ratio == 1.1
        assert result.confidence == "low"

    def test_detect_orientation_north_south_low_ratio_returns_square_low_confidence(self):
        """Test detect_orientation with low N/S ratio returns SQUARE with low confidence."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2000.0, 2200.0), threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert result.width_x == 2000.0
        assert result.depth_z == 2200.0
        assert result.ratio == 1.1
        assert result.confidence == "low"

    def test_detect_orientation_zero_width_returns_square_low_confidence(self):
        """Test detect_orientation with zero width returns SQUARE with low confidence."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(0.0, 2048.0))

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert result.width_x == 0.0
        assert result.depth_z == 2048.0
        assert result.ratio == 1.0
        assert result.confidence == "low"

    def test_detect_orientation_zero_depth_returns_square_low_confidence(self):
        """Test detect_orientation with zero depth returns SQUARE with low confidence."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2048.0, 0.0))

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert result.width_x == 2048.0
        assert result.depth_z == 0.0
        assert result.ratio == 1.0
        assert result.confidence == "low"

    def test_detect_orientation_both_zero_returns_square_low_confidence(self):
        """Test detect_orientation with both dimensions zero returns SQUARE with low confidence."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(0.0, 0.0))

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert result.width_x == 0.0
        assert result.depth_z == 0.0
        assert result.ratio == 1.0
        assert result.confidence == "low"

    def test_detect_orientation_near_square_ratio_below_threshold_returns_square(self):
        """Test detect_orientation with ratio below threshold but close to 1.0 returns SQUARE."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2100.0, 2000.0), threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert abs(result.ratio - 1.05) < 0.01
        assert result.confidence == "low"

    def test_detect_orientation_very_high_east_west_ratio_returns_high_confidence(self):
        """Test detect_orientation with very high E/W ratio returns high confidence."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(5000.0, 2000.0), threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.EAST_WEST
        assert result.ratio == 2.5
        assert result.confidence == "high"

    def test_detect_orientation_very_high_north_south_ratio_returns_high_confidence(self):
        """Test detect_orientation with very high N/S ratio returns high confidence."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(1000.0, 3000.0), threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.NORTH_SOUTH
        assert result.ratio == 3.0
        assert result.confidence == "high"

    def test_detect_orientation_exactly_threshold_ratio_returns_medium_confidence(self):
        """Test detect_orientation with exactly threshold ratio returns medium confidence."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2400.0, 2000.0), threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.EAST_WEST
        assert result.ratio == 1.2
        assert result.confidence == "medium"

    def test_detect_orientation_ratio_between_threshold_and_1_5_returns_medium_confidence(self):
        """Test detect_orientation with ratio between threshold and 1.5 returns medium confidence."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2800.0, 2000.0), threshold=1.2)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.EAST_WEST
        assert result.ratio == 1.4
        assert result.confidence == "medium"

    def test_detect_orientation_returns_orientation_analysis_instance(self):
        """Test detect_orientation returns OrientationAnalysis instance."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2048.0, 2048.0))

        # Act
        result = detector.detect_orientation()

        # Assert
        assert isinstance(result, OrientationAnalysis)


class TestTerrainOrientationDetectorGetBounds:
    """Tests for get_bounds method."""

    def test_get_bounds_square_terrain_returns_centered_bounds(self):
        """Test get_bounds with square terrain returns centered bounds."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2048.0, 2048.0))

        # Act
        min_x, max_x, min_z, max_z = detector.get_bounds()

        # Assert
        assert min_x == -1024.0
        assert max_x == 1024.0
        assert min_z == -1024.0
        assert max_z == 1024.0

    def test_get_bounds_rectangular_terrain_returns_correct_bounds(self):
        """Test get_bounds with rectangular terrain returns correct bounds."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(3000.0, 2000.0))

        # Act
        min_x, max_x, min_z, max_z = detector.get_bounds()

        # Assert
        assert min_x == -1500.0
        assert max_x == 1500.0
        assert min_z == -1000.0
        assert max_z == 1000.0

    def test_get_bounds_small_terrain_returns_correct_bounds(self):
        """Test get_bounds with small terrain returns correct bounds."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(100.0, 50.0))

        # Act
        min_x, max_x, min_z, max_z = detector.get_bounds()

        # Assert
        assert min_x == -50.0
        assert max_x == 50.0
        assert min_z == -25.0
        assert max_z == 25.0

    def test_get_bounds_zero_width_returns_zero_x_bounds(self):
        """Test get_bounds with zero width returns zero X bounds."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(0.0, 2048.0))

        # Act
        min_x, max_x, min_z, max_z = detector.get_bounds()

        # Assert
        assert min_x == 0.0
        assert max_x == 0.0
        assert min_z == -1024.0
        assert max_z == 1024.0

    def test_get_bounds_zero_depth_returns_zero_z_bounds(self):
        """Test get_bounds with zero depth returns zero Z bounds."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2048.0, 0.0))

        # Act
        min_x, max_x, min_z, max_z = detector.get_bounds()

        # Assert
        assert min_x == -1024.0
        assert max_x == 1024.0
        assert min_z == 0.0
        assert max_z == 0.0

    def test_get_bounds_returns_tuple_of_four_floats(self):
        """Test get_bounds returns tuple of four floats."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2048.0, 2048.0))

        # Act
        result = detector.get_bounds()

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 4
        assert all(isinstance(x, float) for x in result)

    def test_get_bounds_asymmetric_terrain_returns_correct_bounds(self):
        """Test get_bounds with asymmetric terrain returns correct bounds."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(1536.0, 3072.0))

        # Act
        min_x, max_x, min_z, max_z = detector.get_bounds()

        # Assert
        assert min_x == -768.0
        assert max_x == 768.0
        assert min_z == -1536.0
        assert max_z == 1536.0


class TestTerrainOrientationDetectorAnalyzeHeightmapVariation:
    """Tests for analyze_heightmap_variation method."""

    def test_analyze_heightmap_variation_falls_back_to_detect_orientation(self):
        """Test analyze_heightmap_variation falls back to detect_orientation."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2048.0, 2048.0))

        # Act
        result = detector.analyze_heightmap_variation()

        # Assert
        assert isinstance(result, OrientationAnalysis)
        assert result.orientation == Orientation.SQUARE
        assert result.width_x == 2048.0
        assert result.depth_z == 2048.0

    def test_analyze_heightmap_variation_with_east_west_terrain_returns_east_west(self):
        """Test analyze_heightmap_variation with E/W terrain returns EAST_WEST."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(3000.0, 2000.0))

        # Act
        result = detector.analyze_heightmap_variation()

        # Assert
        assert result.orientation == Orientation.EAST_WEST
        assert result.width_x == 3000.0
        assert result.depth_z == 2000.0

    def test_analyze_heightmap_variation_with_north_south_terrain_returns_north_south(self):
        """Test analyze_heightmap_variation with N/S terrain returns NORTH_SOUTH."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(1000.0, 2000.0))

        # Act
        result = detector.analyze_heightmap_variation()

        # Assert
        assert result.orientation == Orientation.NORTH_SOUTH
        assert result.width_x == 1000.0
        assert result.depth_z == 2000.0

    def test_analyze_heightmap_variation_matches_detect_orientation_result(self):
        """Test analyze_heightmap_variation matches detect_orientation result."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2500.0, 2000.0))

        # Act
        variation_result = detector.analyze_heightmap_variation()
        detection_result = detector.detect_orientation()

        # Assert
        assert variation_result.orientation == detection_result.orientation
        assert variation_result.width_x == detection_result.width_x
        assert variation_result.depth_z == detection_result.depth_z
        assert variation_result.ratio == detection_result.ratio
        assert variation_result.confidence == detection_result.confidence


class TestTerrainOrientationDetectorEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_small_terrain_dimensions_handled_correctly(self):
        """Test very small terrain dimensions are handled correctly."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(0.1, 0.1))

        # Act
        result = detector.detect_orientation()
        bounds = detector.get_bounds()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert result.ratio == 1.0
        assert bounds == (-0.05, 0.05, -0.05, 0.05)

    def test_very_large_terrain_dimensions_handled_correctly(self):
        """Test very large terrain dimensions are handled correctly."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(100000.0, 50000.0))

        # Act
        result = detector.detect_orientation()
        bounds = detector.get_bounds()

        # Assert
        assert result.orientation == Orientation.EAST_WEST
        assert result.ratio == 2.0
        assert bounds == (-50000.0, 50000.0, -25000.0, 25000.0)

    def test_extreme_aspect_ratio_handled_correctly(self):
        """Test extreme aspect ratio is handled correctly."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(10000.0, 100.0))

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.EAST_WEST
        assert result.ratio == 100.0
        assert result.confidence == "high"

    def test_custom_threshold_affects_orientation_detection(self):
        """Test custom threshold affects orientation detection."""
        # Arrange
        size = (2400.0, 2000.0)
        detector_low_threshold = TerrainOrientationDetector(terrain_size=size, threshold=1.1)
        detector_high_threshold = TerrainOrientationDetector(terrain_size=size, threshold=1.5)

        # Act
        result_low = detector_low_threshold.detect_orientation()
        result_high = detector_high_threshold.detect_orientation()

        # Assert
        assert result_low.orientation == Orientation.EAST_WEST
        assert result_high.orientation == Orientation.SQUARE

    def test_threshold_boundary_condition_exactly_at_threshold(self):
        """Test threshold boundary condition exactly at threshold value."""
        # Arrange
        threshold = 1.2
        detector = TerrainOrientationDetector(terrain_size=(2400.0, 2000.0), threshold=threshold)

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.ratio == 1.2
        assert result.orientation == Orientation.EAST_WEST

    def test_near_square_detection_with_ratio_close_to_1_0(self):
        """Test near-square detection with ratio very close to 1.0."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2050.0, 2000.0))

        # Act
        result = detector.detect_orientation()

        # Assert
        assert abs(result.ratio - 1.025) < 0.01
        assert result.orientation == Orientation.SQUARE
        assert result.confidence == "low"

    def test_floating_point_precision_handled_correctly(self):
        """Test floating point precision is handled correctly."""
        # Arrange
        detector = TerrainOrientationDetector(terrain_size=(2048.000001, 2048.0))

        # Act
        result = detector.detect_orientation()

        # Assert
        assert result.orientation == Orientation.SQUARE
        assert abs(result.ratio - 1.0) < 0.01
