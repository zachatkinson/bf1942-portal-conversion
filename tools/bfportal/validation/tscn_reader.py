#!/usr/bin/env python3
"""TSCN file reader for validation.

Single Responsibility: Only reads and parses .tscn files.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from ..core.interfaces import Vector3


@dataclass
class TscnNode:
    """Represents a node parsed from .tscn file."""
    name: str
    position: Vector3
    rotation_matrix: List[float]  # 3x3 rotation matrix (9 values)
    properties: Dict[str, any]
    raw_content: str


class TscnReader:
    """Reads and parses .tscn files.

    Single Responsibility: Only responsible for reading .tscn files and
    extracting node data. Does not validate or compare.
    """

    def __init__(self, tscn_path: Path):
        """Initialize reader with .tscn file path.

        Args:
            tscn_path: Path to .tscn file
        """
        self.tscn_path = tscn_path
        self.nodes: List[TscnNode] = []

    def parse(self) -> List[TscnNode]:
        """Parse .tscn file and extract all nodes with transforms.

        Returns:
            List of TscnNode objects

        Raises:
            FileNotFoundError: If tscn_path doesn't exist
            ValueError: If file format is invalid
        """
        if not self.tscn_path.exists():
            raise FileNotFoundError(f"TSCN file not found: {self.tscn_path}")

        with open(self.tscn_path, 'r') as f:
            content = f.read()

        # Split into node blocks
        node_blocks = re.findall(
            r'\[node name="([^"]+)"[^\]]*\](.*?)(?=\[node name=|\Z)',
            content,
            re.DOTALL
        )

        for node_name, node_content in node_blocks:
            node = self._parse_node_block(node_name, node_content)
            if node:
                self.nodes.append(node)

        return self.nodes

    def _parse_node_block(self, node_name: str, node_content: str) -> Optional[TscnNode]:
        """Parse a single node block.

        Single Responsibility: Only parses one node block.

        Args:
            node_name: Name of the node
            node_content: Content of the node block

        Returns:
            TscnNode if transform found, None otherwise
        """
        # Extract transform
        transform_match = re.search(
            r'transform = Transform3D\(([^)]+)\)',
            node_content
        )

        if not transform_match:
            return None

        # Parse transform values
        values = [float(v.strip()) for v in transform_match.group(1).split(',')]

        if len(values) != 12:
            return None

        # Transform3D has 12 values: 3x3 rotation matrix + position vector
        position = Vector3(values[9], values[10], values[11])
        rotation_matrix = values[0:9]

        # Extract properties
        properties = self._extract_properties(node_content)

        return TscnNode(
            name=node_name,
            position=position,
            rotation_matrix=rotation_matrix,
            properties=properties,
            raw_content=node_content
        )

    def _extract_properties(self, node_content: str) -> Dict[str, any]:
        """Extract properties from node content.

        Single Responsibility: Only extracts properties.

        Args:
            node_content: Node block content

        Returns:
            Dictionary of properties
        """
        properties = {}

        # Extract Team property
        team_match = re.search(r'Team = (\d+)', node_content)
        if team_match:
            properties['team'] = int(team_match.group(1))

        # Extract ObjId property
        objid_match = re.search(r'ObjId = (\d+)', node_content)
        if objid_match:
            properties['objid'] = int(objid_match.group(1))

        # Extract parent information
        parent_match = re.search(r'parent="([^"]+)"', node_content)
        if parent_match:
            properties['parent'] = parent_match.group(1)

        return properties

    def get_nodes_by_pattern(self, pattern: str) -> List[TscnNode]:
        """Get nodes matching a name pattern.

        Args:
            pattern: Regex pattern to match node names

        Returns:
            List of matching nodes
        """
        regex = re.compile(pattern)
        return [node for node in self.nodes if regex.search(node.name)]

    def get_nodes_by_team(self, team: int) -> List[TscnNode]:
        """Get nodes belonging to a specific team.

        Args:
            team: Team number (1 or 2)

        Returns:
            List of nodes for that team
        """
        return [
            node for node in self.nodes
            if node.properties.get('team') == team
        ]
