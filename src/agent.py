"""
Agent that downloads a git repository, reviews the code using a local model,
and generates integration test cases.
"""
import os
import argparse
import tempfile
import subprocess
from pathlib import Path
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeReviewAgent:
    """Agent for reviewing code and generating integration tests."""
    
    def __init__(self, model_path=None, output_dir=None):
        """
        Initialize the agent.
        
        Args:
            model_path: Path to the local model
            output_dir: Directory to store output files
        """
        self.model_path = model_path
        self.output_dir = output_dir or os.path.join(os.getcwd(), "output")
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir}")
        
        # Check if model exists
        if model_path and not os.path.exists(model_path):
            logger.warning(f"Model not found at {model_path}")
        
    def clone_repository(self, repo_url, target_dir=None):
        """
        Clone a git repository.
        
        Args:
            repo_url: URL of the git repository
            target_dir: Directory to clone the repository into
            
        Returns:
            Path to the cloned repository
        """
        if target_dir is None:
            target_dir = tempfile.mkdtemp(prefix="repo_")
        
        logger.info(f"Cloning repository {repo_url} to {target_dir}")
        try:
            subprocess.run(
                ["git", "clone", repo_url, target_dir],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"Repository cloned successfully to {target_dir}")
            return target_dir
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clone repository: {e.stderr}")
            raise
            
    def analyze_code(self, repo_path):
        """
        Analyze the code in the repository using the local model.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Analysis results
        """
        logger.info(f"Analyzing code in {repo_path}")
        
        # This is where you would load and use your local model
        # For now, we'll just do a simple file scan
        if not self.model_path:
            logger.warning("No model specified, performing basic file analysis")
            return self._basic_file_analysis(repo_path)
        
        # Mock model analysis for now
        logger.info(f"Using model at {self.model_path} to analyze code")
        return {
            "summary": "Model-based code analysis would go here",
            "files_analyzed": self._count_files(repo_path),
            "recommendations": ["Use more descriptive variable names", 
                               "Add more documentation"]
        }
    
    def _basic_file_analysis(self, repo_path):
        """Basic file analysis without a model."""
        file_counts = {}
        total_lines = 0
        
        for ext in ['.py', '.js', '.java', '.cpp', '.h', '.go', '.rs']:
            files = list(Path(repo_path).rglob(f"*{ext}"))
            if files:
                file_counts[ext] = len(files)
                
                # Count lines in these files
                for file in files:
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            total_lines += len(f.readlines())
                    except Exception as e:
                        logger.warning(f"Couldn't read {file}: {e}")
        
        return {
            "summary": "Basic file analysis",
            "file_types": file_counts,
            "total_files": sum(file_counts.values()),
            "total_lines": total_lines
        }
    
    def _count_files(self, repo_path):
        """Count files in the repository."""
        return len(list(Path(repo_path).rglob("*")))
            
    def generate_integration_tests(self, repo_path, analysis_results):
        """
        Generate integration tests based on the code analysis.
        
        Args:
            repo_path: Path to the repository
            analysis_results: Results from the code analysis
            
        Returns:
            Path to the generated test files
        """
        logger.info("Generating integration tests")
        
        # Create a directory for the tests
        tests_dir = os.path.join(self.output_dir, "integration_tests")
        os.makedirs(tests_dir, exist_ok=True)
        
        # Load model integration if available
        if self.model_path:
            try:
                from src.model_integration import ModelIntegration
                model = ModelIntegration(self.model_path)
                test_suggestions = model.generate_integration_tests(repo_path, analysis_results)
                logger.info(f"Generated test suggestions using model: {len(test_suggestions.get('suggested_tests', []))} tests")
            except Exception as e:
                logger.error(f"Error generating test suggestions with model: {e}")
                test_suggestions = None
        else:
            test_suggestions = None
            
        # Generate tests using TestGenerator
        try:
            from src.test_generator import TestGenerator
            generator = TestGenerator(output_dir=tests_dir)
            
            # Generate tests for each language found in the repo
            test_files = {}
            
            # Look for Python files
            if any(file.endswith('.py') for file in analysis_results.get("file_types", {})):
                logger.info("Generating Python integration tests")
                python_tests = generator.generate_python_tests(repo_path, analysis_results, test_suggestions)
                test_files.update(python_tests)
                
            # Look for JavaScript files
            if any(file.endswith('.js') for file in analysis_results.get("file_types", {})):
                logger.info("Generating JavaScript integration tests")
                js_tests = generator.generate_javascript_tests(repo_path, analysis_results)
                test_files.update(js_tests)
                
            # Look for Java files
            if any(file.endswith('.java') for file in analysis_results.get("file_types", {})):
                logger.info("Generating Java integration tests")
                java_tests = generator.generate_java_tests(repo_path, analysis_results)
                test_files.update(java_tests)
                
            # Generate tests from model suggestions if available
            if test_suggestions:
                logger.info("Generating tests from model suggestions")
                suggestion_tests = generator.generate_from_suggestions(repo_path, test_suggestions)
                test_files.update(suggestion_tests)
                
            logger.info(f"Generated {len(test_files)} test files in {tests_dir}")
            
        except Exception as e:
            logger.error(f"Error generating tests with TestGenerator: {e}")
            
            # Fallback to simple template test file
            test_file = os.path.join(tests_dir, "test_integration.py")
            
            with open(test_file, 'w') as f:
                f.write("""
import unittest

class IntegrationTest(unittest.TestCase):
    def setUp(self):
        # Set up test environment
        pass
        
    def tearDown(self):
        # Clean up after tests
        pass
        
    def test_basic_integration(self):
        # A basic integration test
        self.assertTrue(True)
        
    # TODO: Generate more specific tests based on analysis
    
if __name__ == '__main__':
    unittest.main()
""")
            logger.info(f"Created fallback test file at {test_file}")
        
        return tests_dir
    
    def run(self, repo_url):
        """
        Run the full agent workflow.
        
        Args:
            repo_url: URL of the git repository
            
        Returns:
            Summary of the results
        """
        logger.info(f"Starting agent workflow for repository {repo_url}")
        
        # Clone the repository
        repo_path = self.clone_repository(repo_url)
        
        # Analyze the code
        analysis_results = self.analyze_code(repo_path)
        
        # Generate integration tests
        tests_path = self.generate_integration_tests(repo_path, analysis_results)
        
        # Save analysis results
        analysis_file = os.path.join(self.output_dir, "analysis_results.txt")
        with open(analysis_file, 'w') as f:
            f.write(f"Analysis Results for {repo_url}\n")
            f.write("=" * 50 + "\n\n")
            for key, value in analysis_results.items():
                f.write(f"{key}: {value}\n")
        
        # Save a summary report
        summary_file = os.path.join(self.output_dir, "summary_report.md")
        with open(summary_file, 'w') as f:
            f.write(f"# Code Review and Test Generation Report\n\n")
            f.write(f"Repository: {repo_url}\n\n")
            
            f.write("## Analysis Summary\n\n")
            if "summary" in analysis_results:
                f.write(f"{analysis_results['summary']}\n\n")
            
            if "file_types" in analysis_results:
                f.write("### File Types\n\n")
                for file_type, count in analysis_results.get("file_types", {}).items():
                    f.write(f"- {file_type}: {count} files\n")
                f.write("\n")
            
            f.write(f"Total Files Analyzed: {analysis_results.get('total_files', 0)}\n")
            f.write(f"Total Lines of Code: {analysis_results.get('total_lines', 0)}\n\n")
            
            f.write("## Top Recommendations\n\n")
            if "recommendations" in analysis_results:
                for i, rec in enumerate(analysis_results["recommendations"][:10], 1):
                    f.write(f"{i}. {rec}\n")
                
            f.write("\n## Generated Tests\n\n")
            f.write(f"Integration tests have been generated in: {tests_path}\n\n")
            
            f.write("### Test Files\n\n")
            if os.path.exists(tests_path):
                for root, dirs, files in os.walk(tests_path):
                    rel_path = os.path.relpath(root, tests_path)
                    if rel_path != ".":
                        f.write(f"**{rel_path}**\n\n")
                    
                    for file in files:
                        if rel_path == ".":
                            f.write(f"- {file}\n")
                        else:
                            f.write(f"- {os.path.join(rel_path, file)}\n")
            
            f.write("\n## Next Steps\n\n")
            f.write("1. Review the generated test files and implement the actual test logic\n")
            f.write("2. Integrate the tests into your project's test suite\n")
            f.write("3. Run the tests and fix any failing tests\n")
            f.write("4. Add more tests for uncovered code paths\n")
        
        logger.info(f"Generated summary report at {summary_file}")
        
        return {
            "repository": repo_url,
            "repo_path": repo_path,
            "analysis_file": analysis_file,
            "summary_file": summary_file,
            "tests_path": tests_path,
            "analysis_results": analysis_results
        }

