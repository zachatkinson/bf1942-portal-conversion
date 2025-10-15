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

    mock_asset_mapper = MagicMock()
    mock_asset_mapper.load_mappings = MagicMock()

    with (
        patch("portal_convert.BF1942Engine"),
        patch("portal_convert.AssetMapper", return_value=mock_asset_mapper),
        patch("portal_convert.MeshTerrainProvider", return_value=mock_terrain),
        patch("portal_convert.CoordinateOffset"),
        patch("portal_convert.HeightAdjuster"),
        patch.object(Path, "exists", return_value=True),
    ):
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
            rotate_terrain=False,
        )
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

        mock_asset_mapper = MagicMock()
        mock_asset_mapper.load_mappings = MagicMock()

        # Act
        with (
            patch("portal_convert.BF1942Engine"),
            patch("portal_convert.AssetMapper", return_value=mock_asset_mapper),
            patch("portal_convert.MeshTerrainProvider", return_value=mock_terrain),
            patch("portal_convert.CoordinateOffset"),
            patch("portal_convert.HeightAdjuster"),
            patch.object(Path, "exists", return_value=True),
        ):
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
            rotate_terrain=False,
        )

        # Act & Assert
        with (
            patch("portal_convert.BF1942Engine"),
            patch("portal_convert.AssetMapper"),
            patch("portal_convert.CoordinateOffset"),
            patch.object(Path, "exists", return_value=False),
            pytest.raises(BFPortalError, match="Portal terrain mesh not found"),
        ):
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
            rotate_terrain=False,
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
            rotate_terrain=False,
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
            rotate_terrain=False,
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
            rotate_terrain=False,
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
            rotate_terrain=False,
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
            rotate_terrain=False,
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
            rotate_terrain=False,
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
            rotate_terrain=False,
        )
        converter = _create_mock_converter(args, tmp_path)

        # Act
        result = converter._guess_theme()

        # Assert
        assert result == "temperate"


class TestGetTargetCenter:
    """Tests for PortalConverter._get_target_center() method."""

    def test_returns_terrain_mesh_center(self, tmp_path: Path):
        """Test returns Portal terrain's mesh center coordinates.

        The implementation returns the terrain's mesh center (mesh_center_x, 0, mesh_center_z)
        where BF1942 assets will be centered. This keeps the Portal terrain at (0,0,0) in Godot
        while centering the assets on the terrain's geometric center.
        """
        # Arrange
        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
            rotate_terrain=False,
        )
        converter = _create_mock_converter(args, tmp_path)
        converter.terrain.mesh_center_x = 512.0
        converter.terrain.mesh_center_z = -256.0

        # Act
        result = converter._get_target_center()

        # Assert - Expects terrain mesh center coordinates
        assert result.x == 512.0
        assert result.y == 0.0
        assert result.z == -256.0


class TestGuessThemeTropical:
    """Tests for PortalConverter._guess_theme() tropical detection."""

    def test_guesses_tropical_theme_from_map_name(self, tmp_path: Path):
        """Test guessing tropical theme from map name."""
        # Arrange
        args = Namespace(
            map="Wake_Island",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
            rotate_terrain=False,
        )
        converter = _create_mock_converter(args, tmp_path)

        # Act
        result = converter._guess_theme()

        # Assert
        assert result == "tropical"


