# Kimi-Coder-MCP

> Harness the power of Kimi from any agentic AI application through the Model Context Protocol

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)

Kimi-Coder-MCP wraps [Kimi CLI](https://github.com/MoonshotAI/kimi-cli) as an MCP server, enabling AI agents like Claude Code to delegate coding tasks to Kimi as a specialized subagent. Think of it as giving Claude Code the ability to call in a coding expert when needed.

## 🌟 Why This Exists

Different AI models excel at different tasks. Kimi-Coder-MCP creates a **meta-architecture** where AI agents can collaborate:

- **Claude Code** orchestrates your project and handles high-level reasoning
- **Kimi** (via this MCP server) handles specialized coding tasks with its massive 128K-256K token context window
- **You** benefit from the strengths of both

For more on the vision and use cases, see [WHY.md](WHY.md).

## ✨ Key Features

- 🔧 **Five Specialized Tools**: Code tasks, analysis, debugging, refactoring, and generic prompts
- 📁 **File Artifact Capture**: Automatically detects and returns files created/modified by Kimi
- 🔄 **Ephemeral Sessions**: Clean, isolated Kimi sessions for each task
- 🔐 **Smart Authentication**: Auto-configures API keys or uses existing Kimi login
- 🎯 **MCP Native**: Works with Claude Code, Zed, or any MCP-compatible client
- 🚀 **Built with UV**: Fast, modern Python tooling

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- [UV](https://docs.astral.sh/uv/) package manager
- [Kimi CLI](https://github.com/MoonshotAI/kimi-cli) installed
- Moonshot AI API key (get one at [platform.moonshot.ai](https://platform.moonshot.ai/))

### Installation

```bash
# Install Kimi CLI first (if not already installed)
uv tool install --python 3.13 kimi-cli

# Clone this repository
git clone https://github.com/autumnsgrove/kimi-coder-mcp.git
cd kimi-coder-mcp

# Install dependencies
uv sync

# Run the server
uv run kimi-mcp
```

### Configuration

Add to your MCP client configuration (e.g., Claude Desktop's `~/.config/claude/mcp.json`):

```json
{
  "mcpServers": {
    "kimi-coder": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/kimi-coder-mcp",
        "kimi-mcp"
      ],
      "env": {
        "MOONSHOT_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Replace `/path/to/kimi-coder-mcp` with the actual path to this repository.

## 🛠️ Available Tools

### kimi_code_task
Execute a coding task with Kimi and receive file artifacts.

```python
# Example use from Claude Code:
"Can you use Kimi to implement a REST API for user authentication?"
```

### kimi_analyze_code
Analyze existing code files with Kimi's expertise.

```python
# Example:
"Use Kimi to analyze auth.py for security vulnerabilities"
```

### kimi_refactor
Refactor code with specific instructions.

```python
# Example:
"Have Kimi refactor this function to use async/await"
```

### kimi_debug
Debug errors with Kimi's help.

```python
# Example:
"Ask Kimi to debug this stack trace: [error details]"
```

### kimi_prompt
Generic prompt interface for any Kimi interaction.

```python
# Example:
"Send this to Kimi: [any coding-related task]"
```

## 📖 Documentation

- **[WHY.md](WHY.md)** - Why this project exists and its vision
- **[PROJECT_SPEC.md](PROJECT_SPEC.md)** - Complete technical specification
- **[kimi-mcp-server-prompt.md](kimi-mcp-server-prompt.md)** - Development prompt used to build this
- **[FUTURE_IDEAS.md](FUTURE_IDEAS.md)** - Potential enhancements and features
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

## 🎯 Use Cases

### Large Codebase Analysis
Leverage Kimi's massive context window to analyze entire modules at once.

### Second Opinions
Get a different AI's perspective on code quality and architecture.

### Specialized Coding Tasks
Delegate tasks that benefit from Kimi's coding-specific strengths.

### Cost Optimization
Use the right AI for each task to optimize costs.

For more detailed use cases, see [WHY.md](WHY.md).

## 🧪 Development

```bash
# Run tests
uv run pytest

# Run specific test file
uv run pytest tests/test_session.py -v

# Install as editable tool
uv tool install --editable .

# Run with verbose logging
DEBUG=1 uv run kimi-mcp
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Philosophy
- Functional-OOP hybrid approach
- Small, focused functions with clear responsibilities
- Type hints and comprehensive documentation
- Tests for all features and error paths

## 📋 Requirements

- Python 3.11+
- FastMCP
- pexpect
- Kimi CLI (installed separately)
- Moonshot AI API key

## 🐛 Troubleshooting

### Kimi CLI not found
Ensure Kimi CLI is installed: `uv tool install --python 3.13 kimi-cli`

### API Key issues
- Set `MOONSHOT_API_KEY` in your MCP configuration
- Or log into Kimi CLI manually: `kimi` and run `/setup`

### Session timeouts
Default timeout is 5 minutes. For longer tasks, consider breaking them into smaller subtasks.

### File tracking issues
Ensure the MCP server has read/write permissions in the working directory.

For more help, see [GitHub Issues](https://github.com/autumnsgrove/kimi-coder-mcp/issues).

## 📜 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

This matches the license of Kimi CLI upstream.

## 🙏 Acknowledgments

- [MoonshotAI](https://github.com/MoonshotAI) for Kimi CLI
- [Anthropic](https://www.anthropic.com/) for Claude and MCP
- The FastMCP team for the excellent MCP framework

## 📬 Contact

- **Repository**: [github.com/autumnsgrove/kimi-coder-mcp](https://github.com/autumnsgrove/kimi-coder-mcp)
- **Issues**: [GitHub Issues](https://github.com/autumnsgrove/kimi-coder-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/autumnsgrove/kimi-coder-mcp/discussions)
- **Maintainer**: Autumn Brown ([@autumnsgrove](https://github.com/autumnsgrove))

## 🌱 Project Status

**Status**: Early Development (v0.1.0)

This project is in active development. APIs may change. Feedback and contributions are especially welcome during this phase!

---

**Built with** 🤖 **by AI agents, for AI agents** - A meta-project exploring multi-agent collaboration through MCP.
