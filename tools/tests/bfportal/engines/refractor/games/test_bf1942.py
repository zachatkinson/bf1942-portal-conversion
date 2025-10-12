#!/usr/bin/env python3
"""Tests for bf1942.py game engines."""

import sys
from pathlib import Path

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

    def test_get_expansion_info_base_game(self, tmp_path: Path):
        """Test get_expansion_info identifies base game maps."""
        # Arrange
        engine = BF1942Engine()
        map_path = tmp_path / "bf1942" / "levels" / "Kursk"
        map_path.mkdir(parents=True)

        # Act
        result = engine.get_expansion_info(map_path)

        # Assert
        assert result == "base"

    def test_get_expansion_info_road_to_rome_xpack1(self, tmp_path: Path):
        """Test get_expansion_info identifies Road to Rome via xpack1."""
        # Arrange
        engine = BF1942Engine()
        map_path = tmp_path / "xpack1" / "levels" / "Anzio"
        map_path.mkdir(parents=True)

        # Act
        result = engine.get_expansion_info(map_path)

        # Assert
        assert result == "xpack1_rtr"

    def test_get_expansion_info_road_to_rome_string(self, tmp_path: Path):
        """Test get_expansion_info identifies Road to Rome via string."""
        # Arrange
        engine = BF1942Engine()
        map_path = tmp_path / "road_to_rome" / "levels" / "Anzio"
        map_path.mkdir(parents=True)

        # Act
        result = engine.get_expansion_info(map_path)

        # Assert
        assert result == "xpack1_rtr"

    def test_get_expansion_info_secret_weapons_xpack2(self, tmp_path: Path):
        """Test get_expansion_info identifies Secret Weapons via xpack2."""
        # Arrange
        engine = BF1942Engine()
        map_path = tmp_path / "xpack2" / "levels" / "Raid_on_Agheila"
        map_path.mkdir(parents=True)

        # Act
        result = engine.get_expansion_info(map_path)

        # Assert
        assert result == "xpack2_sw"

    def test_get_expansion_info_secret_weapons_string(self, tmp_path: Path):
        """Test get_expansion_info identifies Secret Weapons via string."""
        # Arrange
        engine = BF1942Engine()
        map_path = tmp_path / "secret_weapons" / "levels" / "Raid_on_Agheila"
        map_path.mkdir(parents=True)

        # Act
        result = engine.get_expansion_info(map_path)

        # Assert
        assert result == "xpack2_sw"

    def test_get_expansion_info_case_insensitive(self, tmp_path: Path):
        """Test get_expansion_info is case insensitive."""
        # Arrange
        engine = BF1942Engine()
        map_path = tmp_path / "XPack1" / "LEVELS" / "ANZIO"
        map_path.mkdir(parents=True)

        # Act
        result = engine.get_expansion_info(map_path)

        # Assert
        assert result == "xpack1_rtr"

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