class TestConvertMethod:
    """Tests for PortalConverter.convert() method."""

    def test_convert_succeeds_with_valid_map_data(self, tmp_path: Path):
        """Test successful conversion with valid map data."""
        # Arrange
        from bfportal.core.interfaces import (
            GameObject,
            MapData,
            SpawnPoint,
            Team,
            Transform,
            Vector3,
        )

        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
            rotate_terrain=False,
        )

        # Create mock map data
        from bfportal.core.interfaces import MapBounds, Rotation

        mock_map_data = MapData(
            map_name="Kursk",
            game_mode="Conquest",
            team1_hq=Transform(position=Vector3(100, 0, 100), rotation=Rotation(0, 0, 0)),
            team2_hq=Transform(position=Vector3(-100, 0, -100), rotation=Rotation(0, 0, 0)),
            team1_spawns=[
                SpawnPoint(
                    name="spawn1",
                    team=Team.TEAM_1,
                    transform=Transform(position=Vector3(90, 0, 90), rotation=Rotation(0, 0, 0)),
                )
            ],
            team2_spawns=[
                SpawnPoint(
                    name="spawn2",
                    team=Team.TEAM_2,
                    transform=Transform(position=Vector3(-90, 0, -90), rotation=Rotation(0, 0, 0)),
                )
            ],
            game_objects=[
                GameObject(
                    name="obj1",
                    asset_type="StaticObject",
                    transform=Transform(position=Vector3(50, 0, 50), rotation=Rotation(0, 0, 0)),
                    team=Team.NEUTRAL,
                    properties={},
                )
            ],
            capture_points=[],
            bounds=MapBounds(
                min_point=Vector3(-512, 0, -512),
                max_point=Vector3(512, 100, 512),
                combat_area_polygon=[
                    Vector3(-512, 0, -512),
                    Vector3(512, 0, -512),
                    Vector3(512, 0, 512),
                    Vector3(-512, 0, 512),
                ],
                height=100.0,
            ),
            metadata={},
        )

        map_path = (
            tmp_path
            / "bf1942_source"
            / "extracted"
            / "Bf1942"
            / "Archives"
            / "bf1942"
            / "Levels"
            / "Kursk"
        )
        map_path.mkdir(parents=True)
        tmp_path / "GodotProject" / "levels" / "Kursk.tscn"

        # Create converter with mocked dependencies
        converter = _create_mock_converter(args, tmp_path)
        converter.engine.parse_map = MagicMock(return_value=mock_map_data)
        converter.asset_mapper.map_asset = MagicMock(return_value=MagicMock(type="PortalAsset"))
        converter.asset_mapper._is_terrain_element = MagicMock(return_value=False)

        # Mock coord_offset methods
        converter.coord_offset.calculate_centroid = MagicMock(return_value=Vector3(0, 0, 0))
        converter.coord_offset.calculate_offset = MagicMock(return_value=Vector3(0, 0, 0))
        converter.coord_offset.apply_offset = MagicMock(
            side_effect=lambda transform, offset: transform
        )

        # Mock height_adjuster methods
        converter.height_adjuster.adjust_height = MagicMock(
            side_effect=lambda transform, terrain, ground_offset: transform
        )

        # Mock orientation detection
        mock_source_analysis = MagicMock()
        mock_source_analysis.orientation.value = "horizontal"
        mock_source_analysis.width_x = 1024.0
        mock_source_analysis.depth_z = 1024.0
        mock_source_analysis.ratio = 1.0

        mock_dest_analysis = MagicMock()
        mock_dest_analysis.orientation.value = "horizontal"
        mock_dest_analysis.width_x = 2048.0
        mock_dest_analysis.depth_z = 2048.0

        mock_rotation_result = MagicMock()
        mock_rotation_result.rotation_needed = False
        mock_rotation_result.rotation_degrees = 0

        with (
            patch("portal_convert.MapOrientationDetector") as mock_map_detector_class,
            patch("portal_convert.TerrainOrientationDetector") as mock_terrain_detector_class,
            patch("portal_convert.OrientationMatcher") as mock_matcher_class,
            patch("portal_convert.TscnGenerator") as mock_generator_class,
        ):
            mock_map_detector = MagicMock()
            mock_map_detector.detect_orientation.return_value = mock_source_analysis
            mock_map_detector_class.return_value = mock_map_detector

            mock_terrain_detector = MagicMock()
            mock_terrain_detector.detect_orientation.return_value = mock_dest_analysis
            mock_terrain_detector_class.return_value = mock_terrain_detector

            mock_matcher = MagicMock()
            mock_matcher.match.return_value = mock_rotation_result
            mock_matcher_class.return_value = mock_matcher

            mock_generator = MagicMock()
            mock_generator_class.return_value = mock_generator

            # Act
            result = converter.convert()

        # Assert
        assert result == 0
        converter.engine.parse_map.assert_called_once()
        mock_generator.generate.assert_called_once()

    def test_convert_handles_empty_map_data(self, tmp_path: Path):
        """Test conversion with empty map data (no objects)."""
        # Arrange
        from bfportal.core.interfaces import MapBounds, MapData, Rotation, Transform, Vector3

        args = Namespace(
            map="EmptyMap",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
            rotate_terrain=False,
        )

        mock_map_data = MapData(
            map_name="EmptyMap",
            game_mode="Conquest",
            team1_hq=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
            team2_hq=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
            team1_spawns=[],
            team2_spawns=[],
            game_objects=[],
            capture_points=[],
            bounds=MapBounds(
                min_point=Vector3(-100, 0, -100),
                max_point=Vector3(100, 50, 100),
                combat_area_polygon=[
                    Vector3(-100, 0, -100),
                    Vector3(100, 0, -100),
                    Vector3(100, 0, 100),
                    Vector3(-100, 0, 100),
                ],
                height=50.0,
            ),
            metadata={},
        )

        map_path = (
            tmp_path
            / "bf1942_source"
            / "extracted"
            / "Bf1942"
            / "Archives"
            / "bf1942"
            / "Levels"
            / "EmptyMap"
        )
        map_path.mkdir(parents=True)

        converter = _create_mock_converter(args, tmp_path)
        converter.engine.parse_map = MagicMock(return_value=mock_map_data)

        mock_source_analysis = MagicMock()
        mock_source_analysis.orientation.value = "horizontal"
        mock_source_analysis.width_x = 100.0
        mock_source_analysis.depth_z = 100.0
        mock_source_analysis.ratio = 1.0

        mock_dest_analysis = MagicMock()
        mock_dest_analysis.orientation.value = "horizontal"
        mock_dest_analysis.width_x = 2048.0
        mock_dest_analysis.depth_z = 2048.0

        mock_rotation_result = MagicMock()
        mock_rotation_result.rotation_needed = False

        with (
            patch("portal_convert.MapOrientationDetector") as mock_map_detector_class,
            patch("portal_convert.TerrainOrientationDetector") as mock_terrain_detector_class,
            patch("portal_convert.OrientationMatcher") as mock_matcher_class,
            patch("portal_convert.TscnGenerator") as mock_generator_class,
        ):
            mock_map_detector_class.return_value.detect_orientation.return_value = (
                mock_source_analysis
            )
            mock_terrain_detector_class.return_value.detect_orientation.return_value = (
                mock_dest_analysis
            )
            mock_matcher_class.return_value.match.return_value = mock_rotation_result
            mock_generator_class.return_value = MagicMock()

            # Act
            result = converter.convert()

        # Assert
        assert result == 0

    def test_convert_returns_error_on_bfportal_exception(self, tmp_path: Path):
        """Test convert returns error code on BFPortalError."""
        # Arrange
        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
            rotate_terrain=False,
        )

        map_path = (
            tmp_path
            / "bf1942_source"
            / "extracted"
            / "Bf1942"
            / "Archives"
            / "bf1942"
            / "Levels"
            / "Kursk"
        )
        map_path.mkdir(parents=True)

        converter = _create_mock_converter(args, tmp_path)
        converter.engine.parse_map = MagicMock(side_effect=BFPortalError("Parse failed"))

        # Act
        result = converter.convert()

        # Assert
        assert result == 1

    def test_convert_returns_error_on_unexpected_exception(self, tmp_path: Path):
        """Test convert returns error code on unexpected exception."""
        # Arrange
        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
            rotate_terrain=False,
        )

        map_path = (
            tmp_path
            / "bf1942_source"
            / "extracted"
            / "Bf1942"
            / "Archives"
            / "bf1942"
            / "Levels"
            / "Kursk"
        )
        map_path.mkdir(parents=True)

        converter = _create_mock_converter(args, tmp_path)
        converter.engine.parse_map = MagicMock(side_effect=RuntimeError("Unexpected error"))

        # Act
        result = converter.convert()

        # Assert
        assert result == 1


