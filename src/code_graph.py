"""
Module for building and analyzing comprehensive code graphs.
"""
import os
import ast
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

logger = logging.getLogger(__name__)

class CodeNode:
    """Represents a node in the code graph (file, class, function)."""
    
    def __init__(self, name: str, node_type: str, path: str, metadata: Dict = None):
        """
        Initialize a code node.
        
        Args:
            name: Name of the node
            node_type: Type of node ('file', 'class', 'function')
            path: Path to the file containing this node
            metadata: Additional metadata for the node
        """
        self.name = name
        self.node_type = node_type
        self.path = path
        self.metadata = metadata or {}
        
    def __repr__(self) -> str:
        return f"CodeNode({self.name}, {self.node_type}, {self.path})"
        
    def to_dict(self) -> Dict:
        """Convert node to dictionary representation."""
        return {
            "name": self.name,
            "type": self.node_type,
            "path": self.path,
            "metadata": self.metadata
        }


class CodeEdge:
    """Represents an edge in the code graph (relationship between nodes)."""
    
    def __init__(self, source: str, target: str, edge_type: str, metadata: Dict = None):
        """
        Initialize a code edge.
        
        Args:
            source: Source node identifier
            target: Target node identifier
            edge_type: Type of edge ('imports', 'calls', 'inherits', etc.)
            metadata: Additional metadata for the edge
        """
        self.source = source
        self.target = target
        self.edge_type = edge_type
        self.metadata = metadata or {}
        
    def __repr__(self) -> str:
        return f"CodeEdge({self.source}, {self.target}, {self.edge_type})"
        
    def to_dict(self) -> Dict:
        """Convert edge to dictionary representation."""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.edge_type,
            "metadata": self.metadata
        }


