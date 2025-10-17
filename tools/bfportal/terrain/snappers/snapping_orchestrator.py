#!/usr/bin/env python3
"""Orchestrator for coordinating multiple terrain snappers.

Single Responsibility: Route objects to appropriate snappers and collect results.
Open/Closed: New snappers can be added via dependency injection.
Dependency Inversion: Depends on IObjectSnapper abstraction, not concrete classes.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from .base_snapper import IObjectSnapper, ITerrainProvider
from .snap_validator import SnapValidator


@dataclass
class SnappingStats:
    """Statistics from snapping operation.

    Attributes:
        total_objects: Total objects processed
        snapped_by_category: Dict of category name -> count of adjusted objects
        skipped: Number of objects not handled by any snapper
        errors: Number of objects with errors
    """

    total_objects: int = 0
    snapped_by_category: dict[str, int] = field(default_factory=dict)
    skipped: int = 0
    errors: int = 0


class SnappingOrchestrator:
    """Coordinates terrain snapping across multiple object categories.

    This class:
    1. Parses .tscn files to find objects
    2. Routes each object to the appropriate snapper
    3. Collects results and writes updated .tscn
    4. Tracks statistics per category

    Single Responsibility: Only orchestrates snapping workflow.
    Open/Closed: Add new snappers via constructor, don't modify this class.
    """

    def __init__(self, snappers: list[IObjectSnapper], terrain: ITerrainProvider):
        """Initialize orchestrator.

        Args:
            snappers: List of snapper implementations (priority order)
            terrain: Terrain provider for validation pass

        Note:
            Snappers are checked in order. First snapper that can handle
            an object wins. Order GameplaySnapper before PropSnapper since
            PropSnapper is a catch-all.
        """
        self.snappers = snappers
        self.validator = SnapValidator(terrain)

    def snap_tscn_file(
        self, tscn_path: Path, output_path: Path | None = None, dry_run: bool = False
    ) -> SnappingStats:
        """Snap all objects in .tscn file to terrain.

        SOLID: Single Responsibility - orchestrates the snapping workflow by delegating
        to specialized methods for each step.

        Args:
            tscn_path: Input .tscn file
            output_path: Output path (defaults to overwriting input)
            dry_run: If True, don't write changes

        Returns:
            SnappingStats with results

        Raises:
            FileNotFoundError: If tscn_path doesn't exist
        """
        if not tscn_path.exists():
            raise FileNotFoundError(f"TSCN file not found: {tscn_path}")

        output_path = output_path or tscn_path

        print(f"\n🎯 Snapping {tscn_path.name} to terrain...")
        if dry_run:
            print("   [DRY RUN MODE - no changes will be written]")

        # Read input file
        with open(tscn_path) as f:
            lines = f.readlines()

        # Process all lines (DRY: extracted to separate method)
        new_lines, stats, adjustments_shown = self._process_all_lines(lines)

        # Write results (DRY: extracted to separate method)
        if not dry_run:
            self._write_snapped_file(tscn_path, output_path, new_lines)

        # Print summary
        self._print_stats(stats, adjustments_shown, max_shown=10)

        return stats

    def _process_all_lines(self, lines: list[str]) -> tuple[list[str], SnappingStats, int]:
        """Process all lines in .tscn file and snap objects to terrain.

        SOLID: Single Responsibility - handles the core snapping logic.

        Args:
            lines: Input .tscn file lines

        Returns:
            Tuple of (new_lines, stats, adjustments_shown)
        """
        new_lines = []
        stats = SnappingStats()
        current_node_name = None
        current_asset_type = None
        current_parent = None
        skip_terrain_node = False
        adjustments_shown = 0
        max_adjustments_to_show = 10

        for line in lines:
            # Track current node and its parent
            node_match = re.match(r'\[node name="([^"]+)"(?:.*parent="([^"]+)")?', line)
            if node_match:
                current_node_name = node_match.group(1)
                current_parent = node_match.group(2)  # None if root node, parent name otherwise
                # Try to extract asset type from node name (e.g., "Birch_01_L_1" -> "Birch_01_L")
                current_asset_type = re.sub(r"_\d+$", "", current_node_name)

                # Check if THIS node is terrain (and should be skipped), or if we're exiting terrain skip
                skip_terrain_node = "_Terrain" in current_node_name

            # Check for transform lines
            if (
                current_node_name
                and not skip_terrain_node
                and line.strip().startswith("transform = Transform3D(")
            ):
                # CRITICAL: Skip ONLY children of gameplay nodes (HQs, CapturePoints)
                # These use relative transforms. But DO snap children of Static!
                # Child nodes (like spawns parented to HQs) use relative transforms
                # and should NOT be terrain-snapped in world space
                should_skip_gameplay_child = current_parent and (
                    "HQ" in current_parent or "CapturePoint" in current_parent
                )

                if should_skip_gameplay_child:
                    # This is a child node (spawn under HQ/CP) - keep relative transform
                    new_lines.append(line)
                    continue

                # Allow Static children to be snapped (trees, buildings, props)

                # Parse transform
                transform_result = self._parse_transform_line(line)
                if transform_result:
                    values, indent = transform_result
                    x, current_y, z = values[9], values[10], values[11]

                    # Find appropriate snapper
                    snapper = self._find_snapper(current_node_name, current_asset_type)

                    if snapper:
                        # Snap the object
                        result = snapper.calculate_snapped_height(
                            x, z, current_y, current_node_name
                        )

                        stats.total_objects += 1

                        # PASS 2: Validate the snapped height (safety check for underground objects)
                        validation_result = self.validator.validate_and_correct(
                            x, z, result.snapped_y, current_node_name, min_clearance=0.3
                        )

                        # Use validated height (might be lifted if object was underground)
                        final_y = validation_result.snapped_y
                        was_lifted = validation_result.was_adjusted

                        if result.was_adjusted or was_lifted:
                            # Update transform line with validated height
                            values[10] = final_y
                            new_line = self._format_transform_line(values, indent)
                            new_lines.append(new_line)

                            # Track by category
                            category = snapper.get_category_name()
                            stats.snapped_by_category[category] = (
                                stats.snapped_by_category.get(category, 0) + 1
                            )

                            # Log adjustment
                            if adjustments_shown < max_adjustments_to_show:
                                delta = final_y - result.original_y
                                reason = result.reason
                                if was_lifted:
                                    reason += f" + {validation_result.reason}"
                                print(
                                    f"   [{category}] {current_node_name}: "
                                    f"Y {result.original_y:.1f}m → {final_y:.1f}m "
                                    f"(Δ {delta:+.1f}m) - {reason}"
                                )
                                adjustments_shown += 1
                        else:
                            # No adjustment needed
                            new_lines.append(line)
                    else:
                        # No snapper found
                        stats.skipped += 1
                        new_lines.append(line)
                else:
                    # Parse failed
                    stats.errors += 1
                    new_lines.append(line)
            else:
                # Not a transform line
                new_lines.append(line)

        return new_lines, stats, adjustments_shown

    def _write_snapped_file(self, tscn_path: Path, output_path: Path, new_lines: list[str]) -> None:
        """Write snapped .tscn file with backup.

        SOLID: Single Responsibility - handles file writing and backup creation.

        Args:
            tscn_path: Original .tscn file path (for backup)
            output_path: Output path to write
            new_lines: Lines to write to file
        """
        # Backup original
        backup_path = tscn_path.with_suffix(".tscn.backup")
        if tscn_path.exists():
            tscn_path.rename(backup_path)
            print(f"\n   📦 Backed up original to {backup_path.name}")

        # Write new file
        with open(output_path, "w") as f:
            f.writelines(new_lines)
        print(f"   ✅ Wrote updated .tscn to {output_path}")

    def _find_snapper(self, node_name: str, asset_type: str | None) -> IObjectSnapper | None:
        """Find appropriate snapper for an object.

        Args:
            node_name: Node name from .tscn
            asset_type: Asset type (extracted from node name)

        Returns:
            First snapper that can handle this object, or None
        """
        for snapper in self.snappers:
            if snapper.can_snap(node_name, asset_type):
                return snapper
        return None

    def _parse_transform_line(self, line: str) -> tuple[list[float], str] | None:
        """Parse a Transform3D line.

        Args:
            line: Line containing "transform = Transform3D(...)"

        Returns:
            Tuple of (values_list, indent_string) or None if parse failed
        """
        match = re.match(r"^(\s*)transform = Transform3D\((.*?)\)", line)
        if not match:
            return None

        indent = match.group(1)
        values_str = match.group(2)

        try:
            values = [float(x.strip()) for x in values_str.split(",")]
            if len(values) != 12:
                return None
            return values, indent
        except ValueError:
            return None

    def _format_transform_line(self, values: list[float], indent: str) -> str:
        """Format transform values back into .tscn line.

        Args:
            values: 12-component transform array
            indent: Leading whitespace

        Returns:
            Formatted transform line with newline
        """
        formatted = ", ".join(f"{v:.6g}" for v in values)
        return f"{indent}transform = Transform3D({formatted})\n"

    def _print_stats(self, stats: SnappingStats, adjustments_shown: int, max_shown: int) -> None:
        """Print statistics summary.

        Args:
            stats: Snapping statistics
            adjustments_shown: Number of adjustments logged
            max_shown: Maximum adjustments to show
        """
        print(f"\n{'=' * 70}")
        print("TERRAIN SNAPPING RESULTS")
        print(f"{'=' * 70}")
        print(f"   Total objects processed: {stats.total_objects}")
        print("   Adjusted by category:")
        total_adjusted = sum(stats.snapped_by_category.values())
        for category, count in sorted(stats.snapped_by_category.items()):
            print(f"      - {category}: {count}")
        print(f"   Total adjusted: {total_adjusted}")
        print(f"   Skipped (no snapper): {stats.skipped}")
        print(f"   Errors: {stats.errors}")

        if total_adjusted > adjustments_shown:
            print(
                f"\n   (Showing first {adjustments_shown} adjustments, "
                f"{total_adjusted - adjustments_shown} more adjusted)"
            )