class TestConvertWithCapturePoints:
    """Tests for conversion with capture points containing spawns."""

    def test_convert_offsets_capture_point_spawns_avoiding_duplicates(self, tmp_path: Path):
        """Test conversion offsets capture point spawns and avoids duplicates."""
        # Arrange
        from bfportal.core.interfaces import (
            CapturePoint,
            MapBounds,
            MapData,
            Rotation,
            SpawnPoint,
            Team,
            Transform,
            Vector3,
        )

        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
            rotate_terrain=False,
        )

        spawn1 = SpawnPoint(
            name="cp_spawn1",
            team=Team.TEAM_1,
            transform=Transform(position=Vector3(50, 0, 50), rotation=Rotation(0, 0, 0)),
        )
        spawn2 = SpawnPoint(
            name="cp_spawn2",
            team=Team.TEAM_2,
            transform=Transform(position=Vector3(55, 0, 55), rotation=Rotation(0, 0, 0)),
        )

        cp1 = CapturePoint(
            name="CP1",
            transform=Transform(position=Vector3(50, 0, 50), rotation=Rotation(0, 0, 0)),
            radius=30.0,
            control_area=[
                Vector3(30, 0, 30),
                Vector3(70, 0, 30),
                Vector3(70, 0, 70),
                Vector3(30, 0, 70),
            ],
            team1_spawns=[spawn1],
            team2_spawns=[spawn2],
        )

        mock_map_data = MapData(
            map_name="Kursk",
            game_mode="Conquest",
            team1_hq=Transform(position=Vector3(100, 0, 100), rotation=Rotation(0, 0, 0)),
            team2_hq=Transform(position=Vector3(-100, 0, -100), rotation=Rotation(0, 0, 0)),
            team1_spawns=[],
            team2_spawns=[],
            game_objects=[],
            capture_points=[cp1],
            bounds=MapBounds(
                min_point=Vector3(-512, 0, -512),
                max_point=Vector3(512, 100, 512),
                combat_area_polygon=[
                    Vector3(-512, 0, -512),
                    Vector3(512, 0, -512),
                    Vector3(512, 0, 512),
                    Vector3(-512, 0, 512),
                ],
                height=100.0,
            ),
            metadata={},
        )

        map_path = (
            tmp_path
            / "bf1942_source"
            / "extracted"
            / "Bf1942"
            / "Archives"
            / "bf1942"
            / "Levels"
            / "Kursk"
        )
        map_path.mkdir(parents=True)

        converter = _create_mock_converter(args, tmp_path)
        converter.engine.parse_map = MagicMock(return_value=mock_map_data)

        # Mock coordinate offset methods with proper Vector3 returns
        converter.coord_offset.calculate_centroid = MagicMock(return_value=Vector3(0, 0, 0))
        converter.coord_offset.calculate_offset = MagicMock(return_value=Vector3(10, 0, 10))
        converter.coord_offset.apply_offset = MagicMock(
            side_effect=lambda transform, offset: transform
        )

        # Mock height adjuster
        converter.height_adjuster.adjust_height = MagicMock(
            side_effect=lambda transform, terrain, ground_offset: transform
        )

        mock_source_analysis = MagicMock()
        mock_source_analysis.orientation.value = "horizontal"
        mock_source_analysis.width_x = 1024.0
        mock_source_analysis.depth_z = 1024.0
        mock_source_analysis.ratio = 1.0

        mock_dest_analysis = MagicMock()
        mock_dest_analysis.orientation.value = "horizontal"
        mock_dest_analysis.width_x = 2048.0
        mock_dest_analysis.depth_z = 2048.0

        mock_rotation_result = MagicMock()
        mock_rotation_result.rotation_needed = False

        # Act
        with (
            patch("portal_convert.MapOrientationDetector") as mock_map_detector_class,
            patch("portal_convert.TerrainOrientationDetector") as mock_terrain_detector_class,
            patch("portal_convert.OrientationMatcher") as mock_matcher_class,
            patch("portal_convert.TscnGenerator") as mock_generator_class,
        ):
            mock_map_detector_class.return_value.detect_orientation.return_value = (
                mock_source_analysis
            )
            mock_terrain_detector_class.return_value.detect_orientation.return_value = (
                mock_dest_analysis
            )
            mock_matcher_class.return_value.match.return_value = mock_rotation_result
            mock_generator_class.return_value = MagicMock()

            result = converter.convert()

        # Assert
        assert result == 0


