#!/usr/bin/env python3
"""Static layer node generator for TSCN generation.

Single Responsibility: Generate static object layer with terrain and assets.

This generator creates the Static layer containing terrain mesh and all
static objects (trees, rocks, buildings). It integrates with AssetRandomizer
to provide visual variety for repeated assets.
"""

import json
import math

from ...core.interfaces import MapData
from ..components.asset_catalog import AssetCatalog
from ..components.asset_randomizer import AssetRandomizer
from ..components.asset_registry import AssetRegistry
from ..components.transform_formatter import TransformFormatter
from ..constants.paths import get_mappings_file
from .base_generator import BaseNodeGenerator

# Lake scale metadata (loaded from mappings file)
LAKE_SCALE_DATA: dict[str, dict[str, float]] = {}

# Default puddle dimensions (approximate - verified from Decal_PuddleLong_01 in Godot)
DEFAULT_PUDDLE_WIDTH = 8.0  # meters (X axis)
DEFAULT_PUDDLE_HEIGHT = 3.0  # meters (Z axis)


class StaticLayerGenerator(BaseNodeGenerator):
    """Generates static layer with terrain and objects.

    Creates the Static node hierarchy containing:
    - Terrain mesh instance with optional rotation and Y-offset
    - All static objects (buildings, props, nature) as children
    - Uses AssetRandomizer for tree/rock/shrub variety

    Example Output:
        [node name="Static" type="Node3D" parent="."]

        [node name="MP_Tungsten_Terrain" parent="Static" instance=ExtResource("6")]
        transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, -15.2, 0)

        [node name="Birch_01_L_1" parent="Static" instance=ExtResource("7")]
        transform = Transform3D(...)
    """

    def __init__(
        self,
        base_terrain: str,
        terrain_y_offset: float = 0.0,
        terrain_center_x: float = 0.0,
        terrain_center_z: float = 0.0,
        asset_catalog: AssetCatalog | None = None,
        asset_randomizer: AssetRandomizer | None = None,
    ):
        """Initialize generator.

        Args:
            base_terrain: Base terrain name (e.g., "MP_Tungsten")
            terrain_y_offset: Y offset to apply to terrain mesh for Portal compatibility
            terrain_center_x: X coordinate of terrain mesh center (for centering at origin)
            terrain_center_z: Z coordinate of terrain mesh center (for centering at origin)
            asset_catalog: Asset catalog for scene path lookups
            asset_randomizer: Optional randomizer for asset variety
        """
        self.base_terrain = base_terrain
        self.terrain_y_offset = terrain_y_offset
        self.terrain_center_x = terrain_center_x
        self.terrain_center_z = terrain_center_z
        self.asset_catalog = asset_catalog or AssetCatalog()
        self.asset_randomizer = asset_randomizer

    def generate(
        self,
        map_data: MapData,
        asset_registry: AssetRegistry,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate static layer nodes.

        Args:
            map_data: Complete map data
            asset_registry: Registry for ExtResource IDs
            transform_formatter: Formatter for Transform3D strings

        Returns:
            List of .tscn node lines for static layer
        """
        lines = []

        # Portal_Reference layer for terrain (not exported to spatial.json)
        lines.append('[node name="Portal_Reference" type="Node3D" parent="."]')
        lines.append("")

        # Generate terrain node in Portal_Reference (won't be exported)
        lines.extend(self._generate_terrain_node(map_data, parent="Portal_Reference"))

        # Static layer for exported objects
        lines.append('[node name="Static" type="Node3D" parent="."]')
        lines.append("")

        # Generate static objects
        lines.extend(self._generate_static_objects(map_data, asset_registry, transform_formatter))

        return lines

    def _generate_terrain_node(self, map_data: MapData, parent: str = "Static") -> list[str]:
        """Generate terrain mesh node with rotation and Y-offset.

        Args:
            map_data: Map data with terrain metadata
            parent: Parent node name (default "Static", use "Portal_Reference" to exclude from export)

        Returns:
            List of .tscn lines for terrain node
        """
        lines = []

        # Get terrain rotation from metadata
        terrain_rotation = map_data.metadata.get("terrain_rotation", 0)

        # CRITICAL: Center terrain at world origin (0, 0) by offsetting by negative mesh center.
        # The terrain mesh has internal vertex coordinates that may not be centered at (0, 0).
        # By offsetting the terrain node position by (-mesh_center_x, -mesh_center_z), we place
        # the mesh's geometric center at world origin, ensuring objects align visually.
        x_offset = -self.terrain_center_x
        z_offset = -self.terrain_center_z
        y_offset = -self.terrain_y_offset  # Negative to move terrain DOWN for height alignment

        # Apply rotation if needed
        if terrain_rotation != 0:
            # Y-axis rotation matrix with XYZ translation
            rotation_rad = math.radians(terrain_rotation)
            cos_r = math.cos(rotation_rad)
            sin_r = math.sin(rotation_rad)

            # Rotation matrix for Y-axis rotation:
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
                f'[node name="{self.base_terrain}_Terrain" parent="{parent}" instance=ExtResource("6")]'
            )
            lines.append(f"transform = {terrain_transform}")
        else:
            # No rotation - apply XYZ offsets for centering
            lines.append(
                f'[node name="{self.base_terrain}_Terrain" parent="{parent}" instance=ExtResource("6")]'
            )
            # Always apply transform to center terrain at origin
            terrain_transform = (
                f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, "
                f"{x_offset:.6g}, {y_offset:.6g}, {z_offset:.6g})"
            )
            lines.append(f"transform = {terrain_transform}")

        lines.append("")

        return lines

    def _generate_static_objects(
        self,
        map_data: MapData,
        asset_registry: AssetRegistry,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate static object nodes (trees, rocks, buildings, etc).

        Args:
            map_data: Map data with game objects
            asset_registry: Registry for ExtResource IDs
            transform_formatter: Formatter for Transform3D strings

        Returns:
            List of .tscn lines for static objects
        """
        lines = []

        # Filter out gameplay objects (handled by other generators)
        static_objects = [
            obj
            for obj in map_data.game_objects
            if "vehicle" not in obj.asset_type.lower()
            and "spawner" not in obj.asset_type.lower()
            and "spawnpoint" not in obj.asset_type.lower()
            and "spawn" not in obj.asset_type.lower()
            and "controlpoint" not in obj.asset_type.lower()
            and "capturepoint" not in obj.asset_type.lower()
            and "cpoint" not in obj.asset_type.lower()
        ]

        # Pre-register all unique assets (with randomization if available)
        self._pre_register_static_assets(static_objects, asset_registry)

        # Generate nodes for each static object
        for i, obj in enumerate(static_objects, 1):
            # Get asset type (possibly randomized)
            asset_type = self._get_asset_type_with_variety(obj.asset_type)

            # Get ExtResource ID for this asset
            ext_id = asset_registry.get_id(asset_type)

            if ext_id:
                # Object has valid asset scene - use instance reference
                lines.append(
                    f'[node name="{asset_type}_{i}" parent="Static" instance=ExtResource("{ext_id}")]'
                )
            else:
                # Fallback: create placeholder Node3D (no visual mesh)
                lines.append(f'[node name="{asset_type}_{i}" type="Node3D" parent="Static"]')

            # Check if this is a lake that needs scaling
            transform_str = self._format_transform_with_lake_scaling(
                obj.transform, obj.asset_type, transform_formatter
            )
            lines.append(f"transform = {transform_str}")
            lines.append("")

        return lines

    def _pre_register_static_assets(
        self, static_objects: list, asset_registry: AssetRegistry
    ) -> None:
        """Pre-register all static object assets as ExtResources.

        This includes variety pools if randomization is enabled.

        Args:
            static_objects: List of static game objects
            asset_registry: Registry to register assets with
        """
        # Collect unique asset types
        unique_assets = {obj.asset_type for obj in static_objects}

        # Expand to include variety pools if randomizer is available
        if self.asset_randomizer:
            expanded_assets = set()
            for asset_type in unique_assets:
                if self.asset_randomizer.should_randomize(asset_type):
                    # Add all variants from the pool
                    expanded_assets.update(self.asset_randomizer.get_variety_pool(asset_type))
                else:
                    expanded_assets.add(asset_type)
            unique_assets = expanded_assets

        # Register each asset
        assets_registered = 0
        assets_missing = 0

        for asset_type in sorted(unique_assets):  # Sort for deterministic output
            if not asset_registry.has_asset(asset_type):
                scene_path = self.asset_catalog.get_scene_path(asset_type, self.base_terrain)
                if scene_path:
                    asset_registry.register_asset(asset_type, scene_path)
                    assets_registered += 1
                else:
                    assets_missing += 1

        if assets_registered > 0:
            print(f"   📦 Registered {assets_registered} unique asset types as ExtResources")
        if assets_missing > 0:
            print(
                f"   ⚠️  {assets_missing} asset types not found in Portal catalog (will use placeholders)"
            )

    def _get_asset_type_with_variety(self, asset_type: str) -> str:
        """Get asset type with optional randomization for variety.

        Args:
            asset_type: Original asset type

        Returns:
            Asset type (possibly randomized variant)
        """
        if self.asset_randomizer and self.asset_randomizer.should_randomize(asset_type):
            return self.asset_randomizer.get_random_variant(asset_type)
        return asset_type

    def _format_transform_with_lake_scaling(
        self, transform, bf1942_asset_type: str, transform_formatter: TransformFormatter
    ) -> str:
        """Format transform with lake scaling if applicable.

        Args:
            transform: Transform object
            bf1942_asset_type: Original BF1942 asset type (e.g., "lake", "lake2", "lake3")
            transform_formatter: Formatter for Transform3D strings

        Returns:
            Formatted Transform3D string (with scale if lake asset)
        """
        # Load lake scale data if not already loaded
        global LAKE_SCALE_DATA
        if not LAKE_SCALE_DATA:
            self._load_lake_scale_data()

        # Check if this is a lake asset that needs scaling
        lake_lower = bf1942_asset_type.lower()
        if lake_lower in LAKE_SCALE_DATA:
            scale_info = LAKE_SCALE_DATA[lake_lower]
            scale_x = scale_info["width"] / DEFAULT_PUDDLE_WIDTH
            scale_z = scale_info["height"] / DEFAULT_PUDDLE_HEIGHT
            scale_y = 1.0  # Keep Y scale normal for decals

            # Apply scale to transform
            if not hasattr(transform, "scale") or transform.scale is None:
                # Create scale attribute
                from ...core.interfaces import Vector3

                transform.scale = Vector3(scale_x, scale_y, scale_z)
            else:
                # Multiply existing scale
                transform.scale.x *= scale_x
                transform.scale.y *= scale_y
                transform.scale.z *= scale_z

        return transform_formatter.format(transform)

    def _load_lake_scale_data(self) -> None:
        """Load lake scale metadata from mappings file."""
        global LAKE_SCALE_DATA

        # Find mappings file
        mappings_file = get_mappings_file()

        if not mappings_file.exists():
            print(f"   ⚠️  Warning: Mappings file not found at {mappings_file}")
            return

        try:
            with open(mappings_file) as f:
                data = json.load(f)

            # Extract scale data for lakes
            static_objects = data.get("static_objects", {})
            for asset_type in ["lake", "lake2", "lake3"]:
                if asset_type in static_objects:
                    mapping = static_objects[asset_type]
                    if "scale" in mapping:
                        LAKE_SCALE_DATA[asset_type] = mapping["scale"]

            if LAKE_SCALE_DATA:
                print(f"   🌊 Loaded scale data for {len(LAKE_SCALE_DATA)} lake assets")

        except Exception as e:
            print(f"   ⚠️  Warning: Failed to load lake scale data: {e}")
