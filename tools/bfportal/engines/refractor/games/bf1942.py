#!/usr/bin/env python3
"""BF1942 game engine implementation.

Battlefield 1942 (2002) - Refractor Engine 1.0
"""

from pathlib import Path

from ....core.interfaces import Team
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

    def _swap_teams(self, team: Team) -> Team:
        """Swap BF1942 teams for Portal conversion.

        Swaps team assignments so that:
        - BF1942 Team 1 (German/Axis) → Portal Team 2 (non-NATO)
        - BF1942 Team 2 (Russian/Allied) → Portal Team 1 (NATO)

        This ensures the Russian base gets NATO assets (Leopard, F16, AH64)
        and the German base gets non-NATO assets (Abrams, JAS39, Eurocopter).

        Args:
            team: Original BF1942 team assignment

        Returns:
            Swapped team for Portal
        """
        if team == Team.TEAM_1:
            return Team.TEAM_2
        elif team == Team.TEAM_2:
            return Team.TEAM_1
        else:
            return Team.NEUTRAL  # Neutral stays neutral

    def _parse_spawns(self, con_files, team: Team) -> list:
        """Override to swap teams for BF1942."""
        # Parse with swapped team
        swapped_team = self._swap_teams(team)
        spawns = super()._parse_spawns(con_files, swapped_team)

        # Restore original team assignment in spawns
        # (so Portal Team 1 HQ gets the Russian base spawns)
        for spawn in spawns:
            spawn.team = team

        return spawns

    def _parse_game_objects(self, con_files) -> list:
        """Override to swap teams for BF1942 game objects."""
        game_objects = super()._parse_game_objects(con_files)

        # Swap team assignments for all game objects
        for obj in game_objects:
            obj.team = self._swap_teams(obj.team)

        return game_objects

    def get_expansion_info(self, map_path: Path) -> str:
        """Determine which BF1942 expansion this map belongs to.

        Args:
            map_path: Path to map directory

        Returns:
            Expansion identifier: 'base', 'xpack1_rtr', 'xpack2_sw'
        """
        path_str = str(map_path).lower()

        if "xpack1" in path_str or "road_to_rome" in path_str:
            return "xpack1_rtr"
        elif "xpack2" in path_str or "secret_weapons" in path_str:
            return "xpack2_sw"
        else:
            return "base"


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
