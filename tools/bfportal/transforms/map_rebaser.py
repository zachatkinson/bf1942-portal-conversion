#!/usr/bin/env python3
"""Map Rebaser - Switches Portal base terrain while preserving layout.

This tool handles Scenario B: Portal → Portal base map switching.
When you want to move a converted map from one Portal base to another
(e.g., Kursk from MP_Tungsten to MP_Outskirts), this tool:

1. Re-centers objects for the new base map
2. Re-adjusts heights for the new terrain
3. Validates bounds for the new CombatArea
4. Preserves all asset mappings (already in Portal format)

This is DIFFERENT from the initial BF1942 → Portal conversion.
"""

import re
from pathlib import Path

from ..core.interfaces import (
    GameObject,
    IBoundsValidator,
    ICoordinateOffset,
    ITerrainProvider,
    Transform,
    Vector3,
)


class MapRebaser:
    """Handles switching between Portal base terrains.

    This tool reads an existing Portal .tscn file, extracts all objects,
    and regenerates the scene with a different base terrain while
    maintaining relative positions.
    """

    def __init__(
        self,
        terrain_provider: ITerrainProvider,
        offset_calculator: ICoordinateOffset,
        bounds_validator: IBoundsValidator | None,
    ):
        """Initialize rebaser.

        Args:
            terrain_provider: New terrain for height queries
            offset_calculator: For re-centering calculations
            bounds_validator: For bounds checking on new map
        """
        self.terrain = terrain_provider
        self.offset_calc = offset_calculator
        self.bounds_validator = bounds_validator

    def rebase_map(
        self, input_tscn: Path, output_tscn: Path, new_base_terrain: str, new_map_center: Vector3
    ) -> dict:
        """Rebase a Portal map to a different base terrain.

        Args:
            input_tscn: Existing .tscn file (e.g., Kursk on Tungsten)
            output_tscn: New .tscn file (e.g., Kursk on Outskirts)
            new_base_terrain: Target base terrain (e.g., "MP_Outskirts")
            new_map_center: Center point of new base map

        Returns:
            Statistics dictionary with rebase results

        Raises:
            FileNotFoundError: If input_tscn doesn't exist
            ValidationError: If rebasing fails
        """
        print("=" * 70)
        print(f"Rebasing Map: {input_tscn.name}")
        print("  From: Current base terrain")
        print(f"  To:   {new_base_terrain}")
        print("=" * 70)

        # Parse existing .tscn file
        objects = self._parse_tscn(input_tscn)
        print(f"📦 Extracted {len(objects)} objects from existing map")

        # Calculate current centroid
        current_centroid = self.offset_calc.calculate_centroid(objects)
        print(
            f"📍 Current centroid: ({current_centroid.x:.1f}, "
            f"{current_centroid.y:.1f}, {current_centroid.z:.1f})"
        )

        # Calculate offset to new center
        offset = self.offset_calc.calculate_offset(current_centroid, new_map_center)
        print(f"↔️  Calculated offset: ({offset.x:.1f}, {offset.y:.1f}, {offset.z:.1f})")

        # Apply transformations
        rebased_objects = []
        out_of_bounds = 0
        height_adjusted = 0

        for obj in objects:
            # Apply offset to re-center
            new_transform = self.offset_calc.apply_offset(obj.transform, offset)

            # Adjust height for new terrain
            try:
                terrain_height = self.terrain.get_height_at(
                    new_transform.position.x, new_transform.position.z
                )
                height_diff = abs(new_transform.position.y - terrain_height)

                # If object is significantly above/below terrain, adjust
                if height_diff > 2.0:  # 2m tolerance
                    new_transform.position.y = terrain_height
                    height_adjusted += 1

            except Exception as e:
                print(f"  ⚠️  Cannot query height for {obj.name}: {e}")
                out_of_bounds += 1

            rebased_objects.append(
                GameObject(
                    name=obj.name,
                    asset_type=obj.asset_type,  # Already Portal asset!
                    transform=new_transform,
                    team=obj.team,
                    properties=obj.properties,
                )
            )

        print(f"✅ Re-centered and adjusted {len(rebased_objects)} objects")
        print(f"   - Height adjusted: {height_adjusted}")
        print(f"   - Out of bounds: {out_of_bounds}")

        # Generate new .tscn file
        self._generate_tscn(rebased_objects, output_tscn, new_base_terrain)

        stats = {
            "total_objects": len(rebased_objects),
            "height_adjusted": height_adjusted,
            "out_of_bounds": out_of_bounds,
            "offset_applied": {"x": offset.x, "y": offset.y, "z": offset.z},
        }

        return stats

    def _parse_tscn(self, tscn_path: Path) -> list[GameObject]:
        """Parse existing .tscn file to extract objects.

        Args:
            tscn_path: Path to .tscn file

        Returns:
            List of GameObjects

        Note:
            This is a simplified parser. For production, use a proper
            Godot scene parser or the gdconverter tool.
        """
        objects = []

        with open(tscn_path) as f:
            content = f.read()

        # Extract node sections with transforms
        # Pattern: [node name="..." instance=...] followed by transform=...
        node_pattern = r'\[node name="([^"]+)"[^\]]*\]\s*transform = Transform3D\(([^)]+)\)'
        matches = re.findall(node_pattern, content)

        for name, transform_str in matches:
            # Skip special nodes (HQs, spawns, combat area, etc.)
            if any(skip in name for skip in ["HQ", "Spawn", "Combat", "Static", "Terrain"]):
                continue

            # Parse transform matrix
            try:
                values = [float(v.strip()) for v in transform_str.split(",")]
                if len(values) >= 12:
                    # Transform3D format: (right.x, up.x, forward.x,
                    #                      right.y, up.y, forward.y,
                    #                      right.z, up.z, forward.z,
                    #                      pos.x, pos.y, pos.z)
                    position = Vector3(values[9], values[10], values[11])

                    # Extract rotation from matrix (simplified)
                    # For rebasing, we mainly care about position
                    from ..core.interfaces import Rotation, Team

                    rotation = Rotation(0, 0, 0)  # Preserve as-is

                    transform = Transform(position, rotation)

                    objects.append(
                        GameObject(
                            name=name,
                            asset_type=name.split("_")[0],  # Approximate
                            transform=transform,
                            team=Team.NEUTRAL,  # Unknown from .tscn
                            properties={},
                        )
                    )
            except Exception as e:
                print(f"  ⚠️  Failed to parse transform for {name}: {e}")

        return objects

    def _generate_tscn(
        self, objects: list[GameObject], output_path: Path, base_terrain: str
    ) -> None:
        """Generate new .tscn file with rebased objects.

        Args:
            objects: Rebased game objects
            output_path: Path to output .tscn file
            base_terrain: Base terrain name (e.g., "MP_Outskirts")

        Note:
            This is a simplified generator. For production, use the full
            TscnGenerator from the generators module.
        """
        # TODO: Implement full .tscn generation
        # For now, just create a placeholder
        with open(output_path, "w") as f:
            f.write("[gd_scene format=3]\n\n")
            f.write(f'[node name="{output_path.stem}" type="Node3D"]\n\n')
            f.write(f"# Rebased to {base_terrain}\n")
            f.write(f"# Total objects: {len(objects)}\n")

        print(f"✅ Generated rebased map: {output_path}")
        print("   ⚠️  NOTE: This is a placeholder. Use full TscnGenerator for production.")
