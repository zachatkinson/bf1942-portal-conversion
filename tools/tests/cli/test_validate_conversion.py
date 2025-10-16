#!/usr/bin/env python3
"""Tests for validate_conversion.py CLI script."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from validate_conversion import ConversionValidator, main

# Fixtures


@pytest.fixture
def mock_bf1942_engine():
    """Create a mock BF1942Engine."""
    mock_engine = Mock(spec=["parse_map"])
    mock_engine.parse_map.return_value = Mock(
        metadata={"source_path": "/test/source"},
        team1_spawns=[],
        team2_spawns=[],
        capture_points=[],
        objects=[],
    )
    return mock_engine


@pytest.fixture
def mock_terrain_provider():
    """Create a mock CustomHeightmapProvider."""
    mock_provider = Mock(spec=["get_height_at"])
    mock_provider.get_height_at.return_value = 100.0
    return mock_provider


@pytest.fixture
def mock_validation_orchestrator():
    """Create a mock ValidationOrchestrator."""
    mock_orchestrator = Mock(spec=["validate"])
    mock_orchestrator.validate.return_value = (True, [])
    return mock_orchestrator


@pytest.fixture
def sample_source_path(tmp_path: Path) -> Path:
    """Create a sample source map directory."""
    source_dir = tmp_path / "bf1942_source" / "extracted" / "Kursk"
    source_dir.mkdir(parents=True)
    (source_dir / "init.con").write_text("game.setGameMode Conquest\n")
    return source_dir


@pytest.fixture
def sample_output_path(tmp_path: Path) -> Path:
    """Create a sample output .tscn file."""
    output_file = tmp_path / "GodotProject" / "levels" / "Kursk.tscn"
    output_file.parent.mkdir(parents=True)
    output_file.write_text('[gd_scene load_steps=7 format=3]\n[node name="Kursk" type="Node3D"]')
    return output_file


@pytest.fixture
def sample_heightmap_path(tmp_path: Path) -> Path:
    """Create a sample heightmap file."""
    from PIL import Image

    heightmap_file = tmp_path / "terrain" / "Kursk_heightmap.png"
    heightmap_file.parent.mkdir(parents=True)

    # Create a valid 256x256 grayscale PNG
    img = Image.new("L", (256, 256), color=128)
    img.save(heightmap_file)

    return heightmap_file


# Tests for ConversionValidator.__init__


class TestConversionValidatorInit:
    """Tests for ConversionValidator.__init__() initialization."""

    def test_initializes_validator_with_required_params(
        self, sample_source_path: Path, sample_output_path: Path
    ):
        """Test successful validator initialization with required parameters."""
        # Arrange
        # (fixtures provide paths)

        # Act
        validator = ConversionValidator(sample_source_path, sample_output_path)

        # Assert
        assert validator.source_map_path == sample_source_path
        assert validator.output_tscn_path == sample_output_path
        assert validator.heightmap_path is None
        assert validator.terrain_size == 2048.0
        assert validator.height_range == (70.0, 220.0)

    def test_initializes_validator_with_heightmap(
        self, sample_source_path: Path, sample_output_path: Path, sample_heightmap_path: Path
    ):
        """Test validator initialization with heightmap."""
        # Arrange
        # (fixtures provide paths)

        # Act
        validator = ConversionValidator(
            sample_source_path, sample_output_path, sample_heightmap_path
        )

        # Assert
        assert validator.heightmap_path == sample_heightmap_path
        assert validator.terrain_provider is not None

    def test_initializes_validator_with_custom_terrain_size(
        self, sample_source_path: Path, sample_output_path: Path
    ):
        """Test validator initialization with custom terrain size."""
        # Arrange
        custom_size = 4096.0

        # Act
        validator = ConversionValidator(
            sample_source_path, sample_output_path, terrain_size=custom_size
        )

        # Assert
        assert validator.terrain_size == custom_size

    def test_initializes_validator_with_custom_height_range(
        self, sample_source_path: Path, sample_output_path: Path
    ):
        """Test validator initialization with custom height range."""
        # Arrange
        custom_range = (50.0, 300.0)

        # Act
        validator = ConversionValidator(
            sample_source_path, sample_output_path, height_range=custom_range
        )

        # Assert
        assert validator.height_range == custom_range

    def test_initializes_terrain_provider_when_heightmap_exists(
        self, sample_source_path: Path, sample_output_path: Path, sample_heightmap_path: Path
    ):
        """Test terrain provider is initialized when heightmap exists."""
        # Arrange
        # (fixtures provide paths with existing heightmap)

        # Act
        validator = ConversionValidator(
            sample_source_path, sample_output_path, sample_heightmap_path
        )

        # Assert
        assert validator.terrain_provider is not None

    def test_no_terrain_provider_when_heightmap_missing(
        self, sample_source_path: Path, sample_output_path: Path, tmp_path: Path
    ):
        """Test terrain provider is None when heightmap doesn't exist."""
        # Arrange
        nonexistent_heightmap = tmp_path / "nonexistent.png"

        # Act
        validator = ConversionValidator(
            sample_source_path, sample_output_path, nonexistent_heightmap
        )

        # Assert
        assert validator.terrain_provider is None


