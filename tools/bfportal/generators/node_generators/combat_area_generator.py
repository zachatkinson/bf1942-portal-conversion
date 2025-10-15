#!/usr/bin/env python3
"""Combat area node generator for TSCN generation.

Single Responsibility: Generate combat area boundary nodes.

This generator creates the CombatArea node with polygon boundaries that
define the playable area. Players leaving this area are warned/killed.
"""

from ...core.interfaces import MapData
from ..components.asset_registry import AssetRegistry
from ..components.transform_formatter import TransformFormatter
from ..constants.gameplay import COMBAT_AREA_HEIGHT_M
from ..constants.terrain import DEFAULT_CENTER_HEIGHT_M, DEFAULT_MAP_SIZE_M
from .base_generator import BaseNodeGenerator


class CombatAreaGenerator(BaseNodeGenerator):
    """Generates combat area boundary nodes for Portal maps.

    Creates a CombatArea node with a CollisionPolygon3D child that defines
    the vertical ceiling for the playable area. Players going above this height
    are warned/killed.

    **Important:** CombatArea is a CEILING, not a floor boundary!
    - Official maps (MP_Tungsten, MP_Aftermath) position it ~140m above ground
    - Height is typically 100m (not 200m)
    - This prevents players from flying/climbing too high
    - Ground boundaries are defined by terrain geometry

    Example Output:
        [node name="CombatArea" parent="." node_paths=... instance=ExtResource("5")]
        CombatVolume = NodePath("CollisionPolygon3D")

        [node name="CollisionPolygon3D" type="Area3D" parent="CombatArea"]
        transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 140, 0)
        height = 100.0  # Extends from Y=140 to Y=240
        points = PackedVector2Array(-1024, -1024, 1024, -1024, 1024, 1024, -1024, 1024)
    """

    def generate(
        self,
        map_data: MapData,
        asset_registry: AssetRegistry,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate combat area nodes.

        Args:
            map_data: Complete map data with bounds
            asset_registry: Registry for ExtResource IDs
            transform_formatter: Formatter for Transform3D strings

        Returns:
            List of .tscn node lines for combat area
        """
        lines = []

        # Calculate bounds (use defaults if not provided)
        if not map_data.bounds:
            half_size = DEFAULT_MAP_SIZE_M / 2
            print(
                f"⚠️  Warning: No bounds provided, using default {DEFAULT_MAP_SIZE_M}x{DEFAULT_MAP_SIZE_M}"
            )
            min_x, max_x = -half_size, half_size
            min_z, max_z = -half_size, half_size
            center_x, center_z = 0.0, 0.0
            # Position CombatArea ceiling at reasonable default height
            ceiling_y = 140.0
        else:
            min_x = map_data.bounds.min_point.x
            max_x = map_data.bounds.max_point.x
            min_z = map_data.bounds.min_point.z
            max_z = map_data.bounds.max_point.z
            center_x = (min_x + max_x) / 2
            center_z = (min_z + max_z) / 2

            # Position CombatArea as a CEILING above the terrain
            # Official maps (MP_Tungsten, MP_Aftermath) use ~140m above ground
            # This prevents players from flying/climbing too high
            max_y = map_data.bounds.max_point.y

            # Position ceiling 40-50m above highest terrain point
            # This gives plenty of room for gameplay while limiting vertical bounds
            buffer_above = 40.0
            ceiling_y = max_y + buffer_above

        # Calculate relative coordinates for polygon
        half_width = (max_x - min_x) / 2
        half_depth = (max_z - min_z) / 2

        # Generate CombatArea node (no transform - defaults to origin)
        lines.append(
            '[node name="CombatArea" parent="." node_paths=PackedStringArray("CombatVolume") instance=ExtResource("5")]'
        )
        lines.append('CombatVolume = NodePath("CollisionPolygon3D")')
        lines.append("")

        # Generate collision polygon child with position above terrain
        # This creates the ceiling that prevents players from flying too high
        lines.append('[node name="CollisionPolygon3D" type="Area3D" parent="CombatArea"]')
        lines.append(
            f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {center_x}, {ceiling_y}, {center_z})"
        )

        # Use 100m height (official maps standard) instead of 200m
        ceiling_height = 100.0
        lines.append(f"height = {ceiling_height}")

        # Create rectangular boundary (relative to polygon center)
        lines.append(
            f"points = PackedVector2Array({-half_width}, {-half_depth}, "
            f"{half_width}, {-half_depth}, "
            f"{half_width}, {half_depth}, "
            f"{-half_width}, {half_depth})"
        )
        lines.append("")

        return lines
