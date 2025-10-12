#!/usr/bin/env python3
"""Portal Rebase CLI - Switch Portal base terrains without re-conversion.

This tool implements Workflow B: Portal → Portal base map switching.

Use this when you want to try a different Portal base terrain for an
already-converted map, without re-doing the entire BF1942 → Portal conversion.

Example:
    python3 tools/portal_rebase.py \
        --input GodotProject/levels/Kursk.tscn \
        --output GodotProject/levels/Kursk_outskirts.tscn \
        --new-base MP_Outskirts

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-11
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bfportal.core.exceptions import BFPortalError
from bfportal.core.interfaces import Vector3
from bfportal.terrain.terrain_provider import (
    CustomHeightmapProvider,
    OutskirtsTerrainProvider,
    TungstenTerrainProvider,
)
from bfportal.transforms.coordinate_offset import CoordinateOffset
from bfportal.transforms.map_rebaser import MapRebaser

# Map center coordinates for Portal base terrains
PORTAL_BASE_CENTERS = {
    "MP_Tungsten": Vector3(0.0, 0.0, 0.0),
    "MP_Outskirts": Vector3(0.0, 0.0, 0.0),
    "MP_Aftermath": Vector3(0.0, 0.0, 0.0),
    "MP_Battery": Vector3(0.0, 0.0, 0.0),
    "MP_Everglades": Vector3(0.0, 0.0, 0.0),
    "MP_Breakaway": Vector3(0.0, 0.0, 0.0),
    "MP_Nexus": Vector3(0.0, 0.0, 0.0),
}


class PortalRebaseApp:
    """CLI application for rebasing Portal maps to different base terrains."""

    def __init__(self):
        """Initialize the app."""
        self.args: argparse.Namespace

    def parse_args(self) -> argparse.Namespace:
        """Parse command-line arguments.

        Returns:
            Parsed arguments namespace
        """
        parser = argparse.ArgumentParser(
            description="Switch Portal base terrain without re-conversion",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Basic rebase from Tungsten to Outskirts
  python3 tools/portal_rebase.py \\
      --input GodotProject/levels/Kursk.tscn \\
      --output GodotProject/levels/Kursk_outskirts.tscn \\
      --new-base MP_Outskirts

  # Rebase with custom heightmap
  python3 tools/portal_rebase.py \\
      --input GodotProject/levels/Wake.tscn \\
      --output GodotProject/levels/Wake_tungsten.tscn \\
      --new-base MP_Tungsten \\
      --heightmap GodotProject/terrain/Tungsten_heightmap.png \\
      --terrain-size 2048 \\
      --min-height 50 \\
      --max-height 150

Available Base Terrains:
  - MP_Tungsten (open terrain, large)
  - MP_Outskirts (urban)
  - MP_Aftermath (destroyed city)
  - MP_Battery (coastal)
  - MP_Everglades (swamp)
  - MP_Breakaway (snow)
  - MP_Nexus (futuristic)
            """,
        )

        parser.add_argument(
            "--input", type=Path, required=True, help="Input .tscn file (existing Portal map)"
        )

        parser.add_argument(
            "--output", type=Path, required=True, help="Output .tscn file (rebased map)"
        )

        parser.add_argument(
            "--new-base",
            type=str,
            required=True,
            choices=list(PORTAL_BASE_CENTERS.keys()),
            help="Target Portal base terrain",
        )

        parser.add_argument(
            "--heightmap", type=Path, help="Custom heightmap for new base terrain (PNG)"
        )

        parser.add_argument(
            "--terrain-size", type=int, default=2048, help="Terrain size in meters (default: 2048)"
        )

        parser.add_argument(
            "--min-height",
            type=float,
            default=0.0,
            help="Minimum terrain height in meters (default: 0)",
        )

        parser.add_argument(
            "--max-height",
            type=float,
            default=200.0,
            help="Maximum terrain height in meters (default: 200)",
        )

        parser.add_argument("--map-center-x", type=float, help="Override map center X coordinate")

        parser.add_argument("--map-center-z", type=float, help="Override map center Z coordinate")

        return parser.parse_args()

    def create_terrain_provider(self):
        """Create terrain provider for new base terrain.

        Returns:
            ITerrainProvider instance

        Raises:
            FileNotFoundError: If custom heightmap not found
        """
        if self.args.heightmap:
            # Use custom heightmap
            if not self.args.heightmap.exists():
                raise FileNotFoundError(f"Heightmap not found: {self.args.heightmap}")

            print(f"📊 Using custom heightmap: {self.args.heightmap}")
            return CustomHeightmapProvider(
                heightmap_path=self.args.heightmap,
                terrain_size=(self.args.terrain_size, self.args.terrain_size),
                height_range=(self.args.min_height, self.args.max_height),
            )

        # Use built-in terrain provider
        base_terrain = self.args.new_base
        print(f"🗺️  Using built-in terrain: {base_terrain}")

        # Get portal SDK root (two dirs up from tools/)
        portal_sdk_root = Path(__file__).parent.parent

        if base_terrain == "MP_Tungsten":
            return TungstenTerrainProvider(portal_sdk_root)
        elif base_terrain == "MP_Outskirts":
            return OutskirtsTerrainProvider(portal_sdk_root)
        else:
            # Fallback to generic provider (flat terrain estimation)
            print(f"  ⚠️  No specific terrain provider for {base_terrain}, using flat estimation")
            return TungstenTerrainProvider(portal_sdk_root)  # Generic flat provider

    def run(self) -> int:
        """Execute the rebasing process.

        Returns:
            Exit code (0 for success, 1 for error)
        """
        self.args = self.parse_args()

        print("=" * 70)
        print("🔄 Portal Base Terrain Rebaser")
        print("=" * 70)
        print()

        try:
            # Validate input file
            if not self.args.input.exists():
                print(f"❌ Error: Input file not found: {self.args.input}")
                return 1

            # Ensure output directory exists
            self.args.output.parent.mkdir(parents=True, exist_ok=True)

            # Get map center for new base terrain
            if self.args.map_center_x is not None and self.args.map_center_z is not None:
                map_center = Vector3(self.args.map_center_x, 0.0, self.args.map_center_z)
                print(f"📍 Using custom map center: ({map_center.x}, {map_center.z})")
            else:
                map_center = PORTAL_BASE_CENTERS[self.args.new_base]
                print(f"📍 Using default center for {self.args.new_base}")

            # Create terrain provider
            terrain_provider = self.create_terrain_provider()

            # Create coordinate offset calculator
            offset_calc = CoordinateOffset()

            # TODO: Create bounds validator when implemented
            # For now, use None (rebaser will skip validation)
            bounds_validator = None

            # Create rebaser
            rebaser = MapRebaser(
                terrain_provider=terrain_provider,
                offset_calculator=offset_calc,
                bounds_validator=bounds_validator,
            )

            # Perform rebasing
            print()
            stats = rebaser.rebase_map(
                input_tscn=self.args.input,
                output_tscn=self.args.output,
                new_base_terrain=self.args.new_base,
                new_map_center=map_center,
            )

            # Report results
            print()
            print("=" * 70)
            print("✅ Rebasing Complete!")
            print("=" * 70)
            print("📊 Statistics:")
            print(f"   - Total objects: {stats['total_objects']}")
            print(f"   - Height adjusted: {stats['height_adjusted']}")
            print(f"   - Out of bounds: {stats['out_of_bounds']}")
            print(
                f"   - Offset applied: ({stats['offset_applied']['x']:.1f}, "
                f"{stats['offset_applied']['y']:.1f}, "
                f"{stats['offset_applied']['z']:.1f})"
            )
            print()
            print(f"📄 Output: {self.args.output}")
            print()
            print("⚠️  Next Steps:")
            print("   1. Open in Godot editor")
            print("   2. Verify object placements")
            print("   3. Manually adjust terrain features if needed")
            print("   4. Export via BFPortal panel")
            print()

            return 0

        except BFPortalError as e:
            print(f"❌ Error: {e}")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback

            traceback.print_exc()
            return 1


def main():
    """Entry point."""
    app = PortalRebaseApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
