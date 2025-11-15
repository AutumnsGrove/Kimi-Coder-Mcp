"""Kimi CLI session management with hybrid interactive/one-shot modes.

This module supports two execution modes:
- Interactive mode: Uses pexpect for multi-turn conversations with Kimi
- One-shot mode: Uses subprocess with --print --yolo for simple commands

Default is interactive mode for maximum flexibility.
"""

import logging
import os
import shutil
import subprocess
from typing import Optional
import pexpect

logger = logging.getLogger(__name__)


class KimiSession:
    """Manages Kimi CLI execution with hybrid interactive/one-shot modes.

    Interactive mode (default): Uses pexpect for multi-turn conversations
    where Kimi might ask follow-up questions.

    One-shot mode: Uses subprocess with --print --yolo for simple,
    deterministic commands that don't need interaction.
    """

    def __init__(
        self,
        working_dir: str,
        api_key: Optional[str] = None,
        timeout: int = 300,
        interactive: bool = True
    ):
        """Initialize a Kimi CLI session.

        Args:
            working_dir: Directory where Kimi should operate
            api_key: Optional Moonshot API key (uses env var if not provided)
            timeout: Maximum time to wait for task completion (seconds)
            interactive: If True, use pexpect for multi-turn conversations.
                        If False, use subprocess for one-shot commands.
        """
        self.working_dir = working_dir
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY")
        self.timeout = timeout
        self.interactive = interactive
        self.process: Optional[pexpect.spawn] = None

    def spawn(self) -> None:
        """Spawn Kimi CLI session (interactive) or verify availability (one-shot).

        Raises:
            RuntimeError: If Kimi CLI is not installed or spawn fails
        """
        logger.info(f"Initializing Kimi session ({'interactive' if self.interactive else 'one-shot'}) in {self.working_dir}")

        if shutil.which("kimi") is None:
            raise RuntimeError("Kimi CLI not found. Install with: uv tool install kimi-cli")

        if self.interactive:
            # Spawn pexpect process for interactive mode
            try:
                self.process = pexpect.spawn(
                    "kimi",
                    cwd=self.working_dir,
                    timeout=self.timeout,
                    encoding='utf-8'
                )
                logger.debug("Kimi CLI spawned in interactive mode")
                # Wait for initial prompt (Kimi usually shows a prompt like ">" or "kimi>")
                # You may need to adjust this based on actual Kimi behavior
                self.process.expect([">", pexpect.TIMEOUT], timeout=5)
            except Exception as e:
                raise RuntimeError(f"Failed to spawn Kimi CLI: {e}")
        else:
            logger.debug("Kimi CLI verified (one-shot mode)")

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

    def _send_oneshot(self, prompt: str) -> str:
        """Send a one-shot command using subprocess.

        Args:
            prompt: The prompt/command to send

        Returns:
            Kimi's text response
        """
        logger.info(f"Sending one-shot prompt: {prompt[:50]}...")

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
                check=False
            )

            if result.stderr:
                logger.warning(f"Kimi stderr: {result.stderr}")

            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else f"Exit code {result.returncode}"
                raise RuntimeError(f"Kimi CLI failed: {error_msg}")

            logger.debug(f"Kimi returned {len(result.stdout)} characters")
            return result.stdout

        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Kimi CLI timed out after {self.timeout} seconds")
        except FileNotFoundError:
            raise RuntimeError("Kimi CLI not found. Install with: uv tool install kimi-cli")
        except Exception as e:
            raise RuntimeError(f"Kimi CLI execution failed: {e}")

    def _send_interactive(self, prompt: str) -> str:
        """Send a prompt using interactive pexpect session.

        This allows for multi-turn conversations and follow-up questions.

        Args:
            prompt: The prompt/command to send

        Returns:
            Kimi's text response

        Raises:
            RuntimeError: If session is not active
            TimeoutError: If response times out
        """
        if not self.process or not self.process.isalive():
            raise RuntimeError("Interactive session is not active. Call spawn() first.")

        logger.info(f"Sending interactive prompt: {prompt[:50]}...")

        try:
            # Send the prompt
            self.process.sendline(prompt)

            # Wait for completion indicator
            # Kimi might show completion in various ways - adjust patterns as needed
            # Common patterns: prompt return (">"), specific completion message, etc.
            index = self.process.expect(
                [
                    ">",  # Prompt return
                    "kimi>",  # Alternative prompt
                    pexpect.TIMEOUT
                ],
                timeout=self.timeout
            )

            # Capture output
            output = self.process.before

            if index == 2:  # TIMEOUT
                raise TimeoutError(f"Kimi interactive session timed out after {self.timeout} seconds")

            logger.debug(f"Kimi returned {len(output)} characters")
            return output

        except pexpect.EOF:
            raise RuntimeError("Kimi CLI session ended unexpectedly")
        except pexpect.TIMEOUT:
            raise TimeoutError(f"Kimi interactive session timed out after {self.timeout} seconds")
        except Exception as e:
            raise RuntimeError(f"Kimi interactive session failed: {e}")

    def send_prompt(self, prompt: str) -> str:
        """Send a prompt to Kimi using configured mode.

        Dispatches to interactive or one-shot mode based on session configuration.

        Args:
            prompt: The prompt/command to send

        Returns:
            Kimi's text response

        Raises:
            TimeoutError: If task exceeds timeout
            RuntimeError: If execution fails
        """
        if self.interactive:
            return self._send_interactive(prompt)
        else:
            return self._send_oneshot(prompt)

    def terminate(self) -> None:
        """Cleanup after session completion.

        Interactive mode: Gracefully terminates pexpect process.
        One-shot mode: No-op (subprocess handles cleanup).
        """
        if self.interactive and self.process and self.process.isalive():
            logger.info("Terminating interactive Kimi session")
            try:
                self.process.sendline("exit")
                self.process.expect(pexpect.EOF, timeout=5)
            except:
                # If graceful exit fails, kill it
                self.process.terminate(force=True)
            logger.debug("Interactive session terminated")
        else:
            logger.debug("Session cleanup (automatic with subprocess)")

    def __enter__(self):
        """Context manager entry - spawn and verify Kimi is available."""
        self.spawn()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.terminate()
