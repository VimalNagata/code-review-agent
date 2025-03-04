"""
Module for analyzing and visualizing codebase structure.
"""
import os
import logging
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from .code_graph import CodeGraph

logger = logging.getLogger(__name__)

class CodebaseAnalyzer:
    """Analyzes a codebase and provides insights based on code graph."""
    
    def __init__(self, repo_path: str, output_dir: str = None):
        """
        Initialize the analyzer.
        
        Args:
            repo_path: Path to the repository
            output_dir: Directory to store output files
        """
        self.repo_path = repo_path
        self.output_dir = output_dir or os.path.join(os.getcwd(), "analysis_output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.code_graph = None
        self.analysis_results = {}
        
    def build_code_graph(self, file_patterns: List[str] = None, use_cache: bool = True) -> CodeGraph:
        """
        Build the code graph for the repository.
        
        Args:
            file_patterns: List of file patterns to include
            use_cache: Whether to use cached graph if available
            
        Returns:
            Built code graph
        """
        cache_file = os.path.join(self.repo_path, ".code_review_cache", "code_graph.json")
        
        # Try to load from cache if requested
        if use_cache and os.path.exists(cache_file):
            try:
                logger.info(f"Loading code graph from cache: {cache_file}")
                self.code_graph = CodeGraph.load(cache_file)
                return self.code_graph
            except Exception as e:
                logger.warning(f"Failed to load cached code graph: {e}")
        
        # Build a new graph
        logger.info("Building code graph from repository")
        self.code_graph = CodeGraph(self.repo_path)
        self.code_graph.build_graph(file_patterns)
        
        # Save to cache
        try:
            self.code_graph.save()
            logger.info(f"Saved code graph to cache: {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to save code graph to cache: {e}")
        
        return self.code_graph
    
    def analyze_codebase(self) -> Dict[str, Any]:
        """
        Analyze the codebase using the built code graph.
        
        Returns:
            Analysis results
        """
        if not self.code_graph:
            raise ValueError("Code graph not built. Call build_code_graph() first.")
        
        logger.info("Analyzing codebase structure")
        
        # Collect stats
        stats = self.code_graph.get_stats()
        
        # Find central files
        central_files = self.code_graph.get_central_files(top_n=10)
        central_files_info = []
        for node_id, import_count in central_files:
            node = self.code_graph.get_node(node_id)
            if node:
                central_files_info.append({
                    "path": node.path,
                    "name": node.name,
                    "import_count": import_count
                })
        
        # Find cycles
        cycles = self.code_graph.find_cycles()
        cycle_info = []
        for cycle in cycles:
            cycle_nodes = []
            for node_id in cycle:
                node = self.code_graph.get_node(node_id)
                if node:
                    cycle_nodes.append(node.path)
            if cycle_nodes:
                cycle_info.append(cycle_nodes)
        
        # Gather insights
        insights = self._generate_insights(stats, central_files_info, cycle_info)
        
        # Store results
        self.analysis_results = {
            "stats": stats,
            "central_files": central_files_info,
            "cycles": cycle_info,
            "insights": insights
        }
        
        return self.analysis_results
    
    def _generate_insights(self, stats: Dict, central_files: List, cycles: List) -> List[str]:
        """Generate insights based on analysis."""
        insights = []
        
        # Stats-based insights
        if stats.get('total_files', 0) > 0:
            if stats.get('total_classes', 0) / stats.get('total_files', 1) > 3:
                insights.append("The codebase has a high class-to-file ratio, suggesting complex file organization")
            
            if stats.get('total_functions', 0) / stats.get('total_files', 1) > 10:
                insights.append("Files contain many functions, consider refactoring for better organization")
                
            if stats.get('total_imports', 0) / stats.get('total_files', 1) > 5:
                insights.append("High average import count suggests tight coupling between modules")
        
        # Central files insights
        if central_files:
            insights.append(f"The most central file is {central_files[0]['path']} with {central_files[0]['import_count']} imports")
            
            if len(central_files) > 3:
                top_files = ", ".join([f["path"] for f in central_files[:3]])
                insights.append(f"Key files to understand: {top_files}")
        
        # Cycles
        if cycles:
            insights.append(f"Found {len(cycles)} import cycles, which may indicate architectural issues")
            if len(cycles) > 0:
                cycle_example = " → ".join([os.path.basename(p) for p in cycles[0][:3]])
                insights.append(f"Example cycle: {cycle_example}...")
        
        # Architecture insights
        if 'languages' in stats:
            language_list = ", ".join([f"{lang} ({count})" for lang, count in stats['languages'].items()])
            insights.append(f"Codebase languages: {language_list}")
        
        if stats.get('inheritance_relationships', 0) > 0:
            insights.append(f"Found {stats.get('inheritance_relationships')} inheritance relationships")
        
        return insights
    
    def generate_graph_visualization(self, output_file: str = None) -> Optional[str]:
        """
        Generate a visualization of the code graph.
        
        Args:
            output_file: Path to save the visualization
            
        Returns:
            Path to the visualization file
        """
        if not self.code_graph:
            raise ValueError("Code graph not built. Call build_code_graph() first.")
        
        if output_file is None:
            output_file = os.path.join(self.output_dir, "code_graph.html")
        
        try:
            # Try to import visualization libraries
            import networkx as nx
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            
            # Create NetworkX graph
            G = nx.DiGraph()
            
            # Add nodes - use only file nodes to keep visualization manageable
            file_nodes = self.code_graph.get_nodes_by_type('file')
            for node in file_nodes:
                G.add_node(node.path, name=node.name, type=node.node_type)
            
            # Add edges - only imports between files
            for edge in self.code_graph.get_edges_by_type('imports'):
                source_node = self.code_graph.get_node(edge.source)
                target_node = self.code_graph.get_node(edge.target)
                if source_node and target_node:
                    if source_node.node_type == 'file' and target_node.node_type == 'file':
                        G.add_edge(source_node.path, target_node.path)
            
            # Generate visualization
            plt.figure(figsize=(12, 12))
            pos = nx.spring_layout(G, k=0.3, seed=42)
            nx.draw(G, pos, with_labels=True, node_size=500, node_color="skyblue", 
                    font_size=8, arrows=True, alpha=0.8, width=0.5)
            plt.title("Code Dependency Graph")
            
            # Save figure
            plt.savefig(output_file)
            plt.close()
            
            logger.info(f"Code graph visualization saved to {output_file}")
            return output_file
            
        except ImportError as e:
            logger.warning(f"Could not generate visualization: missing required libraries: {e}")
            logger.warning("Install networkx and matplotlib to enable visualization")
            return None
        except Exception as e:
            logger.warning(f"Failed to generate graph visualization: {e}")
            return None
    
    def generate_html_report(self, output_file: str = None) -> str:
        """
        Generate an HTML report of the analysis.
        
        Args:
            output_file: Path to save the report
            
        Returns:
            Path to the report file
        """
        if not self.analysis_results:
            raise ValueError("Analysis not performed. Call analyze_codebase() first.")
        
        if output_file is None:
            output_file = os.path.join(self.output_dir, "codebase_analysis.html")
        
        # Generate visualization for the report
        viz_file = None
        try:
            viz_path = self.generate_graph_visualization()
            if viz_path:
                viz_file = os.path.basename(viz_path)
        except Exception as e:
            logger.warning(f"Failed to generate visualization for report: {e}")
        
        # Prepare HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Codebase Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .card {{ background: #f8f9fa; border-radius: 5px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .insight {{ background-color: #e9f7ef; padding: 10px; border-left: 4px solid #27ae60; margin-bottom: 10px; }}
                .stats {{ display: flex; flex-wrap: wrap; }}
                .stat-item {{ flex: 1; min-width: 250px; margin: 10px; padding: 15px; background: #fff; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
                .stat-label {{ font-size: 14px; color: #7f8c8d; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .cycle {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Codebase Analysis Report</h1>
                <p>Repository: {self.repo_path}</p>
                
                <div class="card">
                    <h2>Key Insights</h2>
                    {''.join([f'<div class="insight">{insight}</div>' for insight in self.analysis_results['insights']])}
                </div>
                
                <div class="card">
                    <h2>Codebase Statistics</h2>
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-value">{self.analysis_results['stats'].get('total_files', 0)}</div>
                            <div class="stat-label">Total Files</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{self.analysis_results['stats'].get('total_classes', 0)}</div>
                            <div class="stat-label">Classes</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{self.analysis_results['stats'].get('total_functions', 0) + self.analysis_results['stats'].get('total_methods', 0)}</div>
                            <div class="stat-label">Functions & Methods</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{self.analysis_results['stats'].get('total_imports', 0)}</div>
                            <div class="stat-label">Import Relationships</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Key Files (Highest Import Count)</h2>
                    <table>
                        <tr>
                            <th>File</th>
                            <th>Import Count</th>
                        </tr>
                        {''.join([f'<tr><td>{file["path"]}</td><td>{file["import_count"]}</td></tr>' for file in self.analysis_results['central_files'][:10]])}
                    </table>
                </div>
        """
        
        # Add visualization if available
        if viz_file:
            html_content += f"""
                <div class="card">
                    <h2>Dependency Visualization</h2>
                    <img src="{viz_file}" alt="Code Dependency Graph" style="max-width: 100%;">
                    <p>Note: Only file-level dependencies are shown for clarity.</p>
                </div>
            """
        
        # Add cycle information if any
        if self.analysis_results['cycles']:
            html_content += f"""
                <div class="card">
                    <h2>Import Cycles</h2>
                    <p>{len(self.analysis_results['cycles'])} cycles detected. Circular dependencies may indicate design issues.</p>
                    <table>
                        <tr>
                            <th>#</th>
                            <th>Cycle</th>
                        </tr>
                        {''.join([f'<tr><td>{i+1}</td><td class="cycle">{" → ".join([os.path.basename(p) for p in cycle])}</td></tr>' for i, cycle in enumerate(self.analysis_results['cycles'][:5])])}
                    </table>
                </div>
            """
        
        # Close HTML document
        html_content += """
            </div>
        </body>
        </html>
        """
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML report at {output_file}")
        return output_file
    
    def export_json(self, output_file: str = None) -> str:
        """
        Export analysis results to JSON.
        
        Args:
            output_file: Path to save the JSON file
            
        Returns:
            Path to the JSON file
        """
        if not self.analysis_results:
            raise ValueError("Analysis not performed. Call analyze_codebase() first.")
        
        if output_file is None:
            output_file = os.path.join(self.output_dir, "codebase_analysis.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        logger.info(f"Exported analysis results to {output_file}")
        return output_file