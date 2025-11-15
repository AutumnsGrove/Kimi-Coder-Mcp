"""Tests for Kimi CLI session management."""

import subprocess
import pytest
import pexpect
from kimi_mcp.session import KimiSession


class TestKimiSession:
    """Test suite for KimiSession class."""

    def test_session_initialization(self, tmp_path):
        """Test that KimiSession can be initialized with correct parameters."""
        # Test interactive mode (default)
        session_interactive = KimiSession(str(tmp_path))
        assert session_interactive.working_dir == str(tmp_path)
        assert session_interactive.interactive == True
        assert session_interactive.timeout == 300
        assert session_interactive.process is None

        # Test one-shot mode
        session_oneshot = KimiSession(str(tmp_path), interactive=False)
        assert session_oneshot.interactive == False
        assert session_oneshot.working_dir == str(tmp_path)

        # Test with custom timeout
        session_custom = KimiSession(str(tmp_path), timeout=600)
        assert session_custom.timeout == 600

        # Test with API key
        session_with_key = KimiSession(str(tmp_path), api_key="test-key")
        assert session_with_key.api_key == "test-key"

    def test_spawn_process_interactive(self, tmp_path, mocker):
        """Test spawning a Kimi CLI process in interactive mode."""
        # Mock shutil.which to return kimi path
        mocker.patch('kimi_mcp.session.shutil.which', return_value='/usr/bin/kimi')

        # Mock pexpect.spawn
        mock_spawn = mocker.patch('kimi_mcp.session.pexpect.spawn')
        mock_process = mocker.Mock()
        mock_process.expect.return_value = 0  # Prompt found
        mock_spawn.return_value = mock_process

        session = KimiSession(str(tmp_path), interactive=True)
        session.spawn()

        # Verify spawn was called
        mock_spawn.assert_called_once_with(
            "kimi",
            cwd=str(tmp_path),
            timeout=300,
            encoding='utf-8'
        )

        # Verify expect was called for initial prompt
        mock_process.expect.assert_called_once()
        assert session.process is not None

    def test_spawn_process_oneshot(self, tmp_path, mocker):
        """Test spawn in one-shot mode (verification only)."""
        # Mock shutil.which to return kimi path
        mocker.patch('kimi_mcp.session.shutil.which', return_value='/usr/bin/kimi')

        session = KimiSession(str(tmp_path), interactive=False)
        session.spawn()

        # In one-shot mode, no process is spawned
        assert session.process is None

    def test_spawn_kimi_not_found(self, tmp_path, mocker):
        """Test that spawn fails when Kimi CLI is not found."""
        # Mock shutil.which to return None (kimi not found)
        mocker.patch('kimi_mcp.session.shutil.which', return_value=None)

        session = KimiSession(str(tmp_path))

        with pytest.raises(RuntimeError, match="Kimi CLI not found"):
            session.spawn()

    def test_auth_check(self, tmp_path, mocker):
        """Test authentication status checking."""
        # Mock subprocess.run for auth check
        mock_result = mocker.Mock()
        mock_result.returncode = 0
        mock_result.stdout = "test"
        mock_result.stderr = ""
        mock_run = mocker.patch('kimi_mcp.session.subprocess.run', return_value=mock_result)

        session = KimiSession(str(tmp_path))
        result = session.check_auth()

        assert result == True
        mock_run.assert_called_once()

        # Verify command structure
        call_args = mock_run.call_args[0][0]
        assert "kimi" in call_args
        assert "--print" in call_args
        assert "--yolo" in call_args

    def test_auth_check_failed(self, tmp_path, mocker):
        """Test authentication check when Kimi is not authenticated."""
        # Mock subprocess.run for failed auth
        mock_result = mocker.Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Not authenticated"
        mocker.patch('kimi_mcp.session.subprocess.run', return_value=mock_result)

        session = KimiSession(str(tmp_path))
        result = session.check_auth()

        assert result == False

    def test_setup_auth(self, tmp_path, mocker):
        """Test running the setup auth flow."""
        # Mock check_auth to return True
        mocker.patch.object(KimiSession, 'check_auth', return_value=True)

        session = KimiSession(str(tmp_path))
        # Should not raise any errors
        session.setup_auth()

    def test_setup_auth_failed(self, tmp_path, mocker):
        """Test setup auth flow when authentication is not working."""
        # Mock check_auth to return False
        mocker.patch.object(KimiSession, 'check_auth', return_value=False)

        session = KimiSession(str(tmp_path))

        with pytest.raises(RuntimeError, match="not authenticated"):
            session.setup_auth()

    def test_send_prompt_oneshot(self, tmp_path, mocker):
        """Test sending a prompt in one-shot mode."""
        # Mock subprocess.run
        mock_result = mocker.Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Kimi response here"
        mock_result.stderr = ""
        mock_run = mocker.patch('kimi_mcp.session.subprocess.run', return_value=mock_result)

        session = KimiSession(str(tmp_path), interactive=False)
        response = session.send_prompt("create hello.py")

        assert response == "Kimi response here"
        mock_run.assert_called_once()

        # Verify command structure
        call_args = mock_run.call_args[0][0]
        assert "kimi" in call_args
        assert "--print" in call_args
        assert "--yolo" in call_args
        assert "-w" in call_args
        assert "-c" in call_args
        assert "create hello.py" in call_args

    def test_send_prompt_interactive(self, tmp_path, mocker):
        """Test sending a prompt in interactive mode."""
        # Mock shutil.which
        mocker.patch('kimi_mcp.session.shutil.which', return_value='/usr/bin/kimi')

        # Mock pexpect.spawn
        mock_process = mocker.Mock()
        mock_process.isalive.return_value = True
        mock_process.before = "Kimi interactive response"
        mock_process.expect.return_value = 0  # Prompt returned (index 0 = ">")
        mocker.patch('kimi_mcp.session.pexpect.spawn', return_value=mock_process)

        session = KimiSession(str(tmp_path), interactive=True)
        session.spawn()

        response = session.send_prompt("analyze code.py")

        assert response == "Kimi interactive response"
        # Verify sendline was called twice: once during spawn expect, once for actual prompt
        assert mock_process.sendline.call_count >= 1
        mock_process.sendline.assert_called_with("analyze code.py")

    def test_send_prompt_interactive_not_spawned(self, tmp_path):
        """Test that interactive mode fails if session not spawned."""
        session = KimiSession(str(tmp_path), interactive=True)

        with pytest.raises(RuntimeError, match="not active"):
            session.send_prompt("test")

    def test_timeout_handling_oneshot(self, tmp_path, mocker):
        """Test timeout handling in one-shot mode."""
        # Mock subprocess.run to raise TimeoutExpired
        mocker.patch(
            'kimi_mcp.session.subprocess.run',
            side_effect=subprocess.TimeoutExpired("kimi", 300)
        )

        session = KimiSession(str(tmp_path), interactive=False, timeout=300)

        with pytest.raises(TimeoutError, match="timed out after 300 seconds"):
            session.send_prompt("long task")

    def test_timeout_handling_interactive(self, tmp_path, mocker):
        """Test timeout handling in interactive mode."""
        mocker.patch('kimi_mcp.session.shutil.which', return_value='/usr/bin/kimi')

        mock_process = mocker.Mock()
        mock_process.isalive.return_value = True
        # First expect for spawn succeeds, second expect times out
        mock_process.expect.side_effect = [0, pexpect.TIMEOUT("timeout")]
        mocker.patch('kimi_mcp.session.pexpect.spawn', return_value=mock_process)

        session = KimiSession(str(tmp_path), interactive=True)
        session.spawn()

        with pytest.raises(TimeoutError):
            session.send_prompt("long task")

    def test_graceful_termination_interactive(self, tmp_path, mocker):
        """Test that interactive sessions are terminated cleanly."""
        mocker.patch('kimi_mcp.session.shutil.which', return_value='/usr/bin/kimi')

        mock_process = mocker.Mock()
        mock_process.isalive.return_value = True
        mock_process.expect.return_value = 0
        mocker.patch('kimi_mcp.session.pexpect.spawn', return_value=mock_process)

        session = KimiSession(str(tmp_path), interactive=True)
        session.spawn()
        session.terminate()

        # Verify graceful exit was attempted
        mock_process.sendline.assert_any_call("exit")

    def test_graceful_termination_oneshot(self, tmp_path):
        """Test that one-shot mode termination is a no-op."""
        session = KimiSession(str(tmp_path), interactive=False)
        # Should not raise any errors (no-op for one-shot)
        session.terminate()

    def test_context_manager_oneshot(self, tmp_path, mocker):
        """Test using KimiSession as a context manager in one-shot mode."""
        mocker.patch('kimi_mcp.session.shutil.which', return_value='/usr/bin/kimi')

        with KimiSession(str(tmp_path), interactive=False) as session:
            assert session is not None
            assert session.interactive == False

        # Cleanup should happen automatically

    def test_context_manager_interactive(self, tmp_path, mocker):
        """Test using KimiSession as a context manager in interactive mode."""
        mocker.patch('kimi_mcp.session.shutil.which', return_value='/usr/bin/kimi')

        mock_process = mocker.Mock()
        mock_process.isalive.return_value = True
        mock_process.expect.return_value = 0
        mocker.patch('kimi_mcp.session.pexpect.spawn', return_value=mock_process)

        with KimiSession(str(tmp_path), interactive=True) as session:
            assert session is not None
            assert session.process is not None

        # Verify terminate was called
        mock_process.sendline.assert_any_call("exit")

    def test_send_prompt_subprocess_error(self, tmp_path, mocker):
        """Test error handling when subprocess command fails."""
        # Mock subprocess.run to return non-zero exit code
        mock_result = mocker.Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Command failed"
        mocker.patch('kimi_mcp.session.subprocess.run', return_value=mock_result)

        session = KimiSession(str(tmp_path), interactive=False)

        with pytest.raises(RuntimeError, match="Kimi CLI failed"):
            session.send_prompt("bad command")

    def test_send_prompt_interactive_eof(self, tmp_path, mocker):
        """Test handling of unexpected EOF in interactive mode."""
        mocker.patch('kimi_mcp.session.shutil.which', return_value='/usr/bin/kimi')

        mock_process = mocker.Mock()
        mock_process.isalive.return_value = True
        # First expect for spawn succeeds, second raises EOF
        mock_process.expect.side_effect = [0, pexpect.EOF("unexpected EOF")]
        mocker.patch('kimi_mcp.session.pexpect.spawn', return_value=mock_process)

        session = KimiSession(str(tmp_path), interactive=True)
        session.spawn()

        with pytest.raises(RuntimeError, match="ended unexpectedly"):
            session.send_prompt("test prompt")
