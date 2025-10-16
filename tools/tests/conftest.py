#!/usr/bin/env python3
"""Pytest configuration and shared fixtures for BFPortal SDK tests."""

import json
import sys
from pathlib import Path

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bfportal.core.interfaces import MapContext, Team


@pytest.fixture
def sample_map_context() -> MapContext:
    """Create a sample MapContext for testing.

    Returns:
        MapContext with default WW2/open_terrain settings
    """
    return MapContext(
        target_base_map="MP_Tungsten", era="WW2", theme="open_terrain", team=Team.NEUTRAL
    )


@pytest.fixture
def sample_portal_assets(tmp_path: Path) -> Path:
    """Create a sample Portal asset_types.json for testing.

    Args:
        tmp_path: pytest temporary directory fixture

    Returns:
        Path to temporary asset_types.json
    """
    assets_data = {
        "AssetTypes": [
            {
                "type": "Tree_Pine_Large",
                "directory": "Nature/Trees",
                "levelRestrictions": [],
                "properties": [{"name": "ObjId", "type": "int", "default": -1}],
            },
            {
                "type": "Tree_Oak_Medium",
                "directory": "Nature/Trees",
                "levelRestrictions": ["MP_Tungsten"],
                "properties": [{"name": "ObjId", "type": "int", "default": -1}],
            },
            {
                "type": "Rock_Boulder_01",
                "directory": "Nature/Rocks",
                "levelRestrictions": [],
                "properties": [{"name": "ObjId", "type": "int", "default": -1}],
            },
            {
                "type": "Building_Barn_01",
                "directory": "Architecture/Rural",
                "levelRestrictions": ["MP_Tungsten", "MP_Battery"],
                "properties": [{"name": "ObjId", "type": "int", "default": -1}],
            },
            {
                "type": "Prop_Sandbag_Wall",
                "directory": "Props/Military",
                "levelRestrictions": [],
                "properties": [{"name": "ObjId", "type": "int", "default": -1}],
            },
            {
                "type": "Vehicle_Cart_01",
                "directory": "Vehicles/Civilian",
                "levelRestrictions": ["MP_Battery"],
                "properties": [{"name": "ObjId", "type": "int", "default": -1}],
            },
        ]
    }

    assets_path = tmp_path / "asset_types.json"
    with open(assets_path, "w") as f:
        json.dump(assets_data, f)

    return assets_path


@pytest.fixture
def sample_bf1942_mappings(tmp_path: Path) -> Path:
    """Create a sample BF1942 to Portal mappings file for testing.

    Args:
        tmp_path: pytest temporary directory fixture

    Returns:
        Path to temporary mappings.json
    """
    mappings_data = {
        "_metadata": {
            "version": "1.0",
            "description": "Test mappings",
        },
        "vegetation": {
            "treeline_pine_w": {
                "portal_equivalent": "Tree_Pine_Large",
                "category": "vegetation",
                "confidence_score": 5,
                "notes": "Test mapping",
            },
            "treeline_oak_w": {
                "portal_equivalent": "Tree_Oak_Medium",
                "category": "vegetation",
                "confidence_score": 5,
                "fallbacks": {"MP_Battery": "Tree_Pine_Large"},
            },
        },
        "buildings": {
            "barn_m1": {
                "portal_equivalent": "Building_Barn_01",
                "category": "building",
                "confidence_score": 5,
            },
            "building_nonexistent": {
                "portal_equivalent": "NonExistent_Asset",
                "category": "building",
                "confidence_score": 3,
            },
        },
        "props": {
            "sandbags_wall": {
                "portal_equivalent": "Prop_Sandbag_Wall",
                "category": "fortification",
                "confidence_score": 5,
            },
        },
    }

    mappings_path = tmp_path / "mappings.json"
    with open(mappings_path, "w") as f:
        json.dump(mappings_data, f)

    return mappings_path


