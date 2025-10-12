#!/usr/bin/env python3
"""Tests for portal_convert.py CLI script."""

import sys
from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bfportal.core.exceptions import BFPortalError
from portal_convert import PortalConverter, main


def _create_mock_converter(args: Namespace, tmp_path: Path | None = None):
    """Helper to create PortalConverter with mocked dependencies."""
    mock_terrain = MagicMock()
    mock_terrain.vertices = [1, 2, 3]
    mock_terrain.min_height = 0.0
    mock_terrain.max_height = 100.0
    mock_terrain.mesh_min_x = -1024.0
    mock_terrain.mesh_max_x = 1024.0
    mock_terrain.mesh_min_z = -1024.0
    mock_terrain.mesh_max_z = 1024.0
    mock_terrain.mesh_center_x = 0.0
    mock_terrain.mesh_center_z = 0.0
    mock_terrain.grid_resolution = 256

    mock_asset_mapper = MagicMock()
    mock_asset_mapper.load_mappings = MagicMock()

    with patch("portal_convert.BF1942Engine"):
        with patch("portal_convert.AssetMapper", return_value=mock_asset_mapper):
            with patch("portal_convert.MeshTerrainProvider", return_value=mock_terrain):
                with patch("portal_convert.CoordinateOffset"):
                    with patch("portal_convert.HeightAdjuster"):
                        with patch.object(Path, "exists", return_value=True):
                            converter = PortalConverter(args)
                            if tmp_path:
                                converter.project_root = tmp_path
                            return converter


class TestPortalConverterInit:
    """Tests for PortalConverter.__init__() initialization."""

    def test_initializes_converter_successfully(self, tmp_path: Path):
        """Test successful converter initialization with valid paths."""
        # Arrange
        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
        )
        mock_terrain = MagicMock()
        mock_terrain.vertices = [1, 2, 3]
        mock_terrain.min_height = 0.0
        mock_terrain.max_height = 100.0
        mock_terrain.mesh_min_x = -1024.0
        mock_terrain.mesh_max_x = 1024.0
        mock_terrain.mesh_min_z = -1024.0
        mock_terrain.mesh_max_z = 1024.0
        mock_terrain.mesh_center_x = 0.0
        mock_terrain.mesh_center_z = 0.0
        mock_terrain.grid_resolution = 256

        mock_asset_mapper = MagicMock()
        mock_asset_mapper.load_mappings = MagicMock()

        # Act
        with patch("portal_convert.BF1942Engine"):
            with patch("portal_convert.AssetMapper", return_value=mock_asset_mapper):
                with patch("portal_convert.MeshTerrainProvider", return_value=mock_terrain):
                    with patch("portal_convert.CoordinateOffset"):
                        with patch("portal_convert.HeightAdjuster"):
                            with patch.object(Path, "exists", return_value=True):
                                converter = PortalConverter(args)

        # Assert
        assert converter.args == args
        assert converter.engine is not None
        assert converter.asset_mapper is not None
        assert converter.coord_offset is not None

    def test_raises_error_when_terrain_mesh_missing(self, tmp_path: Path):
        """Test error raised when Portal terrain mesh doesn't exist."""
        # Arrange
        args = Namespace(
            map="Kursk",
            base_terrain="MP_NonExistent",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
        )

        # Act & Assert
        with patch("portal_convert.BF1942Engine"):
            with patch("portal_convert.AssetMapper"):
                with patch("portal_convert.CoordinateOffset"):
                    with patch.object(Path, "exists", return_value=False):
                        with pytest.raises(BFPortalError, match="Portal terrain mesh not found"):
                            PortalConverter(args)


