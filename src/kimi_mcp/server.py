"""FastMCP server implementation for Kimi CLI integration.

This module implements the MCP server that exposes Kimi's coding capabilities
through 5 specialized tools.
"""

from typing import Any, Dict, List, Optional
import logging
import os
from pathlib import Path

from fastmcp import FastMCP

from .file_tracker import FileTracker
from .session import KimiSession
from .utils import format_error

# Initialize FastMCP server
app = FastMCP("kimi-coder")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@app.tool()
async def kimi_code_task(
    task_description: str,
    context_files: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Execute a coding task with Kimi.

    Args:
        task_description: Detailed description of the coding task
        context_files: Optional list of file paths to include as context

    Returns:
        Dict containing:
        - output: Kimi's text response
        - files_created: List of created file paths
        - files_modified: List of modified file paths
        - file_contents: Dict mapping file paths to their contents
        - success: Boolean indicating success
        - error: Error message if failed, None otherwise
    """
    logger.info(f"kimi_code_task: {task_description[:50]}...")

    working_dir = os.getcwd()

    try:
        # Initialize file tracker
        tracker = FileTracker(working_dir)
        tracker.take_initial_snapshot()

        # Build prompt with context files if provided
        prompt = task_description
        if context_files:
            prompt += f"\n\nRelevant files: {', '.join(context_files)}"

        # Execute with Kimi (one-shot mode for simple tasks)
        with KimiSession(working_dir, interactive=False) as session:
            output = session.send_prompt(prompt)

        # Detect changes
        tracker.take_final_snapshot()
        created, modified = tracker.detect_changes()
        all_changed = created + modified
        file_contents = tracker.read_file_contents(all_changed)

        logger.info(f"Task complete: {len(created)} created, {len(modified)} modified")

        return {
            "output": output,
            "files_created": created,
            "files_modified": modified,
            "file_contents": file_contents,
            "success": True,
            "error": None
        }

    except TimeoutError as e:
        logger.error(f"Timeout: {e}")
        return {
            "output": "",
            "files_created": [],
            "files_modified": [],
            "file_contents": {},
            "success": False,
            "error": format_error("TimeoutError", str(e),
                                 suggestion="Try breaking the task into smaller pieces")
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "output": "",
            "files_created": [],
            "files_modified": [],
            "file_contents": {},
            "success": False,
            "error": format_error("ExecutionError", str(e))
        }


@app.tool()
async def kimi_analyze_code(
    file_paths: List[str],
    analysis_focus: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze existing code files with Kimi.

    Args:
        file_paths: List of file paths to analyze
        analysis_focus: Optional specific aspect to focus on

    Returns:
        Dict containing:
        - analysis: Detailed analysis from Kimi
        - suggestions: List of improvement suggestions
        - success: Boolean indicating success
        - error: Error message if failed, None otherwise
    """
    logger.info(f"kimi_analyze_code: {file_paths}")

    working_dir = os.getcwd()

    try:
        # Build analysis prompt
        prompt = f"Analyze the following files:\n{', '.join(file_paths)}"
        if analysis_focus:
            prompt += f"\n\nFocus on: {analysis_focus}"

        # Execute with Kimi (interactive mode for analysis)
        with KimiSession(working_dir, interactive=True) as session:
            output = session.send_prompt(prompt)

        # Parse output for suggestions (simple split on newlines)
        suggestions = [line for line in output.split('\n')
                      if line.strip() and ('suggest' in line.lower() or
                                          'recommend' in line.lower() or
                                          'improve' in line.lower())]

        logger.info(f"Analysis complete: {len(suggestions)} suggestions")

        return {
            "analysis": output,
            "suggestions": suggestions,
            "success": True,
            "error": None
        }

    except TimeoutError as e:
        logger.error(f"Timeout: {e}")
        return {
            "analysis": "",
            "suggestions": [],
            "success": False,
            "error": format_error("TimeoutError", str(e))
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "analysis": "",
            "suggestions": [],
            "success": False,
            "error": format_error("ExecutionError", str(e))
        }


@app.tool()
async def kimi_prompt(
    prompt: str,
    include_workspace_context: bool = False
) -> Dict[str, Any]:
    """Send a generic prompt to Kimi.

    Args:
        prompt: The prompt to send to Kimi
        include_workspace_context: Whether to include file structure context

    Returns:
        Dict containing:
        - output: Kimi's text response
        - files_created: List of created file paths
        - files_modified: List of modified file paths
        - file_contents: Dict mapping file paths to their contents
        - success: Boolean indicating success
        - error: Error message if failed, None otherwise
    """
    logger.info(f"kimi_prompt: {prompt[:50]}...")

    working_dir = os.getcwd()

    try:
        # Initialize file tracker
        tracker = FileTracker(working_dir)
        tracker.take_initial_snapshot()

        # Add workspace context if requested
        full_prompt = prompt
        if include_workspace_context:
            # Get list of files in working directory
            files = list(Path(working_dir).rglob('*.py'))[:20]  # Limit to 20
            file_list = '\n'.join(str(f.relative_to(working_dir)) for f in files)
            full_prompt += f"\n\nWorkspace files:\n{file_list}"

        # Execute with Kimi (interactive mode for flexibility)
        with KimiSession(working_dir, interactive=True) as session:
            output = session.send_prompt(full_prompt)

        # Detect changes
        tracker.take_final_snapshot()
        created, modified = tracker.detect_changes()
        all_changed = created + modified
        file_contents = tracker.read_file_contents(all_changed)

        logger.info(f"Prompt complete: {len(created)} created, {len(modified)} modified")

        return {
            "output": output,
            "files_created": created,
            "files_modified": modified,
            "file_contents": file_contents,
            "success": True,
            "error": None
        }

    except TimeoutError as e:
        logger.error(f"Timeout: {e}")
        return {
            "output": "",
            "files_created": [],
            "files_modified": [],
            "file_contents": {},
            "success": False,
            "error": format_error("TimeoutError", str(e))
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "output": "",
            "files_created": [],
            "files_modified": [],
            "file_contents": {},
            "success": False,
            "error": format_error("ExecutionError", str(e))
        }


@app.tool()
async def kimi_refactor(
    file_path: str,
    refactor_instructions: str
) -> Dict[str, Any]:
    """Refactor existing code with Kimi.

    Args:
        file_path: Path to the file to refactor
        refactor_instructions: Instructions for refactoring

    Returns:
        Dict containing:
        - original_content: Original file content
        - refactored_content: New file content
        - explanation: What changed and why
        - files_modified: List of modified file paths
        - success: Boolean indicating success
        - error: Error message if failed, None otherwise
    """
    logger.info(f"kimi_refactor: {file_path}")

    working_dir = os.getcwd()

    try:
        # Read original content
        full_path = Path(working_dir) / file_path
        original_content = ""
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        else:
            raise FileNotFoundError(f"File not found: {file_path}")

        # Initialize file tracker
        tracker = FileTracker(working_dir)
        tracker.take_initial_snapshot()

        # Build refactoring prompt
        prompt = f"Refactor {file_path}:\n{refactor_instructions}"

        # Execute with Kimi (one-shot for specific refactoring)
        with KimiSession(working_dir, interactive=False) as session:
            output = session.send_prompt(prompt)

        # Detect changes
        tracker.take_final_snapshot()
        created, modified = tracker.detect_changes()

        # Read refactored content
        refactored_content = ""
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                refactored_content = f.read()

        logger.info(f"Refactor complete: {len(modified)} files modified")

        return {
            "original_content": original_content,
            "refactored_content": refactored_content,
            "explanation": output,
            "files_modified": modified,
            "success": True,
            "error": None
        }

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return {
            "original_content": "",
            "refactored_content": "",
            "explanation": "",
            "files_modified": [],
            "success": False,
            "error": format_error("FileNotFoundError", str(e))
        }
    except TimeoutError as e:
        logger.error(f"Timeout: {e}")
        return {
            "original_content": "",
            "refactored_content": "",
            "explanation": "",
            "files_modified": [],
            "success": False,
            "error": format_error("TimeoutError", str(e))
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "original_content": "",
            "refactored_content": "",
            "explanation": "",
            "files_modified": [],
            "success": False,
            "error": format_error("ExecutionError", str(e))
        }


@app.tool()
async def kimi_debug(
    error_message: str,
    relevant_files: List[str],
    context: Optional[str] = None
) -> Dict[str, Any]:
    """Debug errors with Kimi's help.

    Args:
        error_message: The error description or message
        relevant_files: List of files related to the error
        context: Optional additional context

    Returns:
        Dict containing:
        - diagnosis: What's causing the error
        - solution: How to fix it
        - code_changes: Suggested code changes
        - files_modified: List of files modified (if Kimi fixed them)
        - success: Boolean indicating success
        - error: Error message if failed, None otherwise
    """
    logger.info(f"kimi_debug: {error_message[:50]}...")

    working_dir = os.getcwd()

    try:
        # Initialize file tracker
        tracker = FileTracker(working_dir)
        tracker.take_initial_snapshot()

        # Build debugging prompt
        prompt = f"Debug this error:\n{error_message}\n\nRelevant files: {', '.join(relevant_files)}"
        if context:
            prompt += f"\n\nContext: {context}"

        # Execute with Kimi (interactive mode for debugging)
        with KimiSession(working_dir, interactive=True) as session:
            output = session.send_prompt(prompt)

        # Detect changes (Kimi might have fixed the issue)
        tracker.take_final_snapshot()
        created, modified = tracker.detect_changes()

        # Parse output for diagnosis and solution
        # Simple heuristic: first part is diagnosis, rest is solution
        lines = output.split('\n')
        diagnosis = output  # Default to full output
        solution = ""
        code_changes = ""

        # Try to extract structured info
        for i, line in enumerate(lines):
            if 'solution' in line.lower() or 'fix' in line.lower():
                diagnosis = '\n'.join(lines[:i])
                solution = '\n'.join(lines[i:])
                break

        logger.info(f"Debug complete: {len(modified)} files modified")

        return {
            "diagnosis": diagnosis,
            "solution": solution,
            "code_changes": output,  # Full output as code changes
            "files_modified": modified,
            "success": True,
            "error": None
        }

    except TimeoutError as e:
        logger.error(f"Timeout: {e}")
        return {
            "diagnosis": "",
            "solution": "",
            "code_changes": "",
            "files_modified": [],
            "success": False,
            "error": format_error("TimeoutError", str(e))
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "diagnosis": "",
            "solution": "",
            "code_changes": "",
            "files_modified": [],
            "success": False,
            "error": format_error("ExecutionError", str(e))
        }


def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Kimi-Coder MCP Server...")
    app.run()


if __name__ == "__main__":
    main()
