# Kimi-Coder-MCP Quick Reference Card

One-page reference for building and working with Kimi-Coder-MCP.

## 🎯 Project Quick Facts

**Name**: Kimi-Coder-MCP  
**Purpose**: Wrap Kimi CLI as MCP server for multi-agent AI collaboration  
**Language**: Python 3.11+ with UV  
**License**: Apache 2.0  
**Repo**: autumnsgrove/kimi-coder-mcp  

## 📁 File Structure

```
kimi-coder-mcp/
├── src/kimi_mcp/
│   ├── server.py       # MCP tools & FastMCP server
│   ├── session.py      # Kimi CLI session management (pexpect)
│   ├── file_tracker.py # Detect created/modified files
│   └── utils.py        # Helpers, auth, logging
├── tests/
├── docs/
│   ├── WHY.md
│   ├── PROJECT_SPEC.md
│   ├── PROMPT.md
│   └── FUTURE_IDEAS.md
├── README.md
├── CONTRIBUTING.md
├── .env.example
├── pyproject.toml
└── LICENSE
```

## 🔧 UV Commands Cheat Sheet

```bash
# Setup
uv init                          # Initialize project
uv sync                          # Install dependencies
uv add fastmcp pexpect           # Add dependencies

# Development
uv run python -m kimi_mcp.server # Run server
uv run pytest                    # Run tests
uv run pytest -v                 # Verbose tests
uv tool install --editable .     # Install as tool

# Kimi CLI
uv tool install --python 3.13 kimi-cli  # Install Kimi
kimi                             # Run Kimi CLI
```

## 🛠️ Five MCP Tools

1. **kimi_code_task**: Execute coding task → file artifacts
2. **kimi_analyze_code**: Analyze files → insights + suggestions
3. **kimi_prompt**: Generic prompt → flexible response
4. **kimi_refactor**: Refactor file → modified code + explanation
5. **kimi_debug**: Debug error → diagnosis + solution

## 📝 Tool Response Format

```json
{
  "output": "Kimi's text response",
  "files_created": ["path1", "path2"],
  "files_modified": ["path3"],
  "file_contents": {"path1": "content..."},
  "success": true,
  "error": null
}
```

## ⚙️ MCP Configuration

```json
{
  "mcpServers": {
    "kimi-coder": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/kimi-coder-mcp", "kimi-mcp"],
      "env": {"MOONSHOT_API_KEY": "your-key"}
    }
  }
}
```

## 🔑 Environment Variables

```bash
MOONSHOT_API_KEY=your_key  # Moonshot API key (optional if logged in)
KIMI_TIMEOUT=300           # Task timeout (seconds)
LOG_LEVEL=INFO             # DEBUG|INFO|WARNING|ERROR
DEBUG=1                    # Enable verbose logging
```

## 🧪 Testing Commands

```bash
uv run pytest                              # All tests
uv run pytest tests/test_session.py        # Specific file
uv run pytest -v                           # Verbose
uv run pytest --cov=kimi_mcp              # With coverage
uv run pytest -k "test_session_spawn"     # Specific test
```

## 🏗️ Architecture Flow

```
User
  ↓
Claude Code (MCP Client)
  ↓
Kimi-Coder-MCP Server (FastMCP)
  ↓
Session Manager (pexpect)
  ↓
Kimi CLI Process
  ↓
File System Changes
  ↓
File Tracker
  ↓
Structured Response → MCP Client
```

## 📊 Key Components

### Session Manager (session.py)
- Spawn Kimi CLI with pexpect
- Send prompts, wait for completion
- Handle timeouts (default: 5 min)
- Clean up processes

### File Tracker (file_tracker.py)
- Snapshot directory pre-execution
- Compare post-execution
- Return created/modified files
- Handle binary files

### Server (server.py)
- Define FastMCP tools
- Orchestrate session lifecycle
- Return structured responses
- Error handling

## 🚨 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Kimi CLI not found | `uv tool install --python 3.13 kimi-cli` |
| API key invalid | Check MOONSHOT_API_KEY or run `kimi` → `/setup` |
| Session timeout | Break task into smaller pieces or increase KIMI_TIMEOUT |
| Permission errors | Check working directory permissions |
| Process zombies | Ensure proper cleanup in session.py |

## 💻 Code Style Rules

```python
# ✅ DO: Small functions, type hints, comprehensions
def parse_output(text: str) -> dict[str, Any]:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return {"response": "\n".join(lines)}

# ✅ DO: Composition over inheritance
tracker = FileTracker(working_dir)
auth = Authenticator(api_key)
session = KimiSession(auth, tracker)

# ❌ DON'T: Deep nesting, > 50 lines, missing types
def big_function():
    if something:
        if something_else:
            if another_thing:
                # too deep!
```

## 📦 Dependencies

**Core**:
- fastmcp - MCP server framework
- pexpect - Interactive process control

**Dev**:
- pytest - Testing
- ruff - Linting (via git hooks)
- black - Formatting (via git hooks)

**External**:
- Kimi CLI (separate install)
- Moonshot API key

## 🎨 Coding Philosophy

- **Functional-OOP hybrid**: Functions for transformations, classes for state
- **Small steps**: ADHD-friendly, focused functions
- **Data transformation**: Map/filter/comprehensions
- **Clear errors**: Actionable messages
- **Type everything**: Type hints required
- **Test everything**: Especially error paths

## 🔄 Git Workflow

```bash
# Feature branch
git checkout -b feature/your-feature

# Commit (conventional commits)
git commit -m "feat: add streaming support"
git commit -m "fix: handle edge case in file tracking"
git commit -m "docs: update API documentation"

# Types: feat, fix, docs, test, refactor, chore, style, perf
```

## 📖 Documentation Map

- **README.md**: Start here, quick overview
- **WHY.md**: Vision, motivation, use cases
- **PROJECT_SPEC.md**: Complete technical spec
- **PROMPT.md**: Development instructions for Claude Code
- **FUTURE_IDEAS.md**: Roadmap and enhancements
- **CONTRIBUTING.md**: How to contribute

## 🔗 Important Links

- **Kimi CLI**: https://github.com/MoonshotAI/kimi-cli
- **MCP Docs**: https://modelcontextprotocol.io/
- **FastMCP**: https://github.com/jlowin/fastmcp
- **UV**: https://docs.astral.sh/uv/
- **Moonshot AI**: https://platform.moonshot.ai/

## ⚡ Quick Start Steps

1. Install Kimi CLI: `uv tool install --python 3.13 kimi-cli`
2. Clone & setup: `git clone ... && cd ... && uv sync`
3. Configure: Copy .env.example → .env, add API key
4. Run server: `uv run python -m kimi_mcp.server`
5. Add to Claude Code MCP config
6. Test: "Use Kimi to [coding task]"

## 🎯 Success Checklist

- [ ] Kimi CLI spawns successfully
- [ ] API key authentication works
- [ ] File artifacts captured correctly
- [ ] All 5 tools functional
- [ ] Errors handled gracefully
- [ ] Tests pass (>80% coverage)
- [ ] Documentation complete
- [ ] Works from Claude Code

## 🚀 Next Steps After MVP

- [ ] Persistent sessions
- [ ] Streaming responses
- [ ] Token usage tracking
- [ ] Multi-model support
- [ ] Windows support
- [ ] Docker container
- [ ] CI/CD pipeline

---

**Keep This Handy** - Print or bookmark for quick reference during development!
