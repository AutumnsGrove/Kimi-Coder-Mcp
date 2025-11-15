"""Utility functions for Kimi-Coder-MCP.

This module provides helper functions for configuration, logging,
error handling, and common transformations.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def get_api_key() -> Optional[str]:
    """Get Moonshot API key from environment.

    Checks multiple environment variable names for flexibility.

    Returns:
        API key if found, None otherwise
    """
    # Check common env var names
    for env_var in ["MOONSHOT_API_KEY", "KIMI_API_KEY"]:
        api_key = os.getenv(env_var)
        if api_key:
            logger.debug(f"Found API key in {env_var}")
            return api_key

    logger.warning("No Moonshot API key found in environment")
    return None


def format_error(
    error_type: str,
    message: str,
    details: Optional[str] = None,
    suggestion: Optional[str] = None
) -> Dict[str, Any]:
    """Format an error response in a consistent structure.

    Args:
        error_type: Type of error (e.g., "TimeoutError", "AuthError")
        message: Main error message
        details: Optional additional details
        suggestion: Optional suggestion for resolution

    Returns:
        Formatted error dict
    """
    error = {
        "type": error_type,
        "message": message
    }

    if details:
        error["details"] = details

    if suggestion:
        error["suggestion"] = suggestion

    return error


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the MCP server.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logger.info(f"Logging configured at {level} level")


def validate_file_path(file_path: str, base_dir: str) -> bool:
    """Validate that a file path is within the allowed base directory.

    Prevents directory traversal attacks.

    Args:
        file_path: File path to validate
        base_dir: Base directory that files must be within

    Returns:
        True if path is valid and safe, False otherwise
    """
    try:
        # Handle empty strings
        if not file_path or not base_dir:
            return False

        # Resolve both paths to absolute paths
        resolved_file = Path(file_path).resolve()
        resolved_base = Path(base_dir).resolve()

        # Check if file_path is relative to base_dir
        resolved_file.relative_to(resolved_base)
        return True
    except (ValueError, RuntimeError, OSError):
        # ValueError: path is not relative to base_dir
        # RuntimeError: symlink loop or other path resolution issues
        # OSError: invalid path or permission issues
        return False


def get_timeout(default: int = 300) -> int:
    """Get timeout value from environment or use default.

    Args:
        default: Default timeout in seconds

    Returns:
        Timeout value in seconds
    """
    timeout_str = os.getenv("KIMI_TIMEOUT")

    if timeout_str:
        try:
            return int(timeout_str)
        except ValueError:
            logger.warning(f"Invalid KIMI_TIMEOUT value: {timeout_str}, using default")

    return default
