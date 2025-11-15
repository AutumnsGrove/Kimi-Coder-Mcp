"""Tests for utility functions in kimi_mcp.utils module."""

import pytest
from pathlib import Path

from kimi_mcp.utils import validate_file_path


class TestValidateFilePath:
    """Test suite for validate_file_path() function."""

    def test_valid_path_within_base_dir(self, tmp_path):
        """Test that a valid path within base_dir returns True."""
        base_dir = tmp_path / "allowed"
        base_dir.mkdir()
        file_path = base_dir / "file.txt"

        assert validate_file_path(str(file_path), str(base_dir)) is True

    def test_valid_nested_path(self, tmp_path):
        """Test that a nested valid path within base_dir returns True."""
        base_dir = tmp_path / "allowed"
        base_dir.mkdir()
        nested_dir = base_dir / "subdir" / "deeper"
        nested_dir.mkdir(parents=True)
        file_path = nested_dir / "file.txt"

        assert validate_file_path(str(file_path), str(base_dir)) is True

    def test_path_exactly_at_base_dir(self, tmp_path):
        """Test that a path exactly at base_dir returns True."""
        base_dir = tmp_path / "allowed"
        base_dir.mkdir()

        assert validate_file_path(str(base_dir), str(base_dir)) is True

    def test_path_with_traversal_outside_base_dir(self, tmp_path):
        """Test that ../ traversal outside base_dir returns False."""
        base_dir = tmp_path / "allowed"
        base_dir.mkdir()
        file_path = base_dir / ".." / "outside.txt"

        assert validate_file_path(str(file_path), str(base_dir)) is False

    def test_absolute_path_outside_base_dir(self, tmp_path):
        """Test that an absolute path outside base_dir returns False."""
        base_dir = tmp_path / "allowed"
        base_dir.mkdir()
        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()
        file_path = outside_dir / "file.txt"

        assert validate_file_path(str(file_path), str(base_dir)) is False

    def test_multiple_traversal_attempts(self, tmp_path):
        """Test that multiple ../ traversal attempts return False."""
        base_dir = tmp_path / "allowed"
        base_dir.mkdir()
        file_path = base_dir / ".." / ".." / "outside.txt"

        assert validate_file_path(str(file_path), str(base_dir)) is False

    def test_non_existent_file_valid_structure(self, tmp_path):
        """Test that non-existent file with valid structure returns True."""
        base_dir = tmp_path / "allowed"
        base_dir.mkdir()
        file_path = base_dir / "nonexistent" / "file.txt"

        assert validate_file_path(str(file_path), str(base_dir)) is True

    def test_non_existent_file_invalid_traversal(self, tmp_path):
        """Test that non-existent file with invalid traversal returns False."""
        base_dir = tmp_path / "allowed"
        base_dir.mkdir()
        file_path = base_dir / ".." / "nonexistent.txt"

        assert validate_file_path(str(file_path), str(base_dir)) is False

    def test_empty_file_path(self, tmp_path):
        """Test that empty file_path returns False."""
        base_dir = tmp_path / "allowed"
        base_dir.mkdir()

        assert validate_file_path("", str(base_dir)) is False

    def test_empty_base_dir(self, tmp_path):
        """Test that empty base_dir returns False."""
        file_path = tmp_path / "file.txt"

        assert validate_file_path(str(file_path), "") is False

    def test_both_paths_empty(self):
        """Test that both empty paths return False."""
        assert validate_file_path("", "") is False

    def test_relative_paths(self, tmp_path):
        """Test with relative paths (should still validate correctly)."""
        # Change to tmp_path and use relative paths
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            base_dir = Path("allowed")
            base_dir.mkdir()
            file_path = Path("allowed") / "file.txt"

            assert validate_file_path(str(file_path), str(base_dir)) is True
        finally:
            os.chdir(original_cwd)

    def test_relative_path_with_traversal(self, tmp_path):
        """Test relative path with traversal (should return False)."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            base_dir = Path("allowed")
            base_dir.mkdir()
            file_path = Path("allowed") / ".." / "outside.txt"

            assert validate_file_path(str(file_path), str(base_dir)) is False
        finally:
            os.chdir(original_cwd)

    def test_case_sensitivity(self, tmp_path):
        """Test that path validation handles case correctly on case-sensitive systems."""
        base_dir = tmp_path / "Allowed"
        base_dir.mkdir()
        file_path = base_dir / "File.txt"

        assert validate_file_path(str(file_path), str(base_dir)) is True

    def test_path_with_current_dir_reference(self, tmp_path):
        """Test path with ./ reference (should still be valid)."""
        base_dir = tmp_path / "allowed"
        base_dir.mkdir()
        file_path = base_dir / "." / "file.txt"

        assert validate_file_path(str(file_path), str(base_dir)) is True

    def test_path_with_mixed_separators(self, tmp_path):
        """Test that mixed path separators are handled correctly."""
        base_dir = tmp_path / "allowed"
        base_dir.mkdir()
        subdir = base_dir / "sub"
        subdir.mkdir()
        # Use string path that might have mixed separators
        file_path = str(base_dir) + "/sub/file.txt"

        assert validate_file_path(file_path, str(base_dir)) is True
