#!/usr/bin/env python3
"""Unit tests for configuration loading."""

import json
import sys
from pathlib import Path

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bfportal.core.game_config import ConfigLoader, ConversionConfig, GameConfig, MapConfig


class TestGameConfigLoader:
    """Test cases for loading GameConfig from JSON."""

    def test_load_game_config_success(self, sample_game_config):
        """Test loading valid game config."""
        config = ConfigLoader.load_game_config(sample_game_config)

        assert config.name == "BF1942"
        assert config.engine == "Refractor 1.0"
        assert config.engine_type == "refractor"
        assert config.version == "1.6"
        assert config.era == "WW2"
        assert config.expansions == ["xpack1_rtr", "xpack2_sw"]

    def test_load_game_config_missing_file(self, tmp_path):
        """Test loading game config raises error when file not found."""
        nonexistent = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            ConfigLoader.load_game_config(nonexistent)

    def test_load_game_config_invalid_json(self, tmp_path):
        """Test loading game config raises error with invalid JSON."""
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("{ invalid json ")

        with pytest.raises(json.JSONDecodeError):
            ConfigLoader.load_game_config(invalid_json)

    def test_load_game_config_missing_required_field(self, tmp_path):
        """Test loading game config raises error when required field missing."""
        config_data = {
            "name": "BF1942",
            "engine": "Refractor 1.0",
            # Missing engine_type, version, era
        }

        config_path = tmp_path / "incomplete.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        with pytest.raises(KeyError):
            ConfigLoader.load_game_config(config_path)

    def test_load_game_config_with_default_expansions(self, tmp_path):
        """Test loading game config with no expansions uses empty list."""
        config_data = {
            "name": "BF1942",
            "engine": "Refractor 1.0",
            "engine_type": "refractor",
            "version": "1.6",
            "era": "WW2",
            # No expansions field
        }

        config_path = tmp_path / "no_expansions.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        config = ConfigLoader.load_game_config(config_path)

        assert config.expansions == []


class TestMapConfigLoader:
    """Test cases for loading MapConfig from JSON."""

    def test_load_map_config_success(self, sample_map_config):
        """Test loading valid map config."""
        config = ConfigLoader.load_map_config(sample_map_config)

        assert config.name == "Kursk"
        assert config.game == "BF1942"
        assert config.expansion == "base"
        assert config.theme == "open_terrain"
        assert config.recommended_base_terrain == "MP_Tungsten"
        assert config.size == "large"
        assert config.dimensions == {"width": 2000.0, "height": 2000.0}
        assert config.notes == "Test map config"

    def test_load_map_config_missing_file(self, tmp_path):
        """Test loading map config raises error when file not found."""
        nonexistent = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            ConfigLoader.load_map_config(nonexistent)

    def test_load_map_config_default_expansion(self, tmp_path):
        """Test loading map config with default expansion value."""
        config_data = {
            "name": "Kursk",
            "game": "BF1942",
            # No expansion field
            "theme": "open_terrain",
            "recommended_base_terrain": "MP_Tungsten",
            "size": "large",
            "dimensions": {"width": 2000.0, "height": 2000.0},
        }

        config_path = tmp_path / "map_config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        config = ConfigLoader.load_map_config(config_path)

        assert config.expansion == "base"

    def test_load_map_config_default_notes(self, tmp_path):
        """Test loading map config with default notes value."""
        config_data = {
            "name": "Kursk",
            "game": "BF1942",
            "expansion": "base",
            "theme": "open_terrain",
            "recommended_base_terrain": "MP_Tungsten",
            "size": "large",
            "dimensions": {"width": 2000.0, "height": 2000.0},
            # No notes field
        }

        config_path = tmp_path / "map_config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        config = ConfigLoader.load_map_config(config_path)

        assert config.notes == ""

    def test_load_map_config_invalid_json(self, tmp_path):
        """Test loading map config raises error with invalid JSON."""
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("{ invalid json ")

        with pytest.raises(json.JSONDecodeError):
            ConfigLoader.load_map_config(invalid_json)


