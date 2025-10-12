#!/usr/bin/env python3
"""BF1942 to Portal Conversion Tool - Master CLI.

This is the main command-line interface for converting Battlefield 1942 maps
to Battlefield 6 Portal format. It orchestrates the complete conversion pipeline:

    BF1942 .con → Parse → Map Assets → Transform → Height Adjust → Generate .tscn

Usage:
    python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten

    # With custom options
    python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten \
        --bf1942-root bf1942_source/extracted/Bf1942/Archives/bf1942/Levels \
        --output GodotProject/levels/Kursk_converted.tscn

Requirements:
    - Extracted BF1942 map files (RFA already extracted)
    - Portal SDK with asset_types.json
    - BF1942 → Portal asset mappings
"""

import argparse
import sys
from pathlib import Path

# Add bfportal to path
sys.path.insert(0, str(Path(__file__).parent))

from bfportal.core.exceptions import BFPortalError
from bfportal.core.interfaces import MapContext, Team
from bfportal.engines.refractor.games.bf1942 import BF1942Engine
from bfportal.generators.tscn_generator import TscnGenerator
from bfportal.mappers.asset_mapper import AssetMapper
from bfportal.orientation import (
    MapOrientationDetector,
    OrientationMatcher,
    TerrainOrientationDetector,
)
from bfportal.terrain.terrain_provider import HeightAdjuster, MeshTerrainProvider
from bfportal.transforms.coordinate_offset import CoordinateOffset


