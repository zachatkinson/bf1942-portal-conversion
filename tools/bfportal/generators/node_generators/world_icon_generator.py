#!/usr/bin/env python3
"""WorldIcon node generator for capture point labels.

Single Responsibility: Generate WorldIcon nodes for capture point labels (A, B, C).

This generator creates WorldIcon nodes positioned at each capture point to display
labels like "A", "B", "C" on the HUD. This is the Portal SDK pattern for capture
point labels, as demonstrated in the BombSquad example mod.

WorldIcon nodes are controlled via TypeScript using:
  mod.GetWorldIcon(ObjId)
  mod.SetWorldIconText(icon, "A")
"""

from ...core.interfaces import MapData
from ..components.asset_registry import AssetRegistry
from ..components.transform_formatter import TransformFormatter
from .base_generator import BaseNodeGenerator


class WorldIconGenerator(BaseNodeGenerator):
    """Generates WorldIcon nodes for capture point labels.

    Creates a WorldIcon at each capture point location with labels A, B, C, etc.
    Icons must be configured via TypeScript in the experience file.

    Example Output:
        [node name="CP_Label_A" parent="CapturePoint_1" instance=ExtResource("WorldIcon")]
        transform = Transform3D(...)
        ObjId = 20
        IconStringKey = "A"
        iconTextVisible = true
    """

    def generate(
        self,
        map_data: MapData,
        asset_registry: AssetRegistry,
        transform_formatter: TransformFormatter,
    ) -> list[str]:
        """Generate WorldIcon nodes for capture points.

        Args:
            map_data: Complete map data with capture points
            asset_registry: Registry for ExtResource IDs
            transform_formatter: Formatter for Transform3D strings

        Returns:
            List of .tscn node lines for WorldIcon labels
        """
        lines: list[str] = []

        # Get capture points
        capture_points = [obj for obj in map_data.game_objects if obj.asset_type == "CapturePoint"]

        if not capture_points:
            return lines

        # Register WorldIcon asset if not already registered
        world_icon_id = asset_registry.register_asset(
            "WorldIcon", "res://objects/Gameplay/Common/WorldIcon.tscn"
        )

        # Generate labels A, B, C, etc.
        labels = [chr(65 + i) for i in range(len(capture_points))]  # A, B, C, ...

        for i, (cp, label) in enumerate(zip(capture_points, labels, strict=False), 1):
            # WorldIcon ObjId starts at 20 (convention from BombSquad mod)
            obj_id = 20 + i - 1

            lines.append(
                f'[node name="CP_Label_{label}" parent="CapturePoint_{i}" '
                f'instance=ExtResource("{world_icon_id}")]'
            )
            lines.append(f"transform = {transform_formatter.format(cp.transform)}")
            lines.append(f"ObjId = {obj_id}")
            lines.append(f'IconStringKey = "{label}"')
            lines.append("iconTextVisible = true")
            lines.append("iconImageVisible = false")
            lines.append("# Portal SDK: Labels set via TypeScript using mod.SetWorldIconText()")
            lines.append("")

        return lines
