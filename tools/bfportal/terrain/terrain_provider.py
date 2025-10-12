#!/usr/bin/env python3
"""Terrain providers for height queries."""

import struct
from pathlib import Path
from typing import TYPE_CHECKING

from ..core.exceptions import OutOfBoundsError, TerrainError
from ..core.interfaces import ITerrainProvider, Vector3

if TYPE_CHECKING:
    import numpy as np


class CenteredTerrainBoundsMixin:
    """Mixin for terrain providers with centered, rectangular bounds.

    DRY helper - eliminates repeated get_bounds() implementation across
    providers that use centered terrain (origin at 0,0).

    Requires the following attributes in the implementing class:
    - terrain_width: float
    - terrain_depth: float
    - min_height: float
    - max_height: float
    """

    def get_bounds(self) -> tuple[Vector3, Vector3]:
        """Get terrain bounds for centered rectangular terrain.

        Returns:
            Tuple of (min_point, max_point) for terrain centered at origin
        """
        # Type hints for mixin contract
        terrain_width: float = self.terrain_width  # type: ignore
        terrain_depth: float = self.terrain_depth  # type: ignore
        min_height: float = self.min_height  # type: ignore
        max_height: float = self.max_height  # type: ignore

        half_width = terrain_width / 2
        half_depth = terrain_depth / 2

        return (
            Vector3(-half_width, min_height, -half_depth),
            Vector3(half_width, max_height, half_depth),
        )


class CustomHeightmapProvider(CenteredTerrainBoundsMixin, ITerrainProvider):
    """Terrain provider using custom heightmap data.

    Reads heightmap from PNG or raw file and provides height queries.
    Used for BF1942 heightmaps converted to image format.
    """

    def __init__(
        self,
        heightmap_path: Path,
        terrain_size: tuple[float, float],
        height_range: tuple[float, float],
    ):
        """Initialize heightmap provider.

        Args:
            heightmap_path: Path to heightmap image (PNG)
            terrain_size: (width, depth) in world units
            height_range: (min_height, max_height) in world units

        Raises:
            FileNotFoundError: If heightmap file not found
            TerrainError: If heightmap cannot be loaded
        """
        self.heightmap_path = heightmap_path
        self.terrain_width, self.terrain_depth = terrain_size
        self.min_height, self.max_height = height_range

        # Load heightmap
        try:
            from PIL import Image

            img = Image.open(heightmap_path).convert("L")  # Grayscale
            self.heightmap = img
            self.width, self.height = img.size
        except ImportError as e:
            raise TerrainError("PIL/Pillow not installed. Run: pip3 install Pillow") from e
        except Exception as e:
            raise TerrainError(f"Failed to load heightmap {heightmap_path}: {e}") from e

    def get_height_at(self, x: float, z: float) -> float:
        """Query terrain height at world coordinates.

        Args:
            x: World X coordinate
            z: World Z coordinate

        Returns:
            Terrain height (Y coordinate)

        Raises:
            OutOfBoundsError: If position is outside terrain bounds
        """
        # Convert world coordinates to heightmap pixel coordinates
        # Assuming terrain centered at origin
        half_width = self.terrain_width / 2
        half_depth = self.terrain_depth / 2

        # Normalize to 0-1 range
        norm_x = (x + half_width) / self.terrain_width
        norm_z = (z + half_depth) / self.terrain_depth

        # Check bounds
        if norm_x < 0 or norm_x > 1 or norm_z < 0 or norm_z > 1:
            raise OutOfBoundsError(
                f"Position ({x}, {z}) is outside terrain bounds "
                f"[{-half_width}, {half_width}] x [{-half_depth}, {half_depth}]"
            )

        # Convert to pixel coordinates
        px = int(norm_x * (self.width - 1))
        py = int(norm_z * (self.height - 1))

        # Get pixel value (0-255)
        # getpixel returns int for mode 'L', tuple for RGB, or None
        pixel_value = self.heightmap.getpixel((px, py))

        # Handle different return types
        if isinstance(pixel_value, tuple):
            # RGB/RGBA - use first channel
            grayscale_value = pixel_value[0]
        elif isinstance(pixel_value, int):
            # Grayscale - use directly
            grayscale_value = pixel_value
        else:
            # None or other - default to 0
            grayscale_value = 0

        # Normalize to 0-1 and scale to height range
        normalized = grayscale_value / 255.0
        height = self.min_height + (normalized * (self.max_height - self.min_height))

        return height


