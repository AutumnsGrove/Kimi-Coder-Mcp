"""Kimi-Coder-MCP: MCP server for Kimi CLI integration.

This package provides an MCP (Model Context Protocol) server that wraps
Kimi CLI, enabling AI agents like Claude Code to delegate coding tasks
to Kimi as a specialized subagent.
"""

__version__ = "0.1.0"
__author__ = "Autumn Brown"
__license__ = "Apache 2.0"

from kimi_mcp.server import app

__all__ = ["app", "__version__"]
