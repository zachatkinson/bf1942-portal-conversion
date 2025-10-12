#!/usr/bin/env python3
"""Validation tool for converted Portal maps.

Verifies that all assets are properly placed, positioned, and oriented.
Performs mathematical validation of:
- Coordinate transformations
- Height adjustments
- Rotation/orientation
- Bounds checking
- Asset placement accuracy

Usage:
    python3 tools/validate_conversion.py --source bf1942_source/extracted/.../Kursk \
                                         --output GodotProject/levels/Kursk.tscn \
                                         --heightmap GodotProject/terrain/Kursk_heightmap.png
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Add bfportal to path
sys.path.insert(0, str(Path(__file__).parent))

from bfportal.engines.refractor.games.bf1942 import BF1942Engine
from bfportal.terrain.terrain_provider import CustomHeightmapProvider
from bfportal.validation import ValidationIssue, ValidationOrchestrator


class ConversionValidator:
    """Validates BF1942 to Portal conversion accuracy.

    Single Responsibility: Only coordinates validation process.
    Uses ValidationOrchestrator for actual validation logic.
    """

    def __init__(
        self,
        source_map_path: Path,
        output_tscn_path: Path,
        heightmap_path: Optional[Path] = None,
        terrain_size: float = 2048.0,
        height_range: Tuple[float, float] = (70.0, 220.0),
    ):
        """Initialize validator.

        Args:
            source_map_path: Path to source BF1942 map directory
            output_tscn_path: Path to generated .tscn file
            heightmap_path: Optional path to heightmap for height validation
            terrain_size: Terrain size in meters
            height_range: (min_height, max_height) in meters
        """
        self.source_map_path = source_map_path
        self.output_tscn_path = output_tscn_path
        self.heightmap_path = heightmap_path
        self.terrain_size = terrain_size
        self.height_range = height_range

        self.engine = BF1942Engine()
        self.terrain_provider = None

        if heightmap_path and heightmap_path.exists():
            self.terrain_provider = CustomHeightmapProvider(
                heightmap_path, terrain_size=(terrain_size, terrain_size), height_range=height_range
            )

    def validate(self) -> Tuple[bool, List[ValidationIssue]]:
        """Run all validation checks.

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        # Parse source map
        print("📂 Parsing source BF1942 map...")
        source_data = self.engine.parse_map(self.source_map_path)
        print()

        # Run validation using SOLID orchestrator
        orchestrator = ValidationOrchestrator(
            source_data, self.output_tscn_path, self.terrain_provider, self.terrain_size
        )

        return orchestrator.validate()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate BF1942 to Portal map conversion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--source", required=True, help="Path to source BF1942 map directory")
    parser.add_argument("--output", required=True, help="Path to generated .tscn file")
    parser.add_argument("--heightmap", type=str, help="Path to heightmap PNG (optional)")
    parser.add_argument(
        "--terrain-size", type=float, default=2048.0, help="Terrain size in meters (default: 2048)"
    )
    parser.add_argument(
        "--min-height", type=float, default=70.0, help="Minimum terrain height (default: 70)"
    )
    parser.add_argument(
        "--max-height", type=float, default=220.0, help="Maximum terrain height (default: 220)"
    )

    args = parser.parse_args()

    # Resolve paths
    source_path = Path(args.source)
    output_path = Path(args.output)
    heightmap_path = Path(args.heightmap) if args.heightmap else None

    if not source_path.exists():
        print(f"❌ Source map not found: {source_path}")
        return 1

    if not output_path.exists():
        print(f"❌ Output .tscn not found: {output_path}")
        return 1

    # Run validation
    validator = ConversionValidator(
        source_path,
        output_path,
        heightmap_path,
        args.terrain_size,
        (args.min_height, args.max_height),
    )

    is_valid, issues = validator.validate()

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
