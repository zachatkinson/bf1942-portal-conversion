#!/usr/bin/env python3
"""Portal Adjust Heights CLI - Adjust object heights to match terrain.

This tool adjusts object heights in a .tscn file to match the underlying terrain.
Useful for:

- Re-adjusting heights after terrain changes
- Fixing floating/underground objects
- Testing different heightmaps
- Running as post-processing step

Can be run multiple times without side effects (idempotent).

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-11
"""

import argparse
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bfportal.core.exceptions import BFPortalError, TerrainError
from bfportal.core.interfaces import Rotation, Transform, Vector3
from bfportal.terrain.terrain_provider import (
    CustomHeightmapProvider,
    HeightAdjuster,
    OutskirtsTerrainProvider,
    TungstenTerrainProvider,
)


class PortalAdjustHeightsApp:
    """CLI application for adjusting object heights."""

    def __init__(self):
        """Initialize the app."""
        self.args: argparse.Namespace
        self.height_adjuster = HeightAdjuster()

    def parse_args(self) -> argparse.Namespace:
        """Parse command-line arguments.

        Returns:
            Parsed arguments namespace
        """
        parser = argparse.ArgumentParser(
            description="Adjust object heights to match terrain",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Adjust heights using custom heightmap
  python3 tools/portal_adjust_heights.py \\
      --input GodotProject/levels/Kursk.tscn \\
      --output GodotProject/levels/Kursk_adjusted.tscn \\
      --heightmap GodotProject/terrain/Kursk_heightmap.png \\
      --terrain-size 2048 \\
      --min-height 73 \\
      --max-height 217

  # In-place adjustment (overwrites input file)
  python3 tools/portal_adjust_heights.py \\
      --input GodotProject/levels/Kursk.tscn \\
      --heightmap GodotProject/terrain/Kursk_heightmap.png \\
      --in-place

  # Use Portal base terrain provider
  python3 tools/portal_adjust_heights.py \\
      --input GodotProject/levels/Wake.tscn \\
      --output GodotProject/levels/Wake_adjusted.tscn \\
      --base-terrain MP_Tungsten

  # Adjust with ground offset
  python3 tools/portal_adjust_heights.py \\
      --input GodotProject/levels/Kursk.tscn \\
      --heightmap GodotProject/terrain/Kursk_heightmap.png \\
      --ground-offset 0.5 \\
      --in-place

Use Cases:
  - After changing base terrain
  - After manual terrain sculpting
  - After importing heightmap changes
  - As final polishing step
            """,
        )

        parser.add_argument("--input", type=Path, required=True, help="Input .tscn file")

        parser.add_argument(
            "--output", type=Path, help="Output .tscn file (required unless --in-place)"
        )

        parser.add_argument(
            "--in-place", action="store_true", help="Modify input file directly (overwrites input)"
        )

        parser.add_argument("--heightmap", type=Path, help="Custom heightmap PNG file")

        parser.add_argument(
            "--base-terrain",
            type=str,
            choices=["MP_Tungsten", "MP_Outskirts"],
            help="Use Portal base terrain provider",
        )

        parser.add_argument(
            "--terrain-size", type=int, default=2048, help="Terrain size in meters (default: 2048)"
        )

        parser.add_argument(
            "--min-height", type=float, default=0.0, help="Minimum terrain height (default: 0)"
        )

        parser.add_argument(
            "--max-height", type=float, default=200.0, help="Maximum terrain height (default: 200)"
        )

        parser.add_argument(
            "--ground-offset",
            type=float,
            default=0.0,
            help="Additional offset above ground in meters (default: 0)",
        )

        parser.add_argument(
            "--tolerance",
            type=float,
            default=2.0,
            help="Height difference tolerance - only adjust if off by more than this (default: 2.0m)",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be adjusted without modifying files",
        )

        return parser.parse_args()

    def create_terrain_provider(self):
        """Create terrain provider.

        Returns:
            ITerrainProvider instance

        Raises:
            ValueError: If terrain provider configuration invalid
        """
        if self.args.heightmap:
            if not self.args.heightmap.exists():
                raise FileNotFoundError(f"Heightmap not found: {self.args.heightmap}")

            print(f"📊 Using custom heightmap: {self.args.heightmap.name}")
            return CustomHeightmapProvider(
                heightmap_path=self.args.heightmap,
                terrain_size=(self.args.terrain_size, self.args.terrain_size),
                height_range=(self.args.min_height, self.args.max_height),
            )

        elif self.args.base_terrain:
            print(f"🗺️  Using base terrain: {self.args.base_terrain}")

            # Get portal SDK root (two dirs up from tools/)
            portal_sdk_root = Path(__file__).parent.parent

            if self.args.base_terrain == "MP_Tungsten":
                return TungstenTerrainProvider(portal_sdk_root)
            elif self.args.base_terrain == "MP_Outskirts":
                return OutskirtsTerrainProvider(portal_sdk_root)

        else:
            raise ValueError("Must specify either --heightmap or --base-terrain")

    def parse_transform(self, transform_str: str) -> Transform | None:
        """Parse Transform3D string from .tscn.

        Args:
            transform_str: Transform string like "1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 50, 200"

        Returns:
            Transform object or None if parsing fails
        """
        try:
            values = [float(v.strip()) for v in transform_str.split(",")]
            if len(values) >= 12:
                position = Vector3(values[9], values[10], values[11])
                # For simplicity, we don't extract rotation from matrix
                rotation = Rotation(0, 0, 0)
                return Transform(position, rotation)
        except Exception:
            pass

        return None

    def format_transform(self, transform: Transform, original_matrix: str) -> str:
        """Format transform back to Transform3D string.

        Args:
            transform: Updated transform
            original_matrix: Original matrix values (to preserve rotation)

        Returns:
            Updated Transform3D string
        """
        try:
            values = [float(v.strip()) for v in original_matrix.split(",")]
            if len(values) >= 12:
                # Preserve rotation matrix, update position
                values[9] = transform.position.x
                values[10] = transform.position.y
                values[11] = transform.position.z
                return ", ".join(str(v) for v in values)
        except Exception:
            pass

        return original_matrix

    def adjust_heights_in_tscn(self, content: str, terrain) -> tuple[str, int]:
        """Adjust heights in .tscn content.

        Args:
            content: .tscn file content
            terrain: Terrain provider

        Returns:
            Tuple of (updated_content, num_adjusted)
        """
        # Pattern to match node with transform
        pattern = r'(\[node name="([^"]+)"[^\]]*\]\s*transform = Transform3D\()([^)]+)(\))'

        adjusted_count = 0
        skip_nodes = ["HQ", "Spawn", "Combat", "Static", "Terrain", "Area", "Volume", "Trigger"]

        def replace_transform(match):
            nonlocal adjusted_count

            full_match = match.group(0)
            node_name = match.group(2)
            transform_values = match.group(3)

            # Skip system nodes
            if any(skip in node_name for skip in skip_nodes):
                return full_match

            # Parse transform
            transform = self.parse_transform(transform_values)
            if not transform:
                return full_match

            # Query terrain height
            try:
                terrain_height = terrain.get_height_at(transform.position.x, transform.position.z)

                height_diff = abs(transform.position.y - terrain_height)

                # Only adjust if difference exceeds tolerance
                if height_diff > self.args.tolerance:
                    if self.args.dry_run:
                        print(
                            f"   Would adjust {node_name}: "
                            f"Y={transform.position.y:.1f} → {terrain_height + self.args.ground_offset:.1f} "
                            f"(diff: {height_diff:.1f}m)"
                        )

                    # Update position
                    new_transform = Transform(
                        position=Vector3(
                            transform.position.x,
                            terrain_height + self.args.ground_offset,
                            transform.position.z,
                        ),
                        rotation=transform.rotation,
                    )

                    adjusted_count += 1

                    # Format back to string
                    new_values = self.format_transform(new_transform, transform_values)
                    return f"{match.group(1)}{new_values}{match.group(4)}"

            except Exception as e:
                if self.args.dry_run:
                    print(f"   ⚠️  Cannot adjust {node_name}: {e}")

            return full_match

        # Replace all transforms
        updated_content = re.sub(pattern, replace_transform, content)

        return updated_content, adjusted_count

    def run(self) -> int:
        """Execute height adjustment.

        Returns:
            Exit code (0 for success, 1 for error)
        """
        self.args = self.parse_args()

        print("=" * 70)
        print("📏 Portal Height Adjuster")
        print("=" * 70)
        print()

        try:
            # Validate arguments
            if not self.args.in_place and not self.args.output:
                print("❌ Error: Must specify either --output or --in-place")
                return 1

            if not self.args.input.exists():
                print(f"❌ Error: Input file not found: {self.args.input}")
                return 1

            # Create terrain provider
            terrain = self.create_terrain_provider()

            # Read input file
            print(f"📖 Reading {self.args.input.name}...")
            with open(self.args.input) as f:
                content = f.read()

            # Adjust heights
            print("🔄 Adjusting heights...")
            print(f"   Tolerance: {self.args.tolerance}m")
            print(f"   Ground offset: {self.args.ground_offset}m")
            if self.args.dry_run:
                print("   🔍 DRY RUN MODE - No files will be modified")
            print()

            updated_content, adjusted_count = self.adjust_heights_in_tscn(content, terrain)

            # Report results
            print()
            print("=" * 70)
            print("📊 Results")
            print("=" * 70)
            print(f"   Objects adjusted: {adjusted_count}")
            print()

            # Write output
            if not self.args.dry_run:
                output_path = self.args.input if self.args.in_place else self.args.output

                if self.args.in_place:
                    # Create backup
                    backup_path = self.args.input.with_suffix(".tscn.backup")
                    with open(backup_path, "w") as f:
                        f.write(content)
                    print(f"💾 Backup saved: {backup_path.name}")

                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(updated_content)

                print(f"✅ Updated file: {output_path}")
                print()
            else:
                print("🔍 DRY RUN - No files modified")
                print()

            return 0

        except TerrainError as e:
            print(f"❌ Terrain error: {e}")
            return 1
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
    app = PortalAdjustHeightsApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
