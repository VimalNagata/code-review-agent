# Code Review and Integration Test Agent

An agent that downloads a git repository, reviews the code using a locally downloaded model, and generates integration test cases.

## Features

- Download and analyze git repositories
- Analyze code using a local AI model
- Generate integration tests based on code analysis
- Support for Python and JavaScript codebases
- Detailed code recommendations

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/code-review-agent.git
cd code-review-agent

# Install the package
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage with default model path
python -m src https://github.com/example/repo-to-analyze.git

# Specify a local model
python -m src https://github.com/example/repo-to-analyze.git --model /path/to/your/model

# Specify output directory
python -m src https://github.com/example/repo-to-analyze.git --output ./output-dir
```

## Components

- **CodeReviewAgent**: Main agent that coordinates downloading and analyzing repositories
- **ModelIntegration**: Handles integration with local AI models
- **TestGenerator**: Generates integration tests based on analysis

## Output

The agent generates the following outputs:

- Code analysis report
- Integration test files
- Test recommendations

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