@pytest.fixture
def sample_fallback_keywords(tmp_path: Path) -> Path:
    """Create a sample asset_fallback_keywords.json for testing.

    Args:
        tmp_path: pytest temporary directory fixture

    Returns:
        Path to temporary fallback keywords JSON
    """
    keywords_data = {
        "_metadata": {"description": "Test keywords"},
        "type_categories": [
            {
                "name": "trees",
                "source_keywords": ["tree", "pine", "oak", "spruce"],
                "portal_keywords": ["tree", "pine", "oak", "spruce"],
            },
            {
                "name": "rocks",
                "source_keywords": ["rock", "stone", "boulder"],
                "portal_keywords": ["rock", "stone", "boulder"],
            },
            {
                "name": "buildings",
                "source_keywords": ["barn", "house", "building"],
                "portal_keywords": ["barn", "house", "building"],
            },
            {
                "name": "fortifications",
                "source_keywords": ["sandbag", "sand"],
                "portal_keywords": ["sandbag", "sand", "bag"],
            },
            {
                "name": "vehicles",
                "source_keywords": ["cart", "wagon"],
                "portal_keywords": ["cart", "wagon"],
            },
        ],
    }

    keywords_path = tmp_path / "asset_fallback_keywords.json"
    with open(keywords_path, "w") as f:
        json.dump(keywords_data, f)

    return keywords_path


@pytest.fixture
def sample_game_config(tmp_path: Path) -> Path:
    """Create a sample game config JSON for testing.

    Args:
        tmp_path: pytest temporary directory fixture

    Returns:
        Path to temporary game config JSON
    """
    config_data = {
        "name": "BF1942",
        "engine": "Refractor 1.0",
        "engine_type": "refractor",
        "version": "1.6",
        "era": "WW2",
        "expansions": ["xpack1_rtr", "xpack2_sw"],
    }

    config_path = tmp_path / "game_config.json"
    with open(config_path, "w") as f:
        json.dump(config_data, f)

    return config_path


@pytest.fixture
def sample_map_config(tmp_path: Path) -> Path:
    """Create a sample map config JSON for testing.

    Args:
        tmp_path: pytest temporary directory fixture

    Returns:
        Path to temporary map config JSON
    """
    config_data = {
        "name": "Kursk",
        "game": "BF1942",
        "expansion": "base",
        "theme": "open_terrain",
        "recommended_base_terrain": "MP_Tungsten",
        "size": "large",
        "dimensions": {"width": 2000.0, "height": 2000.0},
        "notes": "Test map config",
    }

    config_path = tmp_path / "map_config.json"
    with open(config_path, "w") as f:
        json.dump(config_data, f)

    return config_path


@pytest.fixture
def sample_conversion_config(tmp_path: Path) -> Path:
    """Create a sample conversion config JSON for testing.

    Args:
        tmp_path: pytest temporary directory fixture

    Returns:
        Path to temporary conversion config JSON
    """
    config_data = {
        "base_terrain": "MP_Tungsten",
        "target_map_center": {"x": 0.0, "y": 0.0, "z": 0.0},
        "scale_factor": 1.0,
        "height_adjustment": True,
        "validate_bounds": True,
        "debug_mode": False,
    }

    config_path = tmp_path / "conversion_config.json"
    with open(config_path, "w") as f:
        json.dump(config_data, f)

    return config_path


