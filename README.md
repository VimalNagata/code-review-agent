# Code Review and Integration Test Agent

An agent that downloads a git repository, reviews the code using a locally downloaded LLM, and generates integration test cases for Python, JavaScript, and Java codebases.

## Features

- Downloads and analyzes git repositories
- Uses StarCoder or other local LLMs for code review
- Generates language-specific integration tests:
  - Python tests using pytest
  - JavaScript tests using Jest
  - Java tests using JUnit 5 and Mockito
- Provides detailed code recommendations and test suggestions
- Creates comprehensive summary reports

## Installation

```bash
# Clone the repository
git clone https://github.com/VimalNagata/code-review-agent.git
cd code-review-agent

# Install the package
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage (without model, uses mock analysis)
python -m src https://github.com/username/repo-to-analyze.git

# With a local model
python -m src https://github.com/username/repo-to-analyze.git --model ./model

# Specify output directory
python -m src https://github.com/username/repo-to-analyze.git --output ./my-output-dir

# Enable verbose output
python -m src https://github.com/username/repo-to-analyze.git -v
```

## Model Setup

The agent works best with code-specialized LLMs. See `model/DOWNLOAD_INSTRUCTIONS.md` for details on downloading and setting up:

- StarCoder
- StarCoder2-1B (lighter alternative)
- Other compatible Hugging Face models

## Components

- **CodeReviewAgent**: Main agent that coordinates repository analysis and test generation
- **ModelIntegration**: Integrates with local LLMs for code analysis and test suggestions
- **TestGenerator**: Generates language-specific integration tests

## Output

The agent generates:

- Summary report in Markdown format
- Detailed code analysis
- Language-specific integration tests
- Test recommendations based on code patterns

## Testing

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_agent.py
pytest tests/test_model_integration.py
pytest tests/test_test_generator.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License