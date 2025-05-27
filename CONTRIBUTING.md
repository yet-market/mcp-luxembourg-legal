# Contributing to MCP SPARQL Server

Thank you for your interest in contributing to the MCP SPARQL Server! This document provides guidelines and information for contributors.

## 🤖 AI-Assisted Development

This project embraces AI-assisted development. The codebase has been co-developed with:
- **Claude (Anthropic)** - Primary architecture and implementation
- **GitHub Copilot/Codex (OpenAI)** - Code completion and acceleration  
- **GPT-o3 (OpenAI)** - Advanced problem-solving and optimization

Contributors are encouraged to use AI tools responsibly to enhance their contributions while maintaining code quality and understanding.

## 🤝 How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. **Search existing issues** to avoid duplicates
2. **Use the issue templates** provided in `.github/ISSUE_TEMPLATE/`
3. **Provide detailed information** including:
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)
   - Relevant logs or error messages

### Submitting Pull Requests

1. **Fork the repository** and create a new branch for your feature/fix
2. **Follow the coding standards** outlined below
3. **Write or update tests** for your changes
4. **Update documentation** if needed
5. **Test your changes** thoroughly
6. **Submit a pull request** using the provided template

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or newer
- Git
- Virtual environment tool (venv, conda, etc.)

### Setting Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/yet-sparql-mcp-server.git
cd yet-sparql-mcp-server

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install the package in development mode
pip install -e .
```

### Running Tests

```bash
# Run the main test suite
python test_sparql_server.py

# Run specific tests (if using pytest)
pytest tests/ -v

# Run tests with coverage
pytest --cov=sparql_server tests/
```

### Code Formatting and Linting

```bash
# Format code with black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy .
```

## 📋 Coding Standards

### General Guidelines

- Follow [PEP 8](https://pep8.org/) Python style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting (line length: 88)
- Use [isort](https://isort.readthedocs.io/) for import sorting
- Write comprehensive docstrings for all modules, classes, and functions
- Include type hints throughout the codebase

### Code Structure

- **Modular design**: Separate concerns into different modules
- **Clear interfaces**: Define clear APIs between components
- **Error handling**: Use specific exception types and provide informative error messages
- **Logging**: Use appropriate logging levels and structured logging

### Documentation

- **Docstrings**: Follow [Google docstring format](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- **Comments**: Add inline comments for complex logic
- **README updates**: Update documentation for any user-facing changes
- **Examples**: Include usage examples for new features

### Testing

- **Unit tests**: Write tests for all new functionality
- **Integration tests**: Test component interactions
- **Edge cases**: Cover error conditions and edge cases
- **Performance**: Consider performance implications of changes

## 🔄 Development Workflow

### Branch Naming

Use descriptive branch names:
- `feature/add-new-formatter`
- `fix/cache-memory-leak`
- `docs/update-installation-guide`
- `refactor/improve-error-handling`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): brief description

Detailed description if needed

- List specific changes
- Include breaking changes if any
```

Examples:
- `feat(cache): add Redis cache backend support`
- `fix(server): handle connection timeouts gracefully`
- `docs(readme): update FastMCP client examples`
- `refactor(formatters): improve JSON formatter performance`

### Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** following the coding standards
3. **Update tests** and documentation
4. **Run the test suite** and ensure all tests pass
5. **Run linting and formatting** tools
6. **Submit a pull request** with:
   - Clear title and description
   - Link to related issues
   - Screenshots/examples if applicable
   - Testing instructions

## 🏗️ Project Structure

```
yet-sparql-mcp-server/
├── sparql_server/           # Main package
│   ├── core/               # Core functionality
│   ├── cache/              # Caching implementations
│   ├── formatters/         # Result formatters
│   └── __init__.py
├── tests/                  # Test files
├── .github/                # GitHub templates and workflows
├── docs/                   # Additional documentation
├── server.py               # Main entry point
├── setup.py                # Package configuration
├── pyproject.toml          # Modern Python packaging
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── README.md               # Project documentation
```

## 🐛 Debugging Tips

### Common Issues

- **Import errors**: Check PYTHONPATH and virtual environment
- **Connection issues**: Verify SPARQL endpoint accessibility
- **Performance problems**: Use profiling tools and check cache settings
- **Test failures**: Run tests individually to isolate issues

### Useful Commands

```bash
# Debug server startup
python server.py --endpoint https://dbpedia.org/sparql --log-level DEBUG

# Profile performance
python -m cProfile -o profile.stats server.py

# Check dependencies
pip list
pip check
```

## 📝 Documentation Guidelines

### API Documentation

- Document all public functions and classes
- Include parameter types and return values
- Provide usage examples
- Document exceptions that may be raised

### User Documentation

- Keep examples up-to-date
- Test all code examples
- Use clear, concise language
- Include troubleshooting sections

## ❓ Getting Help

If you need help or have questions:

1. **Check the documentation** and existing issues
2. **Ask in discussions** for general questions
3. **Create an issue** for bugs or feature requests
4. **Join our community** channels (if available)

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (AGPL-3.0 for open source use).

## 🙏 Recognition

Contributors will be acknowledged in:
- The project's contributor list
- Release notes for significant contributions
- The project's documentation

Thank you for contributing to the MCP SPARQL Server! 🚀