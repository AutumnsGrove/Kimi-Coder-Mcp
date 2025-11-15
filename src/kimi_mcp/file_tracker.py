"""File system change tracking for detecting Kimi's modifications.

This module tracks file changes before and after Kimi CLI execution
to identify created and modified files.
"""

import hashlib
import logging
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


class FileTracker:
    """Tracks file system changes during Kimi CLI execution."""

    def __init__(self, working_dir: str):
        """Initialize file tracker.

        Args:
            working_dir: Directory to monitor for changes
        """
        self.working_dir = Path(working_dir)
        self.initial_state: Dict[str, str] = {}
        self.final_state: Dict[str, str] = {}

    def snapshot(self) -> Dict[str, str]:
        """Create a snapshot of all files in the working directory.

        Returns:
            Dict mapping file paths to their MD5 checksums
        """
        logger.debug(f"Creating snapshot of {self.working_dir}")
        snapshot = {}

        # Patterns to ignore during traversal
        ignore_patterns = {".git", "__pycache__", ".venv", ".DS_Store", "node_modules"}
        ignore_extensions = {".pyc"}

        try:
            for root, dirs, files in os.walk(self.working_dir):
                # Remove ignored directories from dirs to prevent traversal
                dirs[:] = [d for d in dirs if d not in ignore_patterns]

                for file in files:
                    # Skip ignored file extensions
                    if any(file.endswith(ext) for ext in ignore_extensions):
                        continue

                    file_path = Path(root) / file
                    try:
                        # Calculate relative path from working_dir
                        rel_path = file_path.relative_to(self.working_dir)
                        checksum = self.calculate_checksum(file_path)
                        if checksum:  # Only add if checksum calculation succeeded
                            snapshot[str(rel_path)] = checksum
                    except Exception as e:
                        logger.warning(
                            f"Error processing {file_path}: {e}"
                        )
        except PermissionError as e:
            logger.warning(f"Permission denied accessing {self.working_dir}: {e}")

        return snapshot

    def take_initial_snapshot(self) -> None:
        """Take snapshot before Kimi execution."""
        self.initial_state = self.snapshot()
        logger.info(f"Initial snapshot: {len(self.initial_state)} files")

    def take_final_snapshot(self) -> None:
        """Take snapshot after Kimi execution."""
        self.final_state = self.snapshot()
        logger.info(f"Final snapshot: {len(self.final_state)} files")

    def detect_changes(self) -> Tuple[List[str], List[str]]:
        """Detect created and modified files.

        Returns:
            Tuple of (created_files, modified_files)
        """
        created = []
        modified = []

        # Find created files: in final_state but not in initial_state
        for file_path in self.final_state:
            if file_path not in self.initial_state:
                created.append(file_path)

        # Find modified files: in both states but checksums differ
        for file_path in self.final_state:
            if (
                file_path in self.initial_state
                and self.initial_state[file_path] != self.final_state[file_path]
            ):
                modified.append(file_path)

        logger.info(f"Detected {len(created)} created, {len(modified)} modified")
        return created, modified

    def read_file_contents(self, file_paths: List[str]) -> Dict[str, str]:
        """Read contents of specified files.

        Args:
            file_paths: List of file paths to read

        Returns:
            Dict mapping file paths to their contents
            Binary files are noted but content not included
        """
        contents = {}

        for file_path in file_paths:
            full_path = self.working_dir / file_path
            try:
                # Check if file exists
                if not full_path.exists():
                    logger.warning(f"File not found: {file_path}")
                    continue

                # Detect binary files
                if self.is_binary_file(full_path):
                    contents[file_path] = "[Binary file, not displayed]"
                    continue

                # Read text file contents
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        contents[file_path] = f.read()
                except UnicodeDecodeError:
                    # Fallback to latin-1 encoding if UTF-8 fails
                    try:
                        with open(full_path, "r", encoding="latin-1") as f:
                            contents[file_path] = f.read()
                    except Exception as fallback_error:
                        logger.warning(
                            f"Error reading {file_path} with fallback encoding: {fallback_error}"
                        )

            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")

        return contents

    def is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary.

        Args:
            file_path: Path to the file

        Returns:
            True if binary, False if text
        """
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(8192)  # Read first 8KB
                # Check for null bytes which indicate binary content
                return b"\x00" in chunk
        except Exception as e:
            logger.warning(f"Error checking if file is binary {file_path}: {e}")
            return False

    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file.

        Args:
            file_path: Path to the file

        Returns:
            MD5 checksum as hex string
        """
        md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(8192)  # Read 8KB chunks
                    if not chunk:
                        break
                    md5.update(chunk)
        except Exception as e:
            logger.warning(f"Error calculating checksum for {file_path}: {e}")
            return ""
        return md5.hexdigest()
