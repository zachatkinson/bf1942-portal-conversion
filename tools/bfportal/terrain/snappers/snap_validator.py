#!/usr/bin/env python3
"""Post-snap validator to catch objects that are still underground.

Single Responsibility: Validate and fix objects that ended up underground after snapping.
"""

from .base_snapper import ITerrainProvider, SnapResult


class SnapValidator:
    """Validates snapped objects and fixes any that are still underground.

    This is a safety pass that runs after initial snapping to catch:
    - Objects where multi-point sampling picked a hole in the terrain
    - Objects at terrain edges where sampling failed
    - Objects that need additional clearance

    Single Responsibility: Only validates and corrects underground objects.
    """

    def __init__(self, terrain: ITerrainProvider):
        """Initialize validator.

        Args:
            terrain: Terrain provider for height queries
        """
        self.terrain = terrain

    def validate_and_correct(
        self,
        x: float,
        z: float,
        current_y: float,
        node_name: str,
        min_clearance: float = 0.3,
        max_float_distance: float = 2.0,
    ) -> SnapResult:
        """Validate object height and correct if underground OR floating too high.

        This two-way validator:
        - Lifts objects that are underground (below terrain + min_clearance)
        - Lowers objects that are floating (above terrain + max_float_distance)

        Args:
            x: Object X position
            z: Object Z position
            current_y: Current Y position (after initial snap)
            node_name: Node name for logging
            min_clearance: Minimum clearance above terrain (default: 0.3m)
            max_float_distance: Maximum acceptable distance above terrain (default: 2.0m)

        Returns:
            SnapResult with corrected height if needed
        """
        try:
            # Get terrain height at this exact position
            terrain_height = self.terrain.get_height_at(x, z)

            # Define acceptable range
            min_acceptable_y = terrain_height + min_clearance
            max_acceptable_y = terrain_height + max_float_distance

            if current_y < min_acceptable_y:
                # Object is underground or too close - lift it up
                corrected_y = min_acceptable_y
                delta = corrected_y - current_y

                return SnapResult(
                    original_y=current_y,
                    snapped_y=corrected_y,
                    was_adjusted=True,
                    reason=f"Lifted {delta:.1f}m (was underground)",
                )
            elif current_y > max_acceptable_y:
                # Object is floating too high - lower it
                corrected_y = terrain_height + 0.5  # Settle at reasonable height
                delta = corrected_y - current_y

                return SnapResult(
                    original_y=current_y,
                    snapped_y=corrected_y,
                    was_adjusted=True,
                    reason=f"Lowered {abs(delta):.1f}m (was floating)",
                )
            else:
                # Object is in acceptable range - all good
                return SnapResult(
                    original_y=current_y,
                    snapped_y=current_y,
                    was_adjusted=False,
                    reason="Valid",
                )

        except Exception as e:
            # Query failed - keep original
            return SnapResult(
                original_y=current_y,
                snapped_y=current_y,
                was_adjusted=False,
                reason=f"Validation failed: {e}",
            )
