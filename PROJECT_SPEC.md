# Kimi-Coder-MCP Project Specification

## Project Metadata

**Project Name**: Kimi-Coder-MCP  
**Version**: 0.1.0 (initial development)  
**Repository**: autumnsgrove/kimi-coder-mcp  
**Visibility**: Public  
**License**: Apache 2.0 (matching Kimi CLI upstream)  
**Language**: Python 3.11+  
**Package Manager**: UV  
**Versioning**: Semantic Versioning (semver)

## Project Purpose

Kimi-Coder-MCP is an MCP (Model Context Protocol) server that wraps Kimi CLI, enabling any MCP-compatible AI agent (like Claude Code) to use Kimi's powerful coding capabilities as an on-demand subagent. This creates a meta-architecture where AI agents can delegate specific coding tasks to other specialized AI agents.

## Core Objectives

1. **Expose Kimi CLI through MCP**: Make Kimi's agentic coding abilities accessible to Claude Code and other MCP clients
2. **File Artifact Management**: Capture and return all files created or modified by Kimi
3. **Session Orchestration**: Manage ephemeral Kimi CLI sessions programmatically
4. **Developer Experience**: Provide clear, structured responses and helpful error messages
5. **Seamless Integration**: Work transparently within existing development workflows

## Technical Stack

### Core Dependencies
- **FastMCP**: MCP server framework
- **pexpect**: Interactive process control for managing Kimi CLI sessions
- **Python**: 3.11+ (for modern type hints and async features)

### Development Tools
- **UV**: Package management, virtual environments, and task running
- **pytest**: Testing framework
- **ruff**: Linting (via git hooks)
- **black**: Code formatting (via git hooks)

### External Requirements
- **Kimi CLI**: Must be installed via `uv tool install kimi-cli`
- **Moonshot API Key**: For Kimi authentication

## Architecture Overview

```
Claude Code (or any MCP client)
         ↓
    [MCP Protocol]
         ↓
   Kimi-Coder-MCP Server
         ↓
    [pexpect session]
         ↓
     Kimi CLI
         ↓
   [File System Changes]
```

### Component Breakdown

1. **MCP Server Layer** (`server.py`)
   - Exposes FastMCP tools
   - Handles tool invocations from MCP clients
   - Orchestrates session lifecycle
   - Returns structured responses

2. **Session Manager** (`session.py`)
   - Spawns Kimi CLI processes via pexpect
   - Sends prompts to Kimi
   - Waits for task completion
   - Captures stdout/stderr
   - Manages timeouts and cleanup

3. **File Tracker** (`file_tracker.py`)
   - Snapshots directory state pre-execution
   - Detects created/modified files post-execution
   - Reads and returns file contents
   - Handles binary files appropriately

4. **Utilities** (`utils.py`)
   - API key detection and configuration
   - Error formatting
   - Logging helpers
   - Common data transformations

## MCP Tools Specification

### 1. kimi_code_task
**Purpose**: Execute a coding task with Kimi  
**Parameters**:
- `task_description` (string, required): Detailed task description
- `context_files` (list[string], optional): Files to include as context

**Returns**:
```json
{
  "output": "Kimi's text response",
  "files_created": ["path/to/file1.py", "path/to/file2.py"],
  "files_modified": ["path/to/existing.py"],
  "file_contents": {
    "path/to/file1.py": "file content here...",
    "path/to/file2.py": "more content..."
  },
  "success": true,
  "error": null
}
```

### 2. kimi_analyze_code
**Purpose**: Analyze existing code files  
**Parameters**:
- `file_paths` (list[string], required): Files to analyze
- `analysis_focus` (string, optional): Specific aspect to focus on

**Returns**:
```json
{
  "analysis": "Detailed analysis from Kimi",
  "suggestions": ["suggestion 1", "suggestion 2"],
  "success": true,
  "error": null
}
```

### 3. kimi_prompt
**Purpose**: Generic prompt interface  
**Parameters**:
- `prompt` (string, required): The prompt to send
- `include_workspace_context` (bool, optional): Include file structure

**Returns**: Same structure as `kimi_code_task`

### 4. kimi_refactor
**Purpose**: Refactor existing code  
**Parameters**:
- `file_path` (string, required): File to refactor
- `refactor_instructions` (string, required): Refactoring instructions

**Returns**:
```json
{
  "original_content": "original file content",
  "refactored_content": "new file content",
  "explanation": "What changed and why",
  "files_modified": ["path/to/file"],
  "success": true,
  "error": null
}
```

### 5. kimi_debug
**Purpose**: Debug errors with Kimi's help  
**Parameters**:
- `error_message` (string, required): Error description
- `relevant_files` (list[string], required): Related files
- `context` (string, optional): Additional context

