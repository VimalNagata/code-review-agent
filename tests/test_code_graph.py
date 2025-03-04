"""
Tests for the CodeGraph class.
"""
import os
import unittest
import tempfile
import shutil
from pathlib import Path

try:
    from src.code_graph import CodeGraph
    TESTS_ENABLED = True
except ImportError:
    TESTS_ENABLED = False


@unittest.skipIf(not TESTS_ENABLED, "Code graph module not available")
class TestCodeGraph(unittest.TestCase):
    """Tests for the CodeGraph class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
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
        
        self.code_graph = CodeGraph(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        
    def test_add_node(self):
        """Test adding a node to the graph."""
        node_id = self.code_graph.add_node("test", "file", "test.py", {"key": "value"})
        self.assertIn(node_id, self.code_graph.nodes)
        self.assertEqual(self.code_graph.nodes[node_id].name, "test")
        self.assertEqual(self.code_graph.nodes[node_id].node_type, "file")
        self.assertEqual(self.code_graph.nodes[node_id].path, "test.py")
        self.assertEqual(self.code_graph.nodes[node_id].metadata, {"key": "value"})
        
    def test_add_edge(self):
        """Test adding an edge to the graph."""
        node1_id = self.code_graph.add_node("test1", "file", "test1.py")
        node2_id = self.code_graph.add_node("test2", "file", "test2.py")
        
        self.code_graph.add_edge(node1_id, node2_id, "imports", {"key": "value"})
        
        self.assertIn((node1_id, node2_id), self.code_graph.edges)
        self.assertEqual(self.code_graph.edges[(node1_id, node2_id)].source, node1_id)
        self.assertEqual(self.code_graph.edges[(node1_id, node2_id)].target, node2_id)
        self.assertEqual(self.code_graph.edges[(node1_id, node2_id)].edge_type, "imports")
        self.assertEqual(self.code_graph.edges[(node1_id, node2_id)].metadata, {"key": "value"})
        
    def test_get_nodes_by_type(self):
        """Test getting nodes by type."""
        self.code_graph.add_node("test1", "file", "test1.py")
        self.code_graph.add_node("test2", "class", "test2.py")
        self.code_graph.add_node("test3", "file", "test3.py")
        
        files = self.code_graph.get_nodes_by_type("file")
        self.assertEqual(len(files), 2)
        self.assertTrue(all(node.node_type == "file" for node in files))
        
        classes = self.code_graph.get_nodes_by_type("class")
        self.assertEqual(len(classes), 1)
        self.assertTrue(all(node.node_type == "class" for node in classes))
        
    def test_build_graph(self):
        """Test building a graph from the sample project."""
        self.code_graph.build_graph()
        
        # Check that nodes were created
        files = self.code_graph.get_nodes_by_type("file")
        self.assertGreater(len(files), 0, "No file nodes were created")
        
        classes = self.code_graph.get_nodes_by_type("class")
        self.assertGreater(len(classes), 0, "No class nodes were created")
        
        functions = self.code_graph.get_nodes_by_type("function")
        self.assertGreater(len(functions), 0, "No function nodes were created")
        
        # Check that edges were created
        import_edges = self.code_graph.get_edges_by_type("imports")
        self.assertGreater(len(import_edges), 0, "No import edges were created")
        
        # Check for inheritance edges
        inherit_edges = self.code_graph.get_edges_by_type("inherits")
        self.assertGreater(len(inherit_edges), 0, "No inheritance edges were created")
        
    def test_get_stats(self):
        """Test getting statistics about the graph."""
        self.code_graph.build_graph()
        stats = self.code_graph.get_stats()
        
        self.assertIn('total_files', stats)
        self.assertIn('total_classes', stats)
        self.assertIn('total_functions', stats)
        self.assertIn('total_methods', stats)
        self.assertIn('total_imports', stats)
        self.assertIn('languages', stats)
        
        self.assertGreater(stats['total_files'], 0)
        self.assertGreater(stats['total_classes'], 0)
        
    def test_save_and_load(self):
        """Test saving and loading a graph."""
        # Add some nodes and edges
        node1_id = self.code_graph.add_node("test1", "file", "test1.py")
        node2_id = self.code_graph.add_node("test2", "file", "test2.py")
        self.code_graph.add_edge(node1_id, node2_id, "imports")
        
        # Save the graph
        save_path = os.path.join(self.temp_dir, "graph.json")
        self.code_graph.save(save_path)
        
        # Load the graph
        loaded_graph = CodeGraph.load(save_path)
        
        # Check that the loaded graph is identical
        self.assertEqual(len(self.code_graph.nodes), len(loaded_graph.nodes))
        self.assertEqual(len(self.code_graph.edges), len(loaded_graph.edges))
        
        # Check node equality
        for node_id, node in self.code_graph.nodes.items():
            self.assertIn(node_id, loaded_graph.nodes)
            loaded_node = loaded_graph.nodes[node_id]
            self.assertEqual(node.name, loaded_node.name)
            self.assertEqual(node.node_type, loaded_node.node_type)
            self.assertEqual(node.path, loaded_node.path)
            
        # Check edge equality
        for edge_id, edge in self.code_graph.edges.items():
            self.assertIn(edge_id, loaded_graph.edges)
            loaded_edge = loaded_graph.edges[edge_id]
            self.assertEqual(edge.source, loaded_edge.source)
            self.assertEqual(edge.target, loaded_edge.target)
            self.assertEqual(edge.edge_type, loaded_edge.edge_type)


if __name__ == '__main__':
    unittest.main()