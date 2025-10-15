#!/usr/bin/env python3
"""
Terrain snapping tool using modular SOLID architecture.

This tool adjusts object heights in .tscn files to match the Portal terrain surface.
It uses specialized snappers for different object categories (gameplay, vegetation, props).

Usage:
    python3 tools/terrain_snap.py --map Kursk --terrain MP_Tungsten

Architecture:
- GameplaySnapper: HQs, spawns, capture points
- VegetationSnapper: Trees, plants, bushes
- PropSnapper: Generic objects, rocks, crates (catch-all)
- SnappingOrchestrator: Coordinates all snappers

Best Practices (from CLAUDE.md):
- Single Responsibility: Each snapper handles one object category
- Open/Closed: Add new snappers without modifying existing ones
- Dependency Injection: Snappers injected into orchestrator
- Interface Segregation: Simple, focused IObjectSnapper interface
"""

import argparse
import sys
from pathlib import Path

from bfportal.terrain.snappers import (
    GameplaySnapper,
    PropSnapper,
    VegetationSnapper,
)
from bfportal.terrain.snappers.snapping_orchestrator import SnappingOrchestrator
from bfportal.terrain.terrain_provider import MeshTerrainProvider


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Snap objects to terrain surface in .tscn files using modular snappers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Snap all objects in Kursk to MP_Tungsten terrain:
    %(prog)s --map Kursk --terrain MP_Tungsten

  Dry run (preview changes without writing):
    %(prog)s --map Kursk --terrain MP_Tungsten --dry-run

Architecture:
  This tool uses specialized snappers for different object types:
  - GameplaySnapper: HQs (0m), spawns (+1m), capture points (0m)
  - VegetationSnapper: Trees, plants, bushes (0m)
  - PropSnapper: Generic objects, rocks, crates (0m, catch-all)

  Each snapper handles its category independently, making it easy to:
  - Add new object categories
  - Customize height logic per category
  - Test snappers independently

Workflow:
  1. Run portal_convert.py to create initial .tscn
  2. Run this tool to snap objects to terrain
  3. Export to spatial.json: python3 tools/export_to_portal.py <map>
  4. Import to Portal

This tool uses the same terrain mesh as the conversion pipeline,
ensuring objects are positioned precisely on the terrain surface.
        """,
    )

    parser.add_argument("--map", required=True, help="Map name (e.g., Kursk)")
    parser.add_argument("--terrain", required=True, help="Terrain base map (e.g., MP_Tungsten)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to file",
    )
    parser.add_argument(
        "--terrain-size",
        type=float,
        default=2048.0,
        help="Terrain size in meters (default: 2048)",
    )

    args = parser.parse_args()

    # Paths
    project_root = Path.cwd()
    tscn_path = project_root / "GodotProject" / "levels" / f"{args.map}.tscn"
    terrain_mesh_path = (
        project_root / "GodotProject" / "raw" / "models" / f"{args.terrain}_Terrain.glb"
    )

    # Validate
    if not tscn_path.exists():
        print(f"❌ Error: .tscn not found: {tscn_path}", file=sys.stderr)
        print("\nAvailable maps:", file=sys.stderr)
        levels_dir = project_root / "GodotProject" / "levels"
        if levels_dir.exists():
            for tscn in sorted(levels_dir.glob("*.tscn")):
                print(f"  - {tscn.stem}", file=sys.stderr)
        return 1

    if not terrain_mesh_path.exists():
        print(f"❌ Error: Terrain mesh not found: {terrain_mesh_path}", file=sys.stderr)
        return 1

    try:
        # Load terrain
        print(f"\n🗺️  Loading terrain mesh: {terrain_mesh_path.name}")
        terrain = MeshTerrainProvider(
            mesh_path=terrain_mesh_path,
            terrain_size=(args.terrain_size, args.terrain_size),
        )
        print(f"   ✅ Loaded {len(terrain.vertices):,} vertices")
        print(f"   Height range: {terrain.min_height:.1f}m - {terrain.max_height:.1f}m")

        # Create snappers (order matters - first match wins)
        # GameplaySnapper before PropSnapper since PropSnapper is catch-all
        snappers = [
            GameplaySnapper(terrain),
            VegetationSnapper(terrain),
            PropSnapper(terrain),
        ]

        print(f"\n   📦 Loaded {len(snappers)} snapper modules:")
        for snapper in snappers:
            print(f"      - {snapper.get_category_name()}Snapper")

        # Create orchestrator (with terrain for validation pass)
        orchestrator = SnappingOrchestrator(snappers, terrain)

        # Snap objects
        stats = orchestrator.snap_tscn_file(
            tscn_path=tscn_path,
            dry_run=args.dry_run,
        )

        # Final message
        if not args.dry_run and sum(stats.snapped_by_category.values()) > 0:
            print("\n✅ SUCCESS! Objects snapped to terrain")
            print("\nNext steps:")
            print(f"  1. Open {tscn_path} in Godot to verify")
            print(f"  2. Export to spatial.json: python3 tools/export_to_portal.py {args.map}")
            print("  3. Import to Portal")
        elif args.dry_run:
            print("\n💡 Dry run complete. Run without --dry-run to apply changes.")
        else:
            print("\n✅ No adjustments needed - all objects already on terrain!")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
