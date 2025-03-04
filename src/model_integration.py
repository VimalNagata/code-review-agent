"""
Module for integrating with local AI models for code analysis.
"""
import os
import logging
from pathlib import Path
import torch  # Required for model inference

logger = logging.getLogger(__name__)

class ModelIntegration:
    """Class for handling local model integration."""
    
    def __init__(self, model_path):
        """
        Initialize the model integration.
        
        Args:
            model_path: Path to the local model
        """
        self.model_path = model_path
        self._model = None
        
        # Check if model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
            
        logger.info(f"Initializing model integration with model at {model_path}")
        
    def load_model(self):
        """
        Load the model.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading StarCoder model from {self.model_path}")
            # Import here to avoid requiring transformers when not using a model
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # Load the StarCoder tokenizer
            logger.info("Loading tokenizer...")
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            
            # Load the StarCoder model
            logger.info("Loading model (this may take a while)...")
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                device_map="auto"  # Automatically use available GPUs/CPUs
            )
            
            logger.info("StarCoder model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.error("Make sure you have the transformers library installed: pip install transformers")
            return False
            
    def analyze_file(self, file_path):
        """
        Analyze a single file using the loaded model.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Analysis results for the file
        """
        if not self._model:
            if not self.load_model():
                return {"error": "Failed to load model"}
                
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_stats = {
                "lines": len(content.split('\n')),
                "chars": len(content),
                "file_type": Path(file_path).suffix,
                "filename": Path(file_path).name
            }
            
            # Check if we have a real model or are using the mock
            if hasattr(self._model, 'generate'):
                logger.info(f"Analyzing {file_path} using StarCoder model")
                
                # Prepare the prompt for code analysis
                prompt = f"""
                Analyze the following code and provide recommendations for improvement:
                
                ```{file_stats['file_type']}
                {content[:2000]}  # Limit to first 2000 chars to fit in context window
                ```
                
                Provide recommendations in the following format:
                1. [Issue]: [Description]
                2. [Issue]: [Description]
                """
                
                # Tokenize the prompt
                inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
                
                # Generate the analysis
                with torch.no_grad():
                    output_ids = self._model.generate(
                        inputs["input_ids"],
                        max_new_tokens=500,
                        temperature=0.7,
                        top_p=0.95,
                        do_sample=True,
                        pad_token_id=self._tokenizer.eos_token_id
                    )
                
                # Decode the generated text
                generated_text = self._tokenizer.decode(output_ids[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
                
                # Extract recommendations from generated text
                recommendations = []
                for line in generated_text.strip().split('\n'):
                    if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                        recommendations.append(line.strip())
                
                # If no numbered recommendations were found, use the whole text
                if not recommendations:
                    recommendations = [line for line in generated_text.strip().split('\n') if line.strip()]
                
                # Add common recommendations based on file type
                recommendations.extend(self._get_file_type_recommendations(file_stats["file_type"]))
                    
                analysis = {
                    "file": str(file_path),
                    "stats": file_stats,
                    "model_analysis": generated_text.strip(),
                    "recommendations": recommendations
                }
            else:
                # Fallback to mock analysis if no real model is available
                logger.info(f"Using mock analysis for {file_path}")
                analysis = {
                    "file": str(file_path),
                    "stats": file_stats,
                    "recommendations": self._mock_recommendations(file_stats["file_type"])
                }
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return {"error": str(e), "file": str(file_path)}
    
    def _get_file_type_recommendations(self, file_type):
        """Get common recommendations for a specific file type."""
        common_recs = [
            "Add comprehensive documentation",
            "Ensure proper error handling"
        ]
        
        file_type_recs = {
            ".py": [
                "Use type hints for better code readability",
                "Consider breaking down complex functions"
            ],
            ".js": [
                "Add JSDoc comments for functions",
                "Consider using more modern ES6+ features"
            ],
            ".java": [
                "Follow Java naming conventions consistently",
                "Consider adding more unit tests"
            ]
        }
        
        return common_recs + file_type_recs.get(file_type, [])
            
    def _mock_recommendations(self, file_type):
        """Generate mock recommendations based on file type."""
        common_recs = [
            "Add more comprehensive documentation",
            "Consider adding more unit tests"
        ]
        
        type_specific_recs = {
            ".py": [
                "Use type hints for better code clarity",
                "Consider using dataclasses for data containers"
            ],
            ".js": [
                "Consider using TypeScript for better type safety",
                "Add JSDoc comments for better documentation"
            ],
            ".java": [
                "Follow Java naming conventions",
                "Consider using more interfaces for better abstraction"
            ],
            ".go": [
                "Follow Go error handling conventions",
                "Use more interfaces for better testability"
            ]
        }
        
        return common_recs + type_specific_recs.get(file_type, [])
            
    def analyze_repository(self, repo_path, file_patterns=None):
        """
        Analyze a repository using the loaded model.
        
        Args:
            repo_path: Path to the repository
            file_patterns: List of file patterns to include (e.g., ["*.py", "*.js"])
            
        Returns:
            Analysis results for the repository
        """
        if not self._model:
            if not self.load_model():
                return {"error": "Failed to load model"}
                
        if file_patterns is None:
            file_patterns = ["*.py", "*.js", "*.java", "*.go", "*.cpp", "*.h", "*.rs"]
            
        try:
            # Find all files matching the patterns
            all_files = []
            for pattern in file_patterns:
                all_files.extend(list(Path(repo_path).rglob(pattern)))
                
            # Limit the number of files for demonstration purposes
            all_files = all_files[:100]  # Analyze at most 100 files
            
            # Analyze each file
            file_analyses = []
            for file_path in all_files:
                logger.info(f"Analyzing file: {file_path}")
                file_analysis = self.analyze_file(file_path)
                file_analyses.append(file_analysis)
                
            # Generate repository-level analysis
            repo_analysis = {
                "repository": str(repo_path),
                "files_analyzed": len(file_analyses),
                "file_analyses": file_analyses,
                "overall_recommendations": self._generate_overall_recommendations(file_analyses)
            }
            
            return repo_analysis
        except Exception as e:
            logger.error(f"Error analyzing repository {repo_path}: {e}")
            return {"error": str(e), "repository": str(repo_path)}
            
    def _generate_overall_recommendations(self, file_analyses):
        """Generate overall recommendations based on file analyses."""
        # This is a placeholder for more sophisticated analysis
        # In a real implementation, you would aggregate insights from all files
        
        # Count recommendation frequencies
        rec_count = {}
        for analysis in file_analyses:
            if "recommendations" in analysis:
                for rec in analysis["recommendations"]:
                    rec_count[rec] = rec_count.get(rec, 0) + 1
                    
        # Sort by frequency
        sorted_recs = sorted(rec_count.items(), key=lambda x: x[1], reverse=True)
        
        # Return top recommendations
        top_recs = [rec for rec, _ in sorted_recs[:5]]
        
        # Add generic recommendations
        generic_recs = [
            "Consider implementing continuous integration",
            "Ensure test coverage for critical components",
            "Review error handling across the codebase"
        ]
        
        return top_recs + generic_recs
        
    def generate_integration_tests(self, repo_path, analysis_results):
        """
        Generate integration test suggestions based on code analysis.
        
        Args:
            repo_path: Path to the repository
            analysis_results: Results from code analysis
            
        Returns:
            Suggested integration tests
        """
        if not self._model:
            if not self.load_model():
                return {"error": "Failed to load model"}
        
        # Find potential test targets
        file_analyses = analysis_results.get("file_analyses", [])
        tests = []
        
        # Check if we have a real model or are using the mock
        if hasattr(self._model, 'generate'):
            logger.info("Using StarCoder model to generate test suggestions")
            
            # Process up to 5 files for test generation
            for analysis in file_analyses[:5]:
                file_path = analysis.get("file")
                
                # Skip non-code files
                if not file_path or not (file_path.endswith(".py") or file_path.endswith(".js") or file_path.endswith(".java")):
                    continue
                
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create a prompt for the model to generate test cases
                    prompt = f"""
                    Based on the following code, suggest 3 integration test cases:
                    
                    ```{Path(file_path).suffix}
                    {content[:1500]}  # Limit to first 1500 chars to fit in context window
                    ```
                    
                    Generate 3 integration test cases in the following format:
                    1. Test [functionality]: [description]
                    2. Test [functionality]: [description]
                    3. Test [functionality]: [description]
                    """
                    
                    # Tokenize the prompt
                    inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
                    
                    # Generate test suggestions
                    with torch.no_grad():
                        output_ids = self._model.generate(
                            inputs["input_ids"],
                            max_new_tokens=300,
                            temperature=0.8,
                            top_p=0.95,
                            do_sample=True,
                            pad_token_id=self._tokenizer.eos_token_id
                        )
                    
                    # Decode the generated text
                    generated_text = self._tokenizer.decode(output_ids[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
                    
                    # Extract test cases from generated text
                    test_cases = []
                    for line in generated_text.strip().split('\n'):
                        if line.strip().startswith(('1.', '2.', '3.')):
                            test_cases.append(line.strip())
                    
                    # If no numbered test cases were found, try to parse differently
                    if not test_cases:
                        # Extract paragraphs as test cases
                        paragraphs = [p.strip() for p in generated_text.split('\n\n') if p.strip()]
                        if paragraphs:
                            test_cases = [f"Test case {i+1}: {p}" for i, p in enumerate(paragraphs[:3])]
                    
                    # If still no test cases, add some defaults
                    if not test_cases:
                        test_cases = [
                            f"Test {Path(file_path).stem} integration with dependencies",
                            f"Test {Path(file_path).stem} error handling scenarios",
                            f"Test {Path(file_path).stem} with mock external services"
                        ]
                    
                    # Add to test suggestions
                    test_suggestion = {
                        "target_file": file_path,
                        "test_type": "integration",
                        "model_suggestions": generated_text.strip(),
                        "suggested_test_cases": test_cases
                    }
                    tests.append(test_suggestion)
                    
                except Exception as e:
                    logger.error(f"Error generating tests for {file_path}: {e}")
                    # Add default test suggestion on error
                    test_suggestion = {
                        "target_file": file_path,
                        "test_type": "integration",
                        "error": str(e),
                        "suggested_test_cases": [
                            f"Test {Path(file_path).stem} basic functionality",
                            f"Test {Path(file_path).stem} error handling",
                            f"Test {Path(file_path).stem} integration points"
                        ]
                    }
                    tests.append(test_suggestion)
        else:
            # Fallback to mock test generation
            logger.info("Using mock test generation")
            for analysis in file_analyses:
                file_path = analysis.get("file")
                if file_path and (file_path.endswith(".py") or file_path.endswith(".js") or file_path.endswith(".java")):
                    test_suggestion = {
                        "target_file": file_path,
                        "test_type": "integration",
                        "suggested_test_cases": [
                            f"Test {Path(file_path).stem} integration with other modules",
                            f"Test {Path(file_path).stem} error handling",
                            f"Test {Path(file_path).stem} performance under load"
                        ]
                    }
                    tests.append(test_suggestion)
        
        # Generate model-specific testing advice if we're using a real model
        if hasattr(self._model, 'generate'):
            try:
                advice_prompt = f"""
                Based on code analysis of {len(file_analyses)} files, provide 5 best practices 
                for writing effective integration tests. Format each practice on a new line starting with a dash (-).
                """
                
                # Tokenize the prompt
                inputs = self._tokenizer(advice_prompt, return_tensors="pt").to(self._model.device)
                
                # Generate advice
                with torch.no_grad():
                    output_ids = self._model.generate(
                        inputs["input_ids"],
                        max_new_tokens=200,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self._tokenizer.eos_token_id
                    )
                
                # Decode the generated text
                advice_text = self._tokenizer.decode(output_ids[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
                
                # Extract advice points
                advice = []
                for line in advice_text.strip().split('\n'):
                    if line.strip().startswith('-'):
                        advice.append(line.strip()[2:].strip())  # Remove dash and space
                
                # If no dash-prefixed advice found, use whole paragraphs
                if not advice:
                    advice = [line.strip() for line in advice_text.strip().split('\n') if line.strip()]
            except Exception as e:
                logger.error(f"Error generating testing advice: {e}")
                advice = [
                    "Focus on testing module boundaries",
                    "Test error cases and edge cases",
                    "Consider using mock objects for external dependencies",
                    "Keep tests independent from each other",
                    "Test both happy paths and failure scenarios"
                ]
        else:
            # Default advice
            advice = [
                "Focus on testing module boundaries",
                "Test error cases and edge cases",
                "Consider using mock objects for external dependencies",
                "Keep tests independent from each other",
                "Test both happy paths and failure scenarios"
            ]
                
        return {
            "suggested_tests": tests[:5],  # Limit to 5 test suggestions
            "general_advice": advice
        }