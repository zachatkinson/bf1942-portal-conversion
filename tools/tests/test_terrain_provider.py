#!/usr/bin/env python3
"""Tests for terrain provider implementations."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bfportal.core.exceptions import OutOfBoundsError, TerrainError
from bfportal.core.interfaces import Vector3
from bfportal.terrain.terrain_provider import (
    CustomHeightmapProvider,
    FixedHeightProvider,
    HeightAdjuster,
    OutskirtsTerrainProvider,
    TerrainEstimator,
    TungstenTerrainProvider,
)


class TestFixedHeightProvider:
    """Tests for FixedHeightProvider."""

    def test_returns_fixed_height_within_bounds(self):
        """Test that provider returns fixed height for positions within bounds."""
        provider = FixedHeightProvider(fixed_height=100.0, terrain_size=(2048.0, 2048.0))

        # Test center
        assert provider.get_height_at(0.0, 0.0) == 100.0

        # Test corners (just inside bounds)
        assert provider.get_height_at(1023.0, 1023.0) == 100.0
        assert provider.get_height_at(-1023.0, -1023.0) == 100.0
        assert provider.get_height_at(1023.0, -1023.0) == 100.0
        assert provider.get_height_at(-1023.0, 1023.0) == 100.0

    def test_raises_out_of_bounds_error(self):
        """Test that provider raises OutOfBoundsError for positions outside bounds."""
        provider = FixedHeightProvider(fixed_height=100.0, terrain_size=(2048.0, 2048.0))

        # Test positions outside bounds
        with pytest.raises(OutOfBoundsError, match="outside terrain bounds"):
            provider.get_height_at(2000.0, 0.0)

        with pytest.raises(OutOfBoundsError, match="outside terrain bounds"):
            provider.get_height_at(0.0, 2000.0)

        with pytest.raises(OutOfBoundsError, match="outside terrain bounds"):
            provider.get_height_at(-2000.0, 0.0)

        with pytest.raises(OutOfBoundsError, match="outside terrain bounds"):
            provider.get_height_at(0.0, -2000.0)

    def test_get_bounds_returns_correct_bounds(self):
        """Test that get_bounds returns correct min/max points."""
        provider = FixedHeightProvider(fixed_height=100.0, terrain_size=(2048.0, 2048.0))

        min_point, max_point = provider.get_bounds()

        assert min_point.x == -1024.0
        assert min_point.y == 100.0
        assert min_point.z == -1024.0

        assert max_point.x == 1024.0
        assert max_point.y == 100.0
        assert max_point.z == 1024.0

    def test_different_terrain_size(self):
        """Test provider with different terrain size."""
        provider = FixedHeightProvider(fixed_height=50.0, terrain_size=(1024.0, 1024.0))

        # Test within smaller bounds
        assert provider.get_height_at(0.0, 0.0) == 50.0
        assert provider.get_height_at(500.0, 500.0) == 50.0

        # Test outside smaller bounds
        with pytest.raises(OutOfBoundsError):
            provider.get_height_at(600.0, 0.0)


class TestTungstenTerrainProvider:
    """Tests for TungstenTerrainProvider."""

    def test_initialization_with_valid_sdk_root(self, tmp_path: Path):
        """Test provider initialization with valid Portal SDK structure."""
        # Create mock Portal SDK structure
        godot_dir = tmp_path / "GodotProject" / "static"
        godot_dir.mkdir(parents=True)
        terrain_file = godot_dir / "MP_Tungsten_Terrain.tscn"
        terrain_file.write_text("[gd_scene]\n")

        provider = TungstenTerrainProvider(portal_sdk_root=tmp_path)

        assert provider.terrain_width == 2048.0
        assert provider.terrain_depth == 2048.0
        assert provider.min_height == 50.0
        assert provider.max_height == 250.0

    def test_initialization_missing_terrain_file(self, tmp_path: Path):
        """Test that provider raises TerrainError when terrain file is missing."""
        with pytest.raises(TerrainError, match="Tungsten terrain not found"):
            TungstenTerrainProvider(portal_sdk_root=tmp_path)

    def test_get_height_returns_value_in_range(self, tmp_path: Path):
        """Test that get_height_at returns values within min/max height range."""
        # Create mock Portal SDK structure
        godot_dir = tmp_path / "GodotProject" / "static"
        godot_dir.mkdir(parents=True)
        terrain_file = godot_dir / "MP_Tungsten_Terrain.tscn"
        terrain_file.write_text("[gd_scene]\n")

        provider = TungstenTerrainProvider(portal_sdk_root=tmp_path)

        # Test various positions
        height1 = provider.get_height_at(0.0, 0.0)
        height2 = provider.get_height_at(100.0, 100.0)
        height3 = provider.get_height_at(-100.0, -100.0)

        # Heights should be within terrain range
        assert provider.min_height <= height1 <= provider.max_height
        assert provider.min_height <= height2 <= provider.max_height
        assert provider.min_height <= height3 <= provider.max_height

    def test_get_bounds_returns_centered_bounds(self, tmp_path: Path):
        """Test that get_bounds returns correct centered bounds."""
        # Create mock Portal SDK structure
        godot_dir = tmp_path / "GodotProject" / "static"
        godot_dir.mkdir(parents=True)
        terrain_file = godot_dir / "MP_Tungsten_Terrain.tscn"
        terrain_file.write_text("[gd_scene]\n")

        provider = TungstenTerrainProvider(portal_sdk_root=tmp_path)

        min_point, max_point = provider.get_bounds()

        assert min_point.x == -1024.0
        assert min_point.y == 50.0
        assert min_point.z == -1024.0

        assert max_point.x == 1024.0
        assert max_point.y == 250.0
        assert max_point.z == 1024.0


class TestOutskirtsTerrainProvider:
    """Tests for OutskirtsTerrainProvider."""

    def test_initialization_with_default_values(self):
        """Test provider initialization with default estimated values."""
        provider = OutskirtsTerrainProvider()

        assert provider.terrain_width == 1536.0
        assert provider.terrain_depth == 1536.0
        assert provider.min_height == 0.0
        assert provider.max_height == 50.0

    def test_get_height_returns_value_in_range(self):
        """Test that get_height_at returns values within urban terrain range."""
        provider = OutskirtsTerrainProvider()

        # Test various positions
        height1 = provider.get_height_at(0.0, 0.0)
        height2 = provider.get_height_at(100.0, 100.0)
        height3 = provider.get_height_at(-100.0, -100.0)

        # Heights should be within terrain range (urban is mostly flat)
        assert provider.min_height <= height1 <= provider.max_height
        assert provider.min_height <= height2 <= provider.max_height
        assert provider.min_height <= height3 <= provider.max_height

    def test_get_bounds_returns_centered_bounds(self):
        """Test that get_bounds returns correct centered bounds for urban map."""
        provider = OutskirtsTerrainProvider()

        min_point, max_point = provider.get_bounds()

        assert min_point.x == -768.0
        assert min_point.y == 0.0
        assert min_point.z == -768.0

        assert max_point.x == 768.0
        assert max_point.y == 50.0
        assert max_point.z == 768.0


class TestCustomHeightmapProvider:
    """Tests for CustomHeightmapProvider."""

    @pytest.fixture
    def mock_heightmap_image(self):
        """Create a mock PIL Image for testing."""
        mock_image = MagicMock()
        mock_image.size = (256, 256)
        mock_image.getpixel = Mock(return_value=128)  # Mid-gray (50% height)
        # Make convert() return the same mock object
        mock_image.convert = Mock(return_value=mock_image)
        return mock_image

    def test_initialization_with_valid_heightmap(self, tmp_path: Path, mock_heightmap_image):
        """Test provider initialization with valid heightmap file."""
        heightmap_path = tmp_path / "heightmap.png"
        heightmap_path.write_bytes(b"fake png data")

        with patch("PIL.Image.open", return_value=mock_heightmap_image):
            provider = CustomHeightmapProvider(
                heightmap_path=heightmap_path,
                terrain_size=(2048.0, 2048.0),
                height_range=(0.0, 200.0),
            )

            assert provider.terrain_width == 2048.0
            assert provider.terrain_depth == 2048.0
            assert provider.min_height == 0.0
            assert provider.max_height == 200.0
            assert provider.width == 256
            assert provider.height == 256

    def test_initialization_missing_heightmap_file(self, tmp_path: Path):
        """Test that provider raises TerrainError when heightmap file is missing."""
        heightmap_path = tmp_path / "nonexistent.png"

        with pytest.raises(TerrainError, match="Failed to load heightmap"):
            CustomHeightmapProvider(
                heightmap_path=heightmap_path,
                terrain_size=(2048.0, 2048.0),
                height_range=(0.0, 200.0),
            )

    def test_initialization_without_pillow(self, tmp_path: Path):
        """Test that provider raises TerrainError when PIL/Pillow is not installed."""
        heightmap_path = tmp_path / "heightmap.png"
        heightmap_path.write_bytes(b"fake png data")

        # Mock the import to fail
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "PIL" or name == "PIL.Image":
                raise ImportError("No module named 'PIL'")
            return original_import(name, *args, **kwargs)

        with (
            patch("builtins.__import__", side_effect=mock_import),
            pytest.raises(TerrainError, match="PIL/Pillow not installed"),
        ):
            CustomHeightmapProvider(
                heightmap_path=heightmap_path,
                terrain_size=(2048.0, 2048.0),
                height_range=(0.0, 200.0),
            )

    def test_get_height_at_center(self, tmp_path: Path, mock_heightmap_image):
        """Test height query at terrain center."""
        heightmap_path = tmp_path / "heightmap.png"
        heightmap_path.write_bytes(b"fake png data")

        mock_heightmap_image.getpixel = Mock(return_value=128)  # Mid-gray

        with patch("PIL.Image.open", return_value=mock_heightmap_image):
            provider = CustomHeightmapProvider(
                heightmap_path=heightmap_path,
                terrain_size=(2048.0, 2048.0),
                height_range=(0.0, 200.0),
            )

            height = provider.get_height_at(0.0, 0.0)

            # 128/255 = ~0.502, so height should be ~100.4
            assert 99.0 <= height <= 101.0

    def test_get_height_with_grayscale_value(self, tmp_path: Path, mock_heightmap_image):
        """Test height query with different grayscale values."""
        heightmap_path = tmp_path / "heightmap.png"
        heightmap_path.write_bytes(b"fake png data")

        with patch("PIL.Image.open", return_value=mock_heightmap_image):
            provider = CustomHeightmapProvider(
                heightmap_path=heightmap_path,
                terrain_size=(2048.0, 2048.0),
                height_range=(0.0, 100.0),
            )

            # Test minimum height (black pixel)
            mock_heightmap_image.getpixel = Mock(return_value=0)
            height = provider.get_height_at(0.0, 0.0)
            assert height == 0.0

            # Test maximum height (white pixel)
            mock_heightmap_image.getpixel = Mock(return_value=255)
            height = provider.get_height_at(0.0, 0.0)
            assert height == 100.0

            # Test mid height (gray pixel)
            mock_heightmap_image.getpixel = Mock(return_value=127)
            height = provider.get_height_at(0.0, 0.0)
            assert 49.0 <= height <= 51.0

    def test_get_height_with_rgb_tuple(self, tmp_path: Path, mock_heightmap_image):
        """Test height query when getpixel returns RGB tuple."""
        heightmap_path = tmp_path / "heightmap.png"
        heightmap_path.write_bytes(b"fake png data")

        mock_heightmap_image.getpixel = Mock(return_value=(128, 128, 128))  # RGB tuple

        with patch("PIL.Image.open", return_value=mock_heightmap_image):
            provider = CustomHeightmapProvider(
                heightmap_path=heightmap_path,
                terrain_size=(2048.0, 2048.0),
                height_range=(0.0, 200.0),
            )

            height = provider.get_height_at(0.0, 0.0)

            # Should use first channel (128)
            assert 99.0 <= height <= 101.0

    def test_get_height_out_of_bounds(self, tmp_path: Path, mock_heightmap_image):
        """Test that provider raises OutOfBoundsError for positions outside terrain."""
        heightmap_path = tmp_path / "heightmap.png"
        heightmap_path.write_bytes(b"fake png data")

        with patch("PIL.Image.open", return_value=mock_heightmap_image):
            provider = CustomHeightmapProvider(
                heightmap_path=heightmap_path,
                terrain_size=(2048.0, 2048.0),
                height_range=(0.0, 200.0),
            )

            with pytest.raises(OutOfBoundsError, match="outside terrain bounds"):
                provider.get_height_at(2000.0, 0.0)

            with pytest.raises(OutOfBoundsError, match="outside terrain bounds"):
                provider.get_height_at(0.0, -2000.0)

    def test_get_bounds(self, tmp_path: Path, mock_heightmap_image):
        """Test that get_bounds returns correct terrain bounds."""
        heightmap_path = tmp_path / "heightmap.png"
        heightmap_path.write_bytes(b"fake png data")

        with patch("PIL.Image.open", return_value=mock_heightmap_image):
            provider = CustomHeightmapProvider(
                heightmap_path=heightmap_path,
                terrain_size=(2048.0, 2048.0),
                height_range=(50.0, 250.0),
            )

            min_point, max_point = provider.get_bounds()

            assert min_point.x == -1024.0
            assert min_point.y == 50.0
            assert min_point.z == -1024.0

            assert max_point.x == 1024.0
            assert max_point.y == 250.0
            assert max_point.z == 1024.0


class TestTerrainEstimator:
    """Tests for TerrainEstimator."""

    def test_get_fixed_height_known_maps(self):
        """Test that get_fixed_height returns correct values for known Portal maps."""
        assert TerrainEstimator.get_fixed_height("MP_Battery") == 140.0
        assert TerrainEstimator.get_fixed_height("MP_Tungsten") == 150.0
        assert TerrainEstimator.get_fixed_height("MP_Outskirts") == 25.0
        assert TerrainEstimator.get_fixed_height("MP_Aftermath") == 40.0

    def test_get_fixed_height_unknown_map(self):
        """Test that get_fixed_height returns default value for unknown maps."""
        assert TerrainEstimator.get_fixed_height("MP_Unknown") == 100.0

    def test_get_height_range_known_maps(self):
        """Test that get_height_range returns correct ranges for known Portal maps."""
        min_h, max_h = TerrainEstimator.get_height_range("MP_Battery")
        assert min_h == 24.0
        assert max_h == 255.0

        min_h, max_h = TerrainEstimator.get_height_range("MP_Outskirts")
        assert min_h == 0.0
        assert max_h == 50.0

    def test_get_height_range_unknown_map(self):
        """Test that get_height_range returns default range for unknown maps."""
        min_h, max_h = TerrainEstimator.get_height_range("MP_Unknown")
        assert min_h == 0.0
        assert max_h == 200.0


class TestHeightAdjuster:
    """Tests for HeightAdjuster."""

    def test_adjust_height_with_fixed_terrain(self):
        """Test height adjustment with FixedHeightProvider."""
        from bfportal.core.interfaces import Rotation, Transform

        terrain = FixedHeightProvider(fixed_height=100.0, terrain_size=(2048.0, 2048.0))
        adjuster = HeightAdjuster()

        original_transform = Transform(
            position=Vector3(50.0, 0.0, 50.0),
            rotation=Rotation(0.0, 0.0, 0.0),
        )

        adjusted = adjuster.adjust_height(original_transform, terrain, ground_offset=0.0)

        assert adjusted.position.x == 50.0
        assert adjusted.position.y == 100.0
        assert adjusted.position.z == 50.0

    def test_adjust_height_with_ground_offset(self):
        """Test height adjustment with additional ground offset."""
        from bfportal.core.interfaces import Rotation, Transform

        terrain = FixedHeightProvider(fixed_height=100.0, terrain_size=(2048.0, 2048.0))
        adjuster = HeightAdjuster()

        original_transform = Transform(
            position=Vector3(0.0, 0.0, 0.0),
            rotation=Rotation(0.0, 0.0, 0.0),
        )

        adjusted = adjuster.adjust_height(original_transform, terrain, ground_offset=5.0)

        assert adjusted.position.y == 105.0

    def test_adjust_height_preserves_rotation(self):
        """Test that height adjustment preserves rotation."""
        from bfportal.core.interfaces import Rotation, Transform

        terrain = FixedHeightProvider(fixed_height=100.0, terrain_size=(2048.0, 2048.0))
        adjuster = HeightAdjuster()

        original_transform = Transform(
            position=Vector3(0.0, 0.0, 0.0),
            rotation=Rotation(45.0, 90.0, 180.0),
        )

        adjusted = adjuster.adjust_height(original_transform, terrain)

        assert adjusted.rotation.pitch == 45.0
        assert adjusted.rotation.yaw == 90.0
        assert adjusted.rotation.roll == 180.0

    def test_adjust_height_out_of_bounds_returns_unchanged(self):
        """Test that out of bounds positions return unchanged transform."""
        from bfportal.core.interfaces import Rotation, Transform

        terrain = FixedHeightProvider(fixed_height=100.0, terrain_size=(2048.0, 2048.0))
        adjuster = HeightAdjuster()

        # Position outside terrain bounds
        original_transform = Transform(
            position=Vector3(5000.0, 50.0, 5000.0),
            rotation=Rotation(0.0, 0.0, 0.0),
        )

        adjusted = adjuster.adjust_height(original_transform, terrain)

        # Should return unchanged
        assert adjusted.position.x == 5000.0
        assert adjusted.position.y == 50.0
        assert adjusted.position.z == 5000.0
