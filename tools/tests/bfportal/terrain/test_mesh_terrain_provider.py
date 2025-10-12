#!/usr/bin/env python3
"""Tests for MeshTerrainProvider - GLB mesh terrain queries."""

import struct
import sys
from pathlib import Path

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bfportal.core.exceptions import OutOfBoundsError, TerrainError
from bfportal.terrain.terrain_provider import MeshTerrainProvider


class TestMeshTerrainProvider:
    """Tests for MeshTerrainProvider."""

    @pytest.fixture
    def mock_glb_file(self, tmp_path: Path):
        """Create a minimal valid GLB file for testing."""
        glb_path = tmp_path / "terrain.glb"

        # Create minimal GLB structure
        # GLB Header: magic (glTF), version (2), length
        # JSON chunk: GLTF 2.0 minimal scene
        # BIN chunk: vertex data (3 vertices forming a triangle)

        import json

        gltf_json = {
            "asset": {"version": "2.0"},
            "accessors": [
                {
                    "bufferView": 0,
                    "componentType": 5126,  # FLOAT
                    "count": 9,  # 9 vertices for grid
                    "type": "VEC3",
                }
            ],
            "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": 108}],  # 9 * 3 * 4 bytes
            "buffers": [{"byteLength": 108}],
        }

        json_str = json.dumps(gltf_json)
        json_bytes = json_str.encode("utf-8")
        json_length = len(json_bytes)

        # Pad JSON to 4-byte alignment
        json_padding = (4 - (json_length % 4)) % 4
        json_bytes += b" " * json_padding
        json_length_padded = len(json_bytes)

        # Binary data: 9 vertices in 3x3 grid
        vertices = [
            [-100.0, 0.0, -100.0],  # Bottom-left
            [0.0, 5.0, -100.0],  # Bottom-center
            [100.0, 0.0, -100.0],  # Bottom-right
            [-100.0, 5.0, 0.0],  # Center-left
            [0.0, 10.0, 0.0],  # Center (highest point)
            [100.0, 5.0, 0.0],  # Center-right
            [-100.0, 0.0, 100.0],  # Top-left
            [0.0, 5.0, 100.0],  # Top-center
            [100.0, 0.0, 100.0],  # Top-right
        ]

        binary_data = b""
        for v in vertices:
            binary_data += struct.pack("<fff", *v)

        bin_length = len(binary_data)

        # Calculate total GLB length
        glb_header_size = 12
        json_chunk_header_size = 8
        bin_chunk_header_size = 8
        total_length = (
            glb_header_size
            + json_chunk_header_size
            + json_length_padded
            + bin_chunk_header_size
            + bin_length
        )

        # Write GLB file
        with open(glb_path, "wb") as f:
            # GLB header
            f.write(b"glTF")  # magic
            f.write(struct.pack("<I", 2))  # version
            f.write(struct.pack("<I", total_length))  # length

            # JSON chunk
            f.write(struct.pack("<I", json_length_padded))  # chunk length
            f.write(b"JSON")  # chunk type
            f.write(json_bytes)

            # BIN chunk
            f.write(struct.pack("<I", bin_length))  # chunk length
            f.write(b"BIN\x00")  # chunk type
            f.write(binary_data)

        return glb_path

    def test_initialization_with_valid_glb(self, mock_glb_file: Path):
        """Test MeshTerrainProvider initialization with valid GLB file."""
        # Arrange & Act
        provider = MeshTerrainProvider(mesh_path=mock_glb_file, terrain_size=(200.0, 200.0))

        # Assert
        assert provider.terrain_width == 200.0
        assert provider.terrain_depth == 200.0
        assert provider.vertices.shape == (9, 3)  # 9 vertices, 3 coords each
        assert provider.min_height == 0.0
        assert provider.max_height == 10.0
        assert provider.mesh_center_x == pytest.approx(0.0, abs=1.0)
        assert provider.mesh_center_z == pytest.approx(0.0, abs=1.0)

    def test_initialization_missing_glb_file(self, tmp_path: Path):
        """Test initialization raises error for missing GLB file."""
        # Arrange
        missing_file = tmp_path / "nonexistent.glb"

        # Act & Assert
        with pytest.raises(TerrainError, match="Failed to extract vertices"):
            MeshTerrainProvider(mesh_path=missing_file, terrain_size=(200.0, 200.0))

    def test_initialization_invalid_glb_magic(self, tmp_path: Path):
        """Test initialization raises error for invalid GLB magic number."""
        # Arrange
        invalid_glb = tmp_path / "invalid.glb"
        invalid_glb.write_bytes(b"INVALID_DATA")

        # Act & Assert
        with pytest.raises(TerrainError, match="Invalid GLB file"):
            MeshTerrainProvider(mesh_path=invalid_glb, terrain_size=(200.0, 200.0))

    def test_mesh_bounds_calculated_correctly(self, mock_glb_file: Path):
        """Test that mesh bounds are calculated from actual vertices."""
        # Arrange
        provider = MeshTerrainProvider(mesh_path=mock_glb_file, terrain_size=(200.0, 200.0))

        # Act & Assert - Check calculated bounds from vertices
        assert provider.mesh_min_x == pytest.approx(-100.0)
        assert provider.mesh_max_x == pytest.approx(100.0)
        assert provider.mesh_min_z == pytest.approx(-100.0)
        assert provider.mesh_max_z == pytest.approx(100.0)

    def test_get_height_at_center(self, mock_glb_file: Path):
        """Test get_height_at returns correct height at mesh center."""
        # Arrange
        provider = MeshTerrainProvider(mesh_path=mock_glb_file, terrain_size=(200.0, 200.0))

        # Act - Query at center (highest point in our test data)
        height = provider.get_height_at(0.0, 0.0)

        # Assert - Should be interpolated value close to 10.0 (highest vertex)
        # With grid interpolation, exact value may vary
        assert 5.0 <= height <= 10.0

    def test_get_height_at_corner(self, mock_glb_file: Path):
        """Test get_height_at returns correct height at mesh corners."""
        # Arrange
        provider = MeshTerrainProvider(mesh_path=mock_glb_file, terrain_size=(200.0, 200.0))

        # Act - Query at bottom-left corner (y=0)
        height = provider.get_height_at(-100.0, -100.0)

        # Assert - Should be close to 0.0
        assert -2.0 <= height <= 2.0

    def test_get_height_with_interpolation(self, mock_glb_file: Path):
        """Test get_height_at uses bilinear interpolation."""
        # Arrange
        provider = MeshTerrainProvider(mesh_path=mock_glb_file, terrain_size=(200.0, 200.0))

        # Act - Query halfway between center and corner
        height = provider.get_height_at(-50.0, -50.0)

        # Assert - Should be interpolated value between 0 and 10
        assert 0.0 <= height <= 10.0

    def test_get_height_out_of_bounds_raises_error(self, mock_glb_file: Path):
        """Test get_height_at raises OutOfBoundsError for positions outside mesh."""
        # Arrange
        provider = MeshTerrainProvider(mesh_path=mock_glb_file, terrain_size=(200.0, 200.0))

        # Act & Assert
        with pytest.raises(OutOfBoundsError, match="outside terrain mesh bounds"):
            provider.get_height_at(500.0, 0.0)

        with pytest.raises(OutOfBoundsError, match="outside terrain mesh bounds"):
            provider.get_height_at(0.0, -500.0)

    def test_get_bounds_returns_actual_mesh_bounds(self, mock_glb_file: Path):
        """Test get_bounds returns actual mesh bounds from vertices."""
        # Arrange
        provider = MeshTerrainProvider(mesh_path=mock_glb_file, terrain_size=(200.0, 200.0))

        # Act
        min_point, max_point = provider.get_bounds()

        # Assert
        assert min_point.x == pytest.approx(-100.0, abs=1.0)
        assert min_point.y == 0.0
        assert min_point.z == pytest.approx(-100.0, abs=1.0)

        assert max_point.x == pytest.approx(100.0, abs=1.0)
        assert max_point.y == 10.0
        assert max_point.z == pytest.approx(100.0, abs=1.0)

    def test_grid_resolution_used_for_spatial_queries(self, mock_glb_file: Path):
        """Test that grid resolution is set and used for spatial queries."""
        # Arrange
        provider = MeshTerrainProvider(mesh_path=mock_glb_file, terrain_size=(200.0, 200.0))

        # Act & Assert
        assert provider.grid_resolution == 256
        assert provider.height_grid.shape == (256, 256)

    def test_height_grid_built_from_vertices(self, mock_glb_file: Path):
        """Test that height grid is built and contains valid heights."""
        # Arrange
        provider = MeshTerrainProvider(mesh_path=mock_glb_file, terrain_size=(200.0, 200.0))

        # Act & Assert - Grid should have no NaN values after gap filling
        import numpy as np

        assert not np.isnan(provider.height_grid).any()
        assert provider.height_grid.min() >= provider.min_height
        assert provider.height_grid.max() <= provider.max_height


