# GUIDELINES.md - Development Guidelines

## Code Quality Standards

### General Guidelines
- All code should be production-ready and open source quality
- Follow PEP 8 style guidelines for Python code
- Maximum line length of 88 characters (Black formatter standard)
- Use type annotations throughout the codebase
- Include comprehensive docstrings for all modules, classes, and functions

### Naming Conventions
- Use descriptive, meaningful names for all variables, functions, and classes
- Class names: CamelCase (e.g., `SPARQLServer`, `ResultFormatter`)
- Function/method names: snake_case (e.g., `execute_query`, `format_results`)
- Variable names: snake_case (e.g., `endpoint_url`, `cache_enabled`)
- Constants: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`, `MAX_CACHE_SIZE`)
- Private methods/variables: prefix with underscore (e.g., `_get_cached_result`)

### Documentation
- Every function must have a docstring explaining:
  - What the function does
  - Parameters and their types
  - Return values and types
  - Exceptions that may be raised
- Include examples in docstrings for complex functions
- Add inline comments for complex logic
- Document design decisions and architecture

### Error Handling
- Use specific exception types
- Handle all potential errors gracefully
- Provide informative error messages
- Log errors appropriately

### Testing
- Write unit tests for all functionality
- Ensure tests cover edge cases and error scenarios
- Maintain high test coverage

### Configuration
- No hardcoded values - use configuration parameters
- Support environment variables for all settings
- Provide sensible defaults
- Validate configuration at startup

## Project Structure
- Modular design with separation of concerns
- Clear interfaces between components
- Minimize dependencies between modules

## Useful Commands
- Run tests: `python -m unittest discover`
- Check type hints: `mypy .`
- Format code: `black .`
- Lint code: `flake8 .`

## Development Workflow
1. Update code according to specification
2. Run linting and type checking
3. Add/update tests
4. Run tests to verify functionality
5. Document changes