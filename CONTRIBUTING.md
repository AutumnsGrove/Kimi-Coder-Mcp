# Contributing to Kimi-Coder-MCP

Thank you for your interest in contributing to Kimi-Coder-MCP! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project follows a simple principle: **Be kind and respectful to everyone**. We're all here to learn and build cool things together.

## How to Contribute

### Reporting Bugs

Found a bug? Please open an issue with:

1. **Clear title**: Describe the bug briefly
2. **Steps to reproduce**: What did you do?
3. **Expected behavior**: What should have happened?
4. **Actual behavior**: What actually happened?
5. **Environment**: OS, Python version, Kimi CLI version
6. **Logs**: Include relevant error messages (sanitize sensitive data!)

### Suggesting Features

Have an idea? Open an issue with:

1. **Use case**: What problem does this solve?
2. **Proposed solution**: How would it work?
3. **Alternatives**: Other approaches you considered
4. **Examples**: Show how it would be used

Or check [FUTURE_IDEAS.md](docs/FUTURE_IDEAS.md) and comment on existing ideas.

### Pull Requests

#### Before You Start

1. **Check existing issues**: Make sure someone isn't already working on it
2. **Open an issue first**: Discuss major changes before coding
3. **Ask questions**: Not sure about something? Just ask!

#### Development Setup

```bash
# Fork and clone your fork
git clone https://github.com/YOUR_USERNAME/kimi-coder-mcp.git
cd kimi-coder-mcp

# Install dependencies
uv sync

# Install Kimi CLI (if not already installed)
uv tool install --python 3.13 kimi-cli

# Create a branch
git checkout -b feature/your-feature-name
```

#### Making Changes

1. **Write code** following our style guidelines (below)
2. **Add tests** for new features
3. **Update docs** if needed
4. **Run tests**: `uv run pytest`
5. **Commit with clear messages**: See commit guidelines below

#### Code Style

We use a **functional-OOP hybrid** approach:

```python
# Good: Small, focused functions
def parse_kimi_output(output: str) -> dict:
    """Parse Kimi CLI output into structured data."""
    lines = output.strip().split("\n")
    return {
        "response": "\n".join(lines),
        "success": True
    }

# Good: Data transformation with comprehensions
files_created = [
    f for f in changed_files
    if not f.existed_before
]

# Good: Composition over inheritance
def create_session(config: SessionConfig) -> KimiSession:
    authenticator = Authenticator(config.api_key)
    tracker = FileTracker(config.working_dir)
    return KimiSession(authenticator, tracker)

# Avoid: Deep inheritance hierarchies
# Avoid: Complex nested logic
# Avoid: Functions > 50 lines
```

**Key Principles**:
- Small functions (< 50 lines)
- Type hints everywhere
- Clear, descriptive names
- Map/filter/comprehensions over loops when appropriate
- Docstrings for all public APIs
- Comments for "why" not "what"

#### Type Hints

Always use type hints:

```python
from typing import Optional, Dict, List

def kimi_code_task(
    task_description: str,
    context_files: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Execute a coding task with Kimi.
    
    Args:
        task_description: What to ask Kimi to do
        context_files: Optional files to include as context
        
    Returns:
        Structured response with output and file artifacts
        
    Raises:
        KimiSessionError: If session fails to spawn
        TimeoutError: If task exceeds timeout
    """
    pass
```

#### Testing

Write tests for:
- ✅ New features
- ✅ Bug fixes
- ✅ Error cases
- ✅ Edge cases

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_session.py

# Run with coverage
uv run pytest --cov=kimi_mcp --cov-report=html

# Run with verbose output
uv run pytest -v
```

Example test:

```python
import pytest
from kimi_mcp.session import KimiSession

def test_session_spawn():
    """Test that Kimi session spawns successfully."""
    session = KimiSession()
    assert session.spawn()
    assert session.is_running
    session.terminate()
    assert not session.is_running

def test_session_timeout():
    """Test that session respects timeout."""
    session = KimiSession(timeout=1)
    with pytest.raises(TimeoutError):
        session.run_task("sleep 10")
```

#### Commit Messages

Use conventional commits:

```
feat: add streaming response support
fix: handle API key with special characters
docs: update installation instructions
test: add tests for file tracking
refactor: simplify session management
chore: update dependencies
```

Format:
```
<type>: <short description>

<optional longer description>

<optional footer>
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `style`, `perf`

#### Submitting PR

1. **Push your branch**: `git push origin feature/your-feature-name`
2. **Open PR** on GitHub
3. **Fill in the template**: Describe what and why
4. **Link issues**: "Closes #123"
5. **Wait for review**: Be patient, we'll review ASAP
6. **Address feedback**: Make requested changes
7. **Merge**: Once approved, we'll merge!

### PR Template

When you open a PR, include:

```markdown
## Description
Brief description of what this PR does

## Motivation
Why is this change needed? What problem does it solve?

## Changes
- Bullet list of changes
- Be specific

## Testing
How did you test this? What should reviewers test?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Type hints added
- [ ] All tests passing
- [ ] No breaking changes (or clearly documented)

## Screenshots (if applicable)
Visual changes? Include before/after

## Related Issues
Closes #123
Related to #456
```

## Development Workflow

### Branch Strategy

- `main`: Stable releases only
- `develop`: Active development
- `feature/*`: New features
- `fix/*`: Bug fixes
- `docs/*`: Documentation updates

### Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create PR to `main`
4. Tag release: `git tag v0.1.0`
5. Push tag: `git push origin v0.1.0`
6. GitHub Actions handles the rest

## Project Structure

```
kimi-coder-mcp/
├── src/kimi_mcp/      # Main package
│   ├── server.py      # MCP server & tools
│   ├── session.py     # Kimi CLI session management
│   ├── file_tracker.py # File change detection
│   └── utils.py       # Helper functions
├── tests/             # Test suite
├── docs/              # Documentation
└── pyproject.toml     # Project config
```

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open an Issue
- **Ideas**: Check FUTURE_IDEAS.md or open an Issue
- **Chat**: (Discord/Slack if we set one up)

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Thanked profusely! 🎉

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

**Thank you for contributing to Kimi-Coder-MCP!** Every contribution, no matter how small, helps make this project better. 🌱