class CodeGraph:
    """Represents the codebase as a graph of files, classes, and functions."""
    
    def __init__(self, repo_path: str):
        """
        Initialize the code graph.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = repo_path
        self.nodes: Dict[str, CodeNode] = {}  # node_id -> CodeNode
        self.edges: Dict[Tuple[str, str], CodeEdge] = {}  # (source, target) -> CodeEdge
        self.cache_dir = os.path.join(repo_path, ".code_review_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def add_node(self, name: str, node_type: str, path: str, metadata: Dict = None) -> str:
        """
        Add a node to the graph.
        
        Args:
            name: Name of the node
            node_type: Type of node ('file', 'class', 'function')
            path: Path to the file containing this node
            metadata: Additional metadata for the node
            
        Returns:
            Node identifier
        """
        # Create a unique identifier
        node_id = f"{node_type}:{path}:{name}"
        self.nodes[node_id] = CodeNode(name, node_type, path, metadata)
        return node_id
        
    def add_edge(self, source: str, target: str, edge_type: str, metadata: Dict = None) -> None:
        """
        Add an edge to the graph.
        
        Args:
            source: Source node identifier
            target: Target node identifier
            edge_type: Type of edge ('imports', 'calls', 'inherits', etc.)
            metadata: Additional metadata for the edge
        """
        if source in self.nodes and target in self.nodes:
            self.edges[(source, target)] = CodeEdge(source, target, edge_type, metadata)
            
    def get_node(self, node_id: str) -> Optional[CodeNode]:
        """Get a node by its identifier."""
        return self.nodes.get(node_id)
        
    def get_edge(self, source: str, target: str) -> Optional[CodeEdge]:
        """Get an edge by its source and target."""
        return self.edges.get((source, target))
        
    def get_nodes_by_type(self, node_type: str) -> List[CodeNode]:
        """Get all nodes of a specific type."""
        return [node for node_id, node in self.nodes.items() if node.node_type == node_type]
        
    def get_edges_by_type(self, edge_type: str) -> List[CodeEdge]:
        """Get all edges of a specific type."""
        return [edge for (src, tgt), edge in self.edges.items() if edge.edge_type == edge_type]
        
    def get_outgoing_edges(self, node_id: str) -> List[CodeEdge]:
        """Get all edges going out from a node."""
        return [edge for (src, tgt), edge in self.edges.items() if src == node_id]
        
    def get_incoming_edges(self, node_id: str) -> List[CodeEdge]:
        """Get all edges coming into a node."""
        return [edge for (src, tgt), edge in self.edges.items() if tgt == node_id]
        
    def get_dependencies(self, node_id: str) -> List[str]:
        """Get all nodes that this node depends on."""
        return [edge.target for edge in self.get_outgoing_edges(node_id)]
        
    def get_dependents(self, node_id: str) -> List[str]:
        """Get all nodes that depend on this node."""
        return [edge.source for edge in self.get_incoming_edges(node_id)]
        
    def to_dict(self) -> Dict:
        """Convert the graph to a dictionary representation."""
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": {f"{src}_{tgt}": edge.to_dict() for (src, tgt), edge in self.edges.items()},
            "repo_path": self.repo_path
        }
        
    def save(self, file_path: str = None) -> str:
        """
        Save the graph to a JSON file.
        
        Args:
            file_path: Path to save the file. If None, use default location.
            
        Returns:
            Path to the saved file
        """
        if file_path is None:
            file_path = os.path.join(self.cache_dir, "code_graph.json")
            
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
            
        return file_path
        
    @classmethod
    def load(cls, file_path: str) -> 'CodeGraph':
        """
        Load a graph from a JSON file.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            Loaded CodeGraph object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        graph = cls(data["repo_path"])
        
        # Add all nodes
        for node_id, node_data in data["nodes"].items():
            graph.nodes[node_id] = CodeNode(
                node_data["name"],
                node_data["type"], 
                node_data["path"],
                node_data["metadata"]
            )
            
        # Add all edges
        for edge_id, edge_data in data["edges"].items():
            source = edge_data["source"]
            target = edge_data["target"]
            graph.edges[(source, target)] = CodeEdge(
                source,
                target,
                edge_data["type"],
                edge_data["metadata"]
            )
            
        return graph
    
    def analyze_python_imports(self, file_path: str) -> List[Tuple[str, str]]:
        """
        Analyze Python imports in a file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            List of (import_name, import_type) tuples
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            try:
                tree = ast.parse(content)
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.append((name.name, 'direct'))
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            for name in node.names:
                                import_name = f"{node.module}.{name.name}" if node.module else name.name
                                imports.append((import_name, 'from'))
                
                return imports
            except SyntaxError:
                logger.warning(f"Failed to parse Python syntax in {file_path}")
                return []
        
        except Exception as e:
            logger.warning(f"Failed to analyze imports in {file_path}: {e}")
            return []
    
    def analyze_javascript_imports(self, file_path: str) -> List[Tuple[str, str]]:
        """
        Analyze JavaScript imports in a file.
        
        Args:
            file_path: Path to the JavaScript file
            
        Returns:
            List of (import_name, import_type) tuples
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            imports = []
            
            # ES6 imports
            es6_import_pattern = r'import\s+(?:{[^}]*}|[^{;]*)?\s*from\s+[\'"](.+?)[\'"]'
            es6_matches = re.findall(es6_import_pattern, content)
            for match in es6_matches:
                imports.append((match, 'es6'))
            
            # CommonJS require
            commonjs_pattern = r'(?:const|let|var)\s+.+?\s*=\s*require\([\'"](.+?)[\'"]\)'
            commonjs_matches = re.findall(commonjs_pattern, content)
            for match in commonjs_matches:
                imports.append((match, 'commonjs'))
            
            return imports
        
        except Exception as e:
            logger.warning(f"Failed to analyze imports in {file_path}: {e}")
            return []
    
    def analyze_class_hierarchy(self) -> Dict[str, List[str]]:
        """
        Analyze the class hierarchy in the codebase.
        
        Returns:
            Dictionary mapping class node IDs to lists of parent class node IDs
        """
        hierarchy = {}
        
        # Get all class nodes
        class_nodes = self.get_nodes_by_type('class')
        
        # Map class names to node IDs
        class_name_to_id = {}
        for node in class_nodes:
            class_name_to_id[node.name] = [node_id for node_id, n in self.nodes.items() 
                                         if n.name == node.name and n.node_type == 'class']
        
        # Find inheritance relationships
        for node_id, node in self.nodes.items():
            if node.node_type == 'class' and 'bases' in node.metadata:
                parent_classes = []
                for base in node.metadata['bases']:
                    if base in class_name_to_id:
                        parent_classes.extend(class_name_to_id[base])
                
                hierarchy[node_id] = parent_classes
                
                # Add inheritance edges
                for parent_id in parent_classes:
                    self.add_edge(node_id, parent_id, 'inherits')
        
        return hierarchy
    
    def analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a Python file and add its nodes and edges to the graph.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary with metadata about the file
        """
        rel_path = os.path.relpath(file_path, self.repo_path)
        file_node_id = self.add_node(os.path.basename(file_path), 'file', rel_path, {
            'language': 'python',
            'path': rel_path
        })
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content)
                
                # Analyze classes
                for cls_node in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
                    # Add class node
                    cls_node_id = self.add_node(cls_node.name, 'class', rel_path, {
                        'line': cls_node.lineno,
                        'bases': [base.id for base in cls_node.bases if isinstance(base, ast.Name)],
                        'docstring': ast.get_docstring(cls_node)
                    })
                    
                    # Add contains edge from file to class
                    self.add_edge(file_node_id, cls_node_id, 'contains')
                    
                    # Analyze methods
                    for method_node in [n for n in cls_node.body if isinstance(n, ast.FunctionDef)]:
                        # Add method node
                        method_node_id = self.add_node(method_node.name, 'method', rel_path, {
                            'line': method_node.lineno,
                            'args': [arg.arg for arg in method_node.args.args],
                            'docstring': ast.get_docstring(method_node),
                            'class': cls_node.name
                        })
                        
                        # Add contains edge from class to method
                        self.add_edge(cls_node_id, method_node_id, 'contains')
                
                # Analyze standalone functions
                for func_node in [n for n in ast.walk(tree) 
                                if isinstance(n, ast.FunctionDef) and not hasattr(n, 'parent') and not isinstance(n.parent, ast.ClassDef)]:
                    # Add function node
                    func_node_id = self.add_node(func_node.name, 'function', rel_path, {
                        'line': func_node.lineno,
                        'args': [arg.arg for arg in func_node.args.args],
                        'docstring': ast.get_docstring(func_node)
                    })
                    
                    # Add contains edge from file to function
                    self.add_edge(file_node_id, func_node_id, 'contains')
                
                # Analyze imports
                imports = self.analyze_python_imports(file_path)
                for import_name, import_type in imports:
                    # Try to resolve the import to a file in the codebase
                    import_path = self._resolve_python_import(import_name)
                    if import_path:
                        # Check if we have a node for this file
                        import_file_nodes = [node_id for node_id, node in self.nodes.items()
                                          if node.node_type == 'file' and node.path == import_path]
                        
                        if import_file_nodes:
                            import_file_node_id = import_file_nodes[0]
                        else:
                            # Add a node for the imported file
                            import_file_node_id = self.add_node(os.path.basename(import_path), 'file', import_path, {
                                'language': 'python',
                                'path': import_path
                            })
                        
                        # Add imports edge
                        self.add_edge(file_node_id, import_file_node_id, 'imports', {
                            'import_type': import_type
                        })
                
                return {
                    'language': 'python',
                    'path': rel_path,
                    'status': 'analyzed'
                }
                
            except SyntaxError:
                logger.warning(f"Failed to parse Python syntax in {file_path}")
                return {
                    'language': 'python',
                    'path': rel_path,
                    'status': 'syntax_error'
                }
                
        except Exception as e:
            logger.warning(f"Failed to analyze Python file {file_path}: {e}")
            return {
                'language': 'python',
                'path': rel_path,
                'status': 'error',
                'error': str(e)
            }
    
    def _resolve_python_import(self, import_name: str) -> Optional[str]:
        """
        Resolve a Python import to a file path.
        
        Args:
            import_name: Import name to resolve
            
        Returns:
            Relative path to the file, or None if not found
        """
        # Convert import path to file path
        import_path = import_name.replace('.', os.sep)
        
        # Check for direct file match
        potential_paths = [
            f"{import_path}.py",
            os.path.join(import_path, "__init__.py")
        ]
        
        for path in potential_paths:
            abs_path = os.path.join(self.repo_path, path)
            if os.path.exists(abs_path):
                return os.path.relpath(abs_path, self.repo_path)
        
        return None
    
    def build_graph(self, file_patterns: List[str] = None) -> None:
        """
        Build the code graph for the repository.
        
        Args:
            file_patterns: List of file patterns to include
        """
        if file_patterns is None:
            file_patterns = ["*.py", "*.js", "*.java"]
        
        # Find all files matching the patterns
        all_files = []
        for pattern in file_patterns:
            all_files.extend(list(Path(self.repo_path).rglob(pattern)))
        
        # Process each file
        for file_path in all_files:
            file_path_str = str(file_path)
            
            # Skip files in .git, venv, etc.
            if any(part.startswith(('.', 'venv', 'node_modules')) 
                  for part in file_path_str.split(os.sep)):
                continue
            
            # Process by file type
            if file_path_str.endswith('.py'):
                self.analyze_python_file(file_path_str)
            elif file_path_str.endswith('.js'):
                # Add JavaScript analysis later
                pass
            elif file_path_str.endswith('.java'):
                # Add Java analysis later
                pass
        
        # Analyze class hierarchy
        self.analyze_class_hierarchy()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the graph.
        
        Returns:
            Dictionary with graph statistics
        """
        file_nodes = self.get_nodes_by_type('file')
        class_nodes = self.get_nodes_by_type('class')
        function_nodes = self.get_nodes_by_type('function')
        method_nodes = self.get_nodes_by_type('method')
        
        import_edges = self.get_edges_by_type('imports')
        contains_edges = self.get_edges_by_type('contains')
        inherit_edges = self.get_edges_by_type('inherits')
        
        # Count by language
        languages = {}
        for node in file_nodes:
            lang = node.metadata.get('language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        return {
            'total_files': len(file_nodes),
            'total_classes': len(class_nodes),
            'total_functions': len(function_nodes),
            'total_methods': len(method_nodes),
            'total_imports': len(import_edges),
            'languages': languages,
            'inheritance_relationships': len(inherit_edges)
        }
    
    def get_central_files(self, top_n: int = 5) -> List[Tuple[str, int]]:
        """
        Get the most central files in the codebase (most imported).
        
        Args:
            top_n: Number of files to return
            
        Returns:
            List of (file_node_id, import_count) tuples
        """
        file_nodes = {node_id: node for node_id, node in self.nodes.items() 
                    if node.node_type == 'file'}
        
        # Count incoming imports for each file
        import_counts = {}
        for node_id in file_nodes:
            import_counts[node_id] = len(self.get_incoming_edges(node_id))
        
        # Sort by count
        sorted_files = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_files[:top_n]
    
    def find_cycles(self) -> List[List[str]]:
        """
        Find import cycles in the codebase.
        
        Returns:
            List of cycles (each cycle is a list of node IDs)
        """
        def dfs(node, visited, rec_stack, cycle):
            visited.add(node)
            rec_stack.add(node)
            
            for edge in self.get_outgoing_edges(node):
                if edge.edge_type == 'imports':
                    if edge.target not in visited:
                        if dfs(edge.target, visited, rec_stack, cycle):
                            return True
                    elif edge.target in rec_stack:
                        # Found a cycle
                        cycle.append(edge.target)
                        cycle.append(node)
                        return True
            
            rec_stack.remove(node)
            return False
        
        cycles = []
        file_nodes = {node_id: node for node_id, node in self.nodes.items() 
                      if node.node_type == 'file'}
        
        # Check each file node for cycles
        for node_id in file_nodes:
            visited = set()
            rec_stack = set()
            cycle = []
            
            if node_id not in visited:
                dfs(node_id, visited, rec_stack, cycle)
                
            if cycle:
                # Process cycle into the correct order
                cycles.append(cycle)
        
        return cycles