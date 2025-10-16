#!/usr/bin/env python3
"""Tests for bf1942.py game engines."""

import sys
from pathlib import Path

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))

from bfportal.engines.refractor.games.bf1942 import (
    BF2Engine,
    BF1942Engine,
    BF2142Engine,
    BFVietnamEngine,
)


class TestBF1942Engine:
    """Tests for BF1942Engine."""

    def test_get_game_name_returns_bf1942(self):
        """Test get_game_name returns BF1942."""
        # Arrange
        engine = BF1942Engine()

        # Act
        result = engine.get_game_name()

        # Assert
        assert result == "BF1942"

    def test_get_engine_version_returns_refractor_1_0(self):
        """Test get_engine_version returns Refractor 1.0."""
        # Arrange
        engine = BF1942Engine()

        # Act
        result = engine.get_engine_version()

        # Assert
        assert result == "Refractor 1.0"

    def test_get_game_mode_default_returns_conquest(self):
        """Test get_game_mode_default returns Conquest."""
        # Arrange
        engine = BF1942Engine()

        # Act
        result = engine.get_game_mode_default()

        # Assert
        assert result == "Conquest"

    @pytest.mark.parametrize(
        "path_parts,expected",
        [
            (["bf1942", "levels", "Kursk"], "base"),
            (["xpack1", "levels", "Anzio"], "xpack1_rtr"),
            (["road_to_rome", "levels", "Anzio"], "xpack1_rtr"),
            (["xpack2", "levels", "Raid_on_Agheila"], "xpack2_sw"),
            (["secret_weapons", "levels", "Raid_on_Agheila"], "xpack2_sw"),
            (["XPack1", "LEVELS", "ANZIO"], "xpack1_rtr"),  # Case insensitive
        ],
        ids=[
            "base_game",
            "road_to_rome_xpack1",
            "road_to_rome_string",
            "secret_weapons_xpack2",
            "secret_weapons_string",
            "case_insensitive",
        ],
    )
    def test_get_expansion_info(self, tmp_path: Path, path_parts: list[str], expected: str):
        """Test get_expansion_info identifies expansions correctly."""
        # Arrange
        engine = BF1942Engine()
        map_path = tmp_path.joinpath(*path_parts)
        map_path.mkdir(parents=True)

        # Act
        result = engine.get_expansion_info(map_path)

        # Assert
        assert result == expected

    def test_inherits_from_refractor_engine(self):
        """Test BF1942Engine has RefractorEngine attributes."""
        # Arrange
        engine = BF1942Engine()

        # Act & Assert
        assert hasattr(engine, "con_parser")
        assert hasattr(engine, "coordinate_system")
        assert hasattr(engine, "parse_map")


class TestBFVietnamEngine:
    """Tests for BFVietnamEngine."""

    def test_get_game_name_returns_bfvietnam(self):
        """Test get_game_name returns BFVietnam."""
        # Arrange
        engine = BFVietnamEngine()

        # Act
        result = engine.get_game_name()

        # Assert
        assert result == "BFVietnam"

    def test_get_engine_version_returns_refractor_enhanced(self):
        """Test get_engine_version returns Refractor 1.0 Enhanced."""
        # Arrange
        engine = BFVietnamEngine()

        # Act
        result = engine.get_engine_version()

        # Assert
        assert result == "Refractor 1.0 Enhanced"

    def test_get_game_mode_default_returns_conquest(self):
        """Test get_game_mode_default returns Conquest."""
        # Arrange
        engine = BFVietnamEngine()

        # Act
        result = engine.get_game_mode_default()

        # Assert
        assert result == "Conquest"

    def test_inherits_from_refractor_engine(self):
        """Test BFVietnamEngine has RefractorEngine attributes."""
        # Arrange
        engine = BFVietnamEngine()

        # Act & Assert
        assert hasattr(engine, "con_parser")
        assert hasattr(engine, "coordinate_system")


class TestBF2Engine:
    """Tests for BF2Engine."""

    def test_get_game_name_returns_bf2(self):
        """Test get_game_name returns BF2."""
        # Arrange
        engine = BF2Engine()

        # Act
        result = engine.get_game_name()

        # Assert
        assert result == "BF2"

    def test_get_engine_version_returns_refractor_2_0(self):
        """Test get_engine_version returns Refractor 2.0."""
        # Arrange
        engine = BF2Engine()

        # Act
        result = engine.get_engine_version()

        # Assert
        assert result == "Refractor 2.0"

    def test_get_game_mode_default_returns_conquest(self):
        """Test get_game_mode_default returns Conquest."""
        # Arrange
        engine = BF2Engine()

        # Act
        result = engine.get_game_mode_default()

        # Assert
        assert result == "Conquest"

    def test_inherits_from_refractor_engine(self):
        """Test BF2Engine has RefactorEngine attributes."""
        # Arrange
        engine = BF2Engine()

        # Act & Assert
        assert hasattr(engine, "con_parser")
        assert hasattr(engine, "coordinate_system")


class TestBF2142Engine:
    """Tests for BF2142Engine."""

    def test_get_game_name_returns_bf2142(self):
        """Test get_game_name returns BF2142."""
        # Arrange
        engine = BF2142Engine()

        # Act
        result = engine.get_game_name()

        # Assert
        assert result == "BF2142"

    def test_get_engine_version_returns_refractor_2_0_enhanced(self):
        """Test get_engine_version returns Refractor 2.0 Enhanced."""
        # Arrange
        engine = BF2142Engine()

        # Act
        result = engine.get_engine_version()

        # Assert
        assert result == "Refractor 2.0 Enhanced"

    def test_get_game_mode_default_returns_conquest(self):
        """Test get_game_mode_default returns Conquest."""
        # Arrange
        engine = BF2142Engine()

        # Act
        result = engine.get_game_mode_default()

        # Assert
        assert result == "Conquest"

    def test_inherits_from_refractor_engine(self):
        """Test BF2142Engine has RefractorEngine attributes."""
        # Arrange
        engine = BF2142Engine()

        # Act & Assert
        assert hasattr(engine, "con_parser")
        assert hasattr(engine, "coordinate_system")
