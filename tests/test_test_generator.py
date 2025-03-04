"""
Tests for the TestGenerator class.
"""
import os
import tempfile
import unittest
from pathlib import Path
from src.test_generator import TestGenerator

class TestTestGenerator(unittest.TestCase):
    """Tests for the TestGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = TestGenerator(output_dir=self.temp_dir)
        
    def test_init_sets_output_dir(self):
        """Test that __init__ sets the output directory."""
        self.assertEqual(self.generator.output_dir, self.temp_dir)
        self.assertTrue(os.path.exists(self.temp_dir))
        
    def test_generate_python_tests(self):
        """Test generating Python integration tests."""
        repo_path = os.path.join(self.temp_dir, "repo")
        os.makedirs(repo_path, exist_ok=True)
        
        # Create a mock Python file for analysis
        python_file = os.path.join(repo_path, "module.py")
        with open(python_file, 'w') as f:
            f.write("def function():\n    pass\n")
            
        # Create mock analysis results
        analysis_results = {
            "file_analyses": [
                {
                    "file": python_file,
                    "stats": {"lines": 2, "chars": 24},
                    "recommendations": ["Add more tests"]
                }
            ]
        }
        
        # Generate tests
        result = self.generator.generate_python_tests(repo_path, analysis_results)
        
        # Check that files were generated
        self.assertTrue(len(result) > 0)
        
        # Check that the test file exists
        test_file = next(iter(result.values()))
        self.assertTrue(os.path.exists(test_file))
        
        # Check the runner file
        runner_file = result.get("runner")
        self.assertTrue(os.path.exists(runner_file))
        
    def test_generate_test_cases_for_module(self):
        """Test generating test cases for a module."""
        module_name = "example.module"
        stats = {"lines": 10, "chars": 100}
        recommendations = ["Add more tests"]
        
        test_cases = self.generator._generate_test_cases_for_module(module_name, stats, recommendations)
        
        # Check that we have test cases
        self.assertTrue(len(test_cases) > 0)
        
        # Check the test case structure
        first_case = test_cases[0]
        self.assertIn("name", first_case)
        self.assertIn("description", first_case)
        self.assertIn("code", first_case)
        
        # Check the import test
        self.assertTrue(any("test_can_import" in case["name"] for case in test_cases))
        
        # Check the smoke test
        self.assertTrue(any("smoke_test" in case["name"] for case in test_cases))
        
        # Check the error handling test
        self.assertTrue(any("error_handling" in case["name"] for case in test_cases))
        
    def test_generate_python_test_file(self):
        """Test generating a Python test file."""
        module_name = "example.module"
        test_cases = [
            {
                "name": "test_example",
                "description": "Example test",
                "code": "def test_example():\n    assert True"
            }
        ]
        
        content = self.generator._generate_python_test_file(module_name, test_cases)
        
        # Check the content
        self.assertIn(f"Integration tests for {module_name}", content)
        self.assertIn("import pytest", content)
        self.assertIn("import sys", content)
        self.assertIn("setup_test_environment", content)
        self.assertIn("def test_example():", content)
        
    def test_generate_test_runner(self):
        """Test generating a test runner."""
        content = self.generator._generate_test_runner()
        
        # Check the content
        self.assertIn("#!/usr/bin/env python", content)
        self.assertIn("import pytest", content)
        self.assertIn("def main():", content)
        self.assertIn("if __name__ == '__main__':", content)
        
    def test_generate_javascript_tests(self):
        """Test generating JavaScript integration tests."""
        repo_path = os.path.join(self.temp_dir, "repo")
        os.makedirs(repo_path, exist_ok=True)
        
        # Create a mock JavaScript file for analysis
        js_file = os.path.join(repo_path, "module.js")
        with open(js_file, 'w') as f:
            f.write("function test() { return true; }\n")
            
        # Create mock analysis results
        analysis_results = {
            "file_analyses": [
                {
                    "file": js_file,
                    "stats": {"lines": 1, "chars": 32},
                    "recommendations": ["Add more tests"]
                }
            ]
        }
        
        # Generate tests
        result = self.generator.generate_javascript_tests(repo_path, analysis_results)
        
        # Check that files were generated
        self.assertTrue(len(result) > 0)
        
        # Check that the test file exists
        test_file = result.get("js_tests")
        self.assertTrue(os.path.exists(test_file))
        
        # Check the content
        with open(test_file, 'r') as f:
            content = f.read()
            self.assertIn("Integration tests", content)
            self.assertIn("describe(", content)
            self.assertIn("test(", content)
            
    def test_generate_from_suggestions(self):
        """Test generating tests from suggestions."""
        repo_path = os.path.join(self.temp_dir, "repo")
        os.makedirs(repo_path, exist_ok=True)
        
        # Create mock test suggestions
        test_suggestions = {
            "suggested_tests": [
                {
                    "target_file": f"{repo_path}/file1.py",
                    "test_type": "integration",
                    "suggested_test_cases": ["Test case 1", "Test case 2"]
                },
                {
                    "target_file": f"{repo_path}/file2.js",
                    "test_type": "integration",
                    "suggested_test_cases": ["Test case 3", "Test case 4"]
                }
            ],
            "general_advice": ["Focus on testing module boundaries"]
        }
        
        # Generate tests
        result = self.generator.generate_from_suggestions(repo_path, test_suggestions)
        
        # Check that files were generated
        self.assertTrue(len(result) > 0)
        
        # Check Python tests
        py_file = result.get("python")
        self.assertTrue(os.path.exists(py_file))
        
        # Check JavaScript tests
        js_file = result.get("javascript")
        self.assertTrue(os.path.exists(js_file))
        
        # Check README
        readme = result.get("readme")
        self.assertTrue(os.path.exists(readme))
        
    def test_generate_suggested_python_tests(self):
        """Test generating suggested Python tests."""
        suggestions = [
            {
                "target_file": "file1.py",
                "test_type": "integration",
                "suggested_test_cases": ["Test case 1", "Test case 2"]
            }
        ]
        
        content = self.generator._generate_suggested_python_tests(suggestions)
        
        # Check the content
        self.assertIn("Suggested integration tests", content)
        self.assertIn("import pytest", content)
        self.assertIn("def test_file1_1", content)
        self.assertIn("Test case 1", content)
        
    def test_generate_suggested_js_tests(self):
        """Test generating suggested JavaScript tests."""
        suggestions = [
            {
                "target_file": "file1.js",
                "test_type": "integration",
                "suggested_test_cases": ["Test case 1", "Test case 2"]
            }
        ]
        
        content = self.generator._generate_suggested_js_tests(suggestions)
        
        # Check the content
        self.assertIn("Suggested integration tests", content)
        self.assertIn("describe('Integration tests for file1'", content)
        self.assertIn("test('Test case 1'", content)
        
    def test_generate_test_readme(self):
        """Test generating a test README."""
        advice = ["Focus on testing module boundaries", "Test error cases"]
        content = self.generator._generate_test_readme(advice)
        
        # Check the content
        self.assertIn("# Integration Testing Guide", content)
        self.assertIn("- Focus on testing module boundaries", content)
        self.assertIn("- Test error cases", content)
        self.assertIn("## Best Practices", content)

if __name__ == '__main__':
    unittest.main()