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
from ..constants.extresource_ids import EXT_RESOURCE_WORLD_ICON
from ..constants.gameplay import OBJID_WORLD_ICON_START
from .base_generator import BaseNodeGenerator


class WorldIconGenerator(BaseNodeGenerator):
    """Generates WorldIcon nodes for capture point labels.

    Creates a WorldIcon at each capture point location with labels A, B, C, etc.
    Icons must be configured via TypeScript in the experience file.

    Example Output:
        [node name="CP_Label_A" parent="CapturePointA" instance=ExtResource("11")]
        transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 5, 0)
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

        # Use capture_points from MapData (not game_objects)
        if not map_data.capture_points:
            return lines

        for i, cp in enumerate(map_data.capture_points, 1):
            # Use letter label from CapturePoint
            label = cp.label  # "A", "B", "C", etc.

            # WorldIcon ObjId starts at OBJID_WORLD_ICON_START (20)
            obj_id = OBJID_WORLD_ICON_START + i - 1

            lines.append(
                f'[node name="CP_Label_{label}" parent="CapturePoint{label}" '
                f'instance=ExtResource("{EXT_RESOURCE_WORLD_ICON}")]'
            )
            # Position 5m above capture point for visibility
            lines.append("transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 5, 0)")
            lines.append(f"ObjId = {obj_id}")
            lines.append(f'IconStringKey = "{label}"')
            lines.append("iconTextVisible = true")
            lines.append("iconImageVisible = false")
            lines.append("")

        return lines