class TestConvertWithRotation:
    """Tests for conversion with terrain rotation needed."""

    def test_convert_applies_terrain_rotation_when_needed(self, tmp_path: Path):
        """Test conversion applies terrain rotation to metadata when needed."""
        # Arrange
        from bfportal.core.interfaces import MapBounds, MapData, Rotation, Transform, Vector3

        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
            rotate_terrain=False,
        )

        mock_map_data = MapData(
            map_name="Kursk",
            game_mode="Conquest",
            team1_hq=Transform(position=Vector3(100, 0, 100), rotation=Rotation(0, 0, 0)),
            team2_hq=Transform(position=Vector3(-100, 0, -100), rotation=Rotation(0, 0, 0)),
            team1_spawns=[],
            team2_spawns=[],
            game_objects=[],
            capture_points=[],
            bounds=MapBounds(
                min_point=Vector3(-512, 0, -512),
                max_point=Vector3(512, 100, 512),
                combat_area_polygon=[
                    Vector3(-512, 0, -512),
                    Vector3(512, 0, -512),
                    Vector3(512, 0, 512),
                    Vector3(-512, 0, 512),
                ],
                height=100.0,
            ),
            metadata={},
        )

        map_path = (
            tmp_path
            / "bf1942_source"
            / "extracted"
            / "Bf1942"
            / "Archives"
            / "bf1942"
            / "Levels"
            / "Kursk"
        )
        map_path.mkdir(parents=True)

        converter = _create_mock_converter(args, tmp_path)
        converter.engine.parse_map = MagicMock(return_value=mock_map_data)

        mock_source_analysis = MagicMock()
        mock_source_analysis.orientation.value = "vertical"
        mock_source_analysis.width_x = 1024.0
        mock_source_analysis.depth_z = 2048.0
        mock_source_analysis.ratio = 0.5

        mock_dest_analysis = MagicMock()
        mock_dest_analysis.orientation.value = "horizontal"
        mock_dest_analysis.width_x = 2048.0
        mock_dest_analysis.depth_z = 1024.0

        mock_rotation_result = MagicMock()
        mock_rotation_result.rotation_needed = True
        mock_rotation_result.rotation_degrees = 90
        mock_rotation_result.reasoning = "Source is vertical, destination is horizontal"

        # Act
        with (
            patch("portal_convert.MapOrientationDetector") as mock_map_detector_class,
            patch("portal_convert.TerrainOrientationDetector") as mock_terrain_detector_class,
            patch("portal_convert.OrientationMatcher") as mock_matcher_class,
            patch("portal_convert.TscnGenerator") as mock_generator_class,
        ):
            mock_map_detector_class.return_value.detect_orientation.return_value = (
                mock_source_analysis
            )
            mock_terrain_detector_class.return_value.detect_orientation.return_value = (
                mock_dest_analysis
            )
            mock_matcher_class.return_value.match.return_value = mock_rotation_result
            mock_generator_class.return_value = MagicMock()

            result = converter.convert()

        # Assert
        assert result == 0
        assert mock_map_data.metadata["terrain_rotation"] == 90