# Tests for ConversionValidator.validate


class TestConversionValidatorValidate:
    """Tests for ConversionValidator.validate() method."""

    def test_validate_returns_success_with_no_issues(
        self, sample_source_path: Path, sample_output_path: Path, capsys
    ):
        """Test validate returns success when no issues found."""
        # Arrange
        validator = ConversionValidator(sample_source_path, sample_output_path)

        with patch.object(validator.engine, "parse_map") as mock_parse:
            mock_parse.return_value = Mock(
                metadata={"source_path": str(sample_source_path)},
                team1_spawns=[],
                team2_spawns=[],
                capture_points=[],
                objects=[],
            )

            with patch("validate_conversion.ValidationOrchestrator") as mock_orchestrator_cls:
                mock_orchestrator_instance = Mock(spec=["validate"])
                mock_orchestrator_instance.validate.return_value = (True, [])
                mock_orchestrator_cls.return_value = mock_orchestrator_instance

                # Act
                is_valid, issues = validator.validate()

        # Assert
        assert is_valid is True
        assert issues == []
        captured = capsys.readouterr()
        assert "Parsing source BF1942 map" in captured.out

    def test_validate_returns_failure_with_issues(
        self, sample_source_path: Path, sample_output_path: Path, capsys
    ):
        """Test validate returns failure when issues found."""
        # Arrange
        validator = ConversionValidator(sample_source_path, sample_output_path)
        mock_issue = Mock(severity="error", message="Test error", category="test")

        with patch.object(validator.engine, "parse_map") as mock_parse:
            mock_parse.return_value = Mock(
                metadata={"source_path": str(sample_source_path)},
                team1_spawns=[],
                team2_spawns=[],
                capture_points=[],
                objects=[],
            )

            with patch("validate_conversion.ValidationOrchestrator") as mock_orchestrator_cls:
                mock_orchestrator_instance = Mock(spec=["validate"])
                mock_orchestrator_instance.validate.return_value = (False, [mock_issue])
                mock_orchestrator_cls.return_value = mock_orchestrator_instance

                # Act
                is_valid, issues = validator.validate()

        # Assert
        assert is_valid is False
        assert len(issues) == 1
        assert issues[0].severity == "error"

    def test_validate_calls_engine_parse_map(
        self, sample_source_path: Path, sample_output_path: Path
    ):
        """Test validate calls engine.parse_map with correct path."""
        # Arrange
        validator = ConversionValidator(sample_source_path, sample_output_path)

        with patch.object(validator.engine, "parse_map") as mock_parse:
            mock_parse.return_value = Mock(
                metadata={"source_path": str(sample_source_path)},
                team1_spawns=[],
                team2_spawns=[],
                capture_points=[],
                objects=[],
            )

            with patch("validate_conversion.ValidationOrchestrator") as mock_orchestrator_cls:
                mock_orchestrator_instance = Mock(spec=["validate"])
                mock_orchestrator_instance.validate.return_value = (True, [])
                mock_orchestrator_cls.return_value = mock_orchestrator_instance

                # Act
                validator.validate()

        # Assert
        mock_parse.assert_called_once_with(sample_source_path)

    def test_validate_passes_terrain_provider_to_orchestrator(
        self, sample_source_path: Path, sample_output_path: Path, sample_heightmap_path: Path
    ):
        """Test validate passes terrain provider to orchestrator."""
        # Arrange
        validator = ConversionValidator(
            sample_source_path, sample_output_path, sample_heightmap_path
        )

        with patch.object(validator.engine, "parse_map") as mock_parse:
            mock_parse.return_value = Mock(
                metadata={"source_path": str(sample_source_path)},
                team1_spawns=[],
                team2_spawns=[],
                capture_points=[],
                objects=[],
            )

            with patch("validate_conversion.ValidationOrchestrator") as mock_orchestrator_cls:
                mock_orchestrator_instance = Mock(spec=["validate"])
                mock_orchestrator_instance.validate.return_value = (True, [])
                mock_orchestrator_cls.return_value = mock_orchestrator_instance

                # Act
                validator.validate()

        # Assert
        mock_orchestrator_cls.assert_called_once()
        call_args = mock_orchestrator_cls.call_args
        assert call_args[0][2] is not None  # terrain_provider argument

    def test_validate_prints_parsing_message(
        self, sample_source_path: Path, sample_output_path: Path, capsys
    ):
        """Test validate prints parsing message."""
        # Arrange
        validator = ConversionValidator(sample_source_path, sample_output_path)

        with patch.object(validator.engine, "parse_map") as mock_parse:
            mock_parse.return_value = Mock(
                metadata={"source_path": str(sample_source_path)},
                team1_spawns=[],
                team2_spawns=[],
                capture_points=[],
                objects=[],
            )

            with patch("validate_conversion.ValidationOrchestrator") as mock_orchestrator_cls:
                mock_orchestrator_instance = Mock(spec=["validate"])
                mock_orchestrator_instance.validate.return_value = (True, [])
                mock_orchestrator_cls.return_value = mock_orchestrator_instance

                # Act
                validator.validate()

        captured = capsys.readouterr()

        # Assert
        assert "Parsing source BF1942 map" in captured.out


