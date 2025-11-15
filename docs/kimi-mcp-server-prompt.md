# Kimi CLI MCP Server - Project Prompt

Create an MCP server that wraps Kimi CLI, enabling Claude Code to use Kimi as an on-demand coding subagent. This server will expose Kimi's agentic coding capabilities through the Model Context Protocol.

## Project Overview

**Goal**: Build a FastMCP-based server that spawns and manages Kimi CLI sessions, allowing Claude Code to delegate coding tasks to Kimi while maintaining file artifacts and working within the current project workspace.

**Key Design Decisions**:
- Language: Python with FastMCP
- Session Management: Ephemeral (new session per tool call)
- Working Directory: Current project root where MCP server runs
- Response Format: File artifacts + structured output
- API Key: From MCP server config, with fallback login if needed

## Architecture

### Session Management Strategy

Since Kimi CLI is an interactive chat-based tool, we need to:
1. Use `pexpect` to spawn and control Kimi CLI processes programmatically
2. Create ephemeral sessions for each tool call
3. Send commands, wait for completion, capture output
4. Extract created/modified files from the working directory
5. Gracefully terminate sessions

### Tools to Implement

1. **kimi_code_task**: Send a coding task to Kimi, returns created/modified files
2. **kimi_analyze_code**: Have Kimi analyze existing files in the project
3. **kimi_prompt**: Generic prompt interface for any Kimi interaction
4. **kimi_refactor**: Refactor existing code with specific instructions
5. **kimi_debug**: Debug an error or issue with detailed analysis

## Technical Requirements

### Dependencies

**Package Manager: UV**
Use UV for all package management, virtual environments, and running the server.

```toml
# pyproject.toml
[project]
name = "kimi-mcp-server"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastmcp",
    "pexpect",
]

[project.scripts]
kimi-mcp = "kimi_mcp.server:main"
```

Setup with UV:
```bash
# Initialize project
uv init

# Add dependencies
uv add fastmcp pexpect

# Run the server
uv run kimi-mcp

# Or for development
uv run python -m kimi_mcp.server
```

### Project Structure

```
kimi-mcp-server/
├── src/
│   ├── kimi_mcp/
│   │   ├── __init__.py
│   │   ├── server.py           # Main MCP server
│   │   ├── session.py          # Kimi CLI session management
│   │   ├── file_tracker.py     # Track file changes
│   │   └── utils.py            # Helper functions
├── pyproject.toml
├── README.md
└── .env.example
```

## Implementation Details

### 1. Kimi Session Manager (session.py)

Create a class that:
- Spawns Kimi CLI using `pexpect`
- Detects if Kimi is logged in, performs setup if needed
- Sends prompts and waits for completion
- Tracks filesystem changes during execution
- Returns both text output and file artifacts
- Handles timeouts and errors gracefully

Key considerations:
- Watch for Kimi's prompts (likely `> ` or similar)
- Handle the `/setup` flow if API key needs configuration
- Detect when Kimi finishes a task (look for prompt return)
- Capture all files created/modified in working directory
- Clean up processes on completion or error

### 2. File Tracking (file_tracker.py)

Implement file system monitoring:
- Snapshot directory state before Kimi runs
- Compare after Kimi completes task
- Return list of created/modified files with their content
- Handle binary files gracefully (skip or note them)

### 3. FastMCP Server (server.py)

Implement these tools using FastMCP:

#### Tool: kimi_code_task
```python
@mcp.tool()
def kimi_code_task(task_description: str, context_files: list[str] = None) -> dict:
    """
    Execute a coding task with Kimi CLI.
    
    Args:
        task_description: Detailed description of the coding task
        context_files: Optional list of file paths to include as context
    
    Returns:
        {
            "output": "Kimi's text response",
            "files_created": ["path1", "path2"],
            "files_modified": ["path3", "path4"],
            "file_contents": {"path1": "content...", "path2": "content..."},
            "success": true,
            "error": null
        }
    """
    pass
```

#### Tool: kimi_analyze_code
```python
@mcp.tool()
def kimi_analyze_code(file_paths: list[str], analysis_focus: str = None) -> dict:
    """
    Analyze existing code files with Kimi.
    
    Args:
        file_paths: List of files to analyze
        analysis_focus: Optional specific aspect to focus on (e.g., "security", "performance")
    
    Returns:
        {
            "analysis": "Kimi's detailed analysis",
            "suggestions": ["suggestion1", "suggestion2"],
            "success": true,
            "error": null
        }
    """
    pass
```

#### Tool: kimi_prompt
```python
@mcp.tool()
def kimi_prompt(prompt: str, include_workspace_context: bool = True) -> dict:
    """
    Send a generic prompt to Kimi.
    
    Args:
        prompt: The prompt to send to Kimi
        include_workspace_context: Whether to include workspace file structure
    
    Returns:
        {
            "response": "Kimi's response",
            "files_created": [...],
            "files_modified": [...],
            "file_contents": {...},
            "success": true,
            "error": null
        }
    """
    pass
```