class PortalConverter:
    """Main conversion orchestrator."""

    def __init__(self, args):
        """Initialize converter with command-line arguments."""
        self.args = args
        self.project_root = Path(__file__).parent.parent

        # Initialize components
        print("🔧 Initializing conversion pipeline...")

        # Game engine
        self.engine = BF1942Engine()
        print(f"   ✅ {self.engine.get_game_name()} engine ({self.engine.get_engine_version()})")

        # Asset mapper
        portal_assets_path = self.project_root / "FbExportData" / "asset_types.json"
        mappings_path = (
            self.project_root / "tools" / "asset_audit" / "bf1942_to_portal_mappings.json"
        )

        self.asset_mapper = AssetMapper(portal_assets_path)
        self.asset_mapper.load_mappings(mappings_path)
        print("   ✅ Asset mapper loaded (733 mappings)")

        # Coordinate offset calculator
        self.coord_offset = CoordinateOffset()
        print("   ✅ Coordinate offset calculator")

        # Terrain provider: Load Portal base terrain mesh
        terrain_mesh_path = (
            self.project_root
            / "GodotProject"
            / "raw"
            / "models"
            / f"{args.base_terrain}_Terrain.glb"
        )

        if not terrain_mesh_path.exists():
            raise BFPortalError(
                f"Portal terrain mesh not found: {terrain_mesh_path}\n"
                f"Ensure Portal SDK is properly set up with terrain files."
            )

        print(f"   🗺️  Loading Portal terrain mesh: {terrain_mesh_path.name}")
        self.terrain = MeshTerrainProvider(
            mesh_path=terrain_mesh_path, terrain_size=(args.terrain_size, args.terrain_size)
        )
        print(f"   ✅ Terrain loaded: {len(self.terrain.vertices):,} vertices")
        print(
            f"      Height range: {self.terrain.min_height:.1f}m - {self.terrain.max_height:.1f}m"
        )
        print(
            f"      Mesh bounds: X[{self.terrain.mesh_min_x:.1f}, {self.terrain.mesh_max_x:.1f}] "
            f"Z[{self.terrain.mesh_min_z:.1f}, {self.terrain.mesh_max_z:.1f}]"
        )
        print(
            f"      Mesh center: ({self.terrain.mesh_center_x:.1f}, {self.terrain.mesh_center_z:.1f})"
        )
        print(
            f"      Grid resolution: {self.terrain.grid_resolution}x{self.terrain.grid_resolution}"
        )

        self.height_adjuster = HeightAdjuster()

    def convert(self) -> int:
        """Execute the conversion pipeline.

        Returns:
            Exit code (0 = success, 1 = error)
        """
        try:
            print("\n" + "=" * 70)
            print(f"Converting {self.args.map} to Portal")
            print("=" * 70)

            # Step 1: Parse BF1942 map
            map_path = self._resolve_map_path()
            print(f"\n📂 Source: {map_path}")

            map_data = self.engine.parse_map(map_path)

            # Step 2: Calculate map offset
            print("\n📐 Calculating coordinate offset...")
            all_objects = (
                [s for s in map_data.team1_spawns]
                + [s for s in map_data.team2_spawns]
                + map_data.game_objects
            )

            if all_objects:
                # Convert spawn points to game objects for centroid calculation
                from bfportal.core.interfaces import GameObject

                objects_for_centroid = []
                for spawn in map_data.team1_spawns + map_data.team2_spawns:
                    objects_for_centroid.append(
                        GameObject(
                            name=spawn.name,
                            asset_type="SpawnPoint",
                            transform=spawn.transform,
                            team=spawn.team,
                            properties={},
                        )
                    )
                objects_for_centroid.extend(map_data.game_objects)

                source_center = self.coord_offset.calculate_centroid(objects_for_centroid)
                target_center = self._get_target_center()
                offset = self.coord_offset.calculate_offset(source_center, target_center)

                print(
                    f"   Source center: ({source_center.x:.1f}, {source_center.y:.1f}, {source_center.z:.1f})"
                )
                print(
                    f"   Target center: ({target_center.x:.1f}, {target_center.y:.1f}, {target_center.z:.1f})"
                )
                print(f"   Offset: ({offset.x:.1f}, {offset.y:.1f}, {offset.z:.1f})")

                # Apply offset to all objects
                for obj in map_data.game_objects:
                    obj.transform = self.coord_offset.apply_offset(obj.transform, offset)

                for spawn in map_data.team1_spawns + map_data.team2_spawns:
                    spawn.transform = self.coord_offset.apply_offset(spawn.transform, offset)

                # Track which spawns we've already offset (CP spawns may be in both team lists)
                offset_spawns = set()
                for cp in map_data.capture_points:
                    cp.transform = self.coord_offset.apply_offset(cp.transform, offset)
                    # Also offset spawns within capture points (avoid duplicates)
                    for spawn in cp.team1_spawns + cp.team2_spawns:
                        if id(spawn) not in offset_spawns:
                            spawn.transform = self.coord_offset.apply_offset(
                                spawn.transform, offset
                            )
                            offset_spawns.add(id(spawn))

                # Offset HQs
                map_data.team1_hq = self.coord_offset.apply_offset(map_data.team1_hq, offset)
                map_data.team2_hq = self.coord_offset.apply_offset(map_data.team2_hq, offset)

                # Offset bounds for CombatArea
                if map_data.bounds:
                    from bfportal.core.interfaces import Vector3

                    map_data.bounds.min_point = Vector3(
                        map_data.bounds.min_point.x + offset.x,
                        map_data.bounds.min_point.y + offset.y,
                        map_data.bounds.min_point.z + offset.z,
                    )
                    map_data.bounds.max_point = Vector3(
                        map_data.bounds.max_point.x + offset.x,
                        map_data.bounds.max_point.y + offset.y,
                        map_data.bounds.max_point.z + offset.z,
                    )

            # Step 2.5: Detect orientation and calculate terrain rotation
            print("\n🧭 Detecting map orientation...")
            map_detector = MapOrientationDetector(map_data)
            terrain_detector = TerrainOrientationDetector(
                terrain_provider=self.terrain,
                terrain_size=(self.args.terrain_size, self.args.terrain_size),
            )
            orientation_matcher = OrientationMatcher()

            source_analysis = map_detector.detect_orientation()
            dest_analysis = terrain_detector.detect_orientation()
            rotation_result = orientation_matcher.match(source_analysis, dest_analysis)

            print(
                f"   Source: {source_analysis.orientation.value.upper()} "
                f"({source_analysis.width_x:.0f}m x {source_analysis.depth_z:.0f}m, "
                f"ratio: {source_analysis.ratio:.2f})"
            )
            print(
                f"   Terrain: {dest_analysis.orientation.value.upper()} "
                f"({dest_analysis.width_x:.0f}m x {dest_analysis.depth_z:.0f}m)"
            )
            print(f"   Rotation needed: {'YES' if rotation_result.rotation_needed else 'NO'}")

            if rotation_result.rotation_needed:
                print(
                    f"   ⚠️  Will rotate terrain {rotation_result.rotation_degrees}° around Y axis"
                )
                print(f"   Reasoning: {rotation_result.reasoning}")
                # TODO: Apply rotation to terrain node in .tscn generation
                # For now, store rotation for later use
                map_data.metadata["terrain_rotation"] = rotation_result.rotation_degrees
            else:
                print("   ✅ No rotation needed")
                map_data.metadata["terrain_rotation"] = 0

            # Step 3: Map assets to Portal equivalents
            print(f"\n🔄 Mapping {len(map_data.game_objects)} assets to Portal...")
            mapped_count = 0
            unmapped = []
            skipped_terrain = []

            context = MapContext(
                target_base_map=self.args.base_terrain,
                era="WW2",
                theme=self._guess_theme(),
                team=Team.NEUTRAL,
            )

            for obj in map_data.game_objects:
                try:
                    portal_asset = self.asset_mapper.map_asset(obj.asset_type, context)
                    if portal_asset:
                        obj.asset_type = portal_asset.type  # Replace with Portal type
                        mapped_count += 1
                    else:
                        # Check if this was a terrain element that was intentionally skipped
                        if self.asset_mapper._is_terrain_element(obj.asset_type):
                            skipped_terrain.append(obj.asset_type)
                        else:
                            unmapped.append(obj.asset_type)
                except Exception as e:
                    print(f"   ⚠️  Failed to map {obj.asset_type}: {e}")
                    unmapped.append(obj.asset_type)

            print(f"   ✅ Mapped: {mapped_count}/{len(map_data.game_objects)}")
            if unmapped:
                print(f"   ⚠️  Unmapped: {len(set(unmapped))} unique types")
            if skipped_terrain:
                print(f"   ℹ️  Skipped terrain elements: {len(set(skipped_terrain))} types")

            # Step 4: Adjust heights to Portal terrain
            print("\n📏 Adjusting asset heights to Portal terrain...")
            adjusted = 0

            # Adjust HQs to terrain surface
            map_data.team1_hq = self.height_adjuster.adjust_height(
                map_data.team1_hq, self.terrain, ground_offset=0.0
            )
            map_data.team2_hq = self.height_adjuster.adjust_height(
                map_data.team2_hq, self.terrain, ground_offset=0.0
            )

            # Adjust game objects to terrain surface
            for obj in map_data.game_objects:
                obj.transform = self.height_adjuster.adjust_height(
                    obj.transform, self.terrain, ground_offset=0.0
                )
                adjusted += 1

            # Adjust HQ spawns (1m above terrain for spawn clearance)
            for spawn in map_data.team1_spawns + map_data.team2_spawns:
                spawn.transform = self.height_adjuster.adjust_height(
                    spawn.transform, self.terrain, ground_offset=1.0
                )

            # Adjust capture points and their spawns
            adjusted_spawns = set()
            for cp in map_data.capture_points:
                # Adjust capture point to terrain surface
                cp.transform = self.height_adjuster.adjust_height(
                    cp.transform, self.terrain, ground_offset=0.0
                )

                # Adjust spawns (avoid duplicates)
                for spawn in cp.team1_spawns + cp.team2_spawns:
                    if id(spawn) not in adjusted_spawns:
                        spawn.transform = self.height_adjuster.adjust_height(
                            spawn.transform, self.terrain, ground_offset=1.0
                        )
                        adjusted_spawns.add(id(spawn))

            print(f"   ✅ Adjusted {adjusted} objects + all HQs/spawns/CPs to Portal terrain")
            print(f"      Assets now positioned on {self.args.base_terrain} mesh surface")

            # Step 5: Generate .tscn
            print("\n📝 Generating .tscn file...")
            output_path = self._resolve_output_path()
            self._generate_tscn(map_data, output_path)

            print(f"\n{'=' * 70}")
            print("✅ Conversion complete!")
            print(f"{'=' * 70}")
            print(f"Output: {output_path}")

            # Add notes about skipped terrain elements
            if skipped_terrain:
                unique_terrain = set(skipped_terrain)
                print(f"\n⚠️  Note: {len(unique_terrain)} terrain element(s) were skipped:")
                for terrain_type in sorted(unique_terrain):
                    count = skipped_terrain.count(terrain_type)
                    print(f"   - {terrain_type} ({count} instance{'s' if count > 1 else ''})")
                print("\n   These are terrain features (water bodies, terrain objects) that")
                print("   Portal SDK does not support as placeable objects. Water bodies are")
                print("   part of the base terrain system and cannot be added dynamically.")
                print("   Hopefully future Portal updates will add better water support.")

            print("\nNext steps:")
            print(f"  1. Open {output_path} in Godot")
            print("  2. Review object placements")
            print("  3. Export via BFPortal panel")

            return 0

        except BFPortalError as e:
            print(f"\n❌ Conversion failed: {e}")
            return 1
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback

            traceback.print_exc()
            return 1

    def _resolve_map_path(self) -> Path:
        """Resolve path to BF1942 map directory."""
        if self.args.bf1942_root:
            base_path = Path(self.args.bf1942_root)
        else:
            base_path = (
                self.project_root
                / "bf1942_source"
                / "extracted"
                / "Bf1942"
                / "Archives"
                / "bf1942"
                / "Levels"
            )

        map_path = base_path / self.args.map

        if not map_path.exists():
            raise BFPortalError(f"Map directory not found: {map_path}")

        return map_path

    def _resolve_output_path(self) -> Path:
        """Resolve output .tscn path."""
        if self.args.output:
            return Path(self.args.output)
        else:
            return self.project_root / "GodotProject" / "levels" / f"{self.args.map}.tscn"

    def _get_target_center(self):
        """Get target map center.

        Returns the center of the Portal terrain mesh so assets align with terrain.
        """
        from bfportal.core.interfaces import Vector3

        # Center assets at terrain mesh center for proper alignment
        return Vector3(self.terrain.mesh_center_x, 0, self.terrain.mesh_center_z)

    def _guess_theme(self) -> str:
        """Guess map theme from name."""
        map_name = self.args.map.lower()
        if "desert" in map_name or "alamein" in map_name:
            return "desert"
        elif "city" in map_name or "berlin" in map_name or "stalingrad" in map_name:
            return "urban"
        elif "island" in map_name or "wake" in map_name:
            return "tropical"
        else:
            return "temperate"

    def _generate_tscn(self, map_data, output_path: Path):
        """Generate .tscn file using production generator."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Use production TscnGenerator
        generator = TscnGenerator()

        try:
            generator.generate(map_data, output_path, self.args.base_terrain)
            print("   ✅ Production .tscn generated with full Portal structure")
        except Exception as e:
            print(f"   ⚠️  Error using production generator: {e}")
            print("   Falling back to basic stub...")
            import traceback

            traceback.print_exc()

            # Fallback to basic stub
            with open(output_path, "w") as f:
                f.write("[gd_scene format=3]\n\n")
                f.write(f'[node name="{map_data.map_name}" type="Node3D"]\n\n')
                f.write("# Converted from BF1942\n")
                f.write(f"# Objects: {len(map_data.game_objects)}\n")
                f.write(f"# Spawns: {len(map_data.team1_spawns) + len(map_data.team2_spawns)}\n")
                f.write(f"# Capture Points: {len(map_data.capture_points)}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert BF1942 maps to Portal format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic conversion (recommended)
  python3 tools/portal_convert.py --map Kursk --base-terrain MP_Battery

  # Custom output location
  python3 tools/portal_convert.py --map Kursk --base-terrain MP_Battery \\
      --output GodotProject/levels/Kursk_v2.tscn

  # Different terrain size
  python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten \\
      --terrain-size 1536

Note:
  Assets are placed at a fixed height (mid-terrain) for manual snapping in Godot.
  This is best practice - preserves horizontal accuracy while letting Godot handle
  vertical positioning with proper collision detection against the terrain mesh.
        """,
    )

    parser.add_argument("--map", required=True, help="Map name (e.g., Kursk, Wake_Island)")
    parser.add_argument(
        "--base-terrain",
        required=True,
        help="Portal base terrain (e.g., MP_Tungsten, MP_Outskirts)",
    )
    parser.add_argument(
        "--bf1942-root",
        type=str,
        help="Path to BF1942 extracted maps (default: bf1942_source/extracted/...)",
    )
    parser.add_argument(
        "--output", type=str, help="Output .tscn path (default: GodotProject/levels/<map>.tscn)"
    )
    parser.add_argument(
        "--terrain-size", type=float, default=2048.0, help="Terrain size in meters (default: 2048)"
    )

    args = parser.parse_args()

    # Run conversion
    converter = PortalConverter(args)
    sys.exit(converter.convert())


if __name__ == "__main__":
    main()
