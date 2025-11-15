# TODOs for Kimi-Coder-MCP

## Project Setup ✅
- [x] Create project specification and documentation
- [x] Add BaseProject template structure
- [x] Customize AGENT.md with project details
- [x] Update TODOS.md with project tasks
- [x] Create pyproject.toml with UV configuration
- [x] Set up Python project structure (src/kimi_mcp/)
- [x] Create test directory structure
- [x] Add Apache 2.0 LICENSE file
- [x] Update .gitignore for Python
- [x] Install Kimi CLI: `uv tool install kimi-cli`
- [x] Set up pre-commit hooks for Python

## Core Implementation ✅
- [x] Implement session.py - Kimi CLI session manager (hybrid interactive/one-shot)
  - [x] Verify kimi command availability
  - [x] Authentication check and setup flow
  - [x] Command sending via subprocess and pexpect
  - [x] Timeout and error handling
- [x] Implement file_tracker.py - File change detection
  - [x] Pre-execution directory snapshot
  - [x] Post-execution diff detection
  - [x] File content reading
  - [x] Binary file handling
- [x] Implement utils.py - Helper functions
  - [x] API key configuration
  - [x] Error formatting
  - [x] Logging setup
  - [x] Path validation for security
- [x] Implement server.py - MCP server and tools
  - [x] FastMCP server setup
  - [x] Tool: kimi_code_task (one-shot mode)
  - [x] Tool: kimi_analyze_code (interactive mode)
  - [x] Tool: kimi_prompt (interactive mode)
  - [x] Tool: kimi_refactor (one-shot mode)
  - [x] Tool: kimi_debug (interactive mode)

## Testing ✅
- [x] Set up pytest framework
- [x] Write unit tests for session.py (19 tests, 88.78% coverage)
- [x] Write unit tests for file_tracker.py (12 tests, 80.85% coverage)
- [x] Write unit tests for utils.py (16 tests)
- [x] Write integration tests for MCP tools (13 tests, 79.87% coverage)
- [x] Add test fixtures and mocks
- [x] Achieve >80% test coverage (80.15% overall!)

## CI/CD ✅
- [x] Create GitHub Actions workflow for tests
- [x] Add linting (ruff) to CI
- [x] Add code formatting checks (black)
- [x] Configure automated testing on PR
- [x] Multi-OS testing (Ubuntu, macOS)
- [x] Multi-Python testing (3.11, 3.12, 3.13)

## Documentation ✅
- [x] Update README.md with installation instructions
- [x] Add MCP server configuration examples
- [x] Document all 5 MCP tools with examples
- [x] Add troubleshooting guide
- [x] Create CONTRIBUTING.md with detailed guidelines

## Future Enhancements (v0.2.0+)
- [ ] Streaming responses
- [ ] Persistent session mode
- [ ] Token usage tracking
- [ ] Windows support
- [ ] Multi-user session management
