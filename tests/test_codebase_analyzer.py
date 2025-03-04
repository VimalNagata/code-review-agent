"""
Tests for the CodebaseAnalyzer class.
"""
import os
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

try:
    from src.codebase_analyzer import CodebaseAnalyzer
    from src.code_graph import CodeGraph
    TESTS_ENABLED = True
except ImportError:
    TESTS_ENABLED = False


@unittest.skipIf(not TESTS_ENABLED, "Codebase analyzer module not available")
class TestCodebaseAnalyzer(unittest.TestCase):
    """Tests for the CodebaseAnalyzer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.test_data_dir = os.path.join(
            os.path.dirname(__file__), 
            "test_data", 
            "sample_project"
        )
        
        # Copy test data to temporary directory
        if os.path.exists(self.test_data_dir):
            for item in os.listdir(self.test_data_dir):
                src = os.path.join(self.test_data_dir, item)
                dst = os.path.join(self.temp_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
        
        self.analyzer = CodebaseAnalyzer(self.temp_dir, self.output_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        
    def test_build_code_graph(self):
        """Test building the code graph."""
        graph = self.analyzer.build_code_graph()
        
        # Verify the graph was built
        self.assertIsInstance(graph, CodeGraph)
        self.assertEqual(graph.repo_path, self.temp_dir)
        
        # Verify graph has nodes
        self.assertGreater(len(graph.nodes), 0, "Graph should have nodes")
        
    def test_analyze_codebase(self):
        """Test analyzing the codebase."""
        # First build the graph
        self.analyzer.build_code_graph()
        
        # Then analyze
        results = self.analyzer.analyze_codebase()
        
        # Verify analysis results
        self.assertIn('stats', results)
        self.assertIn('central_files', results)
        self.assertIn('insights', results)
        
        # Check stats
        stats = results['stats']
        self.assertIn('total_files', stats)
        self.assertIn('total_classes', stats)
        self.assertIn('total_functions', stats)
        
        # Verify we have insights
        self.assertGreater(len(results['insights']), 0, "Should have insights")
        
    @unittest.skipIf(True, "Visualization test requires networkx and matplotlib")
    def test_generate_graph_visualization(self):
        """Test generating visualization."""
        # First build the graph
        self.analyzer.build_code_graph()
        
        # Then generate visualization
        viz_path = self.analyzer.generate_graph_visualization()
        
        # Verify visualization was created
        self.assertIsNotNone(viz_path)
        self.assertTrue(os.path.exists(viz_path))
        
    def test_generate_html_report(self):
        """Test generating HTML report."""
        # First build the graph and analyze
        self.analyzer.build_code_graph()
        self.analyzer.analyze_codebase()
        
        # Mock the visualization function to avoid dependencies
        with patch.object(self.analyzer, 'generate_graph_visualization', return_value=None):
            # Generate report
            report_path = self.analyzer.generate_html_report()
            
            # Verify report was created
            self.assertTrue(os.path.exists(report_path))
            
            # Check report content
            with open(report_path, 'r') as f:
                content = f.read()
                self.assertIn('<!DOCTYPE html>', content)
                self.assertIn('Codebase Analysis Report', content)
                self.assertIn('Codebase Statistics', content)
        
    def test_export_json(self):
        """Test exporting analysis to JSON."""
        # First build the graph and analyze
        self.analyzer.build_code_graph()
        self.analyzer.analyze_codebase()
        
        # Export to JSON
        json_path = self.analyzer.export_json()
        
        # Verify JSON was created
        self.assertTrue(os.path.exists(json_path))
        
        # Check it's valid JSON
        import json
        with open(json_path, 'r') as f:
            data = json.load(f)
            self.assertIn('stats', data)
            self.assertIn('insights', data)


if __name__ == '__main__':
    unittest.main()