class TungstenTerrainProvider(CenteredTerrainBoundsMixin, ITerrainProvider):
    """Terrain provider for Portal's MP_Tungsten base map.

    Queries the Tungsten heightmap from Portal SDK static files.
    """

    def __init__(self, portal_sdk_root: Path):
        """Initialize Tungsten terrain provider.

        Args:
            portal_sdk_root: Root directory of Portal SDK

        Raises:
            TerrainError: If Tungsten terrain files not found
        """
        self.portal_root = portal_sdk_root

        # Try to find Tungsten terrain heightmap
        # Portal SDK structure: GodotProject/static/MP_Tungsten_Terrain.tscn
        terrain_path = portal_sdk_root / "GodotProject" / "static" / "MP_Tungsten_Terrain.tscn"

        if not terrain_path.exists():
            raise TerrainError(
                f"Tungsten terrain not found at {terrain_path}. "
                "Ensure Portal SDK is properly set up."
            )

        # TODO: Parse .tscn to extract HeightMapShape3D data
        # For now, use estimated values based on Tungsten terrain
        self.terrain_width = 2048.0  # Estimated
        self.terrain_depth = 2048.0  # Estimated
        self.min_height = 50.0  # Estimated
        self.max_height = 250.0  # Estimated

        print("⚠️  Using estimated Tungsten terrain dimensions:")
        print(f"   Width: {self.terrain_width}m, Depth: {self.terrain_depth}m")
        print(f"   Height range: {self.min_height}m - {self.max_height}m")

    def get_height_at(self, x: float, z: float) -> float:
        """Query terrain height at world coordinates.

        Args:
            x: World X coordinate
            z: World Z coordinate

        Returns:
            Terrain height (Y coordinate)

        Note:
            Currently returns estimated average height.
            TODO: Parse actual Tungsten heightmap data.
        """
        # TODO: Query actual Tungsten heightmap
        # For now, return average height
        avg_height = (self.min_height + self.max_height) / 2

        # Add some variation based on position (temporary)
        import math

        variation = math.sin(x * 0.01) * math.cos(z * 0.01) * 20.0

        return avg_height + variation


class OutskirtsTerrainProvider(CenteredTerrainBoundsMixin, ITerrainProvider):
    """Terrain provider for Portal's MP_Outskirts base map.

    Queries the Outskirts heightmap from Portal SDK static files.
    """

    def __init__(self, portal_sdk_root: Path | None = None):
        """Initialize Outskirts terrain provider.

        Args:
            portal_sdk_root: Root directory of Portal SDK (optional)

        Note:
            Currently uses estimated values. TODO: Parse actual terrain data.
        """
        self.portal_root = portal_sdk_root

        # TODO: Parse .tscn to extract HeightMapShape3D data
        # For now, use estimated values based on Outskirts terrain (urban)
        self.terrain_width = 1536.0  # Smaller urban map
        self.terrain_depth = 1536.0
        self.min_height = 0.0  # Flat urban terrain
        self.max_height = 50.0  # Low buildings/elevation

    def get_height_at(self, x: float, z: float) -> float:
        """Query terrain height at world coordinates.

        Args:
            x: World X coordinate
            z: World Z coordinate

        Returns:
            Terrain height (Y coordinate)

        Note:
            Currently returns estimated height for urban terrain.
            TODO: Parse actual Outskirts heightmap data.
        """
        # TODO: Query actual Outskirts heightmap
        # Urban terrain is mostly flat with slight variations
        import math

        base_height = 5.0  # Slight elevation
        variation = math.sin(x * 0.02) * math.cos(z * 0.02) * 3.0

        return base_height + variation


