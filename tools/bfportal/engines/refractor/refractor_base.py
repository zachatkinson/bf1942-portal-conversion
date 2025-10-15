#!/usr/bin/env python3
"""Base class for Refractor Engine games (BF1942, Vietnam, BF2, BF2142).

This abstract base class implements the Template Method Pattern, providing
shared functionality for all Refractor-based games while allowing subclasses
to customize game-specific behavior.
"""

from abc import abstractmethod
from pathlib import Path

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
from ...parsers.spawner_template_parser import SpawnerTemplateParser


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
            Both Refractor and Godot use Y-up right-handed coordinates.
            However, BF1942 uses +Z as north, while Portal/Godot conventionally
            uses -Z as north. We negate Z to match Portal's orientation.
        """
        # Negate Z-axis to flip north/south orientation
        # BF1942: +Z = north, -Z = south
        # Portal: -Z = north, +Z = south
        return Vector3(position.x, position.y, -position.z)

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
        self.spawn_template_types: set[str] = set()  # Known SpawnPoint template types
        self.spawner_parser = SpawnerTemplateParser()  # Vehicle spawner template parser

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

        # Step 1.5: Load spawn templates (MUST be done before parsing spawns/objects)
        # This establishes single source of truth for what constitutes a spawn point
        self._load_spawn_templates(con_files)

        # Step 1.6: Load vehicle spawner templates
        # This maps spawner names (lighttankspawner) to vehicle types (T34, PanzerIV)
        self._load_vehicle_spawner_templates(map_path)

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

        # Step 6: Extract water bodies from terrain (heightmap + waterLevel)
        water_objects = self._parse_water_bodies(map_path, con_files)
        if water_objects:
            print(f"💧 Water bodies: {len(water_objects)}")
            game_objects.extend(water_objects)

        # Step 7: Calculate map bounds
        bounds = self._calculate_bounds(team1_spawns + team2_spawns, capture_points, game_objects)

        # Step 8: Create MapData
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

    def _load_spawn_templates(self, con_files: ConFileSet) -> None:
        """Load spawn point templates to establish Single Source of Truth.

        Parses template .con files to identify all SpawnPoint type objects.
        This creates a definitive list of what constitutes a spawn point,
        replacing pattern-based detection with type-based detection.

        Single Responsibility: Only loads and stores spawn template types.
        DRY Principle: Spawn detection logic defined once in template files,
                       not repeated across multiple pattern checks.

        Args:
            con_files: ConFileSet with all map .con files

        Note:
            This method establishes the Single Source of Truth for spawn
            point identification. All spawn detection should reference
            self.spawn_template_types rather than using pattern matching.
        """
        parsed_files = con_files.parse_all()

        for _filename, parsed_data in parsed_files.items():
            for obj in parsed_data["objects"]:
                obj_type = obj.get("type", "").lower()

                # If this is a template definition for SpawnPoint
                if obj_type == "spawnpoint":
                    # Store the template name (which becomes the instance type)
                    template_name = obj.get("name", "").lower()
                    if template_name:
                        self.spawn_template_types.add(template_name)

        # Log loaded templates for debugging
        if self.spawn_template_types:
            print(f"   📍 Loaded {len(self.spawn_template_types)} spawn templates")

    def _load_vehicle_spawner_templates(self, map_path: Path) -> None:
        """Load vehicle spawner templates (ObjectSpawnTemplates.con).

        Parses template files to map spawner names to vehicle types.
        This enables automatic vehicle type detection for VehicleSpawner nodes.

        Single Responsibility: Only loads vehicle spawner type mappings.
        DRY Principle: Vehicle assignments defined once in template files.

        Args:
            map_path: Path to map directory

        Note:
            Spawner templates define which vehicles spawn for each team:
            - lighttankspawner: Team 1 = PanzerIV, Team 2 = T34-85
            - heavytankspawner: Team 1 = Tiger, Team 2 = T34
            This is the Single Source of Truth for vehicle→spawner mapping.
        """
        self.spawner_parser.parse_directory(map_path)

        # Log loaded templates for debugging
        template_count = self.spawner_parser.get_template_count()
        if template_count > 0:
            print(f"   🚗 Loaded {template_count} vehicle spawner templates")

    def _is_spawn_point(self, obj_name: str, obj_type: str = "") -> bool:
        """Check if object is a spawn point using template-based detection.

        Single Responsibility: Only checks spawn point identification.
        DRY Principle: Uses loaded templates as Single Source of Truth.
        Open/Closed Principle: Extensible via template loading, not code changes.

        Args:
            obj_name: Lowercase object name
            obj_type: Lowercase object type (optional)

        Returns:
            True if this is a spawn point

        Note:
            This method uses type-based detection against the loaded spawn
            templates (self.spawn_template_types), NOT pattern matching.
            This ensures all spawn points are detected consistently,
            including bot spawns (al_5, ax_6, etc.) that don't match patterns.
        """
        # Exclude control points first
        if "cpoint" in obj_name:
            return False

        # Type-based detection using loaded templates (Single Source of Truth)
        # This catches:
        # - Template definitions: type="spawnpoint"
        # - Template instances: type=template_name (e.g., "al_5", "ax_6", "openbasecammo")
        if obj_type:
            if obj_type == "spawnpoint":
                return True
            if obj_type in self.spawn_template_types:
                return True

        # Fallback: Pattern-based detection for legacy support
        # This should rarely be needed if templates are loaded correctly
        return bool("spawn" in obj_name and "point" in obj_name)

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
        return bool(ownership == "team2" and requested_team == Team.TEAM_2)

    def _parse_spawns(self, con_files: ConFileSet, team: Team) -> list[SpawnPoint]:
        """Parse spawn points for a team.

        Args:
            con_files: ConFileSet with all map .con files
            team: Team to get spawns for

        Returns:
            List of SpawnPoints
        """
        spawns: list[SpawnPoint] = []

        # Parse all .con files to find spawn points
        parsed_files = con_files.parse_all()

        for _filename, parsed_data in parsed_files.items():
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

    def _parse_hq(self, con_files: ConFileSet, team: Team, spawns: list[SpawnPoint]) -> Transform:
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

    def _parse_capture_points(self, con_files: ConFileSet) -> list[CapturePoint]:
        """Parse capture points and their associated spawns.

        Args:
            con_files: ConFileSet with all map .con files

        Returns:
            List of CapturePoints with spawns
        """
        capture_points: list[CapturePoint] = []
        parsed_files = con_files.parse_all()

        # Step 1: Find all control points
        for _filename, parsed_data in parsed_files.items():
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

                    # Auto-generate label (A, B, C, etc.)
                    label = chr(ord('A') + len(capture_points))

                    cp = CapturePoint(
                        name=obj.get("name", f"CP_{len(capture_points) + 1}"),
                        transform=transform,
                        radius=radius,
                        control_area=[],  # TODO: Parse control area polygon
                        label=label,
                    )
                    capture_points.append(cp)

        # Step 2: Find neutral spawns and associate them with capture points
        for _filename, parsed_data in parsed_files.items():
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
                        # __post_init__ ensures these are never None, but need explicit check for mypy
                        cp_team1_spawns = capture_points[cp_index].team1_spawns
                        cp_team2_spawns = capture_points[cp_index].team2_spawns
                        if cp_team1_spawns is not None:
                            cp_team1_spawns.append(spawn)
                        if cp_team2_spawns is not None:
                            cp_team2_spawns.append(spawn)

        # Step 3: Calculate capture point positions from spawn centroids
        # The .con file positions are placeholders - real position is where spawns are
        for cp in capture_points:
            # __post_init__ ensures these are never None, but need explicit check for mypy
            team1_spawns = cp.team1_spawns if cp.team1_spawns is not None else []
            team2_spawns = cp.team2_spawns if cp.team2_spawns is not None else []

            if team1_spawns or team2_spawns:
                all_spawns = team1_spawns + team2_spawns
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

    def _parse_game_objects(self, con_files: ConFileSet) -> list[GameObject]:
        """Parse game objects (vehicles, buildings, props, vehicle spawners).

        Args:
            con_files: ConFileSet with all map .con files

        Returns:
            List of GameObjects (includes vehicle spawners with vehicle type info)
        """
        game_objects = []
        parsed_files = con_files.parse_all()

        for _filename, parsed_data in parsed_files.items():
            for obj in parsed_data["objects"]:
                obj_name = obj.get("name", "").lower()
                obj_type = obj.get("type", "").lower()

                # Handle ObjectSpawners (vehicles and weapon emplacements) specially
                # obj_type will be the spawner template name (e.g., "lighttankspawner")
                # Check if this spawner template is known
                spawner_template = self.spawner_parser.get_template(obj_type)
                if spawner_template:
                    # Categorize spawner types:
                    # 1. Functional weapon emplacements (MG, TOW)
                    # 2. Decorative static props (AA guns, artillery wrecks)
                    # 3. Vehicle spawners (tanks, aircraft, APCs)

                    functional_emplacements = {"machinegunspawner", "antitankgunspawner"}
                    decorative_spawners = {"aagunspawner", "artilleryspawner"}

                    # Functional weapon emplacements (will generate StationaryEmplacementSpawner nodes)
                    if obj_type in functional_emplacements:
                        transform = self.con_parser.parse_transform(obj)
                        if transform:
                            team = self.con_parser.parse_team(obj)
                            properties = obj.get("properties", {}).copy()
                            properties["spawner_type"] = "weapon_emplacement"
                            properties["original_spawner"] = obj_type

                            # Map weapon type for StationaryEmplacementGenerator
                            if obj_type == "machinegunspawner":
                                properties["weapon_type"] = "machinegun"
                            elif obj_type == "antitankgunspawner":
                                properties["weapon_type"] = "tow_launcher"

                            game_objects.append(
                                GameObject(
                                    name=obj["name"],
                                    asset_type="StationaryEmplacementSpawner",
                                    transform=transform,
                                    team=team,
                                    properties=properties,
                                )
                            )
                        continue

                    # Decorative static props (AA guns → sandbags, Artillery → wrecks)
                    if obj_type in decorative_spawners:
                        transform = self.con_parser.parse_transform(obj)
                        if transform:
                            team = self.con_parser.parse_team(obj)
                            properties = obj.get("properties", {}).copy()
                            properties["spawner_type"] = "decorative"
                            properties["original_spawner"] = obj_type

                            game_objects.append(
                                GameObject(
                                    name=obj["name"],
                                    asset_type=obj_type,  # AssetMapper will map to SandBags/WreckTank
                                    transform=transform,
                                    team=team,
                                    properties=properties,
                                )
                            )
                        continue

                    # Regular vehicle spawners (tanks, aircraft, APCs, etc.)
                    transform = self.con_parser.parse_transform(obj)
                    if transform:
                        team = self.con_parser.parse_team(obj)

                        # Get team-specific vehicle type from template
                        vehicle_type = spawner_template.get_vehicle_for_team(team)

                        # If no vehicle type found, use spawner name as fallback
                        if not vehicle_type:
                            vehicle_type = obj_type

                        # Store vehicle type in properties for VehicleSpawnerGenerator
                        properties = obj.get("properties", {}).copy()
                        properties["vehicle_type"] = vehicle_type
                        properties["spawner_template"] = obj_type

                        game_objects.append(
                            GameObject(
                                name=obj["name"],
                                asset_type=vehicle_type,  # Use vehicle type, not spawner template
                                transform=transform,
                                team=team,
                                properties=properties,
                            )
                        )
                    continue

                # Skip control points and spawn points (already handled)
                if obj_type in ["controlpoint", "spawnpoint"]:
                    continue

                # Skip single-player bot spawns (al_5, ax_6, etc.)
                # These are SpawnPoint instances used only in SP campaign
                if self._is_spawn_point(obj_name, obj_type):
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

    def _parse_water_bodies(self, map_path: Path, con_files: ConFileSet) -> list[GameObject]:
        """Extract water bodies from heightmap and terrain config.

        Analyzes heightmap to find terrain below waterLevel, clusters into
        separate lakes, and creates scaled puddle decals for each.

        Args:
            map_path: Path to map directory
            con_files: ConFileSet with terrain config

        Returns:
            List of GameObject representing water surfaces as scaled puddle decals
        """
        import struct

        # Step 1: Parse waterLevel from terrain config
        # waterLevel is defined as: GeometryTemplate.waterLevel 72
        terrain_con = map_path / "Init" / "Terrain.con"
        water_level = None

        if terrain_con.exists():
            content = terrain_con.read_text()
            for line in content.split("\n"):
                if "waterLevel" in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        try:
                            water_level = float(parts[-1])
                            break
                        except ValueError:
                            continue

        if not water_level:
            # No water level defined - skip water extraction
            return []

        # Step 2: Read heightmap
        heightmap_path = map_path / "Heightmap.raw"
        if not heightmap_path.exists():
            return []

        try:
            # Import BF1942 terrain constants
            from ...generators.constants.terrain import BF1942_DEFAULT_HEIGHT_SCALE

            data = heightmap_path.read_bytes()
            size = int((len(data) / 2) ** 0.5)

            # Parse heights and find water pixels
            height_scale = BF1942_DEFAULT_HEIGHT_SCALE
            water_pixels = []

            for y in range(size):
                for x in range(size):
                    idx = y * size + x
                    h = struct.unpack("<H", data[idx * 2 : (idx + 1) * 2])[0]
                    h_scaled = (h / 65535.0) * height_scale
                    if h_scaled < water_level:
                        water_pixels.append((x, y))

            if not water_pixels:
                return []

            # Step 3: Cluster water pixels into separate lakes
            clusters = self._cluster_water_pixels(water_pixels)

            # Step 4: Create puddle decals for each lake
            water_objects = []
            terrain_size = 1024.0  # Typical BF1942 map size
            scale_factor = terrain_size / size

            for i, cluster in enumerate(clusters, 1):
                if len(cluster) < 10:  # Skip tiny puddles (< 10 pixels)
                    continue

                # Calculate bounding box
                min_x = min(p[0] for p in cluster)
                max_x = max(p[0] for p in cluster)
                min_y = min(p[1] for p in cluster)
                max_y = max(p[1] for p in cluster)

                # Convert to world coordinates (centered at origin)
                world_min_x = (min_x * scale_factor) - (terrain_size / 2)
                world_max_x = (max_x * scale_factor) - (terrain_size / 2)
                world_min_z = (min_y * scale_factor) - (terrain_size / 2)
                world_max_z = (max_y * scale_factor) - (terrain_size / 2)

                # Lake center and dimensions
                center_x = (world_min_x + world_max_x) / 2
                center_z = (world_min_z + world_max_z) / 2
                width = world_max_x - world_min_x
                length = world_max_z - world_min_z

                # Create scaled puddle decal
                # Scale transform: (scale_x, scale_y, scale_z)
                # Puddle decals are small by default (~10m), so scale to match lake size
                scale_x = width / 10.0  # Assume default puddle is ~10m wide
                scale_z = length / 10.0

                water_objects.append(
                    GameObject(
                        name=f"Lake_{i}",
                        asset_type="Decal_PuddleLong_01",
                        transform=Transform(
                            position=Vector3(center_x, water_level, center_z),
                            rotation=Rotation(0, 0, 0),
                            scale=Vector3(scale_x, 1.0, scale_z),
                        ),
                        team=Team.NEUTRAL,
                        properties={"water_body": True, "dimensions": f"{width:.0f}x{length:.0f}"},
                    )
                )

            return water_objects

        except Exception as e:
            print(f"  ⚠️  Failed to extract water bodies: {e}")
            return []

    def _cluster_water_pixels(self, pixels: list[tuple[int, int]]) -> list[list[tuple[int, int]]]:
        """Group water pixels into separate clusters (lakes).

        Args:
            pixels: List of (x, y) heightmap coordinates below waterLevel

        Returns:
            List of clusters, each cluster is a list of pixels
        """
        clusters = []
        used = set()

        for px, py in pixels:
            if (px, py) in used:
                continue

            # Start new cluster (BFS)
            cluster = [(px, py)]
            used.add((px, py))
            queue = [(px, py)]

            while queue:
                cx, cy = queue.pop(0)
                # Check 8-connected neighbors
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = cx + dx, cy + dy
                        if (nx, ny) in pixels and (nx, ny) not in used:
                            cluster.append((nx, ny))
                            used.add((nx, ny))
                            queue.append((nx, ny))

            clusters.append(cluster)

        return clusters

    def _calculate_bounds(
        self,
        spawns: list[SpawnPoint],
        capture_points: list[CapturePoint],
        objects: list[GameObject],
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
