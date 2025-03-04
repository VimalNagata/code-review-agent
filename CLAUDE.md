# Code Review Agent Commands and Guidelines

## Commands
- Install: `pip install -e .` or `pip install -r requirements.txt`
- Run all tests: `pytest tests/`
- Run a specific test file: `pytest tests/test_agent.py`
- Run a specific test: `pytest tests/test_agent.py::TestCodeReviewAgent::test_init_sets_output_dir`
- Run entry point script: `code-review-agent`

## Code Style
- **Imports**: Standard library first, third-party second, local modules last
- **Formatting**: 4-space indentation, 120 character line limit
- **Types**: Always use type hints for function parameters and return values
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Documentation**: All classes and methods require docstrings with parameter descriptions
- **Error Handling**: Use specific exception types; log errors appropriately
- **Testing**: Tests inherit from unittest.TestCase with descriptive method names

## Project Structure
- Source code in `src/`
- Tests in `tests/`
- Models in `model/`
- Main entry point: `src.agent:main`