class MeshTerrainProvider(ITerrainProvider):
    """Terrain provider that queries heights from a 3D mesh (.glb file).

    This provider extracts vertex data from Portal terrain meshes and builds
    a spatial grid for efficient height queries. This is the production solution
    for accurate asset placement on Portal terrains.

    Single Responsibility: Only handles mesh-based terrain height queries.
    Dependency Inversion: Depends on ITerrainProvider abstraction.
    Open/Closed: Can be extended with different interpolation strategies.
    """

    def __init__(self, mesh_path: Path, terrain_size: tuple[float, float]):
        """Initialize mesh terrain provider.

        Args:
            mesh_path: Path to .glb terrain mesh file
            terrain_size: (width, depth) in world units

        Raises:
            FileNotFoundError: If mesh file not found
            TerrainError: If mesh cannot be loaded or parsed
        """
        self.mesh_path = mesh_path
        self.terrain_width, self.terrain_depth = terrain_size

        # Extract vertices from GLB
        self.vertices = self._extract_vertices()

        # Calculate terrain mesh center and bounds from actual vertex positions

        self.mesh_center_x = self.vertices[:, 0].mean()
        self.mesh_center_z = self.vertices[:, 2].mean()
        self.mesh_min_x = self.vertices[:, 0].min()
        self.mesh_max_x = self.vertices[:, 0].max()
        self.mesh_min_z = self.vertices[:, 2].min()
        self.mesh_max_z = self.vertices[:, 2].max()

        # Build spatial grid for fast lookups
        self.grid_resolution = 256
        self.height_grid = self._build_height_grid()

        # Calculate actual bounds
        self.min_height = self.vertices[:, 1].min()
        self.max_height = self.vertices[:, 1].max()

    def _extract_vertices(self) -> "np.ndarray":
        """Extract vertex positions from GLB mesh.

        Returns:
            Numpy array of shape (N, 3) containing vertex positions

        Raises:
            TerrainError: If GLB parsing fails
        """
        import json

        try:
            import numpy as np
        except ImportError as e:
            raise TerrainError("NumPy required for mesh terrain. Run: pip3 install numpy") from e

        try:
            with open(self.mesh_path, "rb") as f:
                # Read GLB header
                magic = f.read(4)
                if magic != b"glTF":
                    raise TerrainError(f"Invalid GLB file: {self.mesh_path}")

                struct.unpack("<I", f.read(4))[0]
                struct.unpack("<I", f.read(4))[0]

                # Read JSON chunk
                json_length = struct.unpack("<I", f.read(4))[0]
                json_type = f.read(4)
                if json_type != b"JSON":
                    raise TerrainError("Expected JSON chunk in GLB")

                json_data = f.read(json_length).decode("utf-8")
                gltf = json.loads(json_data)

                # Read binary chunk
                bin_length = struct.unpack("<I", f.read(4))[0]
                bin_type = f.read(4)
                if bin_type != b"BIN\x00":
                    raise TerrainError("Expected BIN chunk in GLB")

                binary_data = f.read(bin_length)

            # Extract position accessor (first VEC3 accessor)
            accessor = gltf["accessors"][0]
            if accessor["type"] != "VEC3":
                raise TerrainError("First accessor is not VEC3 (positions)")

            buffer_view = gltf["bufferViews"][accessor["bufferView"]]
            offset = buffer_view.get("byteOffset", 0)
            count = accessor["count"]

            # Parse vertices (3 floats per vertex)
            vertices = []
            for i in range(count):
                pos = offset + (i * 12)  # 3 floats * 4 bytes each
                x, y, z = struct.unpack("<fff", binary_data[pos : pos + 12])
                vertices.append([x, y, z])

            return np.array(vertices)

        except Exception as e:
            raise TerrainError(f"Failed to extract vertices from {self.mesh_path}: {e}") from e

    def _build_height_grid(self) -> "np.ndarray":
        """Build 2D grid of heights for fast lookups.

        Projects 3D vertices onto 2D grid and stores maximum height at each cell.
        Uses actual mesh bounds, not assumed centered terrain.

        Returns:
            2D numpy array of heights
        """
        import numpy as np

        grid = np.full((self.grid_resolution, self.grid_resolution), np.nan)

        # Calculate mesh dimensions
        mesh_width = self.mesh_max_x - self.mesh_min_x
        mesh_depth = self.mesh_max_z - self.mesh_min_z

        # Project vertices onto grid using actual mesh bounds
        for x, y, z in self.vertices:
            # Normalize to 0-1 range using actual mesh bounds
            norm_x = (x - self.mesh_min_x) / mesh_width
            norm_z = (z - self.mesh_min_z) / mesh_depth

            # Convert to grid indices
            grid_x = int(norm_x * (self.grid_resolution - 1))
            grid_z = int(norm_z * (self.grid_resolution - 1))

            # Keep maximum height at each grid cell
            if (
                0 <= grid_x < self.grid_resolution
                and 0 <= grid_z < self.grid_resolution
                and (np.isnan(grid[grid_z, grid_x]) or y > grid[grid_z, grid_x])
            ):
                grid[grid_z, grid_x] = y

        # Fill gaps using nearest neighbor interpolation
        self._fill_grid_gaps(grid)

        return grid

    def _fill_grid_gaps(self, grid: "np.ndarray") -> None:
        """Fill NaN values in grid using nearest neighbor propagation.

        Modifies grid in-place.

        Args:
            grid: 2D array with potential NaN values
        """
        import numpy as np

        max_iterations = 100
        iteration = 0

        while np.isnan(grid).any() and iteration < max_iterations:
            for i in range(self.grid_resolution):
                for j in range(self.grid_resolution):
                    if np.isnan(grid[i, j]):
                        # Get valid neighbors
                        neighbors = []
                        if i > 0 and not np.isnan(grid[i - 1, j]):
                            neighbors.append(grid[i - 1, j])
                        if i < self.grid_resolution - 1 and not np.isnan(grid[i + 1, j]):
                            neighbors.append(grid[i + 1, j])
                        if j > 0 and not np.isnan(grid[i, j - 1]):
                            neighbors.append(grid[i, j - 1])
                        if j < self.grid_resolution - 1 and not np.isnan(grid[i, j + 1]):
                            neighbors.append(grid[i, j + 1])

                        if neighbors:
                            grid[i, j] = np.mean(neighbors)

            iteration += 1

        # Fill any remaining NaN with mean height
        if np.isnan(grid).any():
            mean_height = np.nanmean(grid)
            grid[np.isnan(grid)] = mean_height

    def get_height_at(self, x: float, z: float) -> float:
        """Query terrain height at world coordinates.

        Uses bilinear interpolation for smooth height transitions.
        Coordinates are in world space, aligned with mesh position.

        Args:
            x: World X coordinate
            z: World Z coordinate

        Returns:
            Interpolated terrain height

        Raises:
            OutOfBoundsError: If position is outside terrain mesh bounds
        """
        import numpy as np

        # Check bounds using actual mesh bounds
        if x < self.mesh_min_x or x > self.mesh_max_x or z < self.mesh_min_z or z > self.mesh_max_z:
            raise OutOfBoundsError(
                f"Position ({x:.1f}, {z:.1f}) is outside terrain mesh bounds "
                f"[{self.mesh_min_x:.1f}, {self.mesh_max_x:.1f}] x "
                f"[{self.mesh_min_z:.1f}, {self.mesh_max_z:.1f}]"
            )

        # Calculate mesh dimensions
        mesh_width = self.mesh_max_x - self.mesh_min_x
        mesh_depth = self.mesh_max_z - self.mesh_min_z

        # Convert to grid coordinates using actual mesh bounds
        norm_x = (x - self.mesh_min_x) / mesh_width
        norm_z = (z - self.mesh_min_z) / mesh_depth
        grid_x = norm_x * (self.grid_resolution - 1)
        grid_z = norm_z * (self.grid_resolution - 1)

        # Bilinear interpolation
        x0 = int(np.floor(grid_x))
        x1 = min(x0 + 1, self.grid_resolution - 1)
        z0 = int(np.floor(grid_z))
        z1 = min(z0 + 1, self.grid_resolution - 1)

        # Interpolation weights
        wx = grid_x - x0
        wz = grid_z - z0

        # Get corner heights
        h00 = self.height_grid[z0, x0]
        h10 = self.height_grid[z0, x1]
        h01 = self.height_grid[z1, x0]
        h11 = self.height_grid[z1, x1]

        # Bilinear interpolation
        h0 = h00 * (1 - wx) + h10 * wx
        h1 = h01 * (1 - wx) + h11 * wx
        height = h0 * (1 - wz) + h1 * wz

        return float(height)

    def get_bounds(self) -> tuple[Vector3, Vector3]:
        """Get terrain bounds.

        Returns actual mesh bounds from vertex data, not assumed centered bounds.

        Returns:
            Tuple of (min_point, max_point)
        """
        return (
            Vector3(self.mesh_min_x, self.min_height, self.mesh_min_z),
            Vector3(self.mesh_max_x, self.max_height, self.mesh_max_z),
        )


