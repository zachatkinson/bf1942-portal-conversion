#!/usr/bin/env python3
"""File system path constants for Portal SDK project.

Single Responsibility: Define project directory and file paths.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-13
"""

from pathlib import Path

# ==============================================================================
# Project Root Detection
# ==============================================================================


def get_project_root() -> Path:
    """Get Portal SDK project root directory.

    Returns:
        Path to project root (where FbExportData and GodotProject are located)

    Example:
        >>> root = get_project_root()
        >>> print(root / "GodotProject")
        /Users/zach/Downloads/PortalSDK/GodotProject
    """
    # Assume current working directory is project root
    # (CLI tools are run from Portal SDK root)
    cwd = Path.cwd()

    # Handle case where we're running from GodotProject subdirectory
    if cwd.name == "GodotProject" or (cwd / "project.godot").exists():
        return cwd.parent

    # Otherwise, assume we're in project root
    return cwd


# ==============================================================================
# Directory Constants (Relative to Project Root)
# ==============================================================================

DIR_BF1942_SOURCE = "bf1942_source"  # Original BF1942 game files
DIR_BF1942_EXTRACTED = "bf1942_source/extracted"  # Extracted RFA files
DIR_GODOT_PROJECT = "GodotProject"  # BF6 Portal Godot workspace
DIR_GODOT_LEVELS = "GodotProject/levels"  # Generated .tscn map files
DIR_GODOT_OBJECTS = "GodotProject/objects"  # BF6 asset library
DIR_GODOT_STATIC = "GodotProject/static"  # Static terrain/assets
DIR_GODOT_RAW_MODELS = "GodotProject/raw/models"  # Large .glb files (ignored in git)
DIR_FB_EXPORT_DATA = "FbExportData"  # Export configurations
DIR_FB_EXPORT_LEVELS = "FbExportData/levels"  # Exported .spatial.json files
DIR_TOOLS = "tools"  # Conversion toolset
DIR_TOOLS_BFPORTAL = "tools/bfportal"  # Core library modules
DIR_MODS = "mods"  # Example Portal game modes

# ==============================================================================
# File Constants (Relative to Project Root)
# ==============================================================================

FILE_ASSET_TYPES = "FbExportData/asset_types.json"  # Complete BF6 asset catalog
FILE_LEVEL_INFO = "FbExportData/level_info.json"  # Level metadata
FILE_PROJECT_GODOT = "GodotProject/project.godot"  # Godot project file
FILE_README = "README.md"  # Project documentation
FILE_README_HTML = "README.html"  # Portal SDK documentation

# ==============================================================================
# BF1942 Source Paths
# ==============================================================================

# RFA archive locations (relative to project root)
DIR_BF1942_RFA_BASE = "bf1942_source/Mods/bf1942/Archives/bf1942/levels"
DIR_BF1942_RFA_XPACK1 = "bf1942_source/Mods/XPack1/Archives/XPack1/levels"
DIR_BF1942_RFA_XPACK2 = "bf1942_source/Mods/XPack2/Archives/XPack2/levels"

# Extracted levels (relative to project root)
DIR_BF1942_EXTRACTED_BASE = "bf1942_source/extracted/Bf1942/Archives/bf1942/Levels"
DIR_BF1942_EXTRACTED_XPACK1 = "bf1942_source/extracted/XPack1/Archives/XPack1/Levels"
DIR_BF1942_EXTRACTED_XPACK2 = "bf1942_source/extracted/XPack2/Archives/XPack2/Levels"

# ==============================================================================
# Helper Functions
# ==============================================================================


def get_godot_project_dir() -> Path:
    """Get GodotProject directory path.

    Returns:
        Absolute path to GodotProject directory

    Example:
        >>> godot_dir = get_godot_project_dir()
        >>> (godot_dir / "project.godot").exists()
        True
    """
    return get_project_root() / DIR_GODOT_PROJECT


def get_fb_export_data_dir() -> Path:
    """Get FbExportData directory path.

    Returns:
        Absolute path to FbExportData directory
    """
    return get_project_root() / DIR_FB_EXPORT_DATA


def get_spatial_levels_dir() -> Path:
    """Get FbExportData/levels directory path (for .spatial.json files).

    Returns:
        Absolute path to spatial levels directory

    Example:
        >>> get_spatial_levels_dir()
        PosixPath('/Users/zach/Downloads/PortalSDK/FbExportData/levels')
    """
    return get_project_root() / DIR_FB_EXPORT_LEVELS


def get_asset_types_path() -> Path:
    """Get asset_types.json file path.

    Returns:
        Absolute path to asset_types.json
    """
    return get_project_root() / FILE_ASSET_TYPES


def get_level_tscn_path(map_name: str) -> Path:
    """Get .tscn file path for a map.

    Args:
        map_name: Map name (e.g., "Kursk")

    Returns:
        Absolute path to map's .tscn file

    Example:
        >>> get_level_tscn_path("Kursk")
        PosixPath('/Users/zach/Downloads/PortalSDK/GodotProject/levels/Kursk.tscn')
    """
    return get_project_root() / DIR_GODOT_LEVELS / f"{map_name}.tscn"


def get_spatial_json_path(map_name: str) -> Path:
    """Get .spatial.json file path for a map.

    Args:
        map_name: Map name (e.g., "Kursk")

    Returns:
        Absolute path to map's .spatial.json file

    Example:
        >>> get_spatial_json_path("Kursk")
        PosixPath('/Users/zach/Downloads/PortalSDK/FbExportData/levels/Kursk.spatial.json')
    """
    return get_project_root() / DIR_FB_EXPORT_LEVELS / f"{map_name}.spatial.json"


def get_bf1942_level_path(map_name: str, expansion: str = "base") -> Path:
    """Get extracted BF1942 level directory path.

    Args:
        map_name: Map name (e.g., "Kursk")
        expansion: Expansion pack ("base", "xpack1", "xpack2")

    Returns:
        Absolute path to extracted level directory

    Example:
        >>> get_bf1942_level_path("Kursk")
        PosixPath('/Users/zach/Downloads/PortalSDK/bf1942_source/extracted/Bf1942/Archives/bf1942/Levels/Kursk')
    """
    expansion_dirs = {
        "base": DIR_BF1942_EXTRACTED_BASE,
        "xpack1": DIR_BF1942_EXTRACTED_XPACK1,
        "xpack2": DIR_BF1942_EXTRACTED_XPACK2,
    }

    base_dir = expansion_dirs.get(expansion, DIR_BF1942_EXTRACTED_BASE)
    return get_project_root() / base_dir / map_name


def get_terrain_glb_path(terrain_name: str) -> Path:
    """Get terrain .glb file path.

    Args:
        terrain_name: Terrain name (e.g., "MP_Tungsten_Terrain")

    Returns:
        Absolute path to terrain .glb file

    Example:
        >>> get_terrain_glb_path("MP_Tungsten_Terrain")
        PosixPath('/Users/zach/Downloads/PortalSDK/GodotProject/raw/models/MP_Tungsten_Terrain.glb')
    """
    return get_project_root() / DIR_GODOT_RAW_MODELS / f"{terrain_name}.glb"


def get_mappings_file() -> Path:
    """Get bf1942_to_portal_mappings.json file path.

    Returns:
        Absolute path to bf1942_to_portal_mappings.json

    Example:
        >>> get_mappings_file()
        PosixPath('/Users/zach/Downloads/PortalSDK/tools/asset_audit/bf1942_to_portal_mappings.json')
    """
    return get_project_root() / "tools" / "asset_audit" / "bf1942_to_portal_mappings.json"