class TestConversionConfigLoader:
    """Test cases for loading ConversionConfig from JSON."""

    def test_load_conversion_config_success(self, sample_conversion_config):
        """Test loading valid conversion config."""
        config = ConfigLoader.load_conversion_config(sample_conversion_config)

        assert config.base_terrain == "MP_Tungsten"
        assert config.target_map_center == {"x": 0.0, "y": 0.0, "z": 0.0}
        assert config.scale_factor == 1.0
        assert config.height_adjustment is True
        assert config.validate_bounds is True
        assert config.debug_mode is False

    def test_load_conversion_config_missing_file(self, tmp_path):
        """Test loading conversion config raises error when file not found."""
        nonexistent = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            ConfigLoader.load_conversion_config(nonexistent)

    def test_load_conversion_config_with_defaults(self, tmp_path):
        """Test loading conversion config uses default values."""
        config_data = {
            "base_terrain": "MP_Tungsten",
            "target_map_center": {"x": 0.0, "y": 0.0, "z": 0.0},
            # No optional fields
        }

        config_path = tmp_path / "conversion_config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        config = ConfigLoader.load_conversion_config(config_path)

        assert config.scale_factor == 1.0
        assert config.height_adjustment is True
        assert config.validate_bounds is True
        assert config.debug_mode is False

    def test_load_conversion_config_custom_values(self, tmp_path):
        """Test loading conversion config with custom values."""
        config_data = {
            "base_terrain": "MP_Battery",
            "target_map_center": {"x": 100.0, "y": 50.0, "z": -200.0},
            "scale_factor": 1.5,
            "height_adjustment": False,
            "validate_bounds": False,
            "debug_mode": True,
        }

        config_path = tmp_path / "conversion_config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        config = ConfigLoader.load_conversion_config(config_path)

        assert config.base_terrain == "MP_Battery"
        assert config.target_map_center == {"x": 100.0, "y": 50.0, "z": -200.0}
        assert config.scale_factor == 1.5
        assert config.height_adjustment is False
        assert config.validate_bounds is False
        assert config.debug_mode is True

    def test_load_conversion_config_invalid_json(self, tmp_path):
        """Test loading conversion config raises error with invalid JSON."""
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("{ invalid json ")

        with pytest.raises(json.JSONDecodeError):
            ConfigLoader.load_conversion_config(invalid_json)


class TestGameConfigDataclass:
    """Test cases for GameConfig dataclass."""

    def test_game_config_creation(self):
        """Test creating GameConfig instance."""
        config = GameConfig(
            name="BF1942",
            engine="Refractor 1.0",
            engine_type="refractor",
            version="1.6",
            era="WW2",
            expansions=["xpack1_rtr"],
        )

        assert config.name == "BF1942"
        assert config.engine == "Refractor 1.0"
        assert config.engine_type == "refractor"
        assert config.version == "1.6"
        assert config.era == "WW2"
        assert config.expansions == ["xpack1_rtr"]


class TestMapConfigDataclass:
    """Test cases for MapConfig dataclass."""

    def test_map_config_creation(self):
        """Test creating MapConfig instance."""
        config = MapConfig(
            name="Kursk",
            game="BF1942",
            expansion="base",
            theme="open_terrain",
            recommended_base_terrain="MP_Tungsten",
            size="large",
            dimensions={"width": 2000.0, "height": 2000.0},
            notes="Test map",
        )

        assert config.name == "Kursk"
        assert config.game == "BF1942"
        assert config.expansion == "base"
        assert config.theme == "open_terrain"
        assert config.recommended_base_terrain == "MP_Tungsten"
        assert config.size == "large"
        assert config.dimensions == {"width": 2000.0, "height": 2000.0}
        assert config.notes == "Test map"


class TestConversionConfigDataclass:
    """Test cases for ConversionConfig dataclass."""

    def test_conversion_config_creation_minimal(self):
        """Test creating ConversionConfig with minimal parameters."""
        config = ConversionConfig(
            base_terrain="MP_Tungsten", target_map_center={"x": 0.0, "y": 0.0, "z": 0.0}
        )

        assert config.base_terrain == "MP_Tungsten"
        assert config.target_map_center == {"x": 0.0, "y": 0.0, "z": 0.0}
        assert config.scale_factor == 1.0
        assert config.height_adjustment is True
        assert config.validate_bounds is True
        assert config.debug_mode is False

    def test_conversion_config_creation_full(self):
        """Test creating ConversionConfig with all parameters."""
        config = ConversionConfig(
            base_terrain="MP_Battery",
            target_map_center={"x": 100.0, "y": 50.0, "z": -200.0},
            scale_factor=1.5,
            height_adjustment=False,
            validate_bounds=False,
            debug_mode=True,
        )

        assert config.base_terrain == "MP_Battery"
        assert config.target_map_center == {"x": 100.0, "y": 50.0, "z": -200.0}
        assert config.scale_factor == 1.5
        assert config.height_adjustment is False
        assert config.validate_bounds is False
        assert config.debug_mode is True
