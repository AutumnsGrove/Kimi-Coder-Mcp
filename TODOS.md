# TODOs for Kimi-Coder-MCP

## Project Setup ✅
- [x] Create project specification and documentation
- [x] Add BaseProject template structure
- [x] Customize AGENT.md with project details
- [x] Update TODOS.md with project tasks
- [ ] Create pyproject.toml with UV configuration
- [ ] Set up Python project structure (src/kimi_mcp/)
- [ ] Create test directory structure
- [ ] Add Apache 2.0 LICENSE file
- [ ] Update .gitignore for Python
- [ ] Install Kimi CLI: `uv tool install kimi-cli`
- [ ] Set up pre-commit hooks for Python

## Core Implementation
- [x] Implement session.py - Kimi CLI session manager
  - [x] Verify kimi command availability via subprocess
  - [x] Authentication check and setup flow
  - [x] Command sending and output capture via subprocess
  - [x] Timeout and error handling
- [ ] Implement file_tracker.py - File change detection
  - [ ] Pre-execution directory snapshot
  - [ ] Post-execution diff detection
  - [ ] File content reading
  - [ ] Binary file handling
- [ ] Implement utils.py - Helper functions
  - [ ] API key configuration
  - [ ] Error formatting
  - [ ] Logging setup
- [ ] Implement server.py - MCP server and tools
  - [ ] FastMCP server setup
  - [ ] Tool: kimi_code_task
  - [ ] Tool: kimi_analyze_code
  - [ ] Tool: kimi_prompt
  - [ ] Tool: kimi_refactor
  - [ ] Tool: kimi_debug

## Testing
- [ ] Set up pytest framework
- [ ] Write unit tests for session.py
- [ ] Write unit tests for file_tracker.py
- [ ] Write integration tests for MCP tools
- [ ] Add test fixtures and mocks
- [ ] Achieve >80% test coverage

## CI/CD
- [ ] Create GitHub Actions workflow for tests
- [ ] Add linting (ruff) to CI
- [ ] Add code formatting checks (black)
- [ ] Configure automated testing on PR

## Documentation
- [ ] Update README.md with installation instructions
- [ ] Add MCP server configuration examples
- [ ] Document all 5 MCP tools with examples
- [ ] Add troubleshooting guide
- [ ] Create CHANGELOG.md

## Future Enhancements (v0.2.0+)
- [ ] Streaming responses
- [ ] Persistent session mode
- [ ] Token usage tracking
- [ ] Windows support
- [ ] Multi-user session management