class TestMeshTerrainProviderEdgeCases:
    """Tests for MeshTerrainProvider edge cases."""

    def test_invalid_json_chunk_type(self, tmp_path: Path):
        """Test error handling for invalid JSON chunk type."""
        # Arrange
        glb_path = tmp_path / "invalid_json.glb"

        with open(glb_path, "wb") as f:
            f.write(b"glTF")  # magic
            f.write(struct.pack("<I", 2))  # version
            f.write(struct.pack("<I", 100))  # length (approximate)

            # Write invalid chunk type (should be JSON)
            f.write(struct.pack("<I", 20))  # chunk length
            f.write(b"XXXX")  # invalid chunk type
            f.write(b'{"test": "data"}  ')

        # Act & Assert
        with pytest.raises(TerrainError, match="Expected JSON chunk"):
            MeshTerrainProvider(mesh_path=glb_path, terrain_size=(200.0, 200.0))

    def test_invalid_bin_chunk_type(self, tmp_path: Path):
        """Test error handling for invalid BIN chunk type."""
        # Arrange
        import json

        glb_path = tmp_path / "invalid_bin.glb"
        gltf_json = {
            "asset": {"version": "2.0"},
            "accessors": [{"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3"}],
            "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": 36}],
            "buffers": [{"byteLength": 36}],
        }

        json_str = json.dumps(gltf_json)
        json_bytes = json_str.encode("utf-8")

        with open(glb_path, "wb") as f:
            f.write(b"glTF")
            f.write(struct.pack("<I", 2))
            f.write(struct.pack("<I", 200))

            f.write(struct.pack("<I", len(json_bytes)))
            f.write(b"JSON")
            f.write(json_bytes)

            # Write invalid BIN chunk type
            f.write(struct.pack("<I", 36))
            f.write(b"XXXX")  # invalid chunk type
            f.write(b"\x00" * 36)

        # Act & Assert
        with pytest.raises(TerrainError, match="Expected BIN chunk"):
            MeshTerrainProvider(mesh_path=glb_path, terrain_size=(200.0, 200.0))

    def test_accessor_not_vec3(self, tmp_path: Path):
        """Test error handling when first accessor is not VEC3."""
        # Arrange
        import json

        glb_path = tmp_path / "non_vec3.glb"
        gltf_json = {
            "asset": {"version": "2.0"},
            "accessors": [
                {"bufferView": 0, "componentType": 5126, "count": 3, "type": "SCALAR"}  # Not VEC3
            ],
            "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": 12}],
            "buffers": [{"byteLength": 12}],
        }

        json_str = json.dumps(gltf_json)
        json_bytes = json_str.encode("utf-8")

        with open(glb_path, "wb") as f:
            f.write(b"glTF")
            f.write(struct.pack("<I", 2))
            f.write(struct.pack("<I", 200))

            f.write(struct.pack("<I", len(json_bytes)))
            f.write(b"JSON")
            f.write(json_bytes)

            f.write(struct.pack("<I", 12))
            f.write(b"BIN\x00")
            f.write(struct.pack("<fff", 0.0, 0.0, 0.0))

        # Act & Assert
        with pytest.raises(TerrainError, match="First accessor is not VEC3"):
            MeshTerrainProvider(mesh_path=glb_path, terrain_size=(200.0, 200.0))