class TestResolveMapPath:
    """Tests for PortalConverter._resolve_map_path() method."""

    def test_resolves_default_bf1942_path(self, tmp_path: Path):
        """Test resolving map path with default BF1942 root."""
        # Arrange
        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
        )
        expected_path = (
            tmp_path
            / "bf1942_source"
            / "extracted"
            / "Bf1942"
            / "Archives"
            / "bf1942"
            / "Levels"
            / "Kursk"
        )
        expected_path.mkdir(parents=True)
        converter = _create_mock_converter(args, tmp_path)

        # Act
        result = converter._resolve_map_path()

        # Assert
        assert result == expected_path

    def test_resolves_custom_bf1942_path(self, tmp_path: Path):
        """Test resolving map path with custom BF1942 root."""
        # Arrange
        custom_root = tmp_path / "custom_bf1942"
        custom_root.mkdir()
        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=str(custom_root),
            output=None,
        )
        expected_path = custom_root / "Kursk"
        expected_path.mkdir()
        converter = _create_mock_converter(args, tmp_path)

        # Act
        result = converter._resolve_map_path()

        # Assert
        assert result == expected_path

    def test_raises_error_when_map_directory_missing(self, tmp_path: Path):
        """Test error raised when map directory doesn't exist."""
        # Arrange
        args = Namespace(
            map="NonExistentMap",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
        )
        converter = _create_mock_converter(args, tmp_path)

        # Act & Assert
        with pytest.raises(BFPortalError, match="Map directory not found"):
            converter._resolve_map_path()


class TestResolveOutputPath:
    """Tests for PortalConverter._resolve_output_path() method."""

    def test_resolves_default_output_path(self, tmp_path: Path):
        """Test resolving output path with default location."""
        # Arrange
        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
        )
        converter = _create_mock_converter(args, tmp_path)

        # Act
        result = converter._resolve_output_path()

        # Assert
        expected = tmp_path / "GodotProject" / "levels" / "Kursk.tscn"
        assert result == expected

    def test_resolves_custom_output_path(self, tmp_path: Path):
        """Test resolving output path with custom location."""
        # Arrange
        custom_output = tmp_path / "custom" / "output.tscn"
        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=str(custom_output),
        )
        converter = _create_mock_converter(args, tmp_path)

        # Act
        result = converter._resolve_output_path()

        # Assert
        assert result == custom_output


class TestGuessTheme:
    """Tests for PortalConverter._guess_theme() method."""

    def test_guesses_desert_theme_from_map_name(self, tmp_path: Path):
        """Test guessing desert theme from map name."""
        # Arrange
        args = Namespace(
            map="El_Alamein",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
        )
        converter = _create_mock_converter(args, tmp_path)

        # Act
        result = converter._guess_theme()

        # Assert
        assert result == "desert"

    def test_guesses_urban_theme_from_map_name(self, tmp_path: Path):
        """Test guessing urban theme from map name."""
        # Arrange
        args = Namespace(
            map="Berlin",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
        )
        converter = _create_mock_converter(args, tmp_path)

        # Act
        result = converter._guess_theme()

        # Assert
        assert result == "urban"

    def test_defaults_to_temperate_theme(self, tmp_path: Path):
        """Test defaulting to temperate theme for unknown map."""
        # Arrange
        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
        )
        converter = _create_mock_converter(args, tmp_path)

        # Act
        result = converter._guess_theme()

        # Assert
        assert result == "temperate"


class TestMainFunction:
    """Tests for main() CLI entry point."""

    def test_returns_success_when_conversion_completes(self):
        """Test main returns success code when conversion completes."""
        # Arrange
        test_args = [
            "portal_convert.py",
            "--map",
            "Kursk",
            "--base-terrain",
            "MP_Tungsten",
        ]

        # Act & Assert
        with patch("sys.argv", test_args):
            with patch("portal_convert.PortalConverter") as mock_converter_class:
                mock_converter = MagicMock(spec=["convert"])
                mock_converter.convert.return_value = 0
                mock_converter_class.return_value = mock_converter
                with pytest.raises(SystemExit) as exc_info:
                    main()

                assert exc_info.value.code == 0

    def test_returns_error_when_conversion_fails(self):
        """Test main returns error code when conversion fails."""
        # Arrange
        test_args = [
            "portal_convert.py",
            "--map",
            "Kursk",
            "--base-terrain",
            "MP_Tungsten",
        ]

        # Act & Assert
        with patch("sys.argv", test_args):
            with patch("portal_convert.PortalConverter") as mock_converter_class:
                mock_converter = MagicMock(spec=["convert"])
                mock_converter.convert.return_value = 1
                mock_converter_class.return_value = mock_converter
                with pytest.raises(SystemExit) as exc_info:
                    main()

                assert exc_info.value.code == 1
