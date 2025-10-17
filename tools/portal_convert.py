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

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-17
"""

import argparse
import sys
from pathlib import Path

# Add bfportal to path
sys.path.insert(0, str(Path(__file__).parent))

# Import CLI utilities (DRY/SOLID)
from bfportal.cli import (
    EXIT_CONVERSION_ERROR,
    EXIT_ERROR,
    EXIT_SUCCESS,
    print_divider,
    print_error,
    print_header,
    print_info,
    print_separator,
    print_success,
    print_warning,
)
from bfportal.core.exceptions import BFPortalError
from bfportal.core.interfaces import MapContext, Team
from bfportal.engines.refractor.games.bf1942 import BF1942Engine
from bfportal.generators.constants.clearance import (
    MANUAL_OFFSET_X_DEFAULT,
    MANUAL_OFFSET_Z_DEFAULT,
)
from bfportal.generators.tscn_generator import TscnGenerator
from bfportal.mappers.asset_mapper import AssetMapper
from bfportal.orientation import (
    MapOrientationDetector,
    OrientationMatcher,
    TerrainOrientationDetector,
)
from bfportal.terrain.terrain_provider import HeightAdjuster, MeshTerrainProvider
from bfportal.transforms.centering_service import CenteringService
from bfportal.transforms.coordinate_offset import CoordinateOffset


class PortalConverter:
    """Main conversion orchestrator."""

    def __init__(self, args):
        """Initialize converter with command-line arguments."""
        self.args = args
        self.project_root = Path(__file__).parent.parent

        # Initialize components
        print_info("Initializing conversion pipeline...")

        # Game engine
        self.engine = BF1942Engine()
        print_success(f"{self.engine.get_game_name()} engine ({self.engine.get_engine_version()})")

        # Asset mapper
        portal_assets_path = self.project_root / "FbExportData" / "asset_types.json"
        mappings_path = (
            self.project_root / "tools" / "asset_audit" / "bf1942_to_portal_mappings.json"
        )

        self.asset_mapper = AssetMapper(portal_assets_path)
        self.asset_mapper.load_mappings(mappings_path)
        print_success("Asset mapper loaded (733 mappings)")

        # Coordinate offset calculator
        self.coord_offset = CoordinateOffset()
        print_success("Coordinate offset calculator")

        # Centering service (SOLID: Single responsibility for all centering logic)
        self.centering_service = CenteringService()
        print_success("Universal centering service")

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

        print_info(f"Loading Portal terrain mesh: {terrain_mesh_path.name}")
        self.terrain = MeshTerrainProvider(
            mesh_path=terrain_mesh_path, terrain_size=(args.terrain_size, args.terrain_size)
        )
        print_success(f"Terrain loaded: {len(self.terrain.vertices):,} vertices")
        print(
            f"   Mesh internal Y: {self.terrain.mesh_min_height:.1f}m - {self.terrain.mesh_max_height:.1f}m"
        )
        print(
            f"   Portal Y (normalized): {self.terrain.min_height:.1f}m - {self.terrain.max_height:.1f}m"
        )
        print(
            f"   Y baseline offset: {self.terrain.terrain_y_baseline:.1f}m (subtracted for Portal compatibility)"
        )
        print(
            f"   Mesh bounds: X[{self.terrain.mesh_min_x:.1f}, {self.terrain.mesh_max_x:.1f}] "
            f"Z[{self.terrain.mesh_min_z:.1f}, {self.terrain.mesh_max_z:.1f}]"
        )
        print(
            f"   Mesh center: ({self.terrain.mesh_center_x:.1f}, {self.terrain.mesh_center_z:.1f})"
        )
        print(f"   Grid resolution: {self.terrain.grid_resolution}x{self.terrain.grid_resolution}")

        self.height_adjuster = HeightAdjuster()

    def convert(self) -> int:
        """Execute the conversion pipeline.

        Returns:
            Exit code (EXIT_SUCCESS, EXIT_ERROR, or EXIT_CONVERSION_ERROR)
        """
        try:
            print_separator()
            print_divider()
            print_header(f"Converting {self.args.map} to Portal")
            print_divider()

            # Step 1: Parse BF1942 map
            map_data = self._step_parse_map()

            # Step 2: Apply coordinate transformations
            map_data = self._step_apply_coordinate_transforms(map_data)

            # Step 3: Handle terrain rotation
            map_data = self._step_handle_terrain_rotation(map_data)

            # Step 4: Map assets to Portal
            map_data, _, _, _ = self._step_map_assets_to_portal(map_data)

            # Step 5: Report height positioning strategy
            self._step_report_height_strategy()

            # Step 6: Generate output
            output_path = self._step_generate_output(map_data)

            # Step 7: Display completion summary
            self._step_display_summary(output_path, map_data)

            return EXIT_SUCCESS

        except BFPortalError as e:
            print_separator()
            print_error(f"Conversion failed: {e}")
            return EXIT_CONVERSION_ERROR
        except Exception as e:
            print_separator()
            print_error(f"Unexpected error: {e}")
            import traceback

            traceback.print_exc()
            return EXIT_ERROR

    def _step_parse_map(self):
        """Step 1: Parse BF1942 map files.

        Returns:
            MapData with parsed objects, spawns, and capture points
        """
        map_path = self._resolve_map_path()
        print_separator()
        print_info(f"Source: {map_path}")

        return self.engine.parse_map(map_path)

    def _step_apply_coordinate_transforms(self, map_data):
        """Step 2: Calculate and apply coordinate offset to center map on terrain.

        Args:
            map_data: Parsed map data

        Returns:
            MapData with offset applied to all objects
        """
        print_separator()
        print_info("Calculating coordinate offset...")
        all_objects = (
            list(map_data.team1_spawns) + list(map_data.team2_spawns) + map_data.game_objects
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
                # __post_init__ ensures these are never None, but need explicit check for mypy
                team1_spawns = cp.team1_spawns if cp.team1_spawns is not None else []
                team2_spawns = cp.team2_spawns if cp.team2_spawns is not None else []
                for spawn in team1_spawns + team2_spawns:
                    if id(spawn) not in offset_spawns:
                        spawn.transform = self.coord_offset.apply_offset(spawn.transform, offset)
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

        return map_data

    def _step_handle_terrain_rotation(self, map_data):
        """Step 3: Handle terrain rotation (user override or automatic detection).

        Args:
            map_data: Parsed map data with coordinate transforms applied

        Returns:
            MapData with terrain rotation metadata and recentered assets if rotated
        """
        if self.args.rotate_terrain:
            # User explicitly requested terrain rotation - skip automatic detection
            print_separator()
            print_info("Terrain rotation: MANUAL (--rotate-terrain flag)")
            print("   User requested 90° CW rotation")
            map_data.metadata["terrain_rotation"] = 90

            # Recenter assets to origin (0, 0) for rotated terrain
            print_separator()
            print_info("Recentering assets for rotated terrain...")

            # Calculate current asset centroid
            from bfportal.core.interfaces import GameObject, Vector3

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

            current_center = self.coord_offset.calculate_centroid(objects_for_centroid)

            # Target position for asset centroid after recentering
            manual_offset_x = MANUAL_OFFSET_X_DEFAULT
            manual_offset_z = MANUAL_OFFSET_Z_DEFAULT
            target_origin = Vector3(manual_offset_x, 0, manual_offset_z)
            recenter_offset = self.coord_offset.calculate_offset(current_center, target_origin)

            print(
                f"   Current center: ({current_center.x:.1f}, {current_center.y:.1f}, {current_center.z:.1f})"
            )
            print("   Target origin: (0.0, 0.0, 0.0)")
            print(
                f"   Recenter offset: ({recenter_offset.x:.1f}, {recenter_offset.y:.1f}, {recenter_offset.z:.1f})"
            )

            # Apply recenter offset to all objects
            for obj in map_data.game_objects:
                obj.transform = self.coord_offset.apply_offset(obj.transform, recenter_offset)

            for spawn in map_data.team1_spawns + map_data.team2_spawns:
                spawn.transform = self.coord_offset.apply_offset(spawn.transform, recenter_offset)

            # Apply to capture points
            offset_spawns = set()
            for cp in map_data.capture_points:
                cp.transform = self.coord_offset.apply_offset(cp.transform, recenter_offset)
                team1_spawns = cp.team1_spawns if cp.team1_spawns is not None else []
                team2_spawns = cp.team2_spawns if cp.team2_spawns is not None else []
                for spawn in team1_spawns + team2_spawns:
                    if id(spawn) not in offset_spawns:
                        spawn.transform = self.coord_offset.apply_offset(
                            spawn.transform, recenter_offset
                        )
                        offset_spawns.add(id(spawn))

            # Apply to HQs
            map_data.team1_hq = self.coord_offset.apply_offset(map_data.team1_hq, recenter_offset)
            map_data.team2_hq = self.coord_offset.apply_offset(map_data.team2_hq, recenter_offset)

            # Apply to bounds
            if map_data.bounds:
                map_data.bounds.min_point = Vector3(
                    map_data.bounds.min_point.x + recenter_offset.x,
                    map_data.bounds.min_point.y + recenter_offset.y,
                    map_data.bounds.min_point.z + recenter_offset.z,
                )
                map_data.bounds.max_point = Vector3(
                    map_data.bounds.max_point.x + recenter_offset.x,
                    map_data.bounds.max_point.y + recenter_offset.y,
                    map_data.bounds.max_point.z + recenter_offset.z,
                )

            print_success("Recentered all objects to origin")
        else:
            # Automatic orientation detection
            print_separator()
            print_info("Detecting map orientation...")
            map_detector = MapOrientationDetector(map_data)

            # Use actual mesh dimensions for orientation detection
            actual_terrain_width = self.terrain.mesh_max_x - self.terrain.mesh_min_x
            actual_terrain_depth = self.terrain.mesh_max_z - self.terrain.mesh_min_z

            terrain_detector = TerrainOrientationDetector(
                terrain_provider=self.terrain,
                terrain_size=(actual_terrain_width, actual_terrain_depth),
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
                print_warning(
                    f"Will rotate terrain {rotation_result.rotation_degrees}° around Y axis"
                )
                print(f"   Reasoning: {rotation_result.reasoning}")
                map_data.metadata["terrain_rotation"] = rotation_result.rotation_degrees
            else:
                print_success("No rotation needed")
                map_data.metadata["terrain_rotation"] = 0

        return map_data

    def _step_map_assets_to_portal(self, map_data):
        """Step 4: Map BF1942 assets to Portal equivalents.

        Args:
            map_data: Parsed map data with transforms applied

        Returns:
            Tuple of (map_data, mapped_count, unmapped_list, skipped_terrain_list)
        """
        print_separator()
        print_info(f"Mapping {len(map_data.game_objects)} assets to Portal...")
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
                    obj.asset_type = portal_asset.type
                    mapped_count += 1
                else:
                    if self.asset_mapper._is_terrain_element(obj.asset_type):
                        skipped_terrain.append(obj.asset_type)
                    else:
                        unmapped.append(obj.asset_type)
            except Exception as e:
                print(f"   ⚠️  Failed to map {obj.asset_type}: {e}")
                unmapped.append(obj.asset_type)

        print_success(f"Mapped: {mapped_count}/{len(map_data.game_objects)}")
        if unmapped:
            print_warning(f"Unmapped: {len(set(unmapped))} unique types")
        if skipped_terrain:
            print_info(f"Skipped terrain elements: {len(set(skipped_terrain))} types")

        return map_data, mapped_count, unmapped, skipped_terrain

    def _step_report_height_strategy(self):
        """Step 5: Report height positioning strategy."""
        print_separator()
        print_info("Height positioning...")
        print("   Heights preserved from BF1942 (use Godot trimesh snapping for final placement)")
        print(f"   Terrain: {self.args.base_terrain} (snap assets manually in Godot editor)")

    def _step_generate_output(self, map_data):
        """Step 6: Generate .tscn output file.

        Args:
            map_data: Fully processed map data

        Returns:
            Path to generated output file
        """
        print_separator()
        print_info("Generating .tscn file...")
        output_path = self._resolve_output_path()
        self._generate_tscn(map_data, output_path)
        return output_path

    def _step_display_summary(self, output_path, map_data):
        """Step 7: Display completion summary and next steps.

        Args:
            output_path: Path to generated output file
            map_data: Processed map data (includes skipped terrain in earlier step)
        """
        # Recalculate skipped terrain for summary (needed since we return it from mapping step)
        skipped_terrain = []
        for obj in map_data.game_objects:
            if self.asset_mapper._is_terrain_element(obj.asset_type):
                skipped_terrain.append(obj.asset_type)

        print_separator()
        print_divider()
        print_success("Conversion complete!")
        print_divider()
        print(f"Output: {output_path}")

        # Add notes about skipped terrain elements
        if skipped_terrain:
            unique_terrain = set(skipped_terrain)
            print_separator()
            print_warning(f"Note: {len(unique_terrain)} terrain element(s) were skipped:")
            for terrain_type in sorted(unique_terrain):
                count = skipped_terrain.count(terrain_type)
                print(f"   - {terrain_type} ({count} instance{'s' if count > 1 else ''})")
            print_separator()
            print("   These are terrain features (water bodies, terrain objects) that")
            print("   Portal SDK does not support as placeable objects. Water bodies are")
            print("   part of the base terrain system and cannot be added dynamically.")
            print("   Hopefully future Portal updates will add better water support.")

        print_separator()
        print_header("Next Steps")
        print(f"  1. Open {output_path} in Godot")
        print("  2. Review object placements")
        print("  3. Export via BFPortal panel")
        print_separator()

    def _resolve_map_path(self) -> Path:
        """Resolve path to BF1942 map directory."""
        # Type-safe access to argparse args
        bf1942_root: str | None = self.args.bf1942_root
        map_name: str = self.args.map

        if bf1942_root:
            base_path = Path(bf1942_root)
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

        map_path = base_path / map_name

        if not map_path.exists():
            raise BFPortalError(f"Map directory not found: {map_path}")

        return map_path

    def _resolve_output_path(self) -> Path:
        """Resolve output .tscn path."""
        if self.args.output:
            return Path(self.args.output)
        else:
            # Capitalize map name for consistent naming convention
            map_name_capitalized = self.args.map.capitalize()
            return self.project_root / "GodotProject" / "levels" / f"{map_name_capitalized}.tscn"

    def _get_target_center(self):
        """Get target center for BF1942 assets - Portal terrain's center.

        NEW APPROACH: Keep Portal terrain at (0,0,0), center BF1942 assets on terrain.
        This eliminates all centering complexity and matches Portal's coordinate system.

        Returns:
            Vector3 at Portal terrain's mesh center (terrain stays at origin)
        """
        from bfportal.core.interfaces import Vector3

        # Return terrain's mesh center - BF1942 assets will center on this point
        # Terrain itself stays at (0,0,0) in Godot, matching Portal requirements
        return Vector3(
            self.terrain.mesh_center_x,
            0.0,
            self.terrain.mesh_center_z,  # Terrain center X/Z  # Y=0 baseline
        )

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

        # Use production TscnGenerator with CenteringService injection (SOLID: Dependency Injection)
        generator = TscnGenerator(centering_service=self.centering_service)

        try:
            # Pass terrain mesh bounds for CombatArea generation with 20m exclusion zone
            terrain_bounds = (
                self.terrain.mesh_min_x,
                self.terrain.mesh_max_x,
                self.terrain.mesh_min_z,
                self.terrain.mesh_max_z,
            )

            # Pass terrain offsets - rotation is already stored in map_data.metadata
            # The generator will check metadata["terrain_rotation"] to handle rotation
            generator.generate(
                map_data,
                output_path,
                self.args.base_terrain,
                terrain_y_offset=self.terrain.terrain_y_baseline,
                terrain_center_x=self.terrain.mesh_center_x,
                terrain_center_z=self.terrain.mesh_center_z,
                rotate_terrain=(map_data.metadata.get("terrain_rotation", 0) != 0),
                terrain_bounds=terrain_bounds,
            )
            print_success("Production .tscn generated with full Portal structure")
            print(
                f"   Terrain offset: {self.terrain.terrain_y_baseline:.1f}m (for Godot visualization)"
            )
            print("   CombatArea: Matches terrain bounds with 20m exclusion zone")
        except Exception as e:
            print_warning(f"Error using production generator: {e}")
            print_info("Falling back to basic stub...")
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
    parser.add_argument(
        "--rotate-terrain",
        action="store_true",
        help="Rotate terrain 90° clockwise for portrait-oriented maps (rotates terrain mesh + CombatArea)",
    )

    args = parser.parse_args()

    # Run conversion
    converter = PortalConverter(args)
    sys.exit(converter.convert())


if __name__ == "__main__":
    main()
