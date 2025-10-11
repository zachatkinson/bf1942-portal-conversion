#!/usr/bin/env python3
"""BF1942 game engine implementation.

Battlefield 1942 (2002) - Refractor Engine 1.0
"""

from pathlib import Path
from typing import List

from ....core.interfaces import SpawnPoint, Team
from ....parsers.con_parser import ConFileSet
from ..refractor_base import RefractorEngine


class BF1942Engine(RefractorEngine):
    """Game engine implementation for Battlefield 1942.

    Extends RefractorEngine with BF1942-specific parsing and features.
    """

    def get_game_name(self) -> str:
        """Return the game name."""
        return "BF1942"

    def get_engine_version(self) -> str:
        """Return the engine version."""
        return "Refractor 1.0"

    def get_game_mode_default(self) -> str:
        """Return default game mode."""
        return "Conquest"

    # ========================================================================
    # BF1942-Specific Methods
    # ========================================================================

    def get_expansion_info(self, map_path: Path) -> str:
        """Determine which BF1942 expansion this map belongs to.

        Args:
            map_path: Path to map directory

        Returns:
            Expansion identifier: 'base', 'xpack1_rtr', 'xpack2_sw'
        """
        path_str = str(map_path).lower()

        if 'xpack1' in path_str or 'road_to_rome' in path_str:
            return 'xpack1_rtr'
        elif 'xpack2' in path_str or 'secret_weapons' in path_str:
            return 'xpack2_sw'
        else:
            return 'base'


class BFVietnamEngine(RefractorEngine):
    """Game engine implementation for Battlefield Vietnam.

    Battlefield Vietnam (2004) - Refractor Engine 1.0 (enhanced)
    Shares most code with BF1942 but adds helicopters and riverboats.
    """

    def get_game_name(self) -> str:
        """Return the game name."""
        return "BFVietnam"

    def get_engine_version(self) -> str:
        """Return the engine version."""
        return "Refractor 1.0 Enhanced"

    def get_game_mode_default(self) -> str:
        """Return default game mode."""
        return "Conquest"

    # BFVietnam can inherit most behavior from RefractorEngine base
    # Only override if Vietnam-specific parsing is needed


class BF2Engine(RefractorEngine):
    """Game engine implementation for Battlefield 2.

    Battlefield 2 (2005) - Refractor Engine 2.0
    Larger maps, commander mode, squad system.
    """

    def get_game_name(self) -> str:
        """Return the game name."""
        return "BF2"

    def get_engine_version(self) -> str:
        """Return the engine version."""
        return "Refractor 2.0"

    def get_game_mode_default(self) -> str:
        """Return default game mode."""
        return "Conquest"

    # TODO: Add BF2-specific parsing (commander assets, UAVs, etc.)


class BF2142Engine(RefractorEngine):
    """Game engine implementation for Battlefield 2142.

    Battlefield 2142 (2006) - Refractor Engine 2.0 (enhanced)
    Titan mode, future warfare theme.
    """

    def get_game_name(self) -> str:
        """Return the game name."""
        return "BF2142"

    def get_engine_version(self) -> str:
        """Return the engine version."""
        return "Refractor 2.0 Enhanced"

    def get_game_mode_default(self) -> str:
        """Return default game mode."""
        return "Conquest"

    # TODO: Add BF2142-specific parsing (Titan assets, etc.)
