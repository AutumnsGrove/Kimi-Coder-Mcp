"""Kimi CLI session management using subprocess.

This module handles executing Kimi CLI commands using subprocess and the
--print --yolo flags for non-interactive mode, eliminating the need for
pexpect and process management.
"""

import logging
import os
import shutil
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


class KimiSession:
    """Manages ephemeral Kimi CLI command execution via subprocess.

    Each session executes a command using subprocess.run() with the
    --print --yolo flags for non-interactive mode. No persistent
    process management is needed.
    """

    def __init__(
        self,
        working_dir: str,
        api_key: Optional[str] = None,
        timeout: int = 300
    ):
        """Initialize a Kimi CLI session.

        Args:
            working_dir: Directory where Kimi should operate
            api_key: Optional Moonshot API key (uses env var if not provided)
            timeout: Maximum time to wait for task completion (seconds)
        """
        self.working_dir = working_dir
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY")
        self.timeout = timeout

    def spawn(self) -> None:
        """Verify that the Kimi CLI is installed and available.

        Raises:
            RuntimeError: If Kimi CLI is not installed
        """
        logger.info(f"Verifying Kimi CLI is available for {self.working_dir}")

        if shutil.which("kimi") is None:
            raise RuntimeError(
                "Kimi CLI not found. Install with: uv tool install kimi-cli"
            )

        logger.debug("Kimi CLI is available")

    def check_auth(self) -> bool:
        """Check if Kimi is authenticated by running a simple test command.

        Returns:
            True if authenticated, False otherwise
        """
        logger.debug("Checking Kimi authentication status")

        try:
            result = subprocess.run(
                ["kimi", "--print", "--yolo", "-c", "echo test"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )

            if result.returncode == 0:
                logger.debug("Kimi authentication check passed")
                return True
            else:
                logger.debug(f"Kimi authentication check failed: {result.stderr}")
                return False

        except Exception as e:
            logger.debug(f"Kimi authentication check error: {e}")
            return False

    def setup_auth(self) -> None:
        """Verify Kimi is already authenticated.

        Since Kimi requires manual authentication via the web interface,
        this method checks that authentication is working and provides
        guidance if not.

        Raises:
            RuntimeError: If Kimi is not authenticated
        """
        logger.info("Verifying Kimi CLI authentication")

        if not self.check_auth():
            raise RuntimeError(
                "Kimi CLI is not authenticated. Please run 'kimi' interactively "
                "to complete authentication via the web interface."
            )

        logger.debug("Kimi authentication verified")

    def send_prompt(self, prompt: str) -> str:
        """Send a prompt to Kimi using subprocess in non-interactive mode.

        Args:
            prompt: The prompt/command to send to Kimi

        Returns:
            Kimi's text response

        Raises:
            TimeoutError: If task exceeds timeout
            RuntimeError: If Kimi CLI execution fails
            FileNotFoundError: If Kimi CLI is not installed
        """
        logger.info(f"Sending prompt to Kimi: {prompt[:50]}...")

        cmd = [
            "kimi",
            "--print",
            "--yolo",
            "-w", str(self.working_dir),
            "-c", prompt
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False  # Don't raise on non-zero exit
            )

            # Log stderr if present
            if result.stderr:
                logger.warning(f"Kimi stderr: {result.stderr}")

            # Check return code
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else f"Exit code {result.returncode}"
                raise RuntimeError(f"Kimi CLI failed: {error_msg}")

            logger.debug(f"Kimi returned {len(result.stdout)} characters")
            return result.stdout

        except subprocess.TimeoutExpired as e:
            raise TimeoutError(f"Kimi CLI timed out after {self.timeout} seconds")
        except FileNotFoundError:
            raise RuntimeError(
                "Kimi CLI not found. Install with: uv tool install kimi-cli"
            )
        except Exception as e:
            raise RuntimeError(f"Kimi CLI execution failed: {e}")

    def terminate(self) -> None:
        """Cleanup after session completion.

        With subprocess.run(), cleanup is automatic. This method is kept
        for compatibility with context manager protocol.
        """
        logger.debug("Session cleanup (automatic with subprocess)")

    def __enter__(self):
        """Context manager entry - spawn and verify Kimi is available."""
        self.spawn()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.terminate()
