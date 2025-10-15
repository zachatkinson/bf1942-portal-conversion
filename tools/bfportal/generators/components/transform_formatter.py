#!/usr/bin/env python3
"""Transform formatter for converting Transform to Godot Transform3D strings.

Single Responsibility: Transform formatting logic only.
"""

import math

from ...core.interfaces import Transform, Vector3


class TransformFormatter:
    """Formats Transform objects to Godot Transform3D strings.

    This class handles the mathematical conversion from our Transform
    representation (position, rotation, scale) to Godot's Transform3D
    format (3x3 basis matrix + origin vector).
    """

    def format(self, transform: Transform) -> str:
        """Format Transform to Transform3D string.

        Args:
            transform: Transform to format

        Returns:
            Transform3D string (e.g., "Transform3D(1, 0, 0, ...)")

        Notes:
            Transform3D format: Transform3D(basis_x, basis_y, basis_z, origin)
            - Basis vectors are columns of the 3x3 rotation-scale matrix
            - Scale is applied by multiplying each basis vector by scale component
            - Rotation uses ZYX Euler angles
        """
        # Convert rotation (pitch, yaw, roll) to rotation matrix
        pitch = math.radians(transform.rotation.pitch)
        yaw = math.radians(transform.rotation.yaw)
        roll = math.radians(transform.rotation.roll)

        # Rotation matrix components
        cos_p, sin_p = math.cos(pitch), math.sin(pitch)
        cos_y, sin_y = math.cos(yaw), math.sin(yaw)
        cos_r, sin_r = math.cos(roll), math.sin(roll)

        # Combined rotation matrix (ZYX order)
        m00 = cos_y * cos_p
        m01 = cos_y * sin_p * sin_r - sin_y * cos_r
        m02 = cos_y * sin_p * cos_r + sin_y * sin_r

        m10 = sin_y * cos_p
        m11 = sin_y * sin_p * sin_r + cos_y * cos_r
        m12 = sin_y * sin_p * cos_r - cos_y * sin_r

        m20 = -sin_p
        m21 = cos_p * sin_r
        m22 = cos_p * cos_r

        # Apply scale to rotation matrix
        scale = transform.scale if transform.scale else Vector3(1.0, 1.0, 1.0)

        # Scale each basis vector (column of the rotation matrix)
        m00 *= scale.x
        m10 *= scale.x
        m20 *= scale.x

        m01 *= scale.y
        m11 *= scale.y
        m21 *= scale.y

        m02 *= scale.z
        m12 *= scale.z
        m22 *= scale.z

        return (
            f"Transform3D({m00:.6g}, {m01:.6g}, {m02:.6g}, "
            f"{m10:.6g}, {m11:.6g}, {m12:.6g}, "
            f"{m20:.6g}, {m21:.6g}, {m22:.6g}, "
            f"{transform.position.x:.6g}, {transform.position.y:.6g}, {transform.position.z:.6g})"
        )

    def make_relative(self, child: Transform, parent: Transform) -> Transform:
        """Make child transform relative to parent.

        Args:
            child: Child's world transform
            parent: Parent's world transform

        Returns:
            Relative transform

        Note:
            This is a simplified implementation that only adjusts position.
            A full implementation would also account for parent rotation.
        """
        rel_pos = Vector3(
            child.position.x - parent.position.x,
            child.position.y - parent.position.y,
            child.position.z - parent.position.z,
        )

        # Keep rotation and scale as-is for now
        return Transform(rel_pos, child.rotation, child.scale)
