"""
Tests for the ModelIntegration class.
"""
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

class TestModelIntegration(unittest.TestCase):
    """Tests for the ModelIntegration class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a mock model file
        self.model_path = os.path.join(self.temp_dir, "model")
        os.makedirs(self.model_path, exist_ok=True)
        
        # Import here to avoid FileNotFoundError for non-existent model path
        from src.model_integration import ModelIntegration
        self.ModelIntegration = ModelIntegration
        
        self.model = self.ModelIntegration(self.model_path)
        
    def test_init_checks_model_path(self):
        """Test that __init__ checks if the model path exists."""
        with self.assertRaises(FileNotFoundError):
            self.ModelIntegration("/path/does/not/exist")
            
    def test_load_model(self):
        """Test model loading."""
        result = self.model.load_model()
        self.assertTrue(result)
        self.assertIsNotNone(self.model._model)
        
    def test_analyze_file(self):
        """Test analyzing a file."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("print('Hello, world!')\n")
            
        # Analyze the file
        result = self.model.analyze_file(test_file)
        
        # Check the results
        self.assertIn("file", result)
        self.assertEqual(result["file"], test_file)
        self.assertIn("stats", result)
        self.assertEqual(result["stats"]["lines"], 1)
        self.assertEqual(result["stats"]["file_type"], ".py")
        
    def test_mock_recommendations(self):
        """Test generating mock recommendations."""
        # Python recommendations
        py_recs = self.model._mock_recommendations(".py")
        self.assertTrue(any("type hints" in rec for rec in py_recs))
        
        # JavaScript recommendations
        js_recs = self.model._mock_recommendations(".js")
        self.assertTrue(any("TypeScript" in rec for rec in js_recs))
        
        # Unknown file type
        unknown_recs = self.model._mock_recommendations(".xyz")
        self.assertTrue(len(unknown_recs) > 0)  # Common recommendations
        
    def test_analyze_repository(self):
        """Test analyzing a repository."""
        repo_path = os.path.join(self.temp_dir, "repo")
        os.makedirs(repo_path, exist_ok=True)
        
        # Create some test files
        files = [
            ("file1.py", "print('Hello')"),
            ("file2.py", "x = 1"),
            ("file3.js", "console.log('World')")
        ]
        
        for filename, content in files:
            with open(os.path.join(repo_path, filename), 'w') as f:
                f.write(content)
                
        # Analyze the repository
        result = self.model.analyze_repository(repo_path)
        
        # Check the results
        self.assertIn("repository", result)
        self.assertEqual(result["repository"], repo_path)
        self.assertIn("files_analyzed", result)
        self.assertEqual(result["files_analyzed"], 3)
        self.assertIn("file_analyses", result)
        self.assertEqual(len(result["file_analyses"]), 3)
        self.assertIn("overall_recommendations", result)
        
    def test_generate_overall_recommendations(self):
        """Test generating overall recommendations."""
        file_analyses = [
            {"recommendations": ["Add more documentation", "Use type hints"]},
            {"recommendations": ["Add more documentation", "Add more tests"]},
            {"recommendations": ["Use interfaces", "Add more tests"]}
        ]
        
        recommendations = self.model._generate_overall_recommendations(file_analyses)
        
        # Check that the most common recommendations are included
        self.assertIn("Add more documentation", recommendations)
        self.assertIn("Add more tests", recommendations)
        
        # Check that the generic recommendations are included
        self.assertTrue(any("continuous integration" in rec for rec in recommendations))
        
    def test_generate_integration_tests(self):
        """Test generating integration test suggestions."""
        repo_path = os.path.join(self.temp_dir, "repo")
        os.makedirs(repo_path, exist_ok=True)
        
        # Create analysis results
        analysis_results = {
            "file_analyses": [
                {"file": f"{repo_path}/file1.py"},
                {"file": f"{repo_path}/file2.js"},
                {"file": f"{repo_path}/file3.txt"}
            ]
        }
        
        # Generate test suggestions
        result = self.model.generate_integration_tests(repo_path, analysis_results)
        
        # Check the results
        self.assertIn("suggested_tests", result)
        self.assertIn("general_advice", result)
        
        # Check that only Python and JavaScript files have test suggestions
        test_files = [s["target_file"] for s in result["suggested_tests"]]
        self.assertTrue(any(".py" in f for f in test_files))
        self.assertTrue(any(".js" in f for f in test_files))
        self.assertFalse(any(".txt" in f for f in test_files))

if __name__ == '__main__':
    unittest.main()