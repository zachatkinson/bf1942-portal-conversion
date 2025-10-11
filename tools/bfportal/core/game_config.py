#!/usr/bin/env python3
"""Configuration data structures for games and maps."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import json


@dataclass
class GameConfig:
    """Configuration for a Battlefield game."""
    name: str  # e.g., "BF1942"
    engine: str  # e.g., "Refractor 1.0"
    engine_type: str  # e.g., "refractor", "frostbite"
    version: str  # e.g., "1.6"
    era: str  # e.g., "WW2"
    expansions: List[str]  # e.g., ["xpack1_rtr", "xpack2_sw"]


@dataclass
class MapConfig:
    """Configuration for a specific map."""
    name: str  # e.g., "Kursk"
    game: str  # e.g., "BF1942"
    expansion: str  # e.g., "base", "xpack1_rtr"
    theme: str  # e.g., "open_terrain", "urban", "desert"
    recommended_base_terrain: str  # e.g., "MP_Tungsten"
    size: str  # e.g., "large", "medium", "small"
    dimensions: Dict[str, float]  # {"width": 2000, "height": 2000}
    notes: str  # Additional notes


@dataclass
class ConversionConfig:
    """Configuration for the conversion process."""
    base_terrain: str  # Target Portal base terrain
    target_map_center: Dict[str, float]  # {"x": 0, "y": 0, "z": 0}
    scale_factor: float = 1.0
    height_adjustment: bool = True
    validate_bounds: bool = True
    debug_mode: bool = False


class ConfigLoader:
    """Loads configuration from JSON files."""

    @staticmethod
    def load_game_config(config_path: Path) -> GameConfig:
        """Load game configuration from JSON.

        Args:
            config_path: Path to game config JSON

        Returns:
            GameConfig instance

        Raises:
            FileNotFoundError: If config file not found
            ValueError: If config is invalid
        """
        with open(config_path, 'r') as f:
            data = json.load(f)

        return GameConfig(
            name=data['name'],
            engine=data['engine'],
            engine_type=data['engine_type'],
            version=data['version'],
            era=data['era'],
            expansions=data.get('expansions', [])
        )

    @staticmethod
    def load_map_config(config_path: Path) -> MapConfig:
        """Load map configuration from JSON.

        Args:
            config_path: Path to map config JSON

        Returns:
            MapConfig instance

        Raises:
            FileNotFoundError: If config file not found
            ValueError: If config is invalid
        """
        with open(config_path, 'r') as f:
            data = json.load(f)

        return MapConfig(
            name=data['name'],
            game=data['game'],
            expansion=data.get('expansion', 'base'),
            theme=data['theme'],
            recommended_base_terrain=data['recommended_base_terrain'],
            size=data['size'],
            dimensions=data['dimensions'],
            notes=data.get('notes', '')
        )

    @staticmethod
    def load_conversion_config(config_path: Path) -> ConversionConfig:
        """Load conversion configuration from JSON.

        Args:
            config_path: Path to conversion config JSON

        Returns:
            ConversionConfig instance

        Raises:
            FileNotFoundError: If config file not found
            ValueError: If config is invalid
        """
        with open(config_path, 'r') as f:
            data = json.load(f)

        return ConversionConfig(
            base_terrain=data['base_terrain'],
            target_map_center=data['target_map_center'],
            scale_factor=data.get('scale_factor', 1.0),
            height_adjustment=data.get('height_adjustment', True),
            validate_bounds=data.get('validate_bounds', True),
            debug_mode=data.get('debug_mode', False)
        )
