#!/usr/bin/env python3
"""TSCN file parsing and formatting utilities.

Shared utilities for parsing and formatting Godot .tscn Transform3D strings.
Eliminates duplication across CLI tools and generators.
"""

import re


class TscnTransformParser:
    """Parse and format Transform3D strings from Godot .tscn files.

    Single Responsibility: Only handles Transform3D string operations.
    """

    @staticmethod
    def parse(transform_str: str) -> tuple[list[float], list[float]]:
        """Parse Transform3D string into rotation matrix and position.

        Args:
            transform_str: Transform3D string from .tscn file

        Returns:
            Tuple of (rotation_matrix, position) where:
            - rotation_matrix is list[9] (3x3 matrix as flat list)
            - position is list[3] (x, y, z)

        Raises:
            ValueError: If transform string is invalid or malformed

        Example:
            >>> parser = TscnTransformParser()
            >>> rotation, position = parser.parse("Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 30)")
            >>> rotation
            [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
            >>> position
            [10.0, 20.0, 30.0]
        """
        match = re.search(r"Transform3D\(([^)]+)\)", transform_str)
        if not match:
            raise ValueError(f"Invalid Transform3D format: {transform_str}")

        values = [float(x.strip()) for x in match.group(1).split(",")]
        if len(values) != 12:
            raise ValueError(f"Expected 12 values in Transform3D, got {len(values)}")

        rotation_matrix = values[:9]
        position = values[9:]

        return rotation_matrix, position

    @staticmethod
    def format(rotation: list[float], position: list[float]) -> str:
        """Format rotation matrix and position into Transform3D string.

        Args:
            rotation: 3x3 rotation matrix as flat list[9]
            position: Position as list[3] (x, y, z)

        Returns:
            Transform3D string suitable for .tscn file

        Raises:
            ValueError: If rotation is not 9 values or position is not 3 values

        Example:
            >>> parser = TscnTransformParser()
            >>> rotation = [1, 0, 0, 0, 1, 0, 0, 0, 1]
            >>> position = [10, 20, 30]
            >>> parser.format(rotation, position)
            'Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 30)'
        """
        if len(rotation) != 9:
            raise ValueError(f"Rotation matrix must have 9 values, got {len(rotation)}")
        if len(position) != 3:
            raise ValueError(f"Position must have 3 values, got {len(position)}")

        values = rotation + position
        values_str = ", ".join(f"{v:.6g}" for v in values)
        return f"Transform3D({values_str})"

    @staticmethod
    def extract_from_line(line: str) -> str | None:
        """Extract Transform3D substring from a .tscn line.

        Args:
            line: Line from .tscn file that may contain Transform3D

        Returns:
            Transform3D string if found, None otherwise

        Example:
            >>> parser = TscnTransformParser()
            >>> line = 'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 30)'
            >>> parser.extract_from_line(line)
            'Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 30)'
        """
        match = re.search(r"Transform3D\([^)]+\)", line)
        return match.group(0) if match else None

    @staticmethod
    def replace_in_line(line: str, new_transform: str) -> str:
        """Replace Transform3D in line with new transform string.

        Args:
            line: Line from .tscn file containing Transform3D
            new_transform: New Transform3D string to replace with

        Returns:
            Line with Transform3D replaced

        Example:
            >>> parser = TscnTransformParser()
            >>> line = 'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)'
            >>> new = 'Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 30)'
            >>> parser.replace_in_line(line, new)
            'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 30)'
        """
        return re.sub(r"Transform3D\([^)]+\)", new_transform, line)