@pytest.fixture
def mock_portal_sdk_structure(tmp_path: Path) -> Path:
    """Create a mock Portal SDK directory structure with required files.

    This fixture creates the minimal Portal SDK directory structure needed
    for PortalConverter initialization to succeed. It creates real files
    instead of mocking Path.exists() globally.

    Args:
        tmp_path: pytest temporary directory fixture

    Returns:
        Path to the mock SDK root directory
    """
    # Create Portal SDK directory structure
    sdk_root = tmp_path / "portal_sdk"
    godot_project = sdk_root / "GodotProject"
    raw_models = godot_project / "raw" / "models"
    raw_models.mkdir(parents=True, exist_ok=True)

    # Create terrain mesh files for common test terrains
    for terrain in ["MP_Tungsten", "MP_Battery", "MP_Outskirts", "MP_NonExistent"]:
        terrain_mesh = raw_models / f"{terrain}_Terrain.glb"
        if terrain != "MP_NonExistent":  # Don't create NonExistent terrain
            terrain_mesh.write_text("# Mock GLB terrain mesh")

    # Create FbExportData structure
    fb_export = sdk_root / "FbExportData"
    fb_export.mkdir(parents=True, exist_ok=True)

    # Create asset_types.json
    asset_types = fb_export / "asset_types.json"
    asset_types.write_text('{"AssetTypes": []}')

    # Create tools/asset_audit structure
    asset_audit = sdk_root / "tools" / "asset_audit"
    asset_audit.mkdir(parents=True, exist_ok=True)

    # Create mappings file
    mappings_file = asset_audit / "bf1942_to_portal_mappings.json"
    mappings_file.write_text('{"_metadata": {}, "vegetation": {}, "buildings": {}}')

    # Create bf1942_source/extracted structure for map files
    bf1942_levels = (
        sdk_root / "bf1942_source" / "extracted" / "Bf1942" / "Archives" / "bf1942" / "Levels"
    )
    bf1942_levels.mkdir(parents=True, exist_ok=True)

    return sdk_root


@pytest.fixture
def mock_terrain_provider():
    """Create a mock terrain provider with realistic test attributes.

    This fixture provides a standard mock TerrainProvider that can be used
    across all tests. It eliminates duplication of terrain setup code.

    Returns:
        MagicMock with terrain provider attributes set to realistic test values
    """
    from unittest.mock import MagicMock

    mock_terrain = MagicMock()
    # Set attributes as actual values (not MagicMocks) so format strings work
    mock_terrain.vertices = [1, 2, 3]
    mock_terrain.min_height = 0.0
    mock_terrain.max_height = 100.0
    mock_terrain.mesh_min_height = 0.0
    mock_terrain.mesh_max_height = 100.0
    mock_terrain.mesh_min_x = -1024.0
    mock_terrain.mesh_max_x = 1024.0
    mock_terrain.mesh_min_z = -1024.0
    mock_terrain.mesh_max_z = 1024.0
    mock_terrain.mesh_center_x = 0.0
    mock_terrain.mesh_center_z = 0.0
    mock_terrain.terrain_y_baseline = 0.0
    mock_terrain.grid_resolution = 256

    return mock_terrain


@pytest.fixture
def map_entry_factory():
    """Factory for creating map entries with customizable fields.

    Returns:
        Callable that creates map entry dicts with overridable defaults

    Example:
        map = map_entry_factory(id="wake_island", status="in_progress")
    """

    def _make_map_entry(**overrides):
        defaults = {
            "id": "kursk",
            "display_name": "Kursk",
            "base_map": "MP_Tungsten",
            "base_map_display": "Tungsten",
            "status": "complete",
        }
        return {**defaults, **overrides}

    return _make_map_entry


@pytest.fixture
def experience_template_factory():
    """Factory for creating experience templates with customizable fields.

    Returns:
        Callable that creates template dicts with overridable defaults

    Example:
        template = experience_template_factory(max_players=64, game_mode="TDM")
    """

    def _make_template(**overrides):
        defaults = {
            "name": "Test Experience",
            "description": "Test description",
            "game_mode": "Conquest",
            "max_players": 32,
            "map_filter": {"status": "complete"},
        }
        return {**defaults, **overrides}

    return _make_template


@pytest.fixture
def registry_factory(map_entry_factory, experience_template_factory):
    """Factory for creating map registries with templates.

    Args:
        map_entry_factory: Factory for creating map entries
        experience_template_factory: Factory for creating templates

    Returns:
        Callable that creates registry dicts

    Example:
        registry = registry_factory(
            maps=[map_entry_factory(id="kursk"), map_entry_factory(id="alamein")],
            template_name="all_maps"
        )
    """

    def _make_registry(maps=None, template_name="test_template", template_overrides=None):
        if maps is None:
            maps = [map_entry_factory()]

        if template_overrides is None:
            template_overrides = {}

        return {
            "maps": maps,
            "experience_templates": {template_name: experience_template_factory(**template_overrides)},
        }

    return _make_registry
