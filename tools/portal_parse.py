#!/usr/bin/env python3
"""Portal Parse CLI - Parse BF1942/Vietnam/BF2/2142 maps to extract data.

This tool parses classic Battlefield maps and extracts gameplay data without
performing conversion. Useful for:

- Analyzing map layout
- Extracting spawn points and objectives
- Understanding map structure
- Debugging conversion issues

Output formats:
- JSON (structured data)
- Summary (human-readable)

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-11
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bfportal.core.exceptions import BFPortalError, ParseError
from bfportal.core.interfaces import Team
from bfportal.engines.refractor.games.bf1942 import (
    BF2Engine,
    BF1942Engine,
    BF2142Engine,
    BFVietnamEngine,
)


class PortalParseApp:
    """CLI application for parsing Battlefield maps."""

    def __init__(self):
        """Initialize the app."""
        self.args: Optional[argparse.Namespace] = None

    def parse_args(self) -> argparse.Namespace:
        """Parse command-line arguments.

        Returns:
            Parsed arguments namespace
        """
        parser = argparse.ArgumentParser(
            description="Parse Battlefield maps to extract gameplay data",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Parse BF1942 Kursk map
  python3 tools/portal_parse.py \\
      --game bf1942 \\
      --map-path bf1942_source/extracted/Bf1942/Archives/bf1942/levels/Kursk

  # Parse and output JSON
  python3 tools/portal_parse.py \\
      --game bf1942 \\
      --map-path bf1942_source/extracted/.../Kursk \\
      --output kursk_data.json \\
      --format json

  # Parse BF Vietnam map
  python3 tools/portal_parse.py \\
      --game bfvietnam \\
      --map-path bfvietnam_source/.../Operation_Hastings

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

        parser.add_argument(
            "--map-path", type=Path, required=True, help="Path to extracted map directory"
        )

        parser.add_argument(
            "--output", type=Path, help="Output file (optional, prints to stdout if not specified)"
        )

        parser.add_argument(
            "--format",
            type=str,
            default="summary",
            choices=["json", "summary"],
            help="Output format (default: summary)",
        )

        parser.add_argument(
            "--verbose", action="store_true", help="Verbose output with debug information"
        )

        return parser.parse_args()

    def create_engine(self):
        """Create appropriate game engine.

        Returns:
            IGameEngine instance
        """
        game = self.args.game

        if game == "bf1942":
            return BF1942Engine()
        elif game == "bfvietnam":
            return BFVietnamEngine()
        elif game == "bf2":
            return BF2Engine()
        elif game == "bf2142":
            return BF2142Engine()
        else:
            raise ValueError(f"Unknown game: {game}")

    def format_map_data_summary(self, map_data) -> str:
        """Format map data as human-readable summary.

        Args:
            map_data: Parsed map data

        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("=" * 70)
        lines.append(f"Map: {map_data.name}")
        lines.append("=" * 70)
        lines.append("")

        # Bounds
        if map_data.bounds:
            lines.append("📐 Bounds:")
            lines.append(
                f"   Min: ({map_data.bounds.min.x:.1f}, "
                f"{map_data.bounds.min.y:.1f}, {map_data.bounds.min.z:.1f})"
            )
            lines.append(
                f"   Max: ({map_data.bounds.max.x:.1f}, "
                f"{map_data.bounds.max.y:.1f}, {map_data.bounds.max.z:.1f})"
            )
            width = map_data.bounds.max.x - map_data.bounds.min.x
            depth = map_data.bounds.max.z - map_data.bounds.min.z
            lines.append(f"   Size: {width:.1f}m x {depth:.1f}m")
            lines.append("")

        # Spawn points
        team1_spawns = [s for s in map_data.spawn_points if s.team == Team.TEAM_1]
        team2_spawns = [s for s in map_data.spawn_points if s.team == Team.TEAM_2]

        lines.append("🎯 Spawn Points:")
        lines.append(f"   Team 1: {len(team1_spawns)} spawns")
        lines.append(f"   Team 2: {len(team2_spawns)} spawns")
        lines.append("")

        # HQs
        team1_hqs = [h for h in map_data.hqs if h.team == Team.TEAM_1]
        team2_hqs = [h for h in map_data.hqs if h.team == Team.TEAM_2]

        lines.append("🏠 Headquarters:")
        lines.append(f"   Team 1: {len(team1_hqs)} HQ(s)")
        lines.append(f"   Team 2: {len(team2_hqs)} HQ(s)")
        lines.append("")

        # Capture points
        if map_data.capture_points:
            lines.append(f"🚩 Capture Points: {len(map_data.capture_points)}")
            for i, cp in enumerate(map_data.capture_points, 1):
                lines.append(
                    f"   {i}. {cp.name} at ({cp.transform.position.x:.1f}, "
                    f"{cp.transform.position.z:.1f})"
                )
            lines.append("")

        # Game objects
        if map_data.game_objects:
            lines.append(f"📦 Game Objects: {len(map_data.game_objects)}")

            # Count by asset type
            asset_counts = {}
            for obj in map_data.game_objects:
                asset_counts[obj.asset_type] = asset_counts.get(obj.asset_type, 0) + 1

            # Show top 10
            top_assets = sorted(asset_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            for asset_type, count in top_assets:
                lines.append(f"   - {asset_type}: {count}")
            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    def format_map_data_json(self, map_data) -> str:
        """Format map data as JSON.

        Args:
            map_data: Parsed map data

        Returns:
            JSON string
        """
        # Convert to serializable dictionary
        data = {
            "name": map_data.name,
            "bounds": None,
            "spawn_points": [],
            "hqs": [],
            "capture_points": [],
            "game_objects": [],
        }

        if map_data.bounds:
            data["bounds"] = {
                "min": {
                    "x": map_data.bounds.min.x,
                    "y": map_data.bounds.min.y,
                    "z": map_data.bounds.min.z,
                },
                "max": {
                    "x": map_data.bounds.max.x,
                    "y": map_data.bounds.max.y,
                    "z": map_data.bounds.max.z,
                },
            }

        for spawn in map_data.spawn_points:
            data["spawn_points"].append(
                {
                    "name": spawn.name,
                    "team": spawn.team.value,
                    "position": {
                        "x": spawn.transform.position.x,
                        "y": spawn.transform.position.y,
                        "z": spawn.transform.position.z,
                    },
                    "rotation": {
                        "pitch": spawn.transform.rotation.pitch,
                        "yaw": spawn.transform.rotation.yaw,
                        "roll": spawn.transform.rotation.roll,
                    },
                }
            )

        for hq in map_data.hqs:
            data["hqs"].append(
                {
                    "name": hq.name,
                    "team": hq.team.value,
                    "position": {
                        "x": hq.transform.position.x,
                        "y": hq.transform.position.y,
                        "z": hq.transform.position.z,
                    },
                }
            )

        for cp in map_data.capture_points:
            data["capture_points"].append(
                {
                    "name": cp.name,
                    "position": {
                        "x": cp.transform.position.x,
                        "y": cp.transform.position.y,
                        "z": cp.transform.position.z,
                    },
                }
            )

        for obj in map_data.game_objects:
            data["game_objects"].append(
                {
                    "name": obj.name,
                    "asset_type": obj.asset_type,
                    "team": obj.team.value if obj.team else 0,
                    "position": {
                        "x": obj.transform.position.x,
                        "y": obj.transform.position.y,
                        "z": obj.transform.position.z,
                    },
                    "rotation": {
                        "pitch": obj.transform.rotation.pitch,
                        "yaw": obj.transform.rotation.yaw,
                        "roll": obj.transform.rotation.roll,
                    },
                }
            )

        return json.dumps(data, indent=2)

    def run(self) -> int:
        """Execute parsing.

        Returns:
            Exit code (0 for success, 1 for error)
        """
        self.args = self.parse_args()

        if not self.args.verbose:
            print("=" * 70)
            print("📖 Portal Map Parser")
            print("=" * 70)
            print()

        try:
            # Validate map path
            if not self.args.map_path.exists():
                print(f"❌ Error: Map path not found: {self.args.map_path}")
                return 1

            if self.args.verbose:
                print(f"🔍 Parsing {self.args.game.upper()} map at {self.args.map_path}")

            # Create engine
            engine = self.create_engine()

            # Parse map
            map_data = engine.parse_map(self.args.map_path)

            if self.args.verbose:
                print(f"✅ Successfully parsed map: {map_data.name}")
                print()

            # Format output
            if self.args.format == "json":
                output = self.format_map_data_json(map_data)
            else:
                output = self.format_map_data_summary(map_data)

            # Write output
            if self.args.output:
                self.args.output.parent.mkdir(parents=True, exist_ok=True)
                with open(self.args.output, "w") as f:
                    f.write(output)
                print(f"✅ Output written to: {self.args.output}")
            else:
                print(output)

            return 0

        except ParseError as e:
            print(f"❌ Parse error: {e}")
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
    app = PortalParseApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
