#!/usr/bin/env python3
"""Portal Map Assets CLI - Map source game assets to Portal equivalents.

This tool performs asset mapping independently from parsing or generation.
Useful for:

- Testing asset mappings
- Creating custom mapping overrides
- Analyzing mapping coverage
- Debugging mapping issues

Input:
- JSON file with source assets (from portal_parse.py)
- Or manual asset list

Output:
- JSON file with Portal asset mappings
- Mapping statistics and warnings

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-11
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bfportal.core.exceptions import BFPortalError, MappingError
from bfportal.core.interfaces import MapContext, Team
from bfportal.mappers.asset_mapper import AssetMapper


class PortalMapAssetsApp:
    """CLI application for mapping assets."""

    def __init__(self):
        """Initialize the app."""
        self.args: argparse.Namespace

    def parse_args(self) -> argparse.Namespace:
        """Parse command-line arguments.

        Returns:
            Parsed arguments namespace
        """
        parser = argparse.ArgumentParser(
            description="Map source game assets to Portal equivalents",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Map assets from parsed map data
  python3 tools/portal_map_assets.py \\
      --input kursk_parsed.json \\
      --output kursk_mapped.json \\
      --game bf1942

  # Map specific asset list
  python3 tools/portal_map_assets.py \\
      --assets "Bf109,PanzerIV,BunkerGerman" \\
      --game bf1942

  # Show mapping statistics
  python3 tools/portal_map_assets.py \\
      --input kursk_parsed.json \\
      --game bf1942 \\
      --stats-only

  # Use custom mappings file
  python3 tools/portal_map_assets.py \\
      --input kursk_parsed.json \\
      --output kursk_mapped.json \\
      --game bf1942 \\
      --mappings-file tools/asset_audit/bf1942_to_portal_mappings_custom.json

Supported Games:
  - bf1942: Battlefield 1942
  - bfvietnam: Battlefield Vietnam
  - bf2: Battlefield 2
  - bf2142: Battlefield 2142
            """,
        )

        parser.add_argument(
            "--game",
            type=str,
            required=True,
            choices=["bf1942", "bfvietnam", "bf2", "bf2142"],
            help="Source game engine",
        )

        parser.add_argument("--input", type=Path, help="Input JSON file from portal_parse.py")

        parser.add_argument("--output", type=Path, help="Output JSON file with mappings")

        parser.add_argument("--assets", type=str, help="Comma-separated list of asset names to map")

        parser.add_argument(
            "--mappings-file",
            type=Path,
            help="Custom asset mappings JSON file (default: auto-detect from game)",
        )

        parser.add_argument(
            "--map-theme",
            type=str,
            choices=["desert", "urban", "forest", "snow", "tropical", "open_terrain"],
            default="open_terrain",
            help="Map theme for context-aware mapping (default: open_terrain)",
        )

        parser.add_argument(
            "--stats-only",
            action="store_true",
            help="Only show mapping statistics, do not write output",
        )

        parser.add_argument(
            "--verbose", action="store_true", help="Verbose output with mapping details"
        )

        return parser.parse_args()

    def load_mappings_file(self) -> Path:
        """Determine mappings file path.

        Returns:
            Path to mappings JSON file

        Raises:
            FileNotFoundError: If mappings file not found
        """
        # Type-safe access to argparse args
        mappings_file: Path | None = self.args.mappings_file
        game: str = self.args.game

        if mappings_file:
            if not mappings_file.exists():
                raise FileNotFoundError(f"Mappings file not found: {mappings_file}")
            return mappings_file

        # Auto-detect based on game
        default_path = Path(__file__).parent / "asset_audit" / f"{game}_to_portal_mappings.json"

        if not default_path.exists():
            raise FileNotFoundError(
                f"Default mappings file not found: {default_path}\n"
                f"Run asset audit tools first or specify --mappings-file"
            )

        return default_path

    def extract_assets_from_parsed_data(self, data: dict) -> list[str]:
        """Extract asset names from parsed map data.

        Args:
            data: Parsed map data dictionary

        Returns:
            List of unique asset names
        """
        assets = set()

        # Extract from game objects
        if "game_objects" in data:
            for obj in data["game_objects"]:
                if "asset_type" in obj:
                    assets.add(obj["asset_type"])

        return sorted(assets)

    def run(self) -> int:
        """Execute asset mapping.

        Returns:
            Exit code (0 for success, 1 for error)
        """
        self.args = self.parse_args()

        print("=" * 70)
        print("🗺️  Portal Asset Mapper")
        print("=" * 70)
        print()

        try:
            # Get asset list
            if self.args.input:
                if not self.args.input.exists():
                    print(f"❌ Error: Input file not found: {self.args.input}")
                    return 1

                with open(self.args.input) as f:
                    parsed_data = json.load(f)

                assets = self.extract_assets_from_parsed_data(parsed_data)
                print(f"📦 Loaded {len(assets)} unique assets from {self.args.input.name}")

            elif self.args.assets:
                assets = [a.strip() for a in self.args.assets.split(",")]
                print(f"📦 Mapping {len(assets)} manually specified assets")

            else:
                print("❌ Error: Must specify either --input or --assets")
                return 1

            # Load mappings file
            mappings_path = self.load_mappings_file()
            print(f"📚 Using mappings: {mappings_path.name}")
            print()

            # Create asset mapper
            mapper = AssetMapper(mappings_path)

            # Map assets
            print("🔄 Mapping assets...")
            print()

            results = []
            mapped_count = 0
            unmapped_count = 0
            restricted_count = 0

            for asset_name in assets:
                # Create context
                context = MapContext(
                    target_base_map="MP_Tungsten",
                    era="WW2",
                    theme=self.args.map_theme,
                    team=Team.NEUTRAL,
                )

                try:
                    portal_asset = mapper.map_asset(asset_name, context)

                    if portal_asset:
                        mapped_count += 1
                        results.append(
                            {
                                "source_asset": asset_name,
                                "portal_asset": portal_asset.type,
                                "category": portal_asset.directory,
                                "level_restricted": bool(portal_asset.level_restrictions),
                                "status": "mapped",
                            }
                        )

                        if self.args.verbose:
                            print(f"✅ {asset_name} → {portal_asset.type}")
                            if portal_asset.level_restrictions:
                                print(
                                    f"   ⚠️  Level restricted: {', '.join(portal_asset.level_restrictions[:3])}"
                                )

                    else:
                        unmapped_count += 1
                        results.append(
                            {"source_asset": asset_name, "portal_asset": None, "status": "unmapped"}
                        )

                        print(f"❌ {asset_name} → NO MAPPING FOUND")

                except MappingError as e:
                    restricted_count += 1
                    results.append(
                        {
                            "source_asset": asset_name,
                            "portal_asset": None,
                            "error": str(e),
                            "status": "error",
                        }
                    )

                    print(f"⚠️  {asset_name} → ERROR: {e}")

            # Statistics
            print()
            print("=" * 70)
            print("📊 Mapping Statistics")
            print("=" * 70)
            print(f"   Total assets: {len(assets)}")
            print(f"   ✅ Mapped: {mapped_count} ({mapped_count / len(assets) * 100:.1f}%)")
            print(f"   ❌ Unmapped: {unmapped_count} ({unmapped_count / len(assets) * 100:.1f}%)")
            if restricted_count > 0:
                print(
                    f"   ⚠️  Errors: {restricted_count} ({restricted_count / len(assets) * 100:.1f}%)"
                )
            print()

            # Write output
            if not self.args.stats_only and self.args.output:
                output_data = {
                    "game": self.args.game,
                    "map_theme": self.args.map_theme,
                    "total_assets": len(assets),
                    "mapped_count": mapped_count,
                    "unmapped_count": unmapped_count,
                    "mappings": results,
                }

                self.args.output.parent.mkdir(parents=True, exist_ok=True)
                with open(self.args.output, "w") as f:
                    json.dump(output_data, f, indent=2)

                print(f"✅ Mappings written to: {self.args.output}")
                print()

            # Exit with error if any unmapped
            if unmapped_count > 0 or restricted_count > 0:
                print("⚠️  Warning: Some assets could not be mapped")
                print("   Review mappings file or add manual overrides")
                return 1

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
    app = PortalMapAssetsApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