#### Tool: kimi_refactor
```python
@mcp.tool()
def kimi_refactor(file_path: str, refactor_instructions: str) -> dict:
    """
    Refactor existing code with Kimi.
    
    Args:
        file_path: Path to file to refactor
        refactor_instructions: Specific refactoring instructions
    
    Returns:
        {
            "original_content": "...",
            "refactored_content": "...",
            "explanation": "What changed and why",
            "files_modified": [...],
            "success": true,
            "error": null
        }
    """
    pass
```

#### Tool: kimi_debug
```python
@mcp.tool()
def kimi_debug(error_message: str, relevant_files: list[str], context: str = None) -> dict:
    """
    Debug an error or issue with Kimi's help.
    
    Args:
        error_message: The error message or issue description
        relevant_files: Files related to the error
        context: Additional context about what you were trying to do
    
    Returns:
        {
            "diagnosis": "What's wrong",
            "solution": "How to fix it",
            "code_changes": "Suggested code changes",
            "files_modified": [...],
            "success": true,
            "error": null
        }
    """
    pass
```

### 4. API Key & Authentication Handling

Priority order:
1. Check if Kimi CLI is already logged in (test by spawning `kimi --help` or checking config)
2. If not logged in, look for `MOONSHOT_API_KEY` in MCP server config
3. If API key found, run `/setup` flow to configure Kimi
4. If no API key and not logged in, return clear error message

### 5. Configuration (MCP Server Config)

Example MCP server configuration that users will add:
```json
{
  "mcpServers": {
    "kimi-agent": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/kimi-mcp-server",
        "kimi-mcp"
      ],
      "env": {
        "MOONSHOT_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

The server will be invoked via `uv run kimi-mcp`, which uses UV's tool running capability.

## Error Handling

Implement robust error handling for:
- Kimi CLI not installed
- Kimi CLI crashes or hangs
- Timeout on long-running tasks (configurable, default 5 minutes)
- API key invalid or missing
- File system permission errors
- Process cleanup on errors

## Testing Strategy

Create tests for:
1. Session spawning and teardown
2. Command sending and response parsing
3. File tracking accuracy
4. Error scenarios (timeout, crashes)
5. API key configuration flow

## Documentation

Include in README.md:
1. Installation instructions (including `uv tool install kimi-cli`)
2. MCP server configuration examples
3. Tool usage examples from Claude Code's perspective
4. Troubleshooting guide
5. Architecture diagram showing Claude Code → MCP → Kimi CLI flow

## Development Workflow

**Use UV for all operations:**

```bash
# Initial setup
uv init
uv add fastmcp pexpect

# Run during development
uv run python -m kimi_mcp.server

# Run tests
uv run pytest

# Install as tool for testing
uv tool install --editable .
```

Development steps:
1. Start with basic session management (spawn, send command, read response)
2. Implement file tracking system
3. Build the simplest tool first (`kimi_prompt`)
4. Add structured tools (`kimi_code_task`, etc.)
5. Implement API key handling and setup flow
6. Add comprehensive error handling
7. Write tests
8. Document everything

## Success Criteria

The MCP server should:
- ✅ Successfully spawn Kimi CLI sessions
- ✅ Send prompts and receive responses
- ✅ Track and return file artifacts
- ✅ Handle API key configuration automatically
- ✅ Gracefully handle errors and timeouts
- ✅ Clean up processes properly
- ✅ Work seamlessly from Claude Code
- ✅ Provide clear, structured responses

## Extra Credit Features (Optional, for later)

- Persistent session mode (reuse session across calls for context)
- Streaming responses for long tasks
- Progress updates for complex operations
- Token usage tracking and reporting
- Automatic workspace context injection
- Integration with git for safer file modifications

## Notes

- Remember: The goal is giving Claude Code access to Kimi's agentic abilities
- Focus on file artifacts over text responses
- Keep sessions ephemeral for simplicity (can add persistence later)
- Make error messages helpful for debugging
- Consider rate limiting if Moonshot AI has API limits

## Implementation Approach

Use functional-OOP hybrid style with data transformation emphasis:
- Small, focused functions
- Map/filter/comprehensions for data processing
- Clear separation between session management and tool logic
- Avoid deep inheritance hierarchies
- Composition over inheritance

---

## Before We Start: Clarification Questions

**IMPORTANT**: Before beginning implementation, please ask me to clarify:

1. **Any ambiguous requirements** - If anything in this spec is unclear or could be interpreted multiple ways
2. **Missing information** - If you need details about error handling, edge cases, or specific behaviors
3. **Technical uncertainties** - If you're unsure about how `pexpect` should interact with Kimi CLI's interactive prompts
4. **Tool design questions** - If you think a tool should work differently or need more parameters
5. **File tracking concerns** - If the file monitoring approach needs refinement
6. **Testing strategy** - If you need guidance on what should be tested or how
7. **Configuration details** - If the MCP server config or API key handling needs clarification
8. **Any other concerns** - Anything else that would help you build this more effectively

**Please list all your questions before starting any implementation.** I want to make sure we're aligned before you write code.

---

Let me know if you need any clarification before starting! This should give you a solid foundation for building a powerful Kimi CLI MCP server wrapper.