def download_codellama(model_dir):
    """Download the CodeLlama model if it doesn't exist."""
    import os
    from pathlib import Path
    
    model_file = os.path.join(model_dir, "codellama-7b-instruct.Q4_K_M.gguf")
    if not os.path.exists(model_file):
        print("CodeLlama model not found. Downloading now (this may take a while)...")
        
        # Create the directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        
        try:
            # Try to use huggingface_hub if available
            try:
                from huggingface_hub import hf_hub_download
                print("Downloading CodeLlama using HuggingFace Hub...")
                hf_hub_download(
                    repo_id="TheBloke/CodeLlama-7B-Instruct-GGUF",
                    filename="codellama-7b-instruct.Q4_K_M.gguf",
                    local_dir=model_dir,
                    local_dir_use_symlinks=False
                )
                print(f"Model downloaded to {model_file}")
                return model_file
            except ImportError:
                print("huggingface_hub not installed, trying with requests...")
                
            # Fallback to direct download with requests
            import requests
            from tqdm import tqdm
            
            url = "https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF/resolve/main/codellama-7b-instruct.Q4_K_M.gguf"
            print(f"Downloading from {url}...")
            
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024 * 1024  # 1MB
            
            with open(model_file, 'wb') as f, tqdm(
                total=total_size, unit='B', unit_scale=True, desc="Downloading"
            ) as progress_bar:
                for data in response.iter_content(block_size):
                    f.write(data)
                    progress_bar.update(len(data))
            
            print(f"Model downloaded to {model_file}")
            return model_file
            
        except Exception as e:
            print(f"Error downloading model: {e}")
            print("Please download the model manually:")
            print("1. Visit: https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF")
            print("2. Download 'codellama-7b-instruct.Q4_K_M.gguf'")
            print(f"3. Save it to {model_dir}")
            if input("Continue without model? (y/n): ").lower() != 'y':
                sys.exit(1)
            return None
    else:
        print(f"CodeLlama model found at {model_file}")
        return model_file

