#!/usr/bin/env python3
"""Orientation matcher for calculating rotation between source and destination.

Single Responsibility: Only compares orientations and calculates required rotation.
"""

from dataclasses import dataclass

from .interfaces import Orientation, OrientationAnalysis


@dataclass
class RotationResult:
    """Result of orientation matching."""

    rotation_degrees: float  # Rotation needed (0, 90, 180, 270)
    rotation_needed: bool  # Whether rotation is required
    source_orientation: Orientation
    destination_orientation: Orientation
    confidence: str  # 'high', 'medium', 'low'
    reasoning: str  # Human-readable explanation


class OrientationMatcher:
    """Matches source and destination orientations and calculates rotation.

    Single Responsibility: Only compares orientations and determines rotation.
    Open/Closed: Can extend with new matching strategies without modification.
    """

    def match(
        self, source_analysis: OrientationAnalysis, destination_analysis: OrientationAnalysis
    ) -> RotationResult:
        """Compare orientations and calculate required rotation.

        Args:
            source_analysis: Source map orientation analysis
            destination_analysis: Destination terrain orientation analysis

        Returns:
            RotationResult with rotation angle and reasoning
        """
        source_orient = source_analysis.orientation
        dest_orient = destination_analysis.orientation

        # Determine confidence based on both analyses
        confidences = [source_analysis.confidence, destination_analysis.confidence]
        if "low" in confidences:
            overall_confidence = "low"
        elif "medium" in confidences:
            overall_confidence = "medium"
        else:
            overall_confidence = "high"

        # Case 1: Both are SQUARE - no rotation needed
        if source_orient == Orientation.SQUARE and dest_orient == Orientation.SQUARE:
            return RotationResult(
                rotation_degrees=0,
                rotation_needed=False,
                source_orientation=source_orient,
                destination_orientation=dest_orient,
                confidence=overall_confidence,
                reasoning="Both source and destination are square - no rotation needed",
            )

        # Case 2: Source is SQUARE but destination is oriented - no rotation
        # (Assets will fit in either orientation)
        if source_orient == Orientation.SQUARE:
            return RotationResult(
                rotation_degrees=0,
                rotation_needed=False,
                source_orientation=source_orient,
                destination_orientation=dest_orient,
                confidence=overall_confidence,
                reasoning="Source is square - fits destination regardless of orientation",
            )

        # Case 3: Destination is SQUARE but source is oriented - no rotation
        # (Terrain is square, can accommodate any asset orientation)
        if dest_orient == Orientation.SQUARE:
            return RotationResult(
                rotation_degrees=0,
                rotation_needed=False,
                source_orientation=source_orient,
                destination_orientation=dest_orient,
                confidence=overall_confidence,
                reasoning="Destination is square - accommodates source orientation",
            )

        # Case 4: Both oriented the same - no rotation
        if source_orient == dest_orient:
            return RotationResult(
                rotation_degrees=0,
                rotation_needed=False,
                source_orientation=source_orient,
                destination_orientation=dest_orient,
                confidence=overall_confidence,
                reasoning=f"Both oriented {source_orient.value} - no rotation needed",
            )

        # Case 5: Orientations differ - 90 degree rotation needed
        # N/S source on E/W terrain (or vice versa) requires 90° rotation
        rotation_degrees = 90

        if source_orient == Orientation.NORTH_SOUTH and dest_orient == Orientation.EAST_WEST:
            reasoning = "Source is N/S but destination is E/W - rotating terrain 90° clockwise"
        else:  # source is E/W, dest is N/S
            reasoning = "Source is E/W but destination is N/S - rotating terrain 90° clockwise"

        return RotationResult(
            rotation_degrees=rotation_degrees,
            rotation_needed=True,
            source_orientation=source_orient,
            destination_orientation=dest_orient,
            confidence=overall_confidence,
            reasoning=reasoning,
        )

    def suggest_rotation_axis(self, rotation_result: RotationResult) -> str:
        """Suggest which axis to rotate around.

        Args:
            rotation_result: Result from match()

        Returns:
            Axis name ('Y', 'X', 'Z')
        """
        # For map orientation, we always rotate around Y axis (vertical)
        return "Y"

    def format_report(self, rotation_result: RotationResult) -> str:
        """Format human-readable report of orientation matching.

        Args:
            rotation_result: Result from match()

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("ORIENTATION ANALYSIS")
        lines.append("=" * 70)
        lines.append(f"Source orientation: {rotation_result.source_orientation.value.upper()}")
        lines.append(
            f"Destination orientation: {rotation_result.destination_orientation.value.upper()}"
        )
        lines.append(f"Confidence: {rotation_result.confidence.upper()}")
        lines.append("")
        lines.append(f"Rotation needed: {'YES' if rotation_result.rotation_needed else 'NO'}")

        if rotation_result.rotation_needed:
            lines.append(f"Rotation angle: {rotation_result.rotation_degrees}°")
            lines.append(f"Rotation axis: {self.suggest_rotation_axis(rotation_result)}")

        lines.append("")
        lines.append(f"Reasoning: {rotation_result.reasoning}")
        lines.append("=" * 70)

        return "\n".join(lines)
