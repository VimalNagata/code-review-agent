"""
Tests for the CodeReviewAgent.
"""
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from src.agent import CodeReviewAgent

class TestCodeReviewAgent(unittest.TestCase):
    """Tests for the CodeReviewAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.agent = CodeReviewAgent(output_dir=self.temp_dir)
        
    def test_init_sets_output_dir(self):
        """Test that __init__ sets the output directory."""
        self.assertEqual(self.agent.output_dir, self.temp_dir)
        
    @patch('subprocess.run')
    def test_clone_repository(self, mock_run):
        """Test repository cloning."""
        mock_run.return_value = MagicMock(returncode=0)
        repo_url = "https://github.com/example/repo.git"
        target_dir = os.path.join(self.temp_dir, "repo")
        
        result = self.agent.clone_repository(repo_url, target_dir)
        
        # Check that git clone was called with correct arguments
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0][0], "git")
        self.assertEqual(args[0][1], "clone")
        self.assertEqual(args[0][2], repo_url)
        self.assertEqual(args[0][3], target_dir)
        
        # Check that the function returned the target directory
        self.assertEqual(result, target_dir)
        
    def test_basic_file_analysis(self):
        """Test the basic file analysis function."""
        # Create a test file
        test_dir = os.path.join(self.temp_dir, "test_repo")
        os.makedirs(test_dir, exist_ok=True)
        
        test_file = os.path.join(test_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("print('Hello, world!')\n")
        
        # Run the analysis
        results = self.agent._basic_file_analysis(test_dir)
        
        # Check that the analysis found the file
        self.assertEqual(results["file_types"][".py"], 1)
        self.assertEqual(results["total_files"], 1)
        self.assertEqual(results["total_lines"], 1)
        
    def test_generate_integration_tests(self):
        """Test that integration tests are generated."""
        repo_path = os.path.join(self.temp_dir, "test_repo")
        os.makedirs(repo_path, exist_ok=True)
        
        analysis_results = {
            "summary": "Test analysis",
            "file_types": {".py": 1},
            "total_files": 1
        }
        
        tests_dir = self.agent.generate_integration_tests(repo_path, analysis_results)
        
        # Check that the tests directory was created
        self.assertTrue(os.path.exists(tests_dir))
        
        # Check that the test file was created
        test_file = os.path.join(tests_dir, "test_integration.py")
        self.assertTrue(os.path.exists(test_file))
        
        # Check the content of the test file
        with open(test_file, 'r') as f:
            content = f.read()
            self.assertIn("IntegrationTest", content)
            self.assertIn("setUp", content)
            self.assertIn("test_basic_integration", content)
        
    @patch('src.agent.CodeReviewAgent.clone_repository')
    @patch('src.agent.CodeReviewAgent.analyze_code')
    @patch('src.agent.CodeReviewAgent.generate_integration_tests')
    def test_run(self, mock_generate_tests, mock_analyze, mock_clone):
        """Test the run method."""
        # Set up mocks
        repo_url = "https://github.com/example/repo.git"
        mock_clone.return_value = os.path.join(self.temp_dir, "repo")
        mock_analyze.return_value = {"summary": "Test analysis"}
        mock_generate_tests.return_value = os.path.join(self.temp_dir, "tests")
        
        # Run the agent
        results = self.agent.run(repo_url)
        
        # Check that all steps were called
        mock_clone.assert_called_once_with(repo_url)
        mock_analyze.assert_called_once()
        mock_generate_tests.assert_called_once()
        
        # Check that the results contain the expected keys
        self.assertIn("repository", results)
        self.assertIn("repo_path", results)
        self.assertIn("analysis_file", results)
        self.assertIn("tests_path", results)
        self.assertIn("analysis_results", results)
        
        # Check that the analysis file was created
        self.assertTrue(os.path.exists(results["analysis_file"]))

if __name__ == '__main__':
    unittest.main()