"""Tests for file change tracking."""

import pytest
from pathlib import Path
from kimi_mcp.file_tracker import FileTracker


class TestFileTracker:
    """Test suite for FileTracker class."""

    def test_initialization(self, tmp_path):
        """Test FileTracker initialization."""
        # Test with absolute path
        tracker = FileTracker(str(tmp_path))
        assert tracker.working_dir == tmp_path
        assert isinstance(tracker.initial_state, dict)
        assert isinstance(tracker.final_state, dict)
        assert len(tracker.initial_state) == 0, "initial_state should be empty"
        assert len(tracker.final_state) == 0, "final_state should be empty"

        # Test with relative path
        relative_path = "."
        tracker_relative = FileTracker(relative_path)
        assert tracker_relative.working_dir == Path(relative_path)
        assert isinstance(tracker_relative.initial_state, dict)
        assert isinstance(tracker_relative.final_state, dict)

    def test_snapshot_creation(self, tmp_path):
        """Test creating a directory snapshot."""
        tracker = FileTracker(str(tmp_path))

        # Create several test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.py"
        file3 = tmp_path / "file3.md"

        file1.write_text("Content of file 1")
        file2.write_text("print('Hello, World!')")
        file3.write_text("# Markdown file")

        # Create snapshot
        snapshot = tracker.snapshot()

        # Verify snapshot contains correct number of files
        assert len(snapshot) == 3, f"Expected 3 files, got {len(snapshot)}"

        # Verify all files are in snapshot with relative paths
        assert "file1.txt" in snapshot, "file1.txt should be in snapshot"
        assert "file2.py" in snapshot, "file2.py should be in snapshot"
        assert "file3.md" in snapshot, "file3.md should be in snapshot"

        # Verify checksums are 32-character hex strings (MD5 format)
        for file_path, checksum in snapshot.items():
            assert isinstance(checksum, str), f"Checksum for {file_path} should be string"
            assert len(checksum) == 32, f"MD5 checksum for {file_path} should be 32 chars, got {len(checksum)}"
            assert all(c in "0123456789abcdef" for c in checksum), f"Checksum for {file_path} should be hex"

    def test_detect_new_files(self, tmp_path):
        """Test detection of newly created files."""
        tracker = FileTracker(str(tmp_path))

        # Create initial file
        initial_file = tmp_path / "initial.txt"
        initial_file.write_text("Initial content")

        # Take initial snapshot
        tracker.take_initial_snapshot()
        assert len(tracker.initial_state) == 1

        # Create new files
        new_file1 = tmp_path / "new_file1.txt"
        new_file2 = tmp_path / "new_file2.txt"
        new_file3 = tmp_path / "new_file3.py"

        new_file1.write_text("New content 1")
        new_file2.write_text("New content 2")
        new_file3.write_text("New code")

        # Take final snapshot
        tracker.take_final_snapshot()
        assert len(tracker.final_state) == 4

        # Detect changes
        created, modified = tracker.detect_changes()

        # Verify created files list contains the new files
        assert len(created) == 3, f"Expected 3 created files, got {len(created)}"
        assert "new_file1.txt" in created, "new_file1.txt should be in created_files"
        assert "new_file2.txt" in created, "new_file2.txt should be in created_files"
        assert "new_file3.py" in created, "new_file3.py should be in created_files"

        # Verify modified files list is empty
        assert len(modified) == 0, "modified_files should be empty"

    def test_detect_modified_files(self, tmp_path):
        """Test detection of modified files."""
        tracker = FileTracker(str(tmp_path))

        # Create initial file with content
        test_file = tmp_path / "test.txt"
        test_file.write_text("original")

        # Take initial snapshot
        tracker.take_initial_snapshot()
        assert len(tracker.initial_state) == 1
        initial_checksum = tracker.initial_state["test.txt"]

        # Modify the file content
        test_file.write_text("modified")

        # Take final snapshot
        tracker.take_final_snapshot()
        assert len(tracker.final_state) == 1
        final_checksum = tracker.final_state["test.txt"]

        # Verify checksums are different
        assert initial_checksum != final_checksum, "Checksums should be different after modification"

        # Detect changes
        created, modified = tracker.detect_changes()

        # Verify modified files list contains the file
        assert len(modified) == 1, f"Expected 1 modified file, got {len(modified)}"
        assert "test.txt" in modified, "test.txt should be in modified_files"

        # Verify created files list is empty
        assert len(created) == 0, "created_files should be empty"

    def test_binary_file_detection(self, tmp_path):
        """Test binary vs text file detection."""
        tracker = FileTracker(str(tmp_path))

        # Create a text file
        text_file = tmp_path / "text.txt"
        text_file.write_text("Hello, World! This is UTF-8 encoded text.")

        # Create a binary file with null bytes
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03\xFF\xFE")

        # Test is_binary_file() on both
        assert tracker.is_binary_file(text_file) is False, "text.txt should not be detected as binary"
        assert tracker.is_binary_file(binary_file) is True, "binary.bin should be detected as binary"

    def test_checksum_calculation(self, tmp_path):
        """Test MD5 checksum calculation."""
        tracker = FileTracker(str(tmp_path))

        # Create a file with known content
        file1 = tmp_path / "file1.txt"
        file1.write_text("Test content for checksum")

        # Calculate checksum twice
        checksum1 = tracker.calculate_checksum(file1)
        checksum2 = tracker.calculate_checksum(file1)

        # Verify checksums are identical (consistency)
        assert checksum1 == checksum2, "Checksums should be identical for same file"

        # Verify checksum is 32-character hex string
        assert len(checksum1) == 32, f"MD5 checksum should be 32 chars, got {len(checksum1)}"
        assert all(c in "0123456789abcdef" for c in checksum1), "Checksum should be hex"

        # Create another file with same content
        file2 = tmp_path / "file2.txt"
        file2.write_text("Test content for checksum")

        checksum3 = tracker.calculate_checksum(file2)

        # Verify both produce same checksum
        assert checksum1 == checksum3, "Files with identical content should have identical checksums"

    def test_read_file_contents(self, tmp_path):
        """Test reading file contents."""
        tracker = FileTracker(str(tmp_path))

        # Create text file
        text_file = tmp_path / "text.txt"
        text_content = "Hello, World!"
        text_file.write_text(text_content)

        # Create binary file with null bytes
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\xFF\xFE")

        # Call read_file_contents
        contents = tracker.read_file_contents(["text.txt", "binary.bin"])

        # Verify text file content is read correctly
        assert "text.txt" in contents, "text.txt should be in contents"
        assert contents["text.txt"] == text_content, "Text file content should match"

        # Verify binary file has marker
        assert "binary.bin" in contents, "binary.bin should be in contents"
        assert contents["binary.bin"] == "[Binary file, not displayed]", "Binary file should have marker"

    def test_ignore_patterns(self, tmp_path):
        """Test that .git, __pycache__, etc. are ignored."""
        tracker = FileTracker(str(tmp_path))

        # Create directory structure with ignored patterns (directories only)
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("git config")

        pycache_dir = tmp_path / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "module.pyc").write_text("compiled python")

        venv_dir = tmp_path / ".venv"
        venv_dir.mkdir()
        (venv_dir / "lib" / "python.py").mkdir(parents=True)
        (venv_dir / "lib" / "python.py" / "site.py").write_text("site packages")

        node_modules_dir = tmp_path / "node_modules"
        node_modules_dir.mkdir()
        (node_modules_dir / "package.json").write_text("{}")

        # Create .pyc file (ignored by extension)
        pyc_file = tmp_path / "module.pyc"
        pyc_file.write_text("compiled python")

        regular_file = tmp_path / "regular_file.txt"
        regular_file.write_text("Regular content")

        # Take snapshot
        snapshot = tracker.snapshot()

        # Verify snapshot contains ONLY regular_file.txt (other ignored dirs and extensions excluded)
        assert len(snapshot) == 1, f"Expected only 1 file, got {len(snapshot)}: {snapshot.keys()}"
        assert "regular_file.txt" in snapshot, "regular_file.txt should be in snapshot"

        # Verify all ignored directories are excluded
        for key in snapshot.keys():
            assert ".git" not in key, f".git files should be ignored: {key}"
            assert "__pycache__" not in key, f"__pycache__ files should be ignored: {key}"
            assert ".venv" not in key, f".venv files should be ignored: {key}"
            assert "node_modules" not in key, f"node_modules files should be ignored: {key}"

        # Verify .pyc files are excluded
        assert "module.pyc" not in snapshot, f".pyc files should be ignored"

    def test_nested_directories(self, tmp_path):
        """Test handling of nested directory structures."""
        tracker = FileTracker(str(tmp_path))

        # Create nested directory structure
        nested_dir = tmp_path / "dir1" / "dir2"
        nested_dir.mkdir(parents=True)

        nested_file = nested_dir / "file.txt"
        nested_file.write_text("Nested file content")

        root_file = tmp_path / "root.txt"
        root_file.write_text("Root file content")

        # Take snapshot
        snapshot = tracker.snapshot()

        # Verify nested files are captured with relative paths
        assert len(snapshot) == 2, f"Expected 2 files, got {len(snapshot)}"
        assert "root.txt" in snapshot, "root.txt should be in snapshot"

        # Check for nested path (might use forward slashes on all platforms)
        nested_path_found = False
        for key in snapshot.keys():
            if "dir1" in key and "dir2" in key and "file.txt" in key:
                nested_path_found = True
                break
        assert nested_path_found, f"Nested path should be in snapshot: {snapshot.keys()}"

    def test_empty_directory(self, tmp_path):
        """Test handling of empty directories."""
        tracker = FileTracker(str(tmp_path))

        # Create empty directory (no files)
        empty_subdir = tmp_path / "empty_dir"
        empty_subdir.mkdir()

        # Take snapshot
        snapshot = tracker.snapshot()

        # Verify snapshot is empty dict
        assert len(snapshot) == 0, f"Empty directory should have no files in snapshot, got {snapshot}"
        assert isinstance(snapshot, dict), "Snapshot should be a dict"

    def test_detect_both_created_and_modified(self, tmp_path):
        """Test detection of both created and modified files simultaneously."""
        tracker = FileTracker(str(tmp_path))

        # Create file1.txt
        file1 = tmp_path / "file1.txt"
        file1.write_text("Original content")

        # Take initial snapshot
        tracker.take_initial_snapshot()
        assert len(tracker.initial_state) == 1

        # Create file2.txt (new)
        file2 = tmp_path / "file2.txt"
        file2.write_text("New file content")

        # Modify file1.txt
        file1.write_text("Modified content")

        # Take final snapshot
        tracker.take_final_snapshot()
        assert len(tracker.final_state) == 2

        # Detect changes
        created, modified = tracker.detect_changes()

        # Verify both created and modified are detected correctly
        assert len(created) == 1, f"Expected 1 created file, got {len(created)}"
        assert "file2.txt" in created, "file2.txt should be in created_files"

        assert len(modified) == 1, f"Expected 1 modified file, got {len(modified)}"
        assert "file1.txt" in modified, "file1.txt should be in modified_files"

    def test_read_nonexistent_file(self, tmp_path):
        """Test reading nonexistent files gracefully."""
        tracker = FileTracker(str(tmp_path))

        # Create one real file
        real_file = tmp_path / "real.txt"
        real_file.write_text("Real content")

        # Call read_file_contents with nonexistent file
        contents = tracker.read_file_contents(["nonexistent.txt", "real.txt"])

        # Verify nonexistent file is skipped gracefully
        assert "nonexistent.txt" not in contents, "Nonexistent file should be skipped"

        # Verify real file is read
        assert "real.txt" in contents, "real.txt should be in contents"
        assert contents["real.txt"] == "Real content", "Real file content should be read correctly"