class TestConvertAssetMapping:
    """Tests for asset mapping during conversion."""

    def test_convert_tracks_terrain_elements_separately(self, tmp_path: Path):
        """Test conversion tracks skipped terrain elements separately from unmapped assets."""
        # Arrange
        from bfportal.core.interfaces import (
            GameObject,
            MapBounds,
            MapData,
            Rotation,
            Team,
            Transform,
            Vector3,
        )

        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
            rotate_terrain=False,
        )

        mock_map_data = MapData(
            map_name="Kursk",
            game_mode="Conquest",
            team1_hq=Transform(position=Vector3(100, 0, 100), rotation=Rotation(0, 0, 0)),
            team2_hq=Transform(position=Vector3(-100, 0, -100), rotation=Rotation(0, 0, 0)),
            team1_spawns=[],
            team2_spawns=[],
            game_objects=[
                GameObject(
                    name="water1",
                    asset_type="WaterPlane",
                    transform=Transform(position=Vector3(50, 0, 50), rotation=Rotation(0, 0, 0)),
                    team=Team.NEUTRAL,
                    properties={},
                ),
                GameObject(
                    name="water2",
                    asset_type="WaterPlane",
                    transform=Transform(position=Vector3(60, 0, 60), rotation=Rotation(0, 0, 0)),
                    team=Team.NEUTRAL,
                    properties={},
                ),
            ],
            capture_points=[],
            bounds=MapBounds(
                min_point=Vector3(-512, 0, -512),
                max_point=Vector3(512, 100, 512),
                combat_area_polygon=[
                    Vector3(-512, 0, -512),
                    Vector3(512, 0, -512),
                    Vector3(512, 0, 512),
                    Vector3(-512, 0, 512),
                ],
                height=100.0,
            ),
            metadata={},
        )

        map_path = (
            tmp_path
            / "bf1942_source"
            / "extracted"
            / "Bf1942"
            / "Archives"
            / "bf1942"
            / "Levels"
            / "Kursk"
        )
        map_path.mkdir(parents=True)

        converter = _create_mock_converter(args, tmp_path)
        converter.engine.parse_map = MagicMock(return_value=mock_map_data)
        converter.asset_mapper.map_asset = MagicMock(return_value=None)
        converter.asset_mapper._is_terrain_element = MagicMock(return_value=True)

        # Mock coordinate offset methods with proper Vector3 returns
        converter.coord_offset.calculate_centroid = MagicMock(return_value=Vector3(0, 0, 0))
        converter.coord_offset.calculate_offset = MagicMock(return_value=Vector3(10, 0, 10))
        converter.coord_offset.apply_offset = MagicMock(
            side_effect=lambda transform, offset: transform
        )

        # Mock height adjuster
        converter.height_adjuster.adjust_height = MagicMock(
            side_effect=lambda transform, terrain, ground_offset: transform
        )

        mock_source_analysis = MagicMock()
        mock_source_analysis.orientation.value = "horizontal"
        mock_source_analysis.width_x = 1024.0
        mock_source_analysis.depth_z = 1024.0
        mock_source_analysis.ratio = 1.0

        mock_dest_analysis = MagicMock()
        mock_dest_analysis.orientation.value = "horizontal"
        mock_dest_analysis.width_x = 2048.0
        mock_dest_analysis.depth_z = 2048.0

        mock_rotation_result = MagicMock()
        mock_rotation_result.rotation_needed = False

        # Act
        with (
            patch("portal_convert.MapOrientationDetector") as mock_map_detector_class,
            patch("portal_convert.TerrainOrientationDetector") as mock_terrain_detector_class,
            patch("portal_convert.OrientationMatcher") as mock_matcher_class,
            patch("portal_convert.TscnGenerator") as mock_generator_class,
        ):
            mock_map_detector_class.return_value.detect_orientation.return_value = (
                mock_source_analysis
            )
            mock_terrain_detector_class.return_value.detect_orientation.return_value = (
                mock_dest_analysis
            )
            mock_matcher_class.return_value.match.return_value = mock_rotation_result
            mock_generator_class.return_value = MagicMock()

            result = converter.convert()

        # Assert
        assert result == 0

    def test_convert_handles_unmapped_assets_gracefully(self, tmp_path: Path):
        """Test conversion handles unmapped assets gracefully."""
        # Arrange
        from bfportal.core.interfaces import (
            GameObject,
            MapBounds,
            MapData,
            Rotation,
            Team,
            Transform,
            Vector3,
        )

        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
            rotate_terrain=False,
        )

        mock_map_data = MapData(
            map_name="Kursk",
            game_mode="Conquest",
            team1_hq=Transform(position=Vector3(100, 0, 100), rotation=Rotation(0, 0, 0)),
            team2_hq=Transform(position=Vector3(-100, 0, -100), rotation=Rotation(0, 0, 0)),
            team1_spawns=[],
            team2_spawns=[],
            game_objects=[
                GameObject(
                    name="unknown1",
                    asset_type="UnknownAsset",
                    transform=Transform(position=Vector3(50, 0, 50), rotation=Rotation(0, 0, 0)),
                    team=Team.NEUTRAL,
                    properties={},
                ),
            ],
            capture_points=[],
            bounds=MapBounds(
                min_point=Vector3(-512, 0, -512),
                max_point=Vector3(512, 100, 512),
                combat_area_polygon=[
                    Vector3(-512, 0, -512),
                    Vector3(512, 0, -512),
                    Vector3(512, 0, 512),
                    Vector3(-512, 0, 512),
                ],
                height=100.0,
            ),
            metadata={},
        )

        map_path = (
            tmp_path
            / "bf1942_source"
            / "extracted"
            / "Bf1942"
            / "Archives"
            / "bf1942"
            / "Levels"
            / "Kursk"
        )
        map_path.mkdir(parents=True)

        converter = _create_mock_converter(args, tmp_path)
        converter.engine.parse_map = MagicMock(return_value=mock_map_data)
        converter.asset_mapper.map_asset = MagicMock(return_value=None)
        converter.asset_mapper._is_terrain_element = MagicMock(return_value=False)

        # Mock coordinate offset methods with proper Vector3 returns
        converter.coord_offset.calculate_centroid = MagicMock(return_value=Vector3(0, 0, 0))
        converter.coord_offset.calculate_offset = MagicMock(return_value=Vector3(10, 0, 10))
        converter.coord_offset.apply_offset = MagicMock(
            side_effect=lambda transform, offset: transform
        )

        # Mock height adjuster
        converter.height_adjuster.adjust_height = MagicMock(
            side_effect=lambda transform, terrain, ground_offset: transform
        )

        mock_source_analysis = MagicMock()
        mock_source_analysis.orientation.value = "horizontal"
        mock_source_analysis.width_x = 1024.0
        mock_source_analysis.depth_z = 1024.0
        mock_source_analysis.ratio = 1.0

        mock_dest_analysis = MagicMock()
        mock_dest_analysis.orientation.value = "horizontal"
        mock_dest_analysis.width_x = 2048.0
        mock_dest_analysis.depth_z = 2048.0

        mock_rotation_result = MagicMock()
        mock_rotation_result.rotation_needed = False

        # Act
        with (
            patch("portal_convert.MapOrientationDetector") as mock_map_detector_class,
            patch("portal_convert.TerrainOrientationDetector") as mock_terrain_detector_class,
            patch("portal_convert.OrientationMatcher") as mock_matcher_class,
            patch("portal_convert.TscnGenerator") as mock_generator_class,
        ):
            mock_map_detector_class.return_value.detect_orientation.return_value = (
                mock_source_analysis
            )
            mock_terrain_detector_class.return_value.detect_orientation.return_value = (
                mock_dest_analysis
            )
            mock_matcher_class.return_value.match.return_value = mock_rotation_result
            mock_generator_class.return_value = MagicMock()

            result = converter.convert()

        # Assert
        assert result == 0

    def test_convert_handles_asset_mapping_exception(self, tmp_path: Path):
        """Test conversion handles exception during asset mapping."""
        # Arrange
        from bfportal.core.interfaces import (
            GameObject,
            MapBounds,
            MapData,
            Rotation,
            Team,
            Transform,
            Vector3,
        )

        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
            rotate_terrain=False,
        )

        mock_map_data = MapData(
            map_name="Kursk",
            game_mode="Conquest",
            team1_hq=Transform(position=Vector3(100, 0, 100), rotation=Rotation(0, 0, 0)),
            team2_hq=Transform(position=Vector3(-100, 0, -100), rotation=Rotation(0, 0, 0)),
            team1_spawns=[],
            team2_spawns=[],
            game_objects=[
                GameObject(
                    name="broken",
                    asset_type="BrokenAsset",
                    transform=Transform(position=Vector3(50, 0, 50), rotation=Rotation(0, 0, 0)),
                    team=Team.NEUTRAL,
                    properties={},
                ),
            ],
            capture_points=[],
            bounds=MapBounds(
                min_point=Vector3(-512, 0, -512),
                max_point=Vector3(512, 100, 512),
                combat_area_polygon=[
                    Vector3(-512, 0, -512),
                    Vector3(512, 0, -512),
                    Vector3(512, 0, 512),
                    Vector3(-512, 0, 512),
                ],
                height=100.0,
            ),
            metadata={},
        )

        map_path = (
            tmp_path
            / "bf1942_source"
            / "extracted"
            / "Bf1942"
            / "Archives"
            / "bf1942"
            / "Levels"
            / "Kursk"
        )
        map_path.mkdir(parents=True)

        converter = _create_mock_converter(args, tmp_path)
        converter.engine.parse_map = MagicMock(return_value=mock_map_data)
        converter.asset_mapper.map_asset = MagicMock(side_effect=Exception("Mapping error"))

        # Mock coordinate offset methods with proper Vector3 returns
        converter.coord_offset.calculate_centroid = MagicMock(return_value=Vector3(0, 0, 0))
        converter.coord_offset.calculate_offset = MagicMock(return_value=Vector3(10, 0, 10))
        converter.coord_offset.apply_offset = MagicMock(
            side_effect=lambda transform, offset: transform
        )

        # Mock height adjuster
        converter.height_adjuster.adjust_height = MagicMock(
            side_effect=lambda transform, terrain, ground_offset: transform
        )

        mock_source_analysis = MagicMock()
        mock_source_analysis.orientation.value = "horizontal"
        mock_source_analysis.width_x = 1024.0
        mock_source_analysis.depth_z = 1024.0
        mock_source_analysis.ratio = 1.0

        mock_dest_analysis = MagicMock()
        mock_dest_analysis.orientation.value = "horizontal"
        mock_dest_analysis.width_x = 2048.0
        mock_dest_analysis.depth_z = 2048.0

        mock_rotation_result = MagicMock()
        mock_rotation_result.rotation_needed = False

        # Act
        with (
            patch("portal_convert.MapOrientationDetector") as mock_map_detector_class,
            patch("portal_convert.TerrainOrientationDetector") as mock_terrain_detector_class,
            patch("portal_convert.OrientationMatcher") as mock_matcher_class,
            patch("portal_convert.TscnGenerator") as mock_generator_class,
        ):
            mock_map_detector_class.return_value.detect_orientation.return_value = (
                mock_source_analysis
            )
            mock_terrain_detector_class.return_value.detect_orientation.return_value = (
                mock_dest_analysis
            )
            mock_matcher_class.return_value.match.return_value = mock_rotation_result
            mock_generator_class.return_value = MagicMock()

            result = converter.convert()

        # Assert
        assert result == 0


class TestGenerateTscn:
    """Tests for _generate_tscn() method."""

    def test_generate_tscn_creates_output_directory(self, tmp_path: Path):
        """Test _generate_tscn creates output directory if it doesn't exist."""
        # Arrange
        from bfportal.core.interfaces import MapBounds, MapData, Rotation, Transform, Vector3

        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
            rotate_terrain=False,
        )

        mock_map_data = MapData(
            map_name="Kursk",
            game_mode="Conquest",
            team1_hq=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
            team2_hq=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
            team1_spawns=[],
            team2_spawns=[],
            game_objects=[],
            capture_points=[],
            bounds=MapBounds(
                min_point=Vector3(-100, 0, -100),
                max_point=Vector3(100, 50, 100),
                combat_area_polygon=[],
                height=50.0,
            ),
            metadata={},
        )

        converter = _create_mock_converter(args, tmp_path)
        output_path = tmp_path / "new_dir" / "output.tscn"

        # Act
        with patch("portal_convert.TscnGenerator") as mock_generator_class:
            mock_generator = MagicMock()
            mock_generator_class.return_value = mock_generator

            converter._generate_tscn(mock_map_data, output_path)

        # Assert
        assert output_path.parent.exists()

    def test_generate_tscn_falls_back_on_generator_exception(self, tmp_path: Path):
        """Test _generate_tscn falls back to basic stub when generator raises exception."""
        # Arrange
        from bfportal.core.interfaces import MapBounds, MapData, Rotation, Transform, Vector3

        args = Namespace(
            map="Kursk",
            base_terrain="MP_Tungsten",
            terrain_size=2048.0,
            bf1942_root=None,
            output=None,
            rotate_terrain=False,
        )

        mock_map_data = MapData(
            map_name="Kursk",
            game_mode="Conquest",
            team1_hq=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
            team2_hq=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
            team1_spawns=[],
            team2_spawns=[],
            game_objects=[],
            capture_points=[],
            bounds=MapBounds(
                min_point=Vector3(-100, 0, -100),
                max_point=Vector3(100, 50, 100),
                combat_area_polygon=[],
                height=50.0,
            ),
            metadata={},
        )

        converter = _create_mock_converter(args, tmp_path)
        output_path = tmp_path / "output.tscn"

        # Act
        with patch("portal_convert.TscnGenerator") as mock_generator_class:
            mock_generator = MagicMock()
            mock_generator.generate.side_effect = Exception("Generator failed")
            mock_generator_class.return_value = mock_generator

            converter._generate_tscn(mock_map_data, output_path)

        # Assert
        assert output_path.exists()
        content = output_path.read_text()
        assert "[gd_scene format=3]" in content
        assert f'[node name="{mock_map_data.map_name}" type="Node3D"]' in content


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
        with (
            patch("sys.argv", test_args),
            patch("portal_convert.PortalConverter") as mock_converter_class,
        ):
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
        with (
            patch("sys.argv", test_args),
            patch("portal_convert.PortalConverter") as mock_converter_class,
        ):
            mock_converter = MagicMock(spec=["convert"])
            mock_converter.convert.return_value = 1
            mock_converter_class.return_value = mock_converter
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
