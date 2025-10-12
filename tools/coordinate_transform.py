#!/usr/bin/env python3
"""Coordinate Transformation Utilities.

Converts BF1942 coordinate system data to BF6 Portal (Godot 4) format.

Key transformations:
- BF1942 Euler angles (pitch/yaw/roll) → Godot Transform3D rotation matrix
- BF1942 position strings (x/y/z) → Godot Vector3
- Validates rotation matrices (orthonormal, no NaN)

Coordinate System Compatibility:
- Both BF1942 and BF6 use Y-up, right-handed coordinate systems
- Both use meters as units
- Scale factor: 1:1 (no conversion needed)

Usage:
    from coordinate_transform import euler_to_transform3d, format_transform3d

    # Convert BF1942 Euler angles to Transform3D matrix string
    matrix = euler_to_transform3d(pitch=0.0, yaw=45.0, roll=0.0)
    transform_str = format_transform3d(matrix, position=(100, 50, 200))

    # Result: "Transform3D(0.707, 0, 0.707, 0, 1, 0, -0.707, 0, 0.707, 100, 50, 200)"
"""

import math
from dataclasses import dataclass


@dataclass
class Vector3:
    """3D vector for positions and directions."""

    x: float
    y: float
    z: float

    def __iter__(self):
        """Allow unpacking: x, y, z = vector."""
        return iter((self.x, self.y, self.z))

    def to_tuple(self) -> tuple[float, float, float]:
        """Convert to tuple."""
        return (self.x, self.y, self.z)


