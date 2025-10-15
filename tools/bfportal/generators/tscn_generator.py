#!/usr/bin/env python3
"""Production TSCN Generator - Creates complete Portal-compatible .tscn files.

This generator creates full Godot 4 scene files with all Portal requirements:
- ExtResource references
- HQ nodes with spawn assignments
- Combat area with polygon boundaries
- Capture points (if applicable)
- Vehicle spawners
- Proper node hierarchy
- Resource management

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-11
"""
# ruff: noqa: F405

import json
import math
from pathlib import Path

from ..core.exceptions import ValidationError
from ..core.interfaces import (
    CapturePoint,
    GameObject,
    ISceneGenerator,
    MapData,
    Transform,
    Vector3,
)
from ..transforms.centering_service import CenteringService
from .components.asset_registry import AssetRegistry
from .components.transform_formatter import TransformFormatter
from .constants import *  # Import all constants from modular constants package  # noqa: F403, F405
from .node_generators.stationary_emplacement_generator import StationaryEmplacementGenerator
from .node_generators.vehicle_spawner_generator import VehicleSpawnerGenerator


class TscnGenerator(ISceneGenerator):
    """Production-quality .tscn scene generator.

    Generates complete Godot 4 scenes with all Portal-required components.
    """

    def __init__(self, centering_service: CenteringService | None = None):
        """Initialize generator.

        Args:
            centering_service: Optional centering service for SOLID dependency injection.
                              If None, creates a new instance.
        """
        self.ext_resources: list[dict] = []
        self.next_ext_resource_id = 1
        self.base_terrain: str = ""
        self.terrain_y_offset: float = 0.0
        self.terrain_center_x: float = 0.0  # Terrain mesh center X coordinate
        self.terrain_center_z: float = 0.0  # Terrain mesh center Z coordinate
        self.terrain_bounds: tuple[float, float, float, float] | None = (
            None  # (min_x, max_x, min_z, max_z)
        )
        self.min_safe_y: float = 0.0  # Minimum safe Y for object placement (above terrain)
        self.asset_type_to_ext_id: dict[str, str] = {}  # Maps asset type to ExtResource ID
        self.asset_catalog: dict[str, dict] = {}  # Maps asset type to Portal metadata
        self._load_asset_catalog()

        # SOLID: Dependency Injection - Use specialized generators
        self.vehicle_spawner_generator = VehicleSpawnerGenerator()
        self.stationary_emplacement_generator = StationaryEmplacementGenerator()
        self.transform_formatter = TransformFormatter()
        self.asset_registry = AssetRegistry()  # Tracks ExtResource IDs
        self.centering_service = centering_service or CenteringService()  # DRY centering logic

    def _load_asset_catalog(self) -> None:
        """Load Portal asset catalog from asset_types.json."""
        from .constants.paths import get_asset_types_path

        catalog_path = get_asset_types_path()

        if not catalog_path.exists():
            print(f"⚠️  Warning: asset_types.json not found at {catalog_path}")
            return

        try:
            with open(catalog_path) as f:
                data = json.load(f)
                for asset in data.get("AssetTypes", []):
                    asset_type = asset.get("type")
                    directory = asset.get("directory", "")
                    if asset_type:
                        self.asset_catalog[asset_type] = {
                            "directory": directory,
                            "level_restrictions": asset.get("levelRestrictions", []),
                        }
        except Exception as e:
            print(f"⚠️  Warning: Failed to load asset catalog: {e}")

    def _get_asset_scene_path(self, asset_type: str) -> str | None:
        """Get Godot scene path for an asset type.

        Args:
            asset_type: Asset type name (e.g., "Birch_01_L")

        Returns:
            Scene path (e.g., "res://objects/.../Birch_01_L.tscn") or None if not found
        """
        # DEBUG FLAG - only log first few assets to avoid spam
        if not hasattr(self, "_debug_asset_count"):
            self._debug_asset_count = 0
        debug_this = self._debug_asset_count < DEBUG_ASSET_LOG_LIMIT
        if debug_this:
            self._debug_asset_count += 1

        # First check asset catalog
        if asset_type in self.asset_catalog:
            directory = self.asset_catalog[asset_type]["directory"]

            if debug_this:
                print(f"\n   🔍 DEBUG: Looking for {asset_type}")
                print(f"      Catalog directory: {directory}")

            # Portal SDK structure:
            # NOTE: The catalog's "directory" field already contains the FULL path including
            # "Generic/Common/" prefix when applicable. We should NOT prepend it again.
            # - Map-specific: res://objects/<MapName>/<Terrain>/directory/asset.tscn
            # - Shared: res://objects/Shared/directory/asset.tscn

            # Try map-specific and shared paths
            if self.base_terrain == "MP_Tungsten":
                paths_to_try = [
                    # Tajikistan/MP_Tungsten map-specific path
                    f"res://objects/Tajikistan/{self.base_terrain}/{directory}/{asset_type}.tscn",
                    # Tajikistan/Shared (region-specific shared assets)
                    f"res://objects/Tajikistan/Shared/{directory}/{asset_type}.tscn",
                    # Shared path (most common)
                    f"res://objects/Shared/{directory}/{asset_type}.tscn",
                    # Global fallback
                    f"res://objects/Global/{directory}/{asset_type}.tscn",
                ]
            else:
                # For other maps, use standard paths
                paths_to_try = [
                    f"res://objects/Shared/{directory}/{asset_type}.tscn",
                    f"res://objects/Global/{directory}/{asset_type}.tscn",
                ]

            # Check which path actually exists on disk
            # Handle both running from Portal SDK root and from GodotProject
            cwd = Path.cwd()
            if cwd.name == "GodotProject" or (cwd / "project.godot").exists():
                # Already in GodotProject directory
                project_root = cwd
            else:
                # In Portal SDK root, navigate to GodotProject
                project_root = cwd / "GodotProject"

            if debug_this:
                print(f"      Project root: {project_root}")
                print("      Trying paths:")

            for res_path in paths_to_try:
                # Convert res:// path to filesystem path
                fs_path = project_root / res_path.replace("res://", "")
                if debug_this:
                    exists_str = "✅ FOUND" if fs_path.exists() else "❌ Not found"
                    print(f"         {res_path}")
                    print(f"            → {fs_path} [{exists_str}]")
                if fs_path.exists():
                    return res_path

            # If none exist, return None to signal asset not found
            if debug_this:
                print(f"      ⚠️  No valid path found for {asset_type}")
            return None
        else:
            if debug_this:
                print(f"\n   ⚠️  DEBUG: {asset_type} NOT in catalog")
            return None

    def generate(
        self,
        map_data: MapData,
        output_path: Path,
        base_terrain: str = "MP_Tungsten",
        terrain_y_offset: float = 0.0,
        terrain_center_x: float = 0.0,
        terrain_center_z: float = 0.0,
        rotate_terrain: bool = False,
        terrain_bounds: tuple[float, float, float, float] | None = None,
    ) -> None:
        """Generate .tscn file from map data.

        Args:
            map_data: Parsed and transformed map data
            output_path: Output .tscn file path
            base_terrain: Portal base terrain name (e.g., "MP_Tungsten")
            terrain_y_offset: Y offset to apply to terrain mesh (to normalize to Y=0 baseline)
            terrain_center_x: X coordinate of terrain mesh center (for centering at origin)
            terrain_center_z: Z coordinate of terrain mesh center (for centering at origin)
            rotate_terrain: If True, rotate terrain 90° CW and adjust CombatArea accordingly
            terrain_bounds: Optional terrain mesh bounds as (min_x, max_x, min_z, max_z)

        Raises:
            ValidationError: If map data is invalid
        """
        self.base_terrain = base_terrain
        self.terrain_y_offset = terrain_y_offset
        self.terrain_center_x = terrain_center_x
        self.terrain_center_z = terrain_center_z
        self.terrain_bounds = terrain_bounds

        # Calculate minimum safe Y for object placement (above terrain)
        # This ensures all physical objects start ABOVE terrain so terrain snapping can work
        if map_data.bounds and map_data.bounds.max_point:
            terrain_max_y = map_data.bounds.max_point.y
            self.min_safe_y = terrain_max_y + INITIAL_PLACEMENT_SAFETY_CLEARANCE_M
        else:
            # Fallback: use terrain Y offset + safety clearance
            self.min_safe_y = terrain_y_offset + INITIAL_PLACEMENT_SAFETY_CLEARANCE_M

        # Store rotation flag for use in generation
        if rotate_terrain:
            map_data.metadata["terrain_rotation"] = 90  # 90° CW
        else:
            map_data.metadata["terrain_rotation"] = 0
        # Validate map data
        self._validate_map_data(map_data)

        # Initialize ext_resources (gameplay assets only - static assets added later)
        self._init_ext_resources()

        # Pre-register all static object assets before writing file
        self._register_static_assets(map_data)

        # Build scene content
        lines = []

        # Header
        load_steps = len(self.ext_resources) + 1
        lines.append(f"[gd_scene load_steps={load_steps} format={TSCN_FORMAT_VERSION}]")
        lines.append("")

        # ExtResources
        for resource in self.ext_resources:
            lines.append(
                f'[ext_resource type="{resource["type"]}" '
                f'path="{resource["path"]}" id="{resource["id"]}"]'
            )
        lines.append("")

        # Root node - use base_terrain name for Portal level restriction validation
        lines.append(f'[node name="{self.base_terrain}" type="Node3D"]')
        lines.append("")

        # Combat area (must be at root level, not in Static)
        lines.extend(self._generate_combat_area(map_data))

        # Deploy camera (REQUIRED for spawn screen to work correctly)
        lines.extend(self._generate_deploy_cam(map_data))

        # Static layer declaration (MUST come before any nodes with parent="Static")
        lines.extend(self._generate_static_layer_declaration())

        # Terrain and assets FIRST (provide collision surfaces for snapping)
        lines.extend(self._generate_terrain_and_assets(map_data))

        # Team HQs and spawns (can now snap to terrain above)
        lines.extend(self._generate_hqs(map_data))

        # Capture points (can now snap to terrain)
        if map_data.capture_points:
            lines.extend(self._generate_capture_points(map_data.capture_points))

        # Vehicle spawners (can now snap to terrain)
        # Pass full map_data so generator has access to HQ positions for team assignment
        vehicle_spawners = [
            obj
            for obj in map_data.game_objects
            if "vehicle_type" in obj.properties or "spawner" in obj.asset_type.lower()
        ]
        if vehicle_spawners:
            lines.extend(self._generate_vehicle_spawners(map_data))

        # Stationary weapon emplacements (can now snap to terrain)
        stationary_emplacements = [
            obj for obj in map_data.game_objects if obj.asset_type == "StationaryEmplacementSpawner"
        ]
        if stationary_emplacements:
            lines.extend(self._generate_stationary_emplacements(stationary_emplacements))

        # Other static objects (decorative props, trees, etc.)
        lines.extend(self._generate_static_objects(map_data))

        # Write file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write("\n".join(lines))

    def _validate_map_data(self, map_data: MapData) -> None:
        """Validate map data has required components.

        Args:
            map_data: Map data to validate

        Raises:
            ValidationError: If required components missing
        """
        # Check for HQs (stored as transforms in MapData)
        if not map_data.team1_hq:
            raise ValidationError(ERROR_MISSING_TEAM1_HQ)
        if not map_data.team2_hq:
            raise ValidationError(ERROR_MISSING_TEAM2_HQ)

        # Check for spawns
        if len(map_data.team1_spawns) < MIN_SPAWNS_PER_TEAM:
            raise ValidationError(
                ERROR_INSUFFICIENT_TEAM1_SPAWNS.format(
                    min=MIN_SPAWNS_PER_TEAM, actual=len(map_data.team1_spawns)
                )
            )
        if len(map_data.team2_spawns) < MIN_SPAWNS_PER_TEAM:
            raise ValidationError(
                ERROR_INSUFFICIENT_TEAM2_SPAWNS.format(
                    min=MIN_SPAWNS_PER_TEAM, actual=len(map_data.team2_spawns)
                )
            )

    def _init_ext_resources(self) -> None:
        """Initialize ExtResource list with Portal SDK paths.

        DRY/SOLID: Uses constants from constants package to avoid hardcoded values.
        """
        self.ext_resources = [
            {
                "id": EXT_RESOURCE_HQ_SPAWNER,
                "type": "PackedScene",
                "path": SCENE_PATH_HQ_SPAWNER,
            },
            {
                "id": EXT_RESOURCE_SPAWN_POINT,
                "type": "PackedScene",
                "path": SCENE_PATH_SPAWN_POINT,
            },
            {
                "id": EXT_RESOURCE_CAPTURE_POINT,
                "type": "PackedScene",
                "path": SCENE_PATH_CAPTURE_POINT,
            },
            {
                "id": EXT_RESOURCE_VEHICLE_SPAWNER,
                "type": "PackedScene",
                "path": SCENE_PATH_VEHICLE_SPAWNER,
            },
            {
                "id": EXT_RESOURCE_STATIONARY_EMPLACEMENT,
                "type": "PackedScene",
                "path": SCENE_PATH_STATIONARY_EMPLACEMENT,
            },
            {
                "id": EXT_RESOURCE_COMBAT_AREA,
                "type": "PackedScene",
                "path": SCENE_PATH_COMBAT_AREA,
            },
            {
                "id": EXT_RESOURCE_DEPLOY_CAM,
                "type": "PackedScene",
                "path": SCENE_PATH_DEPLOY_CAM,
            },
            {
                "id": EXT_RESOURCE_TERRAIN,
                "type": "PackedScene",
                "path": SCENE_PATH_TERRAIN_FORMAT.format(base_terrain=self.base_terrain),
            },
            {
                "id": EXT_RESOURCE_ASSETS,
                "type": "PackedScene",
                "path": SCENE_PATH_ASSETS_FORMAT.format(base_terrain=self.base_terrain),
            },
            {
                "id": EXT_RESOURCE_POLYGON_VOLUME,
                "type": "PackedScene",
                "path": SCENE_PATH_POLYGON_VOLUME,
            },
            {
                "id": EXT_RESOURCE_WORLD_ICON,
                "type": "PackedScene",
                "path": SCENE_PATH_WORLD_ICON,
            },
        ]
        self.next_ext_resource_id = int(EXT_RESOURCE_STATIC_ASSETS_START)

    def _register_static_assets(self, map_data: MapData) -> None:
        """Pre-register all static object assets as ExtResources.

        Args:
            map_data: Map data containing game objects
        """
        # Filter static objects (same logic as in _generate_static_layer)
        # DRY: Use GAMEPLAY_KEYWORDS constant to avoid duplicated filtering logic
        static_objects = [
            obj
            for obj in map_data.game_objects
            if not any(keyword in obj.asset_type.lower() for keyword in GAMEPLAY_KEYWORDS)
        ]

        # Collect unique asset types and register them
        unique_assets = {obj.asset_type for obj in static_objects}
        assets_registered = 0
        assets_missing = 0

        for asset_type in sorted(unique_assets):  # Sort for deterministic output
            if asset_type not in self.asset_type_to_ext_id:
                scene_path = self._get_asset_scene_path(asset_type)
                if scene_path:
                    # Register this asset as an ExtResource
                    ext_id = str(self.next_ext_resource_id)
                    self.asset_type_to_ext_id[asset_type] = ext_id
                    self.ext_resources.append(
                        {
                            "id": ext_id,
                            "type": "PackedScene",
                            "path": scene_path,
                        }
                    )
                    self.next_ext_resource_id += 1
                    assets_registered += 1
                else:
                    assets_missing += 1

        if assets_registered > 0:
            print(f"   📦 Registered {assets_registered} unique asset types as ExtResources")
        if assets_missing > 0:
            print(
                f"   ⚠️  {assets_missing} asset types not found in Portal catalog (will use placeholders)"
            )

    def _generate_hqs(self, map_data: MapData) -> list[str]:
        """Generate HQ nodes with spawn points.

        Args:
            map_data: Map data

        Returns:
            List of .tscn lines
        """
        lines = []

        # Team 1 HQ
        team1_hq_transform = self._ensure_safe_height(map_data.team1_hq)
        team1_spawns = map_data.team1_spawns

        # Build spawn paths array
        spawn_paths = [f'NodePath("SpawnPoint_1_{i + 1}")' for i in range(len(team1_spawns))]
        spawn_paths_str = ", ".join(spawn_paths)

        lines.append(
            f'[node name="TEAM_1_HQ" parent="." node_paths=PackedStringArray("HQArea", "InfantrySpawns") instance=ExtResource("{EXT_RESOURCE_HQ_SPAWNER}")]'
        )
        lines.append(f"transform = {self.transform_formatter.format(team1_hq_transform)}")
        lines.append("AltTeam = 0")
        lines.append("VehicleSpawnersEnabled = true")
        lines.append(f"ObjId = {OBJID_HQ_START}")
        lines.append('HQArea = NodePath("HQ_Team1")')
        lines.append(f"InfantrySpawns = [{spawn_paths_str}]")
        lines.append("")

        # Team 1 HQ Area (safety zone) - matching BF1942
        lines.append(
            f'[node name="HQ_Team1" parent="TEAM_1_HQ" instance=ExtResource("{EXT_RESOURCE_POLYGON_VOLUME}")]'
        )
        lines.append(f"height = {HQ_PROTECTION_HEIGHT_M}")
        # Create square protection zone around HQ
        r = HQ_PROTECTION_RADIUS_M
        lines.append(f"points = PackedVector2Array(-{r}, -{r}, {r}, -{r}, {r}, {r}, -{r}, {r})")
        lines.append("")

        # Team 1 spawns (relative to HQ)
        for i, spawn in enumerate(team1_spawns, 1):
            lines.append(
                f'[node name="SpawnPoint_1_{i}" parent="TEAM_1_HQ" instance=ExtResource("{EXT_RESOURCE_SPAWN_POINT}")]'
            )
            # Use spawn's actual transform (relative to HQ)
            rel_transform = self._make_relative_transform(spawn.transform, team1_hq_transform)
            lines.append(f"transform = {self.transform_formatter.format(rel_transform)}")
            lines.append("")

        # Team 2 HQ
        team2_hq_transform = self._ensure_safe_height(map_data.team2_hq)
        team2_spawns = map_data.team2_spawns

        spawn_paths = [f'NodePath("SpawnPoint_2_{i + 1}")' for i in range(len(team2_spawns))]
        spawn_paths_str = ", ".join(spawn_paths)

        lines.append(
            f'[node name="TEAM_2_HQ" parent="." node_paths=PackedStringArray("HQArea", "InfantrySpawns") instance=ExtResource("{EXT_RESOURCE_HQ_SPAWNER}")]'
        )
        lines.append(f"transform = {self.transform_formatter.format(team2_hq_transform)}")
        lines.append("AltTeam = 0")
        lines.append("VehicleSpawnersEnabled = true")
        lines.append(f"ObjId = {OBJID_HQ_START + 1}")
        lines.append('HQArea = NodePath("HQ_Team2")')
        lines.append(f"InfantrySpawns = [{spawn_paths_str}]")
        lines.append("")

        # Team 2 HQ Area (safety zone) - matching BF1942
        lines.append(
            f'[node name="HQ_Team2" parent="TEAM_2_HQ" instance=ExtResource("{EXT_RESOURCE_POLYGON_VOLUME}")]'
        )
        lines.append(f"height = {HQ_PROTECTION_HEIGHT_M}")
        # Create square protection zone around HQ
        r = HQ_PROTECTION_RADIUS_M
        lines.append(f"points = PackedVector2Array(-{r}, -{r}, {r}, -{r}, {r}, {r}, -{r}, {r})")
        lines.append("")

        # Team 2 spawns
        for i, spawn in enumerate(team2_spawns, 1):
            lines.append(
                f'[node name="SpawnPoint_2_{i}" parent="TEAM_2_HQ" instance=ExtResource("{EXT_RESOURCE_SPAWN_POINT}")]'
            )
            rel_transform = self._make_relative_transform(spawn.transform, team2_hq_transform)
            lines.append(f"transform = {self.transform_formatter.format(rel_transform)}")
            lines.append("")

        return lines

    def _make_relative_transform(self, child: Transform, parent: Transform) -> Transform:
        """Make child transform relative to parent.

        Args:
            child: Child's world transform
            parent: Parent's world transform

        Returns:
            Relative transform
        """
        # Simple approach: subtract parent position
        rel_pos = Vector3(
            child.position.x - parent.position.x,
            child.position.y - parent.position.y,
            child.position.z - parent.position.z,
        )

        # Keep rotation as-is for now (proper solution would account for parent rotation)
        return Transform(rel_pos, child.rotation, child.scale)

    def _ensure_safe_height(self, transform: Transform) -> Transform:
        """Ensure transform Y position is above minimum safe height.

        This prevents objects from being placed underground where terrain snapping
        cannot work (raycast finds no collision below them).

        Args:
            transform: Original transform

        Returns:
            Transform with Y position clamped to min_safe_y if needed
        """
        if transform.position.y < self.min_safe_y:
            # Clamp Y to minimum safe height
            safe_pos = Vector3(
                transform.position.x,
                self.min_safe_y,
                transform.position.z,
            )
            return Transform(safe_pos, transform.rotation, transform.scale)
        return transform

    def _generate_capture_points(self, capture_points: list[CapturePoint]) -> list[str]:
        """Generate capture point nodes with spawn points.

        Args:
            capture_points: List of capture points

        Returns:
            List of .tscn lines
        """
        lines = []

        for i, cp in enumerate(capture_points, 1):
            # __post_init__ ensures these are never None, but need explicit check for mypy
            team1_spawns = cp.team1_spawns if cp.team1_spawns is not None else []
            team2_spawns = cp.team2_spawns if cp.team2_spawns is not None else []

            # Build spawn arrays
            team1_spawn_paths = [
                f'NodePath("CP{i}_Spawn_1_{j + 1}")' for j in range(len(team1_spawns))
            ]
            team2_spawn_paths = [
                f'NodePath("CP{i}_Spawn_2_{j + 1}")' for j in range(len(team2_spawns))
            ]

            team1_spawns_str = ", ".join(team1_spawn_paths) if team1_spawn_paths else ""
            team2_spawns_str = ", ".join(team2_spawn_paths) if team2_spawn_paths else ""

            # Build node_paths array for Portal SDK compatibility
            node_paths = ["CaptureArea"]
            if team1_spawn_paths:
                node_paths.append("InfantrySpawnPoints_Team1")
            if team2_spawn_paths:
                node_paths.append("InfantrySpawnPoints_Team2")
            node_paths_str = ", ".join([f'"{path}"' for path in node_paths])

            lines.append(
                f'[node name="CapturePoint_{i}" parent="." node_paths=PackedStringArray({node_paths_str}) instance=ExtResource("{EXT_RESOURCE_CAPTURE_POINT}")]'
            )
            # Ensure capture point is above terrain for snapping
            safe_cp_transform = self._ensure_safe_height(cp.transform)
            lines.append(f"transform = {self.transform_formatter.format(safe_cp_transform)}")
            lines.append("Team = 0")  # Neutral
            lines.append(f"ObjId = {OBJID_CAPTURE_POINTS_START + i}")
            lines.append(f'CaptureArea = NodePath("CaptureZone_{i}")')

            # Add spawn arrays if capture point has spawns
            if team1_spawn_paths:
                lines.append(f"InfantrySpawnPoints_Team1 = [{team1_spawns_str}]")
            if team2_spawn_paths:
                lines.append(f"InfantrySpawnPoints_Team2 = [{team2_spawns_str}]")

            lines.append("")

            # Add capture zone using BF1942 radius
            radius = cp.radius
            lines.append(
                f'[node name="CaptureZone_{i}" parent="CapturePoint_{i}" instance=ExtResource("{EXT_RESOURCE_POLYGON_VOLUME}")]'
            )
            lines.append(f"height = {CAPTURE_ZONE_HEIGHT_M}")
            # Create square capture zone with BF1942 radius
            lines.append(
                f"points = PackedVector2Array(-{radius}, -{radius}, {radius}, -{radius}, {radius}, {radius}, -{radius}, {radius})"
            )
            lines.append("")

            # Generate spawn point nodes as children of the capture point
            for j, spawn in enumerate(team1_spawns, 1):
                lines.append(
                    f'[node name="CP{i}_Spawn_1_{j}" parent="CapturePoint_{i}" instance=ExtResource("{EXT_RESOURCE_SPAWN_POINT}")]'
                )
                rel_transform = self._make_relative_transform(spawn.transform, cp.transform)
                lines.append(f"transform = {self.transform_formatter.format(rel_transform)}")
                lines.append("")

            for j, spawn in enumerate(team2_spawns, 1):
                lines.append(
                    f'[node name="CP{i}_Spawn_2_{j}" parent="CapturePoint_{i}" instance=ExtResource("{EXT_RESOURCE_SPAWN_POINT}")]'
                )
                rel_transform = self._make_relative_transform(spawn.transform, cp.transform)
                lines.append(f"transform = {self.transform_formatter.format(rel_transform)}")
                lines.append("")

            # Add WorldIcon for capture point label (A, B, C, etc.)
            # Portal SDK pattern from BombSquad mod - labels set via TypeScript
            label = chr(64 + i)  # A, B, C, etc. (65=A, 66=B, ...)
            obj_id = 20 + i - 1  # ObjId starts at 20 (convention from BombSquad)
            lines.append(
                f'[node name="CP_Label_{label}" parent="CapturePoint_{i}" instance=ExtResource("{EXT_RESOURCE_WORLD_ICON}")]'
            )
            lines.append(
                "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 5, 0)"
            )  # 5m above CP
            lines.append(f"ObjId = {obj_id}")
            lines.append(f'IconStringKey = "{label}"')
            lines.append("iconTextVisible = true")
            lines.append("iconImageVisible = false")
            lines.append("")

        return lines

    def _generate_vehicle_spawners(self, map_data: MapData) -> list[str]:
        """Generate vehicle spawner nodes.

        SOLID/DRY: Delegates to VehicleSpawnerGenerator for proper vehicle mapping.

        Args:
            map_data: Complete map data with HQs and vehicle spawners

        Returns:
            List of .tscn lines with VehicleType enum and BF1942→BF6 mappings
        """
        # Delegate to VehicleSpawnerGenerator
        # SOLID: Single Responsibility - vehicle spawner logic centralized
        # DRY: No duplicated vehicle mapping code
        # IMPORTANT: Pass complete map_data so generator can access HQ positions for team assignment
        return self.vehicle_spawner_generator.generate(
            map_data=map_data,
            asset_registry=self.asset_registry,
            transform_formatter=self.transform_formatter,
            min_safe_y=self.min_safe_y,
        )

    def _generate_stationary_emplacements(self, emplacements: list[GameObject]) -> list[str]:
        """Generate stationary weapon emplacement nodes.

        SOLID/DRY: Delegates to StationaryEmplacementGenerator.

        Args:
            emplacements: List of stationary emplacement objects (from game_objects)

        Returns:
            List of .tscn lines with weapon types (MG, TOW, etc.)
        """
        # Create temporary MapData with just emplacements for delegation
        from ..core.interfaces import MapData as TempMapData
        from ..core.interfaces import Rotation, Transform, Vector3

        temp_map_data = TempMapData(
            map_name="temp",
            game_mode="Conquest",
            team1_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),  # Dummy HQ
            team2_hq=Transform(Vector3(0, 0, 0), Rotation(0, 0, 0)),  # Dummy HQ
            team1_spawns=[],
            team2_spawns=[],
            game_objects=emplacements,  # Pass only emplacements
            capture_points=[],
            bounds=None,  # type: ignore
            metadata={},
        )

        # Delegate to StationaryEmplacementGenerator
        # SOLID: Single Responsibility - weapon emplacement logic centralized
        return self.stationary_emplacement_generator.generate(
            map_data=temp_map_data,
            asset_registry=self.asset_registry,
            transform_formatter=self.transform_formatter,
            min_safe_y=self.min_safe_y,
        )

    def _generate_combat_area(self, map_data: MapData) -> list[str]:
        """Generate combat area with polygon boundary.

        Uses actual terrain mesh bounds with 20m exclusion zone inset.

        Args:
            map_data: Map data with bounds

        Returns:
            List of .tscn lines
        """
        lines = []

        # PORTAL REQUIREMENT: CombatArea covers Portal terrain mesh
        # Terrain node is at (0,0,0) BUT the mesh itself has internal offsets.
        # CombatArea must be centered on the MESH center, not the node origin.
        # BF1942 objects are also centered on terrain's mesh center by portal_convert.py.
        if self.terrain_bounds:
            # Use Portal terrain mesh bounds - center on the MESH, not origin
            min_x, max_x, min_z, max_z = self.terrain_bounds
            center_x = self.terrain_center_x  # Terrain MESH center X (e.g., 59.0)
            center_z = self.terrain_center_z  # Terrain MESH center Z (e.g., -295.0)
            center_y = self.terrain_y_offset  # Use terrain Y baseline
        elif map_data.bounds:
            # Fallback to BF1942 object bounds if terrain bounds not provided
            min_x = map_data.bounds.min_point.x
            max_x = map_data.bounds.max_point.x
            min_z = map_data.bounds.min_point.z
            max_z = map_data.bounds.max_point.z
            center_x = (min_x + max_x) / 2
            center_z = (min_z + max_z) / 2
            center_y = (map_data.bounds.min_point.y + map_data.bounds.max_point.y) / 2
        else:
            # Create default bounds
            half_size = DEFAULT_MAP_SIZE_M / 2
            print(
                f"⚠️  Warning: No bounds provided, using default {DEFAULT_MAP_SIZE_M}x{DEFAULT_MAP_SIZE_M}"
            )
            min_x, max_x = -half_size, half_size
            min_z, max_z = -half_size, half_size
            center_x, center_z = 0.0, 0.0
            center_y = DEFAULT_CENTER_HEIGHT_M

        # Calculate polygon size from bounds (absolute coordinates, not centered)
        width = max_x - min_x
        depth = max_z - min_z
        half_width = width / 2
        half_depth = depth / 2

        # Check if terrain is rotated - CombatArea must rotate with terrain
        terrain_rotation = map_data.metadata.get("terrain_rotation", 0)

        if terrain_rotation != 0:
            # CombatArea centered at origin (0, 0) with rotation matching terrain
            # The rotation handles the orientation, position stays at origin like assets
            rotation_rad = math.radians(terrain_rotation)
            cos_r = math.cos(rotation_rad)
            sin_r = math.sin(rotation_rad)

            # Apply Y-axis rotation to CombatArea transform
            lines.append(
                f'[node name="CombatArea" parent="." node_paths=PackedStringArray("CombatVolume") instance=ExtResource("{EXT_RESOURCE_COMBAT_AREA}")]'
            )
            # Rotation matrix for Y-axis rotation with translation
            # [cos, 0, sin]
            # [0,   1, 0  ]
            # [-sin, 0, cos]
            # Position at origin (0, center_y, 0) - only Y height matters
            lines.append(
                f"transform = Transform3D({cos_r:.6g}, 0, {sin_r:.6g}, "
                f"0, 1, 0, "
                f"{-sin_r:.6g}, 0, {cos_r:.6g}, "
                f"0, {center_y}, 0)"
            )
            lines.append('CombatVolume = NodePath("CollisionPolygon3D")')
            lines.append("")

            # Polygon points stay in local space (relative to rotated CombatArea parent)
            # So we DON'T need to rotate the points - the parent's rotation handles it
            lines.append(
                f'[node name="CollisionPolygon3D" parent="CombatArea" instance=ExtResource("{EXT_RESOURCE_POLYGON_VOLUME}")]'
            )
            # Add Y offset to lift collision volume above terrain (ceiling height)
            lines.append(
                f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {COMBAT_AREA_HEIGHT_M}, 0)"
            )
            lines.append(
                f"points = PackedVector2Array({-half_width}, {-half_depth}, "
                f"{half_width}, {-half_depth}, "
                f"{half_width}, {half_depth}, "
                f"{-half_width}, {half_depth})"
            )
            lines.append(f"height = {COMBAT_AREA_HEIGHT_M}")
            lines.append("")
        else:
            # No rotation - standard transform
            lines.append(
                f'[node name="CombatArea" parent="." node_paths=PackedStringArray("CombatVolume") instance=ExtResource("{EXT_RESOURCE_COMBAT_AREA}")]'
            )
            lines.append(
                f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {center_x}, {center_y}, {center_z})"
            )
            lines.append('CombatVolume = NodePath("CollisionPolygon3D")')
            lines.append("")

            lines.append(
                f'[node name="CollisionPolygon3D" parent="CombatArea" instance=ExtResource("{EXT_RESOURCE_POLYGON_VOLUME}")]'
            )
            # Add Y offset to lift collision volume above terrain (ceiling height)
            lines.append(
                f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {COMBAT_AREA_HEIGHT_M}, 0)"
            )
            lines.append(
                f"points = PackedVector2Array({-half_width}, {-half_depth}, "
                f"{half_width}, {-half_depth}, "
                f"{half_width}, {half_depth}, "
                f"{-half_width}, {half_depth})"
            )
            lines.append(f"height = {COMBAT_AREA_HEIGHT_M}")
            lines.append("")

        return lines

    def _generate_deploy_cam(self, map_data: MapData) -> list[str]:
        """Generate DeployCam node for spawn screen.

        According to Portal documentation: "Without this, the spawn screen will not work correctly."
        Camera should be positioned high in the sky, facing downward to show the entire map.

        Args:
            map_data: Map data with bounds

        Returns:
            List of .tscn lines
        """
        lines = []

        # Calculate center position and appropriate height
        if map_data.bounds:
            center_x = (map_data.bounds.min_point.x + map_data.bounds.max_point.x) / 2
            center_z = (map_data.bounds.min_point.z + map_data.bounds.max_point.z) / 2

            # Height should be high enough to see the entire map
            # Camera must be ABOVE terrain, then high enough for wide-angle view
            map_width = map_data.bounds.max_point.x - map_data.bounds.min_point.x
            map_depth = map_data.bounds.max_point.z - map_data.bounds.min_point.z
            max_dimension = max(map_width, map_depth)
            terrain_max_y = map_data.bounds.max_point.y  # Highest point on terrain

            # Formula: terrain_height + viewing_distance + clearance
            # This makes camera height relative to terrain elevation
            # DRY: Use constants from clearance module
            height = (
                terrain_max_y
                + (max_dimension * DEPLOY_CAM_VIEWING_DISTANCE_MULTIPLIER)
                + DEPLOY_CAM_SAFETY_CLEARANCE_M
            )
        else:
            center_x = 0.0
            center_z = 0.0
            height = DEPLOY_CAM_DEFAULT_HEIGHT_M  # Default height if no bounds

        lines.append(
            f'[node name="DeployCam" parent="." instance=ExtResource("{EXT_RESOURCE_DEPLOY_CAM}")]'
        )
        # Camera positioned high, facing straight down (rotation -90° on X axis)
        # Transform3D: right(1,0,0), up(0,0,1), forward(0,-1,0) for downward facing
        lines.append(
            f"transform = Transform3D(1, 0, 0, 0, 0, 1, 0, -1, 0, {center_x}, {height}, {center_z})"
        )
        lines.append("")

        return lines

    def _generate_static_layer_declaration(self) -> list[str]:
        """Generate Static layer node declaration.

        This must be called BEFORE any gameplay objects that use parent="Static".

        Returns:
            List of .tscn lines
        """
        lines = []
        lines.append('[node name="Static" type="Node3D" parent="."]')
        lines.append("")
        return lines

    def _generate_terrain_and_assets(self, map_data: MapData) -> list[str]:
        """Generate terrain and assets nodes (first children of Static layer).

        These provide collision surfaces for gameplay objects to snap to.
        MUST be called BEFORE gameplay objects (HQs, CapturePoints, etc.).

        Args:
            map_data: Map data

        Returns:
            List of .tscn lines
        """
        lines = []

        # Terrain with rotation (if needed) and XYZ-offset for Portal compatibility
        terrain_rotation = map_data.metadata.get("terrain_rotation", 0)

        # PORTAL REQUIREMENT: Terrain MUST stay at (0,0,0)
        # Portal base terrain meshes are designed to be at origin with no transform.
        # Instead of centering terrain, we center BF1942 assets on the terrain's mesh center.
        # This is handled in portal_convert.py's _get_target_center() method.
        x_offset = 0.0
        y_offset = 0.0
        z_offset = 0.0

        if terrain_rotation != 0:
            # Apply Y-axis rotation to terrain with XYZ offset
            rotation_rad = math.radians(terrain_rotation)
            cos_r = math.cos(rotation_rad)
            sin_r = math.sin(rotation_rad)

            # Rotation matrix for Y-axis rotation with translation
            # [cos, 0, sin]
            # [0,   1, 0  ]
            # [-sin, 0, cos]
            terrain_transform = (
                f"Transform3D({cos_r:.6g}, 0, {sin_r:.6g}, "
                f"0, 1, 0, "
                f"{-sin_r:.6g}, 0, {cos_r:.6g}, "
                f"{x_offset:.6g}, {y_offset:.6g}, {z_offset:.6g})"
            )

            lines.append(
                f'[node name="{self.base_terrain}_Terrain" parent="Static" instance=ExtResource("{EXT_RESOURCE_TERRAIN}")]'
            )
            lines.append(f"transform = {terrain_transform}")
        else:
            # No rotation - apply XYZ offsets for centering
            lines.append(
                f'[node name="{self.base_terrain}_Terrain" parent="Static" instance=ExtResource("{EXT_RESOURCE_TERRAIN}")]'
            )
            # Always apply transform to center terrain at origin
            terrain_transform = (
                f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, "
                f"{x_offset:.6g}, {y_offset:.6g}, {z_offset:.6g})"
            )
            lines.append(f"transform = {terrain_transform}")

        lines.append("")

        # Include base terrain Assets mesh with same centering as Terrain
        # Assets must move with terrain to stay aligned at world origin
        lines.append(
            f'[node name="{self.base_terrain}_Assets" parent="Static" instance=ExtResource("{EXT_RESOURCE_ASSETS}")]'
        )
        # Apply the same transform as terrain (same centering offsets)
        if terrain_rotation != 0:
            # Rotated: use same rotation and offsets as terrain
            lines.append(f"transform = {terrain_transform}")
        else:
            # No rotation: same XYZ offsets as terrain
            lines.append(f"transform = {terrain_transform}")
        lines.append("")

        return lines

    def _generate_static_objects(self, map_data: MapData) -> list[str]:
        """Generate other static objects (trees, props, etc.).

        This is called AFTER gameplay objects so they appear later in the tree.

        Args:
            map_data: Map data

        Returns:
            List of .tscn lines
        """
        lines = []

        # Other static objects (exclude gameplay elements that are handled separately)
        # DRY: Use GAMEPLAY_KEYWORDS constant + check for vehicle_type property
        # SOLID: Single Responsibility - only include true static props (trees, rocks, buildings)
        static_objects = [
            obj
            for obj in map_data.game_objects
            if not any(keyword in obj.asset_type.lower() for keyword in GAMEPLAY_KEYWORDS)
            and "vehicle_type" not in obj.properties  # Exclude vehicle spawners
            and obj.asset_type != "StationaryEmplacementSpawner"  # Exclude weapon emplacements
        ]

        # Generate nodes for static objects (assets were pre-registered in generate())
        for i, obj in enumerate(static_objects, 1):
            ext_id = self.asset_type_to_ext_id.get(obj.asset_type)

            if ext_id:
                # Object has valid asset scene - use instance reference
                lines.append(
                    f'[node name="{obj.asset_type}_{i}" parent="Static" instance=ExtResource("{ext_id}")]'
                )
            else:
                # Fallback: create placeholder Node3D (no visual mesh)
                lines.append(f'[node name="{obj.asset_type}_{i}" type="Node3D" parent="Static"]')

            # Ensure static object is above terrain for snapping
            safe_transform = self._ensure_safe_height(obj.transform)
            lines.append(f"transform = {self.transform_formatter.format(safe_transform)}")
            lines.append("")

        return lines

    def validate(self, tscn_path: Path) -> list[str]:
        """Validate generated .tscn file.

        Args:
            tscn_path: Path to .tscn file

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not tscn_path.exists():
            errors.append(f"File not found: {tscn_path}")
            return errors

        # Basic validation - check for required nodes
        with open(tscn_path) as f:
            content = f.read()

        if "TEAM_1_HQ" not in content:
            errors.append("Missing TEAM_1_HQ node")
        if "TEAM_2_HQ" not in content:
            errors.append("Missing TEAM_2_HQ node")
        if "CombatArea" not in content:
            errors.append("Missing CombatArea node")

        return errors