**Returns**:
```json
{
  "diagnosis": "What's causing the error",
  "solution": "How to fix it",
  "code_changes": "Suggested changes",
  "files_modified": ["paths if Kimi made changes"],
  "success": true,
  "error": null
}
```

## File Structure

```
kimi-coder-mcp/
├── src/
│   └── kimi_mcp/
│       ├── __init__.py
│       ├── server.py          # FastMCP server and tool definitions
│       ├── session.py         # Kimi CLI session management
│       ├── file_tracker.py    # File system change detection
│       └── utils.py           # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_session.py
│   ├── test_file_tracker.py
│   ├── test_tools.py
│   └── fixtures/
├── docs/
│   ├── WHY.md                 # Why this project exists
│   ├── PROMPT.md              # Development prompt for Claude Code
│   └── FUTURE_IDEAS.md        # Potential future enhancements
├── .github/
│   └── workflows/
│       └── test.yml           # CI/CD pipeline
├── pyproject.toml             # Project configuration
├── uv.lock                    # Dependency lock file
├── README.md                  # Main documentation
├── LICENSE                    # Apache 2.0 license
├── .gitignore
└── .env.example               # Example environment variables
```

## Configuration

### Environment Variables
- `MOONSHOT_API_KEY`: Moonshot AI API key (optional if already logged into Kimi CLI)

### MCP Server Config
Users add this to their MCP client configuration:
```json
{
  "mcpServers": {
    "kimi-coder": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/kimi-coder-mcp", "kimi-mcp"],
      "env": {
        "MOONSHOT_API_KEY": "optional-api-key-here"
      }
    }
  }
}
```

## Development Workflow

### Setup
```bash
# Clone repository
git clone https://github.com/autumnsgrove/kimi-coder-mcp.git
cd kimi-coder-mcp

# Initialize with UV
uv sync

# Install Kimi CLI (required)
uv tool install --python 3.13 kimi-cli
```

### Development
```bash
# Run the server locally
uv run python -m kimi_mcp.server

# Run tests
uv run pytest

# Run specific test
uv run pytest tests/test_session.py -v

# Install as editable tool for testing
uv tool install --editable .
```

### Testing Strategy
1. **Unit Tests**: Individual components (session, file tracker, utils)
2. **Integration Tests**: Full tool flows with mocked Kimi responses
3. **Error Scenario Tests**: Timeouts, crashes, auth failures
4. **File Tracking Tests**: Ensure accurate change detection

### Code Quality
- Git hooks automatically run `ruff` and `black` on commit
- Type hints required for all public functions
- Docstrings for all public APIs

## Error Handling

### Error Categories
1. **Installation Errors**: Kimi CLI not found
2. **Authentication Errors**: Invalid/missing API key
3. **Session Errors**: Process spawn failures, crashes
4. **Timeout Errors**: Tasks exceeding timeout (default: 5 minutes)
5. **File System Errors**: Permission issues, disk full
6. **Parse Errors**: Unable to parse Kimi's output

### Error Response Format
```json
{
  "success": false,
  "error": {
    "type": "TimeoutError",
    "message": "Kimi CLI session timed out after 300 seconds",
    "details": "Additional context here",
    "suggestion": "Try breaking the task into smaller pieces"
  }
}
```

## Session Management Details

### Kimi CLI Interaction Pattern
1. Spawn process: `kimi` (in target working directory)
2. Wait for initial prompt (detect ">" or similar)
3. Check if `/setup` needed (API key configuration)
4. Send task prompt
5. Monitor for completion indicators
6. Capture output
7. Terminate session gracefully

### Timeout Handling
- Default timeout: 300 seconds (5 minutes)
- Configurable per-tool if needed
- Send SIGTERM, wait 5 seconds, then SIGKILL if necessary

### Process Cleanup
- Always clean up spawned processes
- Use context managers where possible
- Handle cleanup in error paths

## File Tracking Strategy

### Implementation Approach
1. **Pre-execution snapshot**:
   - Record all files in working directory
   - Store modification times
   - Calculate checksums for changed file detection

2. **Post-execution comparison**:
   - Re-scan directory
   - Identify new files (created)
   - Identify modified files (different checksum/mtime)
   - Read contents of changed files

3. **Binary file handling**:
   - Detect binary files by content inspection
   - Don't return binary content in response
   - Note binary files in metadata

## API Key & Authentication

### Priority Order
1. Check if Kimi already logged in (test with simple command)
2. If not logged in, check for `MOONSHOT_API_KEY` in environment
3. If key found, run `/setup` flow programmatically
4. If no key and not logged in, return clear error with instructions

