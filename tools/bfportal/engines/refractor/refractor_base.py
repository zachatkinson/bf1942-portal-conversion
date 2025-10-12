#!/usr/bin/env python3
"""Base class for Refractor Engine games (BF1942, Vietnam, BF2, BF2142).

This abstract base class implements the Template Method Pattern, providing
shared functionality for all Refractor-based games while allowing subclasses
to customize game-specific behavior.
"""

from abc import abstractmethod
from pathlib import Path
from typing import List

from ...core.interfaces import (
    CapturePoint,
    GameObject,
    ICoordinateSystem,
    IGameEngine,
    MapBounds,
    MapData,
    Rotation,
    SpawnPoint,
    Team,
    Transform,
    Vector3,
)
from ...parsers.con_parser import ConFileSet, ConParser


class RefractorCoordinateSystem(ICoordinateSystem):
    """Coordinate system for Refractor Engine games.

    Refractor uses right-handed Y-up coordinate system, same as Godot.
    However, we may need axis swaps or scale adjustments.
    """

    def to_portal(self, position: Vector3) -> Vector3:
        """Convert Refractor position to Portal coordinates.

        Args:
            position: Position in Refractor coordinate system

        Returns:
            Position in Portal coordinate system

        Note:
            Both Refractor and Godot use Y-up, so conversion is minimal.
            May need to adjust in subclasses if specific games differ.
        """
        # For now, direct conversion (both Y-up, right-handed)
        # Subclasses can override if needed
        return Vector3(position.x, position.y, position.z)

    def to_portal_rotation(self, rotation: Rotation) -> Rotation:
        """Convert Refractor rotation to Portal rotation.

        Args:
            rotation: Rotation in Refractor coordinate system

        Returns:
            Rotation in Portal coordinate system
        """
        # Both use Euler angles, but may need axis adjustments
        # Subclasses can override if needed
        return Rotation(rotation.pitch, rotation.yaw, rotation.roll)

    def get_scale_factor(self) -> float:
        """Get the scale factor between Refractor and Portal.

        Returns:
            1.0 (both use meters)
        """
        return 1.0