@dataclass
class RotationMatrix:
    """3x3 rotation matrix represented as three basis vectors.

    Attributes:
        right: Right vector (X-axis)
        up: Up vector (Y-axis)
        forward: Forward vector (Z-axis)
    """

    right: Vector3  # X-axis basis vector
    up: Vector3  # Y-axis basis vector
    forward: Vector3  # Z-axis basis vector

    def to_flat_list(self) -> list[float]:
        """Convert to flat list for Transform3D matrix.

        Returns:
            List of 9 floats: [rx, ux, fx, ry, uy, fy, rz, uz, fz]
        """
        return [
            self.right.x,
            self.up.x,
            self.forward.x,
            self.right.y,
            self.up.y,
            self.forward.y,
            self.right.z,
            self.up.z,
            self.forward.z,
        ]

    def is_orthonormal(self, tolerance: float = 1e-4) -> bool:
        """Check if matrix is orthonormal (valid rotation matrix).

        Args:
            tolerance: Maximum allowed deviation from perfect orthonormality

        Returns:
            True if matrix is orthonormal within tolerance
        """

        # Check each basis vector is unit length
        def length(v: Vector3) -> float:
            return math.sqrt(v.x**2 + v.y**2 + v.z**2)

        right_len = length(self.right)
        up_len = length(self.up)
        forward_len = length(self.forward)

        if abs(right_len - 1.0) > tolerance:
            return False
        if abs(up_len - 1.0) > tolerance:
            return False
        if abs(forward_len - 1.0) > tolerance:
            return False

        # Check vectors are orthogonal (dot product = 0)
        def dot(v1: Vector3, v2: Vector3) -> float:
            return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z

        if abs(dot(self.right, self.up)) > tolerance:
            return False
        if abs(dot(self.up, self.forward)) > tolerance:
            return False
        if abs(dot(self.forward, self.right)) > tolerance:
            return False

        return True

    def has_nan(self) -> bool:
        """Check if any matrix element is NaN.

        Returns:
            True if any element is NaN
        """
        values = [
            self.right.x,
            self.right.y,
            self.right.z,
            self.up.x,
            self.up.y,
            self.up.z,
            self.forward.x,
            self.forward.y,
            self.forward.z,
        ]
        return any(math.isnan(v) for v in values)


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians.

    Args:
        degrees: Angle in degrees

    Returns:
        Angle in radians
    """
    return degrees * math.pi / 180.0


def euler_to_transform3d(
    pitch: float, yaw: float, roll: float, position: tuple[float, float, float] = (0.0, 0.0, 0.0)
) -> tuple[RotationMatrix, Vector3]:
    """Convert BF1942 Euler angles to Godot Transform3D components.

    BF1942 uses intrinsic Euler angles in pitch/yaw/roll order.
    This converts to a 3x3 rotation matrix compatible with Godot.

    Rotation order: Pitch (X) → Yaw (Y) → Roll (Z)

    Args:
        pitch: Rotation around X-axis in degrees
        yaw: Rotation around Y-axis in degrees
        roll: Rotation around Z-axis in degrees
        position: Position as (x, y, z) tuple

    Returns:
        Tuple of (RotationMatrix, Vector3)

    Raises:
        ValueError: If resulting matrix is invalid (NaN or not orthonormal)
    """
    # Convert to radians
    pitch_rad = degrees_to_radians(pitch)
    yaw_rad = degrees_to_radians(yaw)
    roll_rad = degrees_to_radians(roll)

    # Precompute sin/cos
    cp = math.cos(pitch_rad)
    sp = math.sin(pitch_rad)
    cy = math.cos(yaw_rad)
    sy = math.sin(yaw_rad)
    cr = math.cos(roll_rad)
    sr = math.sin(roll_rad)

    # Build rotation matrix using intrinsic Euler angles (pitch, yaw, roll)
    # Matrix = Rz(roll) * Ry(yaw) * Rx(pitch)

    # Right vector (X-axis)
    right_x = cy * cr
    right_y = cy * sr
    right_z = -sy

    # Up vector (Y-axis)
    up_x = sp * sy * cr - cp * sr
    up_y = sp * sy * sr + cp * cr
    up_z = sp * cy

    # Forward vector (Z-axis)
    forward_x = cp * sy * cr + sp * sr
    forward_y = cp * sy * sr - sp * cr
    forward_z = cp * cy

    # Create rotation matrix
    rotation = RotationMatrix(
        right=Vector3(right_x, right_y, right_z),
        up=Vector3(up_x, up_y, up_z),
        forward=Vector3(forward_x, forward_y, forward_z),
    )

    # Validate matrix
    if rotation.has_nan():
        raise ValueError(
            f"Rotation matrix contains NaN values for Euler angles: pitch={pitch}, yaw={yaw}, roll={roll}"
        )

    if not rotation.is_orthonormal():
        raise ValueError(
            f"Rotation matrix is not orthonormal for Euler angles: pitch={pitch}, yaw={yaw}, roll={roll}"
        )

    pos = Vector3(position[0], position[1], position[2])

    return rotation, pos


def format_transform3d(rotation: RotationMatrix, position: Vector3, precision: int = 6) -> str:
    """Format rotation matrix and position as Godot Transform3D string.

    Args:
        rotation: Rotation matrix (3x3)
        position: Position vector (x, y, z)
        precision: Number of decimal places for floating point values

    Returns:
        Transform3D string for .tscn file

    Example:
        >>> rotation, pos = euler_to_transform3d(0, 45, 0, position=(100, 50, 200))
        >>> format_transform3d(rotation, pos)
        "Transform3D(0.707107, 0, 0.707107, 0, 1, 0, -0.707107, 0, 0.707107, 100, 50, 200)"
    """
    # Get flat matrix values
    matrix_values = rotation.to_flat_list()

    # Round to specified precision
    rounded = [round(v, precision) for v in matrix_values]

    # Add position
    rounded.extend(
        [round(position.x, precision), round(position.y, precision), round(position.z, precision)]
    )

    # Format as Transform3D string
    values_str = ", ".join(str(v) for v in rounded)
    return f"Transform3D({values_str})"


def format_identity_transform(position: tuple[float, float, float], precision: int = 6) -> str:
    """Create an identity rotation Transform3D (no rotation).

    Args:
        position: Position as (x, y, z) tuple
        precision: Number of decimal places

    Returns:
        Transform3D string with identity rotation

    Example:
        >>> format_identity_transform((100, 50, 200))
        "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 50, 200)"
    """
    x, y, z = position
    x = round(x, precision)
    y = round(y, precision)
    z = round(z, precision)

    return f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x}, {y}, {z})"


def validate_position(position: tuple[float, float, float]) -> bool:
    """Validate position values (no NaN or infinity).

    Args:
        position: Position tuple (x, y, z)

    Returns:
        True if position is valid
    """
    return all(not math.isnan(v) and not math.isinf(v) for v in position)


def convert_bf1942_to_godot(
    bf1942_position: tuple[float, float, float], bf1942_rotation: tuple[float, float, float]
) -> str:
    """Convert BF1942 position and rotation to Godot Transform3D string.

    Main convenience function for conversion pipeline.

    Args:
        bf1942_position: (x, y, z) position in meters
        bf1942_rotation: (pitch, yaw, roll) in degrees

    Returns:
        Transform3D string for .tscn file

    Raises:
        ValueError: If inputs are invalid

    Example:
        >>> convert_bf1942_to_godot((100, 50, 200), (0, 45, 0))
        "Transform3D(0.707107, 0, 0.707107, 0, 1, 0, -0.707107, 0, 0.707107, 100, 50, 200)"
    """
    # Validate inputs
    if not validate_position(bf1942_position):
        raise ValueError(f"Invalid position: {bf1942_position}")

    pitch, yaw, roll = bf1942_rotation

    # Convert Euler to matrix
    rotation, position = euler_to_transform3d(
        pitch=pitch, yaw=yaw, roll=roll, position=bf1942_position
    )

    # Format as Transform3D string
    return format_transform3d(rotation, position)


# Convenience functions for common scenarios


def convert_vehicle_spawner(
    position: tuple[float, float, float], rotation: tuple[float, float, float]
) -> str:
    """Convert vehicle spawner transform.

    Args:
        position: (x, y, z) position
        rotation: (pitch, yaw, roll) rotation in degrees

    Returns:
        Transform3D string
    """
    return convert_bf1942_to_godot(position, rotation)


def convert_control_point(position: tuple[float, float, float]) -> str:
    """Convert control point position (no rotation needed).

    Args:
        position: (x, y, z) position

    Returns:
        Transform3D string with identity rotation
    """
    return format_identity_transform(position)


def convert_spawn_point(position: tuple[float, float, float], facing_angle: float = 0.0) -> str:
    """Convert infantry spawn point with facing direction.

    Args:
        position: (x, y, z) position relative to parent HQ
        facing_angle: Yaw angle in degrees (direction player faces when spawning)

    Returns:
        Transform3D string
    """
    # Spawn points typically only need yaw rotation
    rotation, pos = euler_to_transform3d(pitch=0.0, yaw=facing_angle, roll=0.0, position=position)
    return format_transform3d(rotation, pos)


if __name__ == "__main__":
    """Test coordinate transformations."""

    print("Coordinate Transformation Test Suite")
    print("=" * 60)

    # Test 1: Identity rotation
    print("\nTest 1: Identity rotation (no rotation)")
    rotation, pos = euler_to_transform3d(0, 0, 0, position=(100, 50, 200))
    transform = format_transform3d(rotation, pos)
    print("  Input: pitch=0, yaw=0, roll=0, pos=(100, 50, 200)")
    print(f"  Output: {transform}")
    print(f"  Orthonormal: {rotation.is_orthonormal()}")

    # Test 2: 90-degree yaw
    print("\nTest 2: 90-degree yaw rotation")
    rotation, pos = euler_to_transform3d(0, 90, 0, position=(0, 0, 0))
    transform = format_transform3d(rotation, pos)
    print("  Input: pitch=0, yaw=90, roll=0, pos=(0, 0, 0)")
    print(f"  Output: {transform}")
    print(f"  Orthonormal: {rotation.is_orthonormal()}")

    # Test 3: 45-degree yaw (common case)
    print("\nTest 3: 45-degree yaw rotation")
    rotation, pos = euler_to_transform3d(0, 45, 0, position=(500, 80, 400))
    transform = format_transform3d(rotation, pos)
    print("  Input: pitch=0, yaw=45, roll=0, pos=(500, 80, 400)")
    print(f"  Output: {transform}")
    print(f"  Orthonormal: {rotation.is_orthonormal()}")

    # Test 4: Complex rotation
    print("\nTest 4: Complex rotation (pitch + yaw + roll)")
    rotation, pos = euler_to_transform3d(15, 45, 10, position=(100, 50, 200))
    transform = format_transform3d(rotation, pos)
    print("  Input: pitch=15, yaw=45, roll=10, pos=(100, 50, 200)")
    print(f"  Output: {transform}")
    print(f"  Orthonormal: {rotation.is_orthonormal()}")

    # Test 5: Actual Kursk vehicle spawner data
    print("\nTest 5: Real Kursk light tank spawner")
    kursk_pos = (450.345, 78.6349, 249.093)
    kursk_rot = (0.0, 0.103998, 1.52588)
    transform = convert_bf1942_to_godot(kursk_pos, kursk_rot)
    print(f"  Input: pos={kursk_pos}, rot={kursk_rot}")
    print(f"  Output: {transform}")

    # Test 6: Control point (no rotation)
    print("\nTest 6: Control point (identity rotation)")
    cp_pos = (437.315, 77.8547, 238.39)
    transform = convert_control_point(cp_pos)
    print(f"  Input: pos={cp_pos}")
    print(f"  Output: {transform}")

    # Test 7: Spawn point with facing direction
    print("\nTest 7: Spawn point with 180-degree facing")
    sp_pos = (5, 0, 0)  # Relative to HQ
    transform = convert_spawn_point(sp_pos, facing_angle=180.0)
    print(f"  Input: pos={sp_pos}, facing=180°")
    print(f"  Output: {transform}")

    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
