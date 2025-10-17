#!/usr/bin/env python3
"""Tests for SnappingOrchestrator.

Tests the terrain snapping orchestration system that coordinates multiple
snapper implementations to adjust object heights in .tscn files.
"""

from unittest.mock import MagicMock

import pytest

from tools.bfportal.terrain.snappers.snapping_orchestrator import (
    SnappingOrchestrator,
    SnappingStats,
)


class TestSnappingStats:
    """Tests for SnappingStats dataclass."""

    def test_snapping_stats_default_values(self):
        """Test SnappingStats initializes with correct defaults."""
        # Arrange & Act
        stats = SnappingStats()

        # Assert
        assert stats.total_objects == 0
        assert stats.snapped_by_category == {}
        assert stats.skipped == 0
        assert stats.errors == 0

    def test_snapping_stats_with_values(self):
        """Test SnappingStats can be initialized with custom values."""
        # Arrange & Act
        stats = SnappingStats(
            total_objects=10,
            snapped_by_category={"Props": 5, "Vegetation": 3},
            skipped=1,
            errors=1,
        )

        # Assert
        assert stats.total_objects == 10
        assert stats.snapped_by_category == {"Props": 5, "Vegetation": 3}
        assert stats.skipped == 1
        assert stats.errors == 1


class TestSnappingOrchestrator:
    """Tests for SnappingOrchestrator class."""

    @pytest.fixture
    def mock_terrain(self):
        """Provide mocked terrain provider."""
        terrain = MagicMock()
        terrain.get_height_at_position.return_value = 10.0
        return terrain

    @pytest.fixture
    def mock_snapper(self):
        """Provide mocked object snapper."""
        snapper = MagicMock()
        snapper.can_snap.return_value = True
        snapper.get_category_name.return_value = "Props"

        # Mock snap result
        snap_result = MagicMock()
        snap_result.snapped_y = 10.5
        snap_result.original_y = 5.0
        snap_result.was_adjusted = True
        snap_result.reason = "Snapped to terrain"
        snapper.calculate_snapped_height.return_value = snap_result

        return snapper

    @pytest.fixture
    def orchestrator(self, mock_snapper, mock_terrain):
        """Provide SnappingOrchestrator instance."""
        return SnappingOrchestrator([mock_snapper], mock_terrain)

    def test_init_creates_validator(self, mock_snapper, mock_terrain):
        """Test SnappingOrchestrator initializes with validator."""
        # Arrange & Act
        orchestrator = SnappingOrchestrator([mock_snapper], mock_terrain)

        # Assert
        assert orchestrator.snappers == [mock_snapper]
        assert orchestrator.validator is not None

    def test_snap_tscn_file_raises_error_for_missing_file(self, orchestrator, tmp_path):
        """Test snap_tscn_file raises FileNotFoundError for missing file."""
        # Arrange
        missing_file = tmp_path / "nonexistent.tscn"

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="TSCN file not found"):
            orchestrator.snap_tscn_file(missing_file)

    def test_snap_tscn_file_dry_run_does_not_write(self, orchestrator, tmp_path, capsys):
        """Test snap_tscn_file in dry-run mode does not write changes."""
        # Arrange
        tscn_file = tmp_path / "test.tscn"
        tscn_file.write_text('[gd_scene format=3]\n[node name="Root" type="Node3D"]\n')
        original_content = tscn_file.read_text()

        # Act
        stats = orchestrator.snap_tscn_file(tscn_file, dry_run=True)

        # Assert
        assert tscn_file.read_text() == original_content  # File unchanged
        captured = capsys.readouterr()
        assert "DRY RUN MODE" in captured.out
        assert isinstance(stats, SnappingStats)

    def test_snap_tscn_file_creates_backup(self, orchestrator, tmp_path, mock_snapper):
        """Test snap_tscn_file creates backup of original file."""
        # Arrange
        tscn_file = tmp_path / "test.tscn"
        content = """[gd_scene format=3]
[node name="Tree_1" type="Node3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 5, 200)
"""
        tscn_file.write_text(content)

        # Mock snapper to trigger adjustment
        mock_snapper.can_snap.return_value = True

        # Act
        orchestrator.snap_tscn_file(tscn_file)

        # Assert
        backup_path = tmp_path / "test.tscn.backup"
        assert backup_path.exists()
        assert backup_path.read_text() == content

    def test_snap_tscn_file_writes_output_to_different_path(self, orchestrator, tmp_path):
        """Test snap_tscn_file can write to different output path."""
        # Arrange
        input_file = tmp_path / "input.tscn"
        output_file = tmp_path / "output.tscn"
        input_content = '[gd_scene format=3]\n[node name="Root" type="Node3D"]\n'
        input_file.write_text(input_content)

        # Act
        orchestrator.snap_tscn_file(input_file, output_path=output_file)

        # Assert
        assert output_file.exists()
        # Original file moved to backup
        backup_file = tmp_path / "input.tscn.backup"
        assert backup_file.exists()
        assert backup_file.read_text() == input_content

    def test_find_snapper_returns_first_matching_snapper(self, orchestrator, mock_snapper):
        """Test _find_snapper returns first snapper that can handle object."""
        # Arrange
        mock_snapper.can_snap.return_value = True

        # Act
        result = orchestrator._find_snapper("Tree_1", "Tree")

        # Assert
        assert result == mock_snapper
        mock_snapper.can_snap.assert_called_once_with("Tree_1", "Tree")

    def test_find_snapper_returns_none_when_no_match(self, orchestrator, mock_snapper):
        """Test _find_snapper returns None when no snapper matches."""
        # Arrange
        mock_snapper.can_snap.return_value = False

        # Act
        result = orchestrator._find_snapper("Unknown", "Unknown")

        # Assert
        assert result is None

    def test_parse_transform_line_valid_transform(self, orchestrator):
        """Test _parse_transform_line correctly parses valid Transform3D."""
        # Arrange
        line = "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 5, 200)\n"

        # Act
        result = orchestrator._parse_transform_line(line)

        # Assert
        assert result is not None
        values, indent = result
        assert len(values) == 12
        assert values[9] == 100.0  # x
        assert values[10] == 5.0  # y
        assert values[11] == 200.0  # z
        assert indent == ""

    def test_parse_transform_line_with_indentation(self, orchestrator):
        """Test _parse_transform_line preserves indentation."""
        # Arrange
        line = "    transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 5, 200)\n"

        # Act
        result = orchestrator._parse_transform_line(line)

        # Assert
        assert result is not None
        _, indent = result
        assert indent == "    "

    def test_parse_transform_line_invalid_format_returns_none(self, orchestrator):
        """Test _parse_transform_line returns None for invalid format."""
        # Arrange
        invalid_lines = [
            "not a transform line",
            "transform = InvalidFormat(1, 2, 3)",
            "transform = Transform3D(1, 2)",  # Too few values
        ]

        # Act & Assert
        for line in invalid_lines:
            result = orchestrator._parse_transform_line(line)
            assert result is None

    def test_format_transform_line_creates_valid_output(self, orchestrator):
        """Test _format_transform_line creates correctly formatted output."""
        # Arrange
        values = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 100.5, 10.3, 200.7]
        indent = "    "

        # Act
        result = orchestrator._format_transform_line(values, indent)

        # Assert
        assert result.startswith("    transform = Transform3D(")
        assert "100.5" in result
        assert "10.3" in result
        assert "200.7" in result
        assert result.endswith(")\n")

    def test_process_all_lines_skips_terrain_nodes(self, orchestrator, mock_snapper):
        """Test _process_all_lines skips nodes with _Terrain in name."""
        # Arrange
        lines = [
            "[gd_scene format=3]\n",
            '[node name="MP_Tungsten_Terrain" type="Node3D" parent="."]\n',
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)\n",
        ]

        # Act
        new_lines, stats, _ = orchestrator._process_all_lines(lines)

        # Assert
        mock_snapper.calculate_snapped_height.assert_not_called()  # Should skip terrain
        assert stats.total_objects == 0

    def test_process_all_lines_skips_hq_children(self, orchestrator, mock_snapper):
        """Test _process_all_lines skips children of HQ nodes (relative transforms)."""
        # Arrange
        lines = [
            '[node name="TEAM_1_HQ" type="Node3D" parent="."]\n',
            '[node name="SpawnPoint_1_1" type="Node3D" parent="TEAM_1_HQ"]\n',
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 5, 0, 10)\n",  # Relative transform
        ]

        # Act
        new_lines, stats, _ = orchestrator._process_all_lines(lines)

        # Assert
        mock_snapper.calculate_snapped_height.assert_not_called()  # Should skip HQ children
        assert stats.total_objects == 0

    def test_process_all_lines_snaps_static_children(self, orchestrator, mock_snapper):
        """Test _process_all_lines snaps children of Static node."""
        # Arrange
        lines = [
            '[node name="Static" type="Node3D" parent="."]\n',
            '[node name="Tree_1" type="Node3D" parent="Static"]\n',
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 5, 200)\n",
        ]
        mock_snapper.can_snap.return_value = True

        # Act
        new_lines, stats, _ = orchestrator._process_all_lines(lines)

        # Assert
        mock_snapper.calculate_snapped_height.assert_called_once()  # Should snap Static children
        assert stats.total_objects == 1

    def test_process_all_lines_counts_skipped_objects(self, orchestrator, mock_snapper):
        """Test _process_all_lines counts objects with no matching snapper."""
        # Arrange
        lines = [
            '[node name="Unknown_1" type="Node3D" parent="."]\n',
            "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)\n",
        ]
        mock_snapper.can_snap.return_value = False  # No snapper matches

        # Act
        new_lines, stats, _ = orchestrator._process_all_lines(lines)

        # Assert
        assert stats.skipped == 1
        assert stats.total_objects == 0

    def test_write_snapped_file_creates_backup_and_writes(self, orchestrator, tmp_path):
        """Test _write_snapped_file creates backup and writes new content."""
        # Arrange
        original_file = tmp_path / "original.tscn"
        original_content = "original content"
        original_file.write_text(original_content)

        new_lines = ["new", "content"]
        output_path = tmp_path / "original.tscn"

        # Act
        orchestrator._write_snapped_file(original_file, output_path, new_lines)

        # Assert
        backup_path = tmp_path / "original.tscn.backup"
        assert backup_path.exists()
        assert backup_path.read_text() == original_content
        assert output_path.read_text() == "newcontent"

    def test_print_stats_shows_summary(self, orchestrator, capsys):
        """Test _print_stats displays statistics summary."""
        # Arrange
        stats = SnappingStats(
            total_objects=10,
            snapped_by_category={"Props": 5, "Vegetation": 3},
            skipped=1,
            errors=1,
        )

        # Act
        orchestrator._print_stats(stats, adjustments_shown=5, max_shown=10)

        # Assert
        captured = capsys.readouterr()
        assert "TERRAIN SNAPPING RESULTS" in captured.out
        assert "Total objects processed: 10" in captured.out
        assert "Props: 5" in captured.out
        assert "Vegetation: 3" in captured.out
        assert "Total adjusted: 8" in captured.out
        assert "Skipped (no snapper): 1" in captured.out
        assert "Errors: 1" in captured.out

    def test_print_stats_shows_truncation_message(self, orchestrator, capsys):
        """Test _print_stats shows truncation message when adjustments exceed max."""
        # Arrange
        stats = SnappingStats(
            total_objects=20,
            snapped_by_category={"Props": 15},
        )

        # Act
        orchestrator._print_stats(stats, adjustments_shown=10, max_shown=10)

        # Assert
        captured = capsys.readouterr()
        assert "Showing first 10 adjustments" in captured.out
        assert "5 more adjusted" in captured.out
