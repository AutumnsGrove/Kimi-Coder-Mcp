"""Integration tests for MCP tools."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open

from kimi_mcp import server

# Extract the actual functions from FastMCP wrappers
kimi_code_task = server.kimi_code_task.fn
kimi_analyze_code = server.kimi_analyze_code.fn
kimi_prompt = server.kimi_prompt.fn
kimi_refactor = server.kimi_refactor.fn
kimi_debug = server.kimi_debug.fn


class TestKimiCodeTask:
    """Tests for kimi_code_task tool."""

    @pytest.mark.asyncio
    async def test_basic_task(self, mocker, tmp_path):
        """Test executing a basic coding task."""
        mocker.patch('kimi_mcp.server.os.getcwd', return_value=str(tmp_path))

        # Mock FileTracker
        mock_tracker = Mock()
        mock_tracker.detect_changes.return_value = (["new.py"], [])
        mock_tracker.read_file_contents.return_value = {"new.py": "print('hello')"}
        mocker.patch('kimi_mcp.server.FileTracker', return_value=mock_tracker)

        # Mock KimiSession
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.send_prompt.return_value = "Created hello world function"
        mocker.patch('kimi_mcp.server.KimiSession', return_value=mock_session)

        result = await kimi_code_task("Create a hello world function")

        assert result["success"] == True
        assert result["error"] is None
        assert "new.py" in result["files_created"]
        assert result["file_contents"]["new.py"] == "print('hello')"

        # Verify one-shot mode was used
        server.KimiSession.assert_called_with(str(tmp_path), interactive=False)

    @pytest.mark.asyncio
    async def test_task_with_context_files(self, mocker, tmp_path):
        """Test task with context files provided."""
        mocker.patch('kimi_mcp.server.os.getcwd', return_value=str(tmp_path))

        mock_tracker = Mock()
        mock_tracker.detect_changes.return_value = ([], [])
        mock_tracker.read_file_contents.return_value = {}
        mocker.patch('kimi_mcp.server.FileTracker', return_value=mock_tracker)

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.send_prompt.return_value = "Task complete"
        mocker.patch('kimi_mcp.server.KimiSession', return_value=mock_session)

        result = await kimi_code_task(
            "Update function",
            context_files=["utils.py", "helpers.py"]
        )

        assert result["success"] == True
        # Verify context files were included in prompt
        call_args = mock_session.send_prompt.call_args[0][0]
        assert "utils.py" in call_args
        assert "helpers.py" in call_args

    @pytest.mark.asyncio
    async def test_file_creation(self, mocker, tmp_path):
        """Test that created files are tracked and returned."""
        mocker.patch('kimi_mcp.server.os.getcwd', return_value=str(tmp_path))

        mock_tracker = Mock()
        mock_tracker.detect_changes.return_value = (["file1.py", "file2.py"], [])
        mock_tracker.read_file_contents.return_value = {
            "file1.py": "content1",
            "file2.py": "content2"
        }
        mocker.patch('kimi_mcp.server.FileTracker', return_value=mock_tracker)

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.send_prompt.return_value = "Files created"
        mocker.patch('kimi_mcp.server.KimiSession', return_value=mock_session)

        result = await kimi_code_task("Create two files")

        assert len(result["files_created"]) == 2
        assert "file1.py" in result["files_created"]
        assert "file2.py" in result["files_created"]
        assert result["file_contents"]["file1.py"] == "content1"

    @pytest.mark.asyncio
    async def test_timeout_error(self, mocker, tmp_path):
        """Test timeout handling."""
        mocker.patch('kimi_mcp.server.os.getcwd', return_value=str(tmp_path))
        mocker.patch('kimi_mcp.server.FileTracker')

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.send_prompt.side_effect = TimeoutError("Timed out")
        mocker.patch('kimi_mcp.server.KimiSession', return_value=mock_session)

        result = await kimi_code_task("Long task")

        assert result["success"] == False
        assert result["error"] is not None
        assert "type" in result["error"]


class TestKimiAnalyzeCode:
    """Tests for kimi_analyze_code tool."""

    @pytest.mark.asyncio
    async def test_analyze_single_file(self, mocker, tmp_path):
        """Test analyzing a single file."""
        mocker.patch('kimi_mcp.server.os.getcwd', return_value=str(tmp_path))

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.send_prompt.return_value = "Code looks good. Suggest adding tests."
        mocker.patch('kimi_mcp.server.KimiSession', return_value=mock_session)

        result = await kimi_analyze_code(["main.py"])

        assert result["success"] == True
        assert "good" in result["analysis"]
        assert len(result["suggestions"]) > 0

        # Verify interactive mode was used
        server.KimiSession.assert_called_with(str(tmp_path), interactive=True)

    @pytest.mark.asyncio
    async def test_analyze_multiple_files(self, mocker, tmp_path):
        """Test analyzing multiple files."""
        mocker.patch('kimi_mcp.server.os.getcwd', return_value=str(tmp_path))

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.send_prompt.return_value = "Analysis complete"
        mocker.patch('kimi_mcp.server.KimiSession', return_value=mock_session)

        result = await kimi_analyze_code(["file1.py", "file2.py", "file3.py"])

        assert result["success"] == True
        call_args = mock_session.send_prompt.call_args[0][0]
        assert "file1.py" in call_args
        assert "file2.py" in call_args
        assert "file3.py" in call_args

    @pytest.mark.asyncio
    async def test_focused_analysis(self, mocker, tmp_path):
        """Test analysis with specific focus."""
        mocker.patch('kimi_mcp.server.os.getcwd', return_value=str(tmp_path))

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.send_prompt.return_value = "Recommend using type hints"
        mocker.patch('kimi_mcp.server.KimiSession', return_value=mock_session)

        result = await kimi_analyze_code(
            ["utils.py"],
            analysis_focus="type safety"
        )

        assert result["success"] == True
        call_args = mock_session.send_prompt.call_args[0][0]
        assert "type safety" in call_args


class TestKimiPrompt:
    """Tests for kimi_prompt tool."""

    @pytest.mark.asyncio
    async def test_generic_prompt(self, mocker, tmp_path):
        """Test sending a generic prompt."""
        mocker.patch('kimi_mcp.server.os.getcwd', return_value=str(tmp_path))

        mock_tracker = Mock()
        mock_tracker.detect_changes.return_value = ([], [])
        mock_tracker.read_file_contents.return_value = {}
        mocker.patch('kimi_mcp.server.FileTracker', return_value=mock_tracker)

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.send_prompt.return_value = "Response to prompt"
        mocker.patch('kimi_mcp.server.KimiSession', return_value=mock_session)

        result = await kimi_prompt("Explain recursion")

        assert result["success"] == True
        assert result["output"] == "Response to prompt"

        # Verify interactive mode
        server.KimiSession.assert_called_with(str(tmp_path), interactive=True)

    @pytest.mark.asyncio
    async def test_with_workspace_context(self, mocker, tmp_path):
        """Test prompt with workspace context included."""
        mocker.patch('kimi_mcp.server.os.getcwd', return_value=str(tmp_path))

        # Create fake Python files
        (tmp_path / "test1.py").write_text("# test file 1")
        (tmp_path / "test2.py").write_text("# test file 2")

        mock_tracker = Mock()
        mock_tracker.detect_changes.return_value = ([], [])
        mock_tracker.read_file_contents.return_value = {}
        mocker.patch('kimi_mcp.server.FileTracker', return_value=mock_tracker)

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.send_prompt.return_value = "Analyzed workspace"
        mocker.patch('kimi_mcp.server.KimiSession', return_value=mock_session)

        result = await kimi_prompt(
            "What files are in this project?",
            include_workspace_context=True
        )

        assert result["success"] == True
        call_args = mock_session.send_prompt.call_args[0][0]
        assert "Workspace files" in call_args or "test1.py" in call_args or "test2.py" in call_args


class TestKimiRefactor:
    """Tests for kimi_refactor tool."""

    @pytest.mark.asyncio
    async def test_basic_refactoring(self, mocker, tmp_path):
        """Test basic code refactoring."""
        mocker.patch('kimi_mcp.server.os.getcwd', return_value=str(tmp_path))

        # Create file to refactor
        test_file = tmp_path / "code.py"
        original_content = "def old_func(): pass"
        test_file.write_text(original_content)

        mock_tracker = Mock()
        mock_tracker.detect_changes.return_value = ([], ["code.py"])
        mocker.patch('kimi_mcp.server.FileTracker', return_value=mock_tracker)

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)

        # Simulate refactoring by updating file when send_prompt is called
        def mock_send_prompt(prompt):
            test_file.write_text("def new_func(): pass")
            return "Refactored successfully"

        mock_session.send_prompt = mock_send_prompt
        mocker.patch('kimi_mcp.server.KimiSession', return_value=mock_session)

        result = await kimi_refactor("code.py", "Rename function")

        assert result["success"] == True
        assert result["original_content"] == original_content
        assert "code.py" in result["files_modified"]
        assert result["refactored_content"] == "def new_func(): pass"

        # Verify one-shot mode
        server.KimiSession.assert_called_with(str(tmp_path), interactive=False)

    @pytest.mark.asyncio
    async def test_refactor_nonexistent_file(self, mocker, tmp_path):
        """Test refactoring a nonexistent file."""
        mocker.patch('kimi_mcp.server.os.getcwd', return_value=str(tmp_path))

        result = await kimi_refactor("nonexistent.py", "Refactor this")

        assert result["success"] == False
        assert result["error"] is not None
        assert "FileNotFoundError" in result["error"]["type"]


class TestKimiDebug:
    """Tests for kimi_debug tool."""

    @pytest.mark.asyncio
    async def test_debug_simple_error(self, mocker, tmp_path):
        """Test debugging a simple error."""
        mocker.patch('kimi_mcp.server.os.getcwd', return_value=str(tmp_path))

        mock_tracker = Mock()
        mock_tracker.detect_changes.return_value = ([], [])
        mocker.patch('kimi_mcp.server.FileTracker', return_value=mock_tracker)

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.send_prompt.return_value = "The issue is a typo.\nSolution: fix the variable name"
        mocker.patch('kimi_mcp.server.KimiSession', return_value=mock_session)

        result = await kimi_debug(
            "NameError: name 'x' is not defined",
            ["main.py"]
        )

        assert result["success"] == True
        assert "typo" in result["diagnosis"] or "typo" in result["code_changes"]
        assert len(result["solution"]) > 0

        # Verify interactive mode
        server.KimiSession.assert_called_with(str(tmp_path), interactive=True)

    @pytest.mark.asyncio
    async def test_debug_with_context(self, mocker, tmp_path):
        """Test debugging with additional context."""
        mocker.patch('kimi_mcp.server.os.getcwd', return_value=str(tmp_path))

        mock_tracker = Mock()
        mock_tracker.detect_changes.return_value = ([], [])
        mocker.patch('kimi_mcp.server.FileTracker', return_value=mock_tracker)

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.send_prompt.return_value = "Debug complete"
        mocker.patch('kimi_mcp.server.KimiSession', return_value=mock_session)

        result = await kimi_debug(
            "Error in production",
            ["api.py"],
            context="This only happens with large datasets"
        )

        assert result["success"] == True
        call_args = mock_session.send_prompt.call_args[0][0]
        assert "large datasets" in call_args