### Setup Flow
```
1. Spawn Kimi CLI
2. Send "/setup"
3. Wait for API key prompt
4. Send API key from env
5. Confirm setup successful
6. Proceed with actual task
```

## Documentation Structure

### README.md
- Project overview
- Quick start guide
- Installation instructions
- Usage examples
- MCP configuration
- Troubleshooting
- Contributing guidelines

### WHY.md
- Problem statement
- Why wrap Kimi CLI in MCP?
- Use cases and benefits
- Meta-architecture advantages
- When to use Kimi vs native Claude Code

### PROMPT.md
- Complete development prompt (the one we created)
- Used to guide Claude Code during implementation

### FUTURE_IDEAS.md
- Potential enhancements
- Community suggestions
- Technical explorations

## Success Criteria

The project is successful when:
- ✅ MCP server successfully exposes all 5 tools
- ✅ Kimi CLI sessions spawn and terminate reliably
- ✅ File artifacts are accurately captured and returned
- ✅ API key configuration works automatically
- ✅ Error handling is robust and informative
- ✅ Works seamlessly from Claude Code
- ✅ Documentation is clear and complete
- ✅ Tests provide good coverage (>80%)

## Non-Goals (Out of Scope for v0.1.0)

- ❌ Persistent session mode (all sessions are ephemeral)
- ❌ Streaming responses (batch responses only)
- ❌ Token usage tracking (future enhancement)
- ❌ GUI or web interface (CLI/MCP only)
- ❌ Windows support (macOS/Linux only initially)
- ❌ Multi-user/concurrent session management
- ❌ Built-in rate limiting (rely on Moonshot's API limits)

## Development Philosophy

### Coding Style
- **Functional-OOP hybrid**: Use functions for transformations, classes for stateful components
- **Data transformation focus**: Map/filter/comprehensions preferred
- **Composition over inheritance**: Build from small, focused pieces
- **ADHD-friendly**: Small steps, clear patterns, avoid deep nesting

### Best Practices
- Type hints everywhere
- Clear error messages with actionable suggestions
- Log important events (session start/end, errors)
- Keep functions small (<50 lines)
- One responsibility per function
- Test error paths, not just happy paths

## Maintenance & Support

### Versioning Strategy
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking MCP API changes
- MINOR: New tools or significant features
- PATCH: Bug fixes and small improvements

### Release Process
1. Update CHANGELOG.md
2. Bump version in pyproject.toml
3. Tag release in git
4. Push to PyPI (future: when stable)

### Community
- GitHub Issues for bug reports
- GitHub Discussions for questions
- Pull requests welcome
- Maintain CODE_OF_CONDUCT.md

## Dependencies & Compatibility

### Python Version
- Minimum: Python 3.11
- Recommended: Python 3.13 (for best performance)

### Kimi CLI Version
- Track latest stable release
- Document compatibility in README
- Test against new versions

### MCP Protocol
- Support current MCP specification
- Update as protocol evolves
- Maintain backward compatibility where possible

## Security Considerations

### API Key Handling
- Never log API keys
- Don't include in error messages
- Store securely (env vars only)
- Clear from memory after use

### File System Access
- Operate only in designated working directory
- Validate file paths (prevent directory traversal)
- Respect .gitignore patterns
- Don't access sensitive system files

### Process Isolation
- Each Kimi session is isolated
- Clean up processes thoroughly
- Limit resource usage (memory, CPU)
- Handle zombies and orphaned processes

## Performance Targets

### Response Times (Approximate)
- Tool invocation overhead: <100ms
- Simple tasks: 5-30 seconds
- Complex tasks: 1-5 minutes
- Maximum timeout: 5 minutes (configurable)

### Resource Usage
- Memory: <100MB per session
- CPU: Variable (depends on Kimi's work)
- Disk: Only for file artifacts

## Monitoring & Observability

### Logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log session lifecycle events
- Log tool invocations
- Include request IDs for tracing

### Metrics (Future)
- Tool usage counts
- Success/failure rates
- Average execution times
- Error types and frequencies

## Contributing Guidelines

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass (`uv run pytest`)
5. Submit a pull request

### Code Review Process
- At least one approval required
- All CI checks must pass
- Documentation updated if needed
- Follows project style guidelines

## License

Apache License 2.0 - matching Kimi CLI upstream project

## Contact & Support

- **Repository**: https://github.com/autumnsgrove/kimi-coder-mcp
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Maintainer**: Autumn Brown (@autumnsgrove)

---

This specification will evolve as the project develops. Major changes will be documented in version history.
