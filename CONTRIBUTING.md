# Contributing to Kimi-Coder-MCP

Thank you for your interest in contributing to Kimi-Coder-MCP! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment (see below)
4. Create a new branch for your changes
5. Make your changes
6. Run tests and ensure they pass
7. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.11 or higher
- UV package manager
- Kimi CLI installed (`uv tool install kimi-cli`)
- Git

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/kimi-coder-mcp.git
cd kimi-coder-mcp

# Install dependencies
uv sync

# Install Kimi CLI if not already installed
uv tool install kimi-cli

# Run tests to verify setup
uv run pytest
```

## Making Changes

### Branch Naming

- `feat/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `test/description` - Test additions/changes
- `refactor/description` - Code refactoring

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks
- `perf:` - Performance improvements

**Examples:**
```
feat: add streaming support for Kimi responses

fix: correct timeout handling in KimiSession

docs: update README with installation instructions

test: add integration tests for kimi_debug tool
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_session.py

# Run with coverage
uv run pytest --cov=src/kimi_mcp --cov-report=term-missing

# Run specific test
uv run pytest tests/test_session.py::TestKimiSession::test_session_initialization
```

### Writing Tests

- All new features must include tests
- Aim for >80% code coverage
- Use pytest fixtures for common setup
- Mock external dependencies (Kimi CLI, file system where appropriate)
- Test both success and error paths

**Test file locations:**
- Unit tests: `tests/test_*.py`
- Integration tests: `tests/test_tools.py`
- Fixtures: `tests/fixtures/`

## Code Quality

### Linting and Formatting

```bash
# Check linting with ruff
uv run ruff check src/ tests/

# Auto-fix linting issues
uv run ruff check --fix src/ tests/

# Format code with black
uv run black src/ tests/

# Check formatting
uv run black --check src/ tests/
```

### Code Style Guidelines

- Follow PEP 8
- Use type hints for all public functions
- Write docstrings for all public APIs (Google style)
- Keep functions small (<50 lines)
- One responsibility per function
- Prefer composition over inheritance

**Example:**
```python
def calculate_checksum(file_path: Path) -> str:
    """Calculate MD5 checksum of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MD5 checksum as hex string
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()
```

## Submitting Changes

### Pull Request Process

1. **Update Documentation**: Ensure README and docstrings are updated
2. **Add Tests**: Include tests for new functionality
3. **Run Tests**: Verify all tests pass locally
4. **Update CHANGELOG**: Add entry in [Unreleased] section (if applicable)
5. **Push Changes**: Push to your fork
6. **Create PR**: Submit pull request with clear description

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass locally
- [ ] Added new tests for changes
- [ ] Updated documentation

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Code Review

- At least one approval required
- All CI checks must pass
- Address all reviewer comments
- Keep PRs focused and reasonably sized
- Link related issues

## Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking API changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with release notes
3. Run full test suite
4. Create git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
5. Push tag: `git push origin v0.1.0`
6. Create GitHub release with notes

## Project Structure

```
kimi-coder-mcp/
├── src/kimi_mcp/          # Main source code
│   ├── __init__.py        # Package initialization
│   ├── server.py          # MCP server and tools
│   ├── session.py         # Kimi CLI session management
│   ├── file_tracker.py    # File change detection
│   └── utils.py           # Helper functions
├── tests/                  # Test files
│   ├── test_session.py    # Session tests
│   ├── test_file_tracker.py
│   ├── test_tools.py      # Integration tests
│   └── test_utils.py
├── docs/                   # Documentation
├── .github/workflows/     # CI/CD
└── pyproject.toml         # Project configuration
```

## Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact maintainer for sensitive issues

## Additional Resources

- [PROJECT_SPEC.md](docs/PROJECT_SPEC.md) - Full technical specification
- [README.md](README.md) - Project overview and usage
- [docs/WHY.md](docs/WHY.md) - Project rationale
- [MCP Documentation](https://modelcontextprotocol.io/) - Model Context Protocol

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
