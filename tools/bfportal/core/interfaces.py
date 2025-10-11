#!/usr/bin/env python3
"""Core interfaces for the BF Portal conversion toolset.

This module defines all abstract base classes (interfaces) following SOLID principles.
All implementations must adhere to these interfaces for consistency and testability.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum


# ============================================================================
# Data Classes
# ============================================================================

class Team(Enum):
    """Team identifiers."""
    TEAM_1 = 1
    TEAM_2 = 2
    NEUTRAL = 0


@dataclass
class Vector3:
    """3D position vector."""
    x: float
    y: float
    z: float


@dataclass
class Rotation:
    """3D rotation (Euler angles in degrees)."""
    pitch: float  # X-axis rotation
    yaw: float    # Y-axis rotation
    roll: float   # Z-axis rotation


@dataclass
class Transform:
    """Complete 3D transform (position + rotation)."""
    position: Vector3
    rotation: Rotation
    scale: Vector3 = None  # Optional scale

    def __post_init__(self):
        if self.scale is None:
            self.scale = Vector3(1.0, 1.0, 1.0)


@dataclass
class GameObject:
    """Represents a game object (vehicle, building, prop, etc.)."""
    name: str
    asset_type: str  # Original game asset type
    transform: Transform
    team: Team
    properties: Dict  # Additional properties from source game


@dataclass
class SpawnPoint:
    """Player spawn point."""
    name: str
    transform: Transform
    team: Team


@dataclass
class CapturePoint:
    """Conquest-style capture point."""
    name: str
    transform: Transform
    radius: float
    control_area: List[Vector3]  # Polygon points for control area
    team1_spawns: List['SpawnPoint'] = None  # Spawns for Team 1 when captured
    team2_spawns: List['SpawnPoint'] = None  # Spawns for Team 2 when captured

    def __post_init__(self):
        """Initialize spawn lists if not provided."""
        if self.team1_spawns is None:
            self.team1_spawns = []
        if self.team2_spawns is None:
            self.team2_spawns = []


@dataclass
class MapBounds:
    """Map boundaries and playable area."""
    min_point: Vector3
    max_point: Vector3
    combat_area_polygon: List[Vector3]  # 2D polygon (X, Z)
    height: float  # Vertical extent


@dataclass
class MapData:
    """Complete map data extracted from source game."""
    map_name: str
    game_mode: str
    team1_hq: Transform
    team2_hq: Transform
    team1_spawns: List[SpawnPoint]
    team2_spawns: List[SpawnPoint]
    capture_points: List[CapturePoint]
    game_objects: List[GameObject]
    bounds: MapBounds
    metadata: Dict  # Additional map-specific data


@dataclass
class PortalAsset:
    """Portal SDK asset information."""
    type: str  # Portal asset type
    directory: str
    level_restrictions: List[str]  # Maps where this asset is allowed
    properties: Dict


@dataclass
class MapContext:
    """Context for asset mapping decisions."""
    target_base_map: str  # e.g., "MP_Tungsten"
    era: str  # e.g., "WW2", "Modern"
    theme: str  # e.g., "urban", "desert", "forest"
    team: Team


# ============================================================================
# Core Interfaces
# ============================================================================

class IGameEngine(ABC):
    """Interface for game engine implementations.

    Each game (BF1942, Vietnam, BF2, etc.) implements this interface
    to provide game-specific parsing and data extraction.
    """

    @abstractmethod
    def get_game_name(self) -> str:
        """Return the game name (e.g., 'BF1942')."""
        pass

    @abstractmethod
    def get_engine_version(self) -> str:
        """Return the engine version (e.g., 'Refractor 1.0')."""
        pass

    @abstractmethod
    def parse_map(self, map_path: Path) -> MapData:
        """Parse map files and extract all data.

        Args:
            map_path: Path to map directory (extracted RFA)

        Returns:
            Complete MapData structure

        Raises:
            FileNotFoundError: If map files not found
            ParseError: If map files are corrupted or invalid
        """
        pass

    @abstractmethod
    def get_coordinate_system(self) -> 'ICoordinateSystem':
        """Get the coordinate system for this engine."""
        pass


class ICoordinateSystem(ABC):
    """Interface for coordinate system transformations.

    Handles conversions between source game coordinates and Portal coordinates.
    """

    @abstractmethod
    def to_portal(self, position: Vector3) -> Vector3:
        """Convert source game position to Portal coordinates.

        Args:
            position: Position in source game coordinate system

        Returns:
            Position in Portal coordinate system
        """
        pass

    @abstractmethod
    def to_portal_rotation(self, rotation: Rotation) -> Rotation:
        """Convert source game rotation to Portal rotation.

        Args:
            rotation: Rotation in source game coordinate system

        Returns:
            Rotation in Portal coordinate system
        """
        pass

    @abstractmethod
    def get_scale_factor(self) -> float:
        """Get the scale factor between source game and Portal (usually 1.0)."""
        pass


class ICoordinateOffset(ABC):
    """Interface for map center offset calculations.

    Ensures objects from source maps are centered properly on Portal base maps.
    """

    @abstractmethod
    def calculate_centroid(self, objects: List[GameObject]) -> Vector3:
        """Calculate the centroid of all objects.

        Args:
            objects: List of game objects

        Returns:
            Centroid position
        """
        pass

    @abstractmethod
    def calculate_offset(self, source_center: Vector3, target_center: Vector3) -> Vector3:
        """Calculate offset vector between two map centers.

        Args:
            source_center: Center of source map
            target_center: Center of target Portal base map

        Returns:
            Offset vector to apply to all objects
        """
        pass

    @abstractmethod
    def apply_offset(self, transform: Transform, offset: Vector3) -> Transform:
        """Apply offset to a transform.

        Args:
            transform: Original transform
            offset: Offset vector

        Returns:
            Transformed position with offset applied
        """
        pass


class ITerrainProvider(ABC):
    """Interface for terrain height queries.

    Provides terrain height at any XZ coordinate for height adjustment.
    """

    @abstractmethod
    def get_height_at(self, x: float, z: float) -> float:
        """Query terrain height at world coordinates.

        Args:
            x: World X coordinate
            z: World Z coordinate

        Returns:
            Terrain height (Y coordinate) at this position

        Raises:
            OutOfBoundsError: If position is outside terrain bounds
        """
        pass

    @abstractmethod
    def get_bounds(self) -> Tuple[Vector3, Vector3]:
        """Get terrain bounds (min, max).

        Returns:
            Tuple of (min_point, max_point)
        """
        pass


class IHeightAdjuster(ABC):
    """Interface for object height adjustment.

    Ensures objects sit properly on terrain (not underground/floating).
    """

    @abstractmethod
    def adjust_height(self, transform: Transform, terrain: ITerrainProvider,
                     ground_offset: float = 0.0) -> Transform:
        """Adjust object height to sit on terrain.

        Args:
            transform: Original transform
            terrain: Terrain provider for height queries
            ground_offset: Additional offset above ground (e.g., for objects with pivot at top)

        Returns:
            Transform with adjusted Y coordinate
        """
        pass


class IBoundsValidator(ABC):
    """Interface for bounds validation.

    Ensures objects are within the playable CombatArea.
    """

    @abstractmethod
    def is_in_bounds(self, position: Vector3, bounds: MapBounds) -> bool:
        """Check if position is within bounds.

        Args:
            position: Position to check
            bounds: Map bounds

        Returns:
            True if position is within bounds
        """
        pass

    @abstractmethod
    def clamp_to_bounds(self, position: Vector3, bounds: MapBounds) -> Vector3:
        """Clamp position to stay within bounds.

        Args:
            position: Original position
            bounds: Map bounds

        Returns:
            Clamped position
        """
        pass


class IAssetMapper(ABC):
    """Interface for asset mapping.

    Maps source game assets to Portal equivalents using lookup tables.
    """

    @abstractmethod
    def map_asset(self, source_asset: str, context: MapContext) -> Optional[PortalAsset]:
        """Map source game asset to Portal equivalent.

        Args:
            source_asset: Source game asset type
            context: Context for mapping decisions (era, theme, team)

        Returns:
            Portal asset if mapping found, None otherwise
        """
        pass

    @abstractmethod
    def load_mappings(self, mappings_file: Path) -> None:
        """Load asset mappings from JSON file.

        Args:
            mappings_file: Path to mappings JSON file

        Raises:
            FileNotFoundError: If mappings file not found
            ValueError: If mappings file is invalid
        """
        pass


class ISceneGenerator(ABC):
    """Interface for scene generation.

    Generates Portal-compatible scene files (.tscn) from MapData.
    """

    @abstractmethod
    def generate(self, map_data: MapData, output_path: Path,
                base_terrain: str = "MP_Tungsten") -> None:
        """Generate Portal scene file.

        Args:
            map_data: Complete map data
            output_path: Path to output .tscn file
            base_terrain: Base terrain to use (e.g., "MP_Tungsten")

        Raises:
            IOError: If output file cannot be written
        """
        pass

    @abstractmethod
    def validate(self, tscn_path: Path) -> List[str]:
        """Validate generated .tscn file.

        Args:
            tscn_path: Path to .tscn file

        Returns:
            List of validation errors (empty if valid)
        """
        pass


class IParser(ABC):
    """Interface for file parsers.

    Parses game-specific file formats (.con, .sct, etc.).
    """

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the file.

        Args:
            file_path: Path to file

        Returns:
            True if parser can handle this file
        """
        pass

    @abstractmethod
    def parse(self, file_path: Path) -> Dict:
        """Parse file and return data.

        Args:
            file_path: Path to file

        Returns:
            Parsed data as dictionary

        Raises:
            ParseError: If file cannot be parsed
        """
        pass