class RefractorEngine(IGameEngine):
    """Base class for all Refractor Engine implementations.

    This class provides shared functionality for parsing .con files,
    extracting map data, and converting to Portal format.

    Subclasses (BF1942Engine, BFVietnamEngine, etc.) customize:
    - Game name and version
    - Asset-specific parsing
    - Game-specific features
    """

    def __init__(self):
        """Initialize RefractorEngine."""
        self.con_parser = ConParser()
        self.coordinate_system = RefractorCoordinateSystem()

    # ========================================================================
    # Abstract Methods (Subclasses MUST implement)
    # ========================================================================

    @abstractmethod
    def get_game_name(self) -> str:
        """Return the game name (e.g., 'BF1942')."""

    @abstractmethod
    def get_engine_version(self) -> str:
        """Return the engine version (e.g., 'Refractor 1.0')."""

    @abstractmethod
    def get_game_mode_default(self) -> str:
        """Return default game mode for this game (e.g., 'Conquest')."""

    # ========================================================================
    # Template Method (Defines algorithm, subclasses customize steps)
    # ========================================================================

    def parse_map(self, map_path: Path) -> MapData:
        """Parse map files and extract all data.

        This is the Template Method that defines the parsing algorithm.
        Subclasses customize behavior via hook methods.

        Args:
            map_path: Path to map directory (extracted RFA)

        Returns:
            Complete MapData structure

        Raises:
            FileNotFoundError: If map files not found
            ParseError: If map files are corrupted or invalid
        """
        if not map_path.exists():
            raise FileNotFoundError(f"Map directory not found: {map_path}")

        print(f"{'=' * 70}")
        print(f"Parsing {self.get_game_name()} Map: {map_path.name}")
        print(f"{'=' * 70}")

        # Step 1: Load all .con files
        con_files = ConFileSet(map_path)
        print(f"📁 Found {len(con_files.con_files)} .con files")

        # Step 2: Parse spawn points
        team1_spawns = self._parse_spawns(con_files, Team.TEAM_1)
        team2_spawns = self._parse_spawns(con_files, Team.TEAM_2)
        print(f"🔫 Team 1 spawns: {len(team1_spawns)}")
        print(f"🔫 Team 2 spawns: {len(team2_spawns)}")

        # Step 3: Parse HQ positions (estimate from spawns if not explicit)
        team1_hq = self._parse_hq(con_files, Team.TEAM_1, team1_spawns)
        team2_hq = self._parse_hq(con_files, Team.TEAM_2, team2_spawns)

        # Step 4: Parse capture points
        capture_points = self._parse_capture_points(con_files)
        print(f"🚩 Capture points: {len(capture_points)}")

        # Step 5: Parse game objects (vehicles, buildings, props)
        game_objects = self._parse_game_objects(con_files)
        print(f"📦 Game objects: {len(game_objects)}")

        # Step 6: Calculate map bounds
        bounds = self._calculate_bounds(team1_spawns + team2_spawns, capture_points, game_objects)

        # Step 7: Create MapData
        map_data = MapData(
            map_name=map_path.name,
            game_mode=self.get_game_mode_default(),
            team1_hq=team1_hq,
            team2_hq=team2_hq,
            team1_spawns=team1_spawns,
            team2_spawns=team2_spawns,
            capture_points=capture_points,
            game_objects=game_objects,
            bounds=bounds,
            metadata={
                "game": self.get_game_name(),
                "engine": self.get_engine_version(),
                "source_path": str(map_path),
            },
        )

        print("✅ Map parsing complete")
        return map_data

    def get_coordinate_system(self) -> ICoordinateSystem:
        """Get the coordinate system for this engine."""
        return self.coordinate_system

    # ========================================================================
    # Hook Methods (Subclasses CAN override for customization)
    # ========================================================================

    def _is_spawn_point(self, obj_name: str, obj_type: str = "") -> bool:
        """Check if object name or type indicates a spawn point.

        Single Responsibility: Only checks spawn point identification logic.

        Args:
            obj_name: Lowercase object name
            obj_type: Lowercase object type (optional)

        Returns:
            True if this is a spawn point
        """
        # Exclude control points first
        if "cpoint" in obj_name:
            return False

        # Check if type is SpawnPoint (template) or contains SpawnPoint
        if obj_type and "spawnpoint" in obj_type:
            return True

        # Check name for spawn point pattern
        if "spawn" in obj_name and "point" in obj_name:
            return True

        # Check for spawn instance pattern: name_groupnum_spawnnum (e.g., openbasecammo_4_13)
        # These are instances created from SpawnPoint templates but have instance name as type
        import re

        if re.search(r"_\d+_\d+$", obj_name):
            # Has pattern like _X_Y at end, likely a spawn instance
            # Also check if it has spawn-related keywords
            if "spawn" in obj_name or "open" in obj_name or "base" in obj_name:
                return True

        return False

    def _classify_spawn_ownership(self, obj_name: str) -> str:
        """Classify spawn point ownership by team.

        Single Responsibility: Only determines team ownership classification.

        Args:
            obj_name: Lowercase object name

        Returns:
            'team1', 'team2', or 'neutral'
        """
        # Team-specific spawns
        if "axis" in obj_name or "_1_" in obj_name:
            return "team1"
        if "allies" in obj_name or "_2_" in obj_name:
            return "team2"

        # Neutral spawns (open bases, capture points)
        # Pattern: _3_, _4_, 'open', etc.
        return "neutral"

    def _should_include_spawn_for_team(self, ownership: str, requested_team: Team) -> bool:
        """Determine if spawn should be included for requested team.

        Single Responsibility: Only decides inclusion logic.
        Open/Closed Principle: Can extend with new ownership types without modifying.

        Args:
            ownership: 'team1', 'team2', or 'neutral'
            requested_team: Team being parsed

        Returns:
            True if spawn should be included
        """
        # Neutral spawns belong to capture points, NOT team HQs
        # They will be handled separately in _parse_capture_points
        if ownership == "neutral":
            return False
        if ownership == "team1" and requested_team == Team.TEAM_1:
            return True
        if ownership == "team2" and requested_team == Team.TEAM_2:
            return True

        return False

    def _parse_spawns(self, con_files: ConFileSet, team: Team) -> List[SpawnPoint]:
        """Parse spawn points for a team.

        Args:
            con_files: ConFileSet with all map .con files
            team: Team to get spawns for

        Returns:
            List of SpawnPoints
        """
        spawns = []

        # Parse all .con files to find spawn points
        parsed_files = con_files.parse_all()

        for filename, parsed_data in parsed_files.items():
            for obj in parsed_data["objects"]:
                obj_name = obj.get("name", "").lower()
                obj_type = obj.get("type", "").lower()

                # Step 1: Check if this is a spawn point
                if not self._is_spawn_point(obj_name, obj_type):
                    continue

                # Step 2: Classify ownership
                ownership = self._classify_spawn_ownership(obj_name)

                # Step 3: Check if this spawn belongs to requested team
                if not self._should_include_spawn_for_team(ownership, team):
                    continue

                # Step 4: Extract transform and create spawn point
                transform = self.con_parser.parse_transform(obj)
                if transform:
                    spawns.append(
                        SpawnPoint(
                            name=obj.get("name", f"Spawn_{team.value}_{len(spawns) + 1}"),
                            transform=transform,
                            team=team,
                        )
                    )

        # Warn if too few spawns
        if len(spawns) < 4:
            print(
                f"  ⚠️  Only {len(spawns)} spawns found for team {team.value}. Portal requires minimum 4."
            )

        return spawns

    def _parse_hq(self, con_files: ConFileSet, team: Team, spawns: List[SpawnPoint]) -> Transform:
        """Parse HQ position from spawn centroid.

        Args:
            con_files: ConFileSet with all map .con files
            team: Team to get HQ for
            spawns: Spawn points for this team (for centroid calculation)

        Returns:
            HQ Transform

        Note:
            We calculate HQ position as the centroid of its spawns, NOT from
            the .con file position, because the .con file position is often
            just a placeholder (0, Y, 0) and doesn't reflect actual gameplay position.
        """
        # Calculate centroid of spawns (this is where the HQ actually is in gameplay)
        if spawns:
            total_x = sum(s.transform.position.x for s in spawns)
            total_y = sum(s.transform.position.y for s in spawns)
            total_z = sum(s.transform.position.z for s in spawns)
            count = len(spawns)

            return Transform(
                position=Vector3(total_x / count, total_y / count, total_z / count),
                rotation=Rotation(0, 0, 0),
            )

        # Fallback: Default position (shouldn't happen if spawns are parsed correctly)
        return Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0))

    def _parse_capture_points(self, con_files: ConFileSet) -> List[CapturePoint]:
        """Parse capture points and their associated spawns.

        Args:
            con_files: ConFileSet with all map .con files

        Returns:
            List of CapturePoints with spawns
        """
        capture_points = []
        parsed_files = con_files.parse_all()

        # Step 1: Find all control points
        for filename, parsed_data in parsed_files.items():
            for obj in parsed_data["objects"]:
                obj_name = obj.get("name", "").lower()
                obj_type = obj.get("type", "").lower()

                # Check if this is a control point by type (not name pattern)
                if obj_type != "controlpoint":
                    continue

                # Skip HQ bases - those are handled by _parse_hq()
                if "base" in obj_name and (
                    "axis" in obj_name
                    or "allies" in obj_name
                    or "_1_" in obj_name
                    or "_2_" in obj_name
                ):
                    continue

                # This is a neutral/contestable capture point
                transform = self.con_parser.parse_transform(obj)
                if transform:
                    # Default radius (can be overridden in subclasses)
                    radius = float(obj.get("properties", {}).get("radius", 50.0))

                    cp = CapturePoint(
                        name=obj.get("name", f"CP_{len(capture_points) + 1}"),
                        transform=transform,
                        radius=radius,
                        control_area=[],  # TODO: Parse control area polygon
                    )
                    capture_points.append(cp)

        # Step 2: Find neutral spawns and associate them with capture points
        for filename, parsed_data in parsed_files.items():
            for obj in parsed_data["objects"]:
                obj_name = obj.get("name", "").lower()
                obj_type = obj.get("type", "").lower()

                # Check if this is a spawn point
                if not self._is_spawn_point(obj_name, obj_type):
                    continue

                # Check if it's a neutral spawn
                ownership = self._classify_spawn_ownership(obj_name)
                if ownership != "neutral":
                    continue

                # Extract spawn group number (e.g., _3_, _4_)
                # This tells us which capture point it belongs to
                import re

                match = re.search(r"_(\d+)_", obj_name)
                if not match:
                    continue

                group_num = int(match.group(1))
                # Capture point index is group_num - 3 (since CP 1 and 2 are HQs)
                cp_index = group_num - 3

                if 0 <= cp_index < len(capture_points):
                    transform = self.con_parser.parse_transform(obj)
                    if transform:
                        # Create spawn point (belongs to both teams when captured)
                        spawn = SpawnPoint(
                            name=obj.get("name", f"NeutralSpawn_{group_num}"),
                            transform=transform,
                            team=Team.NEUTRAL,
                        )
                        # Add to both team spawn lists for this capture point
                        capture_points[cp_index].team1_spawns.append(spawn)
                        capture_points[cp_index].team2_spawns.append(spawn)

        # Step 3: Calculate capture point positions from spawn centroids
        # The .con file positions are placeholders - real position is where spawns are
        for cp in capture_points:
            if cp.team1_spawns or cp.team2_spawns:
                all_spawns = cp.team1_spawns + cp.team2_spawns
                total_x = sum(s.transform.position.x for s in all_spawns)
                total_y = sum(s.transform.position.y for s in all_spawns)
                total_z = sum(s.transform.position.z for s in all_spawns)
                count = len(all_spawns)

                # Update CP transform to be at centroid of its spawns
                cp.transform = Transform(
                    position=Vector3(total_x / count, total_y / count, total_z / count),
                    rotation=cp.transform.rotation,  # Keep original rotation
                )

        return capture_points

    def _parse_game_objects(self, con_files: ConFileSet) -> List[GameObject]:
        """Parse game objects (vehicles, buildings, props).

        Args:
            con_files: ConFileSet with all map .con files

        Returns:
            List of GameObjects
        """
        game_objects = []
        parsed_files = con_files.parse_all()

        for filename, parsed_data in parsed_files.items():
            for obj in parsed_data["objects"]:
                # Skip spawners and control points (already handled)
                if obj["type"] in ["ObjectSpawner", "ControlPoint"]:
                    continue

                transform = self.con_parser.parse_transform(obj)
                if transform:
                    team = self.con_parser.parse_team(obj)

                    game_objects.append(
                        GameObject(
                            name=obj["name"],
                            asset_type=obj["type"],
                            transform=transform,
                            team=team,
                            properties=obj["properties"],
                        )
                    )

        return game_objects

    def _calculate_bounds(
        self,
        spawns: List[SpawnPoint],
        capture_points: List[CapturePoint],
        objects: List[GameObject],
    ) -> MapBounds:
        """Calculate map bounds from all objects.

        Args:
            spawns: All spawn points
            capture_points: All capture points
            objects: All game objects

        Returns:
            MapBounds
        """
        all_positions = []

        # Collect all positions
        for spawn in spawns:
            all_positions.append(spawn.transform.position)

        for cp in capture_points:
            all_positions.append(cp.transform.position)

        for obj in objects:
            all_positions.append(obj.transform.position)

        if not all_positions:
            # Default bounds
            return MapBounds(
                min_point=Vector3(-1000, 0, -1000),
                max_point=Vector3(1000, 200, 1000),
                combat_area_polygon=[],
                height=200,
            )

        # Calculate min/max
        min_x = min(p.x for p in all_positions)
        max_x = max(p.x for p in all_positions)
        min_y = min(p.y for p in all_positions)
        max_y = max(p.y for p in all_positions)
        min_z = min(p.z for p in all_positions)
        max_z = max(p.z for p in all_positions)

        # Add padding (10%)
        padding = 0.1
        width = max_x - min_x
        depth = max_z - min_z

        min_x -= width * padding
        max_x += width * padding
        min_z -= depth * padding
        max_z += depth * padding

        return MapBounds(
            min_point=Vector3(min_x, min_y, min_z),
            max_point=Vector3(max_x, max_y, max_z),
            combat_area_polygon=[],  # TODO: Generate polygon from bounds
            height=max_y - min_y + 100,  # Add 100m vertical buffer
        )