class TerrainEstimator:
    """Estimates terrain characteristics for Portal base maps.

    Single Responsibility: Provides estimated height ranges for Portal terrains.
    Open/Closed: Easy to extend with new map estimates without modification.
    """

    # Terrain height estimates for Portal base maps
    # Format: 'map_name': (min_height, max_height, recommended_fixed_height)
    TERRAIN_ESTIMATES = {
        "MP_Battery": (24.0, 255.0, 140.0),  # Hilly coastal terrain
        "MP_Tungsten": (50.0, 250.0, 150.0),  # Moderate hills
        "MP_Outskirts": (0.0, 50.0, 25.0),  # Flat urban terrain
        "MP_Aftermath": (0.0, 80.0, 40.0),  # Urban with slight elevation
        "MP_Dumbo": (0.0, 100.0, 50.0),  # Mixed urban/natural
        "MP_Capstone": (0.0, 120.0, 60.0),  # Moderate terrain
        "MP_FireStorm": (0.0, 150.0, 75.0),  # Varied terrain
        "MP_Limestone": (0.0, 100.0, 50.0),  # Moderate elevation
        "MP_Abbasid": (0.0, 80.0, 40.0),  # Urban terrain
    }

    @classmethod
    def get_fixed_height(cls, map_name: str) -> float:
        """Get recommended fixed height for a Portal map.

        Args:
            map_name: Portal base map name (e.g., 'MP_Battery')

        Returns:
            Recommended fixed height in meters

        Note:
            Returns middle of terrain range, suitable for manual snapping in Godot.
        """
        if map_name in cls.TERRAIN_ESTIMATES:
            min_h, max_h, fixed_h = cls.TERRAIN_ESTIMATES[map_name]
            return fixed_h
        else:
            # Default: assume moderate terrain
            return 100.0

    @classmethod
    def get_height_range(cls, map_name: str) -> tuple[float, float]:
        """Get estimated height range for a Portal map.

        Args:
            map_name: Portal base map name

        Returns:
            Tuple of (min_height, max_height) in meters
        """
        if map_name in cls.TERRAIN_ESTIMATES:
            min_h, max_h, _ = cls.TERRAIN_ESTIMATES[map_name]
            return (min_h, max_h)
        else:
            return (0.0, 200.0)


class FixedHeightProvider(ITerrainProvider):
    """Terrain provider that returns a fixed height for all positions.

    Used when placing assets at a uniform height for later manual snapping
    in Godot editor. This is the recommended approach as it:
    - Simplifies conversion pipeline (no heightmap sampling needed)
    - Allows visual verification in Godot
    - Lets Godot handle terrain snapping with proper collision detection
    - Preserves horizontal positioning accuracy while deferring vertical

    Single Responsibility: Only provides a constant height value.
    """

    def __init__(self, fixed_height: float, terrain_size: tuple[float, float] = (2048.0, 2048.0)):
        """Initialize fixed height provider.

        Args:
            fixed_height: The constant Y value to return for all queries
            terrain_size: Terrain dimensions (width, depth) for bounds checking
        """
        self.fixed_height = fixed_height
        self.terrain_width, self.terrain_depth = terrain_size

    def get_height_at(self, x: float, z: float) -> float:
        """Query terrain height at world coordinates.

        Args:
            x: World X coordinate
            z: World Z coordinate

        Returns:
            The fixed height value

        Raises:
            OutOfBoundsError: If position is outside terrain bounds
        """
        # Check bounds
        half_width = self.terrain_width / 2
        half_depth = self.terrain_depth / 2

        if abs(x) > half_width or abs(z) > half_depth:
            raise OutOfBoundsError(
                f"Position ({x}, {z}) is outside terrain bounds "
                f"[{-half_width}, {half_width}] x [{-half_depth}, {half_depth}]"
            )

        return self.fixed_height

    def get_bounds(self) -> tuple[Vector3, Vector3]:
        """Get terrain bounds.

        Returns:
            Tuple of (min_point, max_point)
        """
        half_width = self.terrain_width / 2
        half_depth = self.terrain_depth / 2

        return (
            Vector3(-half_width, self.fixed_height, -half_depth),
            Vector3(half_width, self.fixed_height, half_depth),
        )


class HeightAdjuster:
    """Adjusts object heights to sit on terrain.

    Implements IHeightAdjuster interface.
    Open/Closed Principle: Works with any ITerrainProvider implementation.
    """

    def adjust_height(self, transform, terrain: ITerrainProvider, ground_offset: float = 0.0):
        """Adjust object height to sit on terrain.

        Args:
            transform: Original transform
            terrain: Terrain provider for height queries
            ground_offset: Additional offset above ground

        Returns:
            Transform with adjusted Y coordinate

        Raises:
            OutOfBoundsError: If object position is outside terrain bounds
        """
        from ..core.interfaces import Transform

        try:
            terrain_height = terrain.get_height_at(transform.position.x, transform.position.z)

            # Create new position with adjusted height
            from ..core.interfaces import Vector3

            new_position = Vector3(
                transform.position.x, terrain_height + ground_offset, transform.position.z
            )

            return Transform(
                position=new_position, rotation=transform.rotation, scale=transform.scale
            )

        except OutOfBoundsError:
            # Object is out of bounds, return unchanged
            return transform