def main():
    """Main entry point for the agent."""
    parser = argparse.ArgumentParser(description="Code Review and Integration Test Generator")
    parser.add_argument("repo_url", help="URL of the git repository to analyze")
    parser.add_argument("--model", help="Path to the local model or 'codellama' to use CodeLlama", default=None)
    parser.add_argument("--output", help="Output directory", default=None)
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--download-only", action="store_true", help="Only download the model, don't run analysis")
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    
    try:
        # Handle CodeLlama special case
        if args.model == 'codellama':
            model_dir = os.path.join(os.getcwd(), "model")
            model_path = download_codellama(model_dir)
            
            if args.download_only:
                print("Model download complete. Exiting as --download-only was specified.")
                sys.exit(0)
                
            args.model = model_dir
        else:
            # Check if model path is valid
            if args.model and not os.path.exists(args.model):
                print(f"Warning: Model path {args.model} does not exist.")
                if input("Continue without model? (y/n): ").lower() != 'y':
                    sys.exit(1)
        
        print(f"Starting code review and test generation for {args.repo_url}...")
        
        # Create agent and run
        agent = CodeReviewAgent(model_path=args.model, output_dir=args.output)
        results = agent.run(args.repo_url)
        
        # Print results
        print("\n✅ Agent completed successfully!")
        print(f"Repository: {results['repository']}")
        print(f"Repository cloned to: {results['repo_path']}")
        print(f"Analysis saved to: {results['analysis_file']}")
        print(f"Summary report: {results.get('summary_file', 'N/A')}")
        print(f"Integration tests generated at: {results['tests_path']}")
        
        print("\nTo view the results:")
        print(f"  - Open {results.get('summary_file', results['analysis_file'])} for the analysis summary")
        print(f"  - Browse {results['tests_path']} for the generated test files")
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("An unexpected error occurred")
        sys.exit(1)

if __name__ == "__main__":
    main()