# Tests for main() function


class TestMainFunction:
    """Tests for main() CLI entry point."""

    def test_main_returns_success_with_valid_args(
        self, sample_source_path: Path, sample_output_path: Path, capsys
    ):
        """Test main returns success code with valid arguments."""
        # Arrange
        test_args = [
            "validate_conversion.py",
            "--source",
            str(sample_source_path),
            "--output",
            str(sample_output_path),
        ]

        with (
            patch("sys.argv", test_args),
            patch("validate_conversion.ConversionValidator") as mock_validator_cls,
        ):
            mock_validator_instance = Mock(spec=["validate"])
            mock_validator_instance.validate.return_value = (True, [])
            mock_validator_cls.return_value = mock_validator_instance

            # Act
            result = main()

        # Assert
        assert result == 0

    def test_main_returns_failure_with_validation_errors(
        self, sample_source_path: Path, sample_output_path: Path
    ):
        """Test main returns error code with validation errors."""
        # Arrange
        test_args = [
            "validate_conversion.py",
            "--source",
            str(sample_source_path),
            "--output",
            str(sample_output_path),
        ]

        with (
            patch("sys.argv", test_args),
            patch("validate_conversion.ConversionValidator") as mock_validator_cls,
        ):
            mock_validator_instance = Mock(spec=["validate"])
            mock_validator_instance.validate.return_value = (False, [Mock(severity="error")])
            mock_validator_cls.return_value = mock_validator_instance

            # Act
            result = main()

        # Assert
        assert result == 1

    def test_main_returns_error_when_source_not_found(
        self, sample_output_path: Path, tmp_path: Path, capsys
    ):
        """Test main returns error when source path doesn't exist."""
        # Arrange
        nonexistent_source = tmp_path / "nonexistent"
        test_args = [
            "validate_conversion.py",
            "--source",
            str(nonexistent_source),
            "--output",
            str(sample_output_path),
        ]

        with patch("sys.argv", test_args):
            # Act
            result = main()

        captured = capsys.readouterr()

        # Assert
        assert result == 1
        assert "Source map not found" in captured.out

    def test_main_returns_error_when_output_not_found(
        self, sample_source_path: Path, tmp_path: Path, capsys
    ):
        """Test main returns error when output path doesn't exist."""
        # Arrange
        nonexistent_output = tmp_path / "nonexistent.tscn"
        test_args = [
            "validate_conversion.py",
            "--source",
            str(sample_source_path),
            "--output",
            str(nonexistent_output),
        ]

        with patch("sys.argv", test_args):
            # Act
            result = main()

        captured = capsys.readouterr()

        # Assert
        assert result == 1
        assert "Output .tscn not found" in captured.out

    def test_main_parses_heightmap_arg(
        self, sample_source_path: Path, sample_output_path: Path, sample_heightmap_path: Path
    ):
        """Test main parses heightmap argument."""
        # Arrange
        test_args = [
            "validate_conversion.py",
            "--source",
            str(sample_source_path),
            "--output",
            str(sample_output_path),
            "--heightmap",
            str(sample_heightmap_path),
        ]

        with (
            patch("sys.argv", test_args),
            patch("validate_conversion.ConversionValidator") as mock_validator_cls,
        ):
            mock_validator_instance = Mock(spec=["validate"])
            mock_validator_instance.validate.return_value = (True, [])
            mock_validator_cls.return_value = mock_validator_instance

            # Act
            main()

        # Assert
        mock_validator_cls.assert_called_once()
        call_args = mock_validator_cls.call_args
        assert call_args[0][2] == sample_heightmap_path

    def test_main_parses_terrain_size_arg(self, sample_source_path: Path, sample_output_path: Path):
        """Test main parses terrain-size argument."""
        # Arrange
        test_args = [
            "validate_conversion.py",
            "--source",
            str(sample_source_path),
            "--output",
            str(sample_output_path),
            "--terrain-size",
            "4096.0",
        ]

        with (
            patch("sys.argv", test_args),
            patch("validate_conversion.ConversionValidator") as mock_validator_cls,
        ):
            mock_validator_instance = Mock(spec=["validate"])
            mock_validator_instance.validate.return_value = (True, [])
            mock_validator_cls.return_value = mock_validator_instance

            # Act
            main()

        # Assert
        mock_validator_cls.assert_called_once()
        call_args = mock_validator_cls.call_args
        assert call_args[0][3] == 4096.0

    def test_main_parses_height_range_args(
        self, sample_source_path: Path, sample_output_path: Path
    ):
        """Test main parses min-height and max-height arguments."""
        # Arrange
        test_args = [
            "validate_conversion.py",
            "--source",
            str(sample_source_path),
            "--output",
            str(sample_output_path),
            "--min-height",
            "50.0",
            "--max-height",
            "300.0",
        ]

        with (
            patch("sys.argv", test_args),
            patch("validate_conversion.ConversionValidator") as mock_validator_cls,
        ):
            mock_validator_instance = Mock(spec=["validate"])
            mock_validator_instance.validate.return_value = (True, [])
            mock_validator_cls.return_value = mock_validator_instance

            # Act
            main()

        # Assert
        mock_validator_cls.assert_called_once()
        call_args = mock_validator_cls.call_args
        assert call_args[0][4] == (50.0, 300.0)

    def test_main_uses_default_terrain_size(
        self, sample_source_path: Path, sample_output_path: Path
    ):
        """Test main uses default terrain size when not specified."""
        # Arrange
        test_args = [
            "validate_conversion.py",
            "--source",
            str(sample_source_path),
            "--output",
            str(sample_output_path),
        ]

        with (
            patch("sys.argv", test_args),
            patch("validate_conversion.ConversionValidator") as mock_validator_cls,
        ):
            mock_validator_instance = Mock(spec=["validate"])
            mock_validator_instance.validate.return_value = (True, [])
            mock_validator_cls.return_value = mock_validator_instance

            # Act
            main()

        # Assert
        mock_validator_cls.assert_called_once()
        call_args = mock_validator_cls.call_args
        assert call_args[0][3] == 2048.0

    def test_main_uses_default_height_range(
        self, sample_source_path: Path, sample_output_path: Path
    ):
        """Test main uses default height range when not specified."""
        # Arrange
        test_args = [
            "validate_conversion.py",
            "--source",
            str(sample_source_path),
            "--output",
            str(sample_output_path),
        ]

        with (
            patch("sys.argv", test_args),
            patch("validate_conversion.ConversionValidator") as mock_validator_cls,
        ):
            mock_validator_instance = Mock(spec=["validate"])
            mock_validator_instance.validate.return_value = (True, [])
            mock_validator_cls.return_value = mock_validator_instance

            # Act
            main()

        # Assert
        mock_validator_cls.assert_called_once()
        call_args = mock_validator_cls.call_args
        assert call_args[0][4] == (70.0, 220.0)

    def test_main_handles_none_heightmap(self, sample_source_path: Path, sample_output_path: Path):
        """Test main handles None heightmap when not specified."""
        # Arrange
        test_args = [
            "validate_conversion.py",
            "--source",
            str(sample_source_path),
            "--output",
            str(sample_output_path),
        ]

        with (
            patch("sys.argv", test_args),
            patch("validate_conversion.ConversionValidator") as mock_validator_cls,
        ):
            mock_validator_instance = Mock(spec=["validate"])
            mock_validator_instance.validate.return_value = (True, [])
            mock_validator_cls.return_value = mock_validator_instance

            # Act
            main()

        # Assert
        mock_validator_cls.assert_called_once()
        call_args = mock_validator_cls.call_args
        assert call_args[0][2